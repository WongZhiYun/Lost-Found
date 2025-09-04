from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hello'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    with app.app_context():
        db.create_all()

        # --- create default admin if not exists ---
        admin_email = "lostandfoundmmu@gmail.com"
        admin_password = "lostandfoundmmu.1"

        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                email = admin_email,
                username = "Admin",
                password = generate_password_hash(admin_password, method="pbkdf2:sha256"),
                role = "admin"
            )
            db.session.add(admin)
            db.session.commit()


    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app
