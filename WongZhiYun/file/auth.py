from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", category="success")

            if user.role == "admin":
                return redirect(url_for('views.admin_dashboard'))
            else:
                return redirect(url_for('views.home'))
        else:
            flash("Invalid email or password", category='error')
    return render_template("login.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        print("DEBUG -> Email:", email)
        print("DEBUG -> Username:", username)
        print("DEBUG -> Password:", password)

        if not password:
            flash("Password field is empty!", category="error")
            return redirect(url_for("auth.sign_up"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists", category='error')
            return redirect(url_for('auth.sign_up'))
        
        new_user = User(
            email=email,
            username=username,
            password = generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Account created!", category='success')
        return redirect(url_for('auth.login'))

    return render_template("sign_up.html")

