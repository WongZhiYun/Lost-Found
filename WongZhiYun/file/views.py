from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import login_required, current_user
from .models import Post, db
from werkzeug.utils import secure_filename
import os

views = Blueprint('views', __name__)

@views.route('/')
def home():
    if current_user.is_authenticated:
        return render_template("base.html", username=current_user.username)
    else:
        return render_template("base.html", username=None)
    
@views.route('/report', methods=['GET', 'POST'])
def report_post():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        location = request.form.get('location')
        date = request.form.get('date')

        # handle image
        image_file = request.files.get('image')
        filename = None
        if image_file:
            filename = secure_filename(image_file.filename)
            upload_path = os.path.join(current_app.root_path, 'static/uploads', filename)
            image_file.save(upload_path)

        # save to database
        new_post = Post(
            title=title,
            description=description,
            type=status,
            category=location,
            image=filename,
            author = current_user
        )
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('views.feed'))

    return render_template('report.html')

@views.route('/feed')
def feed():
    filter_type = request.args.get('type', 'all')
    
    if filter_type == 'lost':
        posts = Post.query.filter_by(type='lost').order_by(Post.date_posted.desc()).all()
    elif filter_type == 'found':
        posts = Post.query.filter_by(type='found').order_by(Post.date_posted.desc()).all()
    else:
        posts = Post.query.order_by(Post.date_posted.desc()).all()

    return render_template("feed.html", posts=posts, filter_type=filter_type)



