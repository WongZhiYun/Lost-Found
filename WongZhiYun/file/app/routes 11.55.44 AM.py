from flask import Blueprint, request, render_template, current_app, url_for, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import imagehash
import os

from app import db
from app.models import Report

# 创建蓝图
bp = Blueprint('search', __name__, template_folder='templates')

# 获取上传文件夹路径（用于保存用户上传的图片）
def get_upload_folder():
    return current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'static', 'uploads'))

# 计算图像哈希（pHash）
def compute_image_hash(image_path):
    img = Image.open(image_path).convert('RGB')
    h = imagehash.phash(img)
    return str(h)

# 计算两张图片哈希值的汉明距离（距离越小，越相似）
def hamming_distance_hex(hash_hex1, hash_hex2):
    if not hash_hex1 or not hash_hex2:
        return None
    try:
        h1 = imagehash.hex_to_hash(hash_hex1)
        h2 = imagehash.hex_to_hash(hash_hex2)
        return h1 - h2
    except Exception:
        return None

# 根据距离计算图像相似度（0~1之间）
def image_similarity_from_distance(distance, hash_hex):
    if distance is None:
        return 0.0
    try:
        bits = imagehash.hex_to_hash(hash_hex).hash.size
    except Exception:
        bits = 64  # 默认 8x8 的哈希值，即 64 bits
    sim = max(0.0, 1.0 - (distance / bits))
    return sim

# 简单的文本得分计算
def simple_text_score(item, q):
    if not q:
        return 0.0
    q_lower = q.lower()
    score = 0.0
    if getattr(item, 'title', None) and q_lower in item.title.lower():
        score += 0.6
    if getattr(item, 'description', None) and q_lower in item.description.lower():
        score += 0.4
    if getattr(item, 'place', None) and q_lower in item.place.lower():
        score += 0.2
    return min(score, 1.0)

# 合并文本得分和图像得分（基于权重 alpha）
def combine_scores(text_score, image_score, alpha=0.6):
    return alpha * image_score + (1 - alpha) * text_score

# 关键词搜索页面
@bp.route('/', methods=['GET'])
def search_page():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    page = max(1, int(request.args.get('page', 1)))
    per_page = 10

    query = Report.query
    # 只显示已审核的报告
    query = query.filter(Report.status == 'approved')

    if category:
        query = query.filter(Report.category == category)

    if q:
        like_q = f"%{q}%"
        query = query.filter(
            (Report.title.ilike(like_q)) |
            (Report.description.ilike(like_q)) |
            (Report.place.ilike(like_q))
        )

    total = query.count()
    results = query.order_by(Report.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()

    scored = []
    for r in results:
        ts = simple_text_score(r, q)
        scored.append({'report': r, 'text_score': ts, 'image_score': 0.0, 'final_score': ts})

    scored_sorted = sorted(scored, key=lambda x: x['final_score'], reverse=True)

    return render_template('search/results.html', results=scored_sorted, q=q, category=category, page=page, total=total)

# 搜索 API (返回 JSON 数据)
@bp.route('/api', methods=['GET'])
def search_api():
    """
    JSON API: 返回基本字段 + text_score + image_hash。
    """
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    query = Report.query
    query = query.filter(Report.status == 'approved')

    if category:
        query = query.filter(Report.category == category)
    if q:
        like_q = f"%{q}%"
        query = query.filter(
            (Report.title.ilike(like_q)) |
            (Report.description.ilike(like_q)) |
            (Report.place.ilike(like_q))
        )

    results = query.order_by(Report.created_at.desc()).limit(200).all()
    data = []
    for r in results:
        ts = simple_text_score(r, q)
        data.append({
            'id': r.id,
            'title': r.title,
            'category': r.category,
            'place': r.place,
            'image': url_for('static', filename='uploads/' + (r.image_filename or '')) if r.image_filename else None,
            'text_score': ts,
            'image_hash': r.image_hash
        })
    return jsonify({'results': data})

# 上传图片搜索
@bp.route('/by-image', methods=['POST'])
def search_by_image():
    """
    图片上传 -> 计算哈希值 -> 与数据库中的图像哈希值进行比较 -> 展示结果。
    """
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # 保存上传的图片
    filename = secure_filename(file.filename)
    upload_folder = get_upload_folder()
    os.makedirs(upload_folder, exist_ok=True)
    saved_path = os.path.join(upload_folder, filename)
    file.save(saved_path)

    try:
        query_hash = compute_image_hash(saved_path)
    except Exception as e:
        current_app.logger.error(f"Hash compute error: {e}")
        return "Error processing image", 500

    candidates = Report.query.filter(Report.status == 'approved').all()

    scored = []
    for r in candidates:
        if not r.image_hash:
            distance = None
            img_score = 0.0
        else:
            distance = hamming_distance_hex(query_hash, r.image_hash)
            img_score = image_similarity_from_distance(distance, query_hash)
        scored.append({'report': r, 'image_distance': distance, 'image_score': img_score, 'text_score': 0.0, 'final_score': img_score})

    # 显示最相似的前20条结果
    scored_sorted = sorted(scored, key=lambda x: x['final_score'], reverse=True)[:20]

    return render_template('search/results.html', results=scored_sorted, q='[image search]', category='')

# 组合搜索（关键词 + 图像）+ alpha
@bp.route('/combined', methods=['POST'])
def combined_search():
    """
    接收 q（可选）+ 文件（可选）+ alpha（图像得分的权重）。
    合并 text_score 和 image_score 计算 final_score，并展示结果。
    """
    q = request.form.get('q', '').strip()
    category = request.form.get('category', '').strip()
    alpha = float(request.form.get('alpha', 0.6))

    query_hash = None
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        filename = secure_filename(file.filename)
        upload_folder = get_upload_folder()
        os.makedirs(upload_folder, exist_ok=True)
        saved_path = os.path.join(upload_folder, filename)
        file.save(saved_path)
        try:
            query_hash = compute_image_hash(saved_path)
        except Exception as e:
            current_app.logger.error(f"Hash compute error: {e}")
            query_hash = None

    query = Report.query.filter(Report.status == 'approved')
    if category:
        query = query.filter(Report.category == category)
    if q:
        like_q = f"%{q}%"
        query = query.filter(
            (Report.title.ilike(like_q)) |
            (Report.description.ilike(like
