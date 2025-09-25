from . import db
from datetime import datetime

class Report(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(10), nullable=False)   # lost / found
    location = db.Column(db.String(50))
    category = db.Column(db.String(50))
    image = db.Column(db.String(100))   # 注意：数据库列名是 image
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer)
    is_approved = db.Column(db.Boolean, default=False)
    image_hash = db.Column(db.Text)

    def __repr__(self):
        return f"<Report {self.id} {self.title}>"
