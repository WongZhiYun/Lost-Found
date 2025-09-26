import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#Initialize SQLAlchemy object
db = SQLAlchemy()

def create_app(config_object=None):
    #Create Flask app, set static and template folders
    app = Flask(__name__, static_folder='static', template_folder='templates')


     # --- Database path setup ---
     #Default database path
    default_db_path = "/Users/chloechew/Documents/Lost-Found/WongZhiYun/file/instance/users.db"
    default_db_uri = f"sqlite:///{default_db_path}"

     # --- App configuration ---
     # Load config from env vars, fallback to defaults if not set
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', default_db_uri),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.abspath(os.path.join(app.root_path, 'static', 'uploads')),
    )

    #Bind SQLAlchemy db object to Flask app
    db.init_app(app)

    # --- Blueprint registration ---
    #Register "search" blueprint, URL prefix = /search
    from .search import bp as search_bp
    app.register_blueprint(search_bp, url_prefix='/search')

    #Return Flask app
    return app
