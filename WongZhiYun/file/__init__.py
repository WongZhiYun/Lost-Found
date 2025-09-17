def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hello'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

    # Mail setup
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = "lostandfoundmmu@gmail.com"
    app.config['MAIL_PASSWORD'] = "urpk trgm foog hxme"
    mail.init_app(app)

    # DB & Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import all models for migrations
    from .models import User, Post

    # Setup login manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
