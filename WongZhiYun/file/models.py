from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), default="user")
    posts = db.relationship('Post', backref='author',lazy=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    profile_image = db.Column(db.String(200), default="default.png")

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # "lost" or "found"
    location = db.Column(db.String(50), nullable=True) # optional
    category = db.Column(db.String(50), nullable=True)  # optional    
    image = db.Column(db.String(100))  # filename if uploaded
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)