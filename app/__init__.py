import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_object=None):
    # Create a Flask application instance,
    # specifying the static and template folder locations
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # Configure Flask
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:////../instance/users.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.root_path, 'static', 'uploads'),
    )

    # Bind the SQLAlchemy object to the Flask app instance
    db.init_app(app)

    # Import and register the "search" blueprint with URL search
    from .search import bp as search_bp
    app.register_blueprint(search_bp, url_prefix='/search')

     # Return the configured Flask app
    return app
