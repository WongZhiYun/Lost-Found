from . import db
from datetime import datetime

#Define Report model class (maps to "post" table in DB)
class Report(db.Model):
    __tablename__ = 'post'

    # --- Field definitions ---
    id = db.Column(db.Integer, primary_key=True)       # Primary key ID, auto-increment
    title = db.Column(db.String(100), nullable=False)  # Title, required
    description = db.Column(db.Text, nullable=False)   # Detailed description, required
    type = db.Column(db.String(10), nullable=False)    # lost / found
    location = db.Column(db.String(50))                # Location where item was lost/found
    category = db.Column(db.String(50))                # Category (e.g., wallet/phone/pen)
    image = db.Column(db.String(100))                  # Image filename or path
    date_posted = db.Column(db.DateTime, default=datetime.utcnow) # Post timestamp
    user_id = db.Column(db.Integer)                    # ID of the posting user
    is_approved = db.Column(db.Boolean, default=False) # Whether the report is approved
    image_hash = db.Column(db.Text)                    # to prevent duplicate uploads

    def __repr__(self):
        # Representation string for debugging
        return f"<Report {self.id} {self.title}>"
