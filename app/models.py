from datetime import datetime
from . import db 

class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    date_event = db.Column(db.DateTime)
    place = db.Column(db.String(200))
    category = db.Column(db.String(100))
    image_filename = db.Column(db.String(300))
    image_hash = db.Column(db.String(64))   # for save picture（hex string）
    status = db.Column(db.String(50), default='pending')
    owner_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Report {self.id} {self.title}>"
