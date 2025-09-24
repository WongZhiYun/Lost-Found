from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeSerializer
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db,mail
from flask_mail import Message
from .otp import generate_otp, send_otp_email

auth = Blueprint('auth', __name__)
s = URLSafeSerializer("hello")

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

        if User.query.filter_by(email=email).first():
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

# 1️⃣ Request Reset Page
@auth.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = s.dumps(email, salt='reset-password')
            link = url_for('auth.reset_password', token=token, _external=True)

            msg = Message('Password Reset Request',
                          sender='lostandfoundmmu@gmail.com',
                          recipients=[email])
            msg.body = f'Click the link to reset your password: {link}\n\nThis link expires in 30 minutes.'
            mail.send(msg)

            flash('Reset link sent to your email!', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('No account found with that email.', 'error')
    return render_template('forgot.html')

# 2️⃣ Reset Password Page
@auth.route('/reset/<token>', methods=['GET','POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='reset-password', max_age=1800)  # 30 min expiry
    except:
        flash('The reset link is invalid or expired.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()
            flash('Your password has been reset!', 'success')
            return redirect(url_for('auth.login'))
    return render_template('reset.html')