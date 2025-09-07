from flask import Flask

def create_app():
    app = Flask(__name__) # craete Flask app

    app.config['SECRET_KEY'] = 'dev'  

    # register Blueprint
    from app.search import bp as search_bp
    app.register_blueprint(search_bp, url_prefix='/search')

    return app
