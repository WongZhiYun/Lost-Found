import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_object=None):
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # DB 路径：指向 instance/users.db
    default_db_path = os.path.abspath(os.path.join(app.root_path, '..', 'instance', 'users.db'))
    default_db_uri = f"sqlite:///{default_db_path}"

    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', default_db_uri),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.abspath(os.path.join(app.root_path, 'static', 'uploads')),
    )

    db.init_app(app)

    from .search import bp as search_bp
    app.register_blueprint(search_bp, url_prefix='/search')

    return app
