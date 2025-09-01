from flask import Flask

def create_app():
    # craete Flask app
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'dev-key'  
    app.config['UPLOAD_FOLDER'] = 'static/uploads'  # for AI image search

    # register Blueprint
    from app.search import bp as search_bp
    app.register_blueprint(search_bp, url_prefix='/search')

    return app
