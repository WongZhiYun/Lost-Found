import sys, os
sys.path.append(os.path.dirname(__file__))

"""
run.py
Purpose:Entry point script for the application.Calls the create_app factory to build the Flask app instance, then start Flask's development server(for development).
Note:Useful for quick local development.For production use a WSGI server (gunicorn/uWSGI)
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
    
