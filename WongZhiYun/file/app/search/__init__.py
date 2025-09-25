import os
from flask import Blueprint, request, render_template, current_app, url_for, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import imagehash

from app import db
from app.models import Report

bp = Blueprint('search', __name__, template_folder='templates')

# ---------- helpers ----------
def get_upload_folder():
    return current_app.config.get('UPLOAD_FOLDER', os.path.abspath(os.path.join(current_app.root_path, 'static', 'uploads')))

def compute_image_hash(image_path):
    img = Image.open(image_path).convert('RGB')
    h = imagehash.phash(img)
    return str(h)

def hamming_distance_hex(hash_hex1, hash_hex2):
    if not hash_hex1 or not hash_hex2:
        return None
    try:
        h1 = imagehash.hex_to_hash(hash_hex1)
        h2 = imagehash.hex_to_hash(hash_hex2)
        return h1 - h2
    except Exception:
        return None

def image_similarity_from_distance(distance, hash_hex):
    if distance is None:
        return 0.0
    try:
        bits = imagehash.hex_to_hash(hash_hex).hash.size
    except Exception:
        bits = 64
    sim = max(0.0, 1.0 - (distance / bits))
    return sim

def simple_text_score(item, q):
    if not q:
        return 0.0
    q_lower = q.lower()
    score = 0.0
    if getattr(item, 'title', None) and q_lower in item.title.lower():
        score += 0.6
    if getattr(item, 'description', None) and q_lower in item.description.lower():
        score += 0.4
    if getattr(item, 'location', None) and q_lower in item.location.lower():
        score += 0.2
    return min(score, 1.0)

def combine_scores(text_score, image_score, alpha=0.6):
    return alpha * image_score + (1 - alpha) * text_score

# ---------- routes ----------
@bp.route('/', methods=['GET'])
def search_page():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    page = max(1, int(request.args.get('page', 1)))
    per_page = 10

    query = Report.query.filter(Report.is_approved == True)

    if category:
        query = query.filter(Report.category == category)

    if q:
        like_q = f"%{q}%"
        query = query.filter(
            (Report.title.ilike(like_q)) |
            (Report.description.ilike(like_q)) |
            (Report.location.ilike(like_q))
        )

    total = query.count()
    results = query.order_by(Report.date_posted.desc()).offset((page-1)*per_page).limit(per_page).all()

    scored = []
    for r in results:
        ts = simple_text_score(r, q)
        scored.append({'report': r, 'text_score': ts, 'image_score': 0.0, 'final_score': ts})

    scored_sorted = sorted(scored, key=lambda x: x['final_score'], reverse=True)
    return render_template('search/results.html', results=scored_sorted, q=q, category=category, page=page, total=total)

@bp.route('/api', methods=['GET'])
def search_api():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    query = Report.query.filter(Report.is_approved == True)

    if category:
        query = query.filter(Report.category == category)
    if q:
        like_q = f"%{q}%"
        query = query.filter(
            (Report.title.ilike(like_q)) |
            (Report.description.ilike(like_q)) |
            (Report.location.ilike(like_q))
        )

    results = query.order_by(Report.date_posted.desc()).limit(200).all()
    data = []
    for r in results:
        ts = simple_text_score(r, q)
        data.append({
            'id': r.id,
            'title': r.title,
            'category': r.category,
            'location': r.location,
            'image': url_for('static', filename='uploads/' + (r.image or '')) if r.image else None,
            'text_score': ts,
            'image_hash': r.image_hash
        })
    return jsonify({'results': data})

@bp.route('/by-image', methods=['POST'])
def search_by_image():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

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

    candidates = Report.query.filter(Report.is_approved == True).all()
    scored = []
    for r in candidates:
        if not r.image_hash:
            distance = None
            img_score = 0.0
        else:
            distance = hamming_distance_hex(query_hash, r.image_hash)
            img_score = image_similarity_from_distance(distance, query_hash)
        scored.append({'report': r, 'image_distance': distance, 'image_score': img_score, 'text_score': 0.0, 'final_score': img_score})

    scored_sorted = sorted(scored, key=lambda x: x['final_score'], reverse=True)[:20]
    return render_template('search/results.html', results=scored_sorted, q='[image search]', category='')

@bp.route('/combined', methods=['POST'])
def combined_search():
    q = request.form.get('q', '').strip()
    category = request.form.get('category', '').strip()
    alpha = 0.6 

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

    query = Report.query.filter(Report.is_approved == True)
    if category:
        query = query.filter(Report.category == category)
    if q:
        like_q = f"%{q}%"
        query = query.filter(
            (Report.title.ilike(like_q)) |
            (Report.description.ilike(like_q)) |
            (Report.location.ilike(like_q))
        )

    candidates = query.order_by(Report.date_posted.desc()).limit(200).all()
    scored = []
    for r in candidates:
        ts = simple_text_score(r, q) if q else 0.0
        if query_hash and r.image_hash:
            distance = hamming_distance_hex(query_hash, r.image_hash)
            iscore = image_similarity_from_distance(distance, query_hash)
        else:
            iscore = 0.0
        final = combine_scores(ts, iscore, alpha=alpha)
        scored.append({'report': r, 'text_score': ts, 'image_score': iscore, 'final_score': final})

    scored_sorted = sorted(scored, key=lambda x: x['final_score'], reverse=True)
    return render_template('search/results.html', results=scored_sorted, q=q, category=category)
