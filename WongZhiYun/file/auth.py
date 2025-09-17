from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db
from .otp import generate_otp, send_otp_email

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
                return redirect(url_for('views.home'))
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

        if User.query.filter_by(email=email).first()
            flash("Email already exists", category='error')
            return redirect(url_for('auth.sign_up'))
        
        # --- Generate OTP ---
        otp = generate_otp()
        session['otp'] = otp
        session['reg_email'] = email
        session['reg_username'] = username
        session['reg_password'] = generate_password_hash(password, method='pbkdf2:sha256')

        # Send OTP from admin email
        send_otp_email(email, otp)

        # Reload signup page with OTP popup
        return render_template("sign_up.html", show_otp=True)

    return render_template("sign_up.html")


@auth.route('/verify_otp', methods=['POST'])
def verify_otp():
    input_otp = request.form.get('otp')

    if input_otp == session.get('otp'):
        # --- Now we create the user in the database ---
        new_user = User(
            email=session.get('reg_email'),
            username=session.get('reg_username'),
            password=session.get('reg_password')
        )
        db.session.add(new_user)
        db.session.commit()

        # Clear temporary session data
        session.pop('otp', None)
        session.pop('reg_email', None)
        session.pop('reg_username', None)
        session.pop('reg_password', None)

        flash("Account created successfully!", category='success')
        return redirect(url_for('auth.login'))

    else:
        flash("Invalid OTP. Try again.", category='error')
        return redirect(url_for('auth.sign_up'))
