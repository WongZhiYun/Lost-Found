from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from .models import Post, db, Comment, User
from werkzeug.utils import secure_filename
import os
from sqlalchemy import func


views = Blueprint('views', __name__)

@views.route('/')
def home():
    if current_user.is_authenticated:
        return render_template("home.html", username=current_user.username)
    else:
        return render_template("home.html", username=None)
    
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
            location=location,
            image=filename,
            author = current_user,
            is_approved=False
            )
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('views.feed'))

    return render_template('report.html')

@views.route('/feed')
def feed():
    filter_type = request.args.get('type', 'all')
    
    if filter_type == 'lost':
        posts = Post.query.filter_by(type='lost',is_approved=True).order_by(Post.date_posted.desc()).all()
    elif filter_type == 'found':
        posts = Post.query.filter_by(type='found',is_approved=True).order_by(Post.date_posted.desc()).all()
    else:
        posts = Post.query.filter_by(is_approved=True).order_by(Post.date_posted.desc()).all()

    return render_template("feed.html", posts=posts, filter_type=filter_type)


@views.route('/my_posts')
@login_required
def my_posts():
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).all()
    return render_template('feed.html',posts=posts,filter_type='all')

@views.route('/profile')
@login_required
def profile():
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).all()
    return render_template('profile.html', user=current_user, posts=posts)


@views.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        profile_image = request.files.get('profile_image')
        

        if profile_image:
            filename = secure_filename(profile_image.filename)
            upload_path = os.path.join(current_app.root_path, 'static/profile_pics', filename)
            profile_image.save(upload_path)
            current_user.profile_image = filename

        # Update username & email
        if new_username:
            current_user.username = new_username
        if new_email:
            current_user.email = new_email
     

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('views.profile'))

    return render_template("edit_profile.html", user=current_user)

@views.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        text = request.form.get('comment')
        if text.strip():
            new_comment = Comment(text=text, user_id=current_user.id, post_id=post.id)
            db.session.add(new_comment)
            db.session.commit()
        else:
            flash("Comment cannot be empty", "error")
        return redirect(url_for('views.post_detail', post_id=post.id))

    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.asc()).all()
    return render_template('post_detail.html', post=post, comments=comments)

@views.route('/profile/<int:user_id>')
def public_profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user.id, is_approved=True).order_by(Post.date_posted.desc()).all()
    return render_template('profile.html', user=user, posts=posts)

@views.route('/close_post/<int:post_id>', methods=['POST'])
@login_required
def close_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash("You cannot close this post.", "error")
        return redirect(url_for('views.profile'))

    post.is_closed = True
    db.session.commit()
    flash("Post marked as founded.", "success")
    return redirect(url_for('views.profile'))

@views.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Unauthorized access", "danger")
        return redirect(url_for('views.home'))

    # Pending & approved posts
    pending_posts = Post.query.filter_by(is_approved=False).order_by(Post.date_posted.desc()).all()
    approved_posts = Post.query.filter_by(is_approved=True).order_by(Post.date_posted.desc()).all()

    # Counts for overview
    pending_count = len(pending_posts)
    approved_count = len(approved_posts)

    # Group by type (Lost, Found, etc.)
    type_counts = (
        db.session.query(Post.type, func.count(Post.id))
        .group_by(Post.type)
        .all()
    )
    type_data = {t: c for t, c in type_counts}  # dict: {"Lost": 5, "Found": 7, "Other": 2}

    return render_template(
        "admin.html",
        pending_posts=pending_posts,
        approved_posts=approved_posts,
        pending_count=pending_count,
        approved_count=approved_count,
        type_data=type_data
    )
@views.route('/admin/approve_post/<int:post_id>', methods=['POST'])
@login_required
def approve_post(post_id):
    if current_user.role != "admin":
        flash("Unauthorized action", "danger")
        return redirect(url_for('views.home'))

    post = Post.query.get_or_404(post_id)
    post.is_approved = True
    db.session.commit()
    flash("Post approved successfully!", "success")
    return redirect(url_for('views.admin_dashboard'))

@views.route('/admin/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    if current_user.role != "admin":
        flash("Unauthorized action", "danger")
        return redirect(url_for('views.home'))

    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully!", "success")
    return redirect(url_for('views.admin_dashboard'))