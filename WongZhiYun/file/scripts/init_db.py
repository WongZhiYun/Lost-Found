import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Report

app = create_app()
with app.app_context():
    db.create_all()
    print("Database initialized, tables created.")
