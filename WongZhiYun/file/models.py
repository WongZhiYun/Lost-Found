from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
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
    comments = db.relationship('Comment', backref='user', lazy=True)

     # -------------------- Password Methods --------------------
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # "lost" or "found"
    location = db.Column(db.String(50), nullable=True) # optional
    category = db.Column(db.String(50), nullable=True) # optional
    image = db.Column(db.String(100))  # filename if uploaded
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    is_closed = db.Column(db.Boolean, default=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Message(db.Model):
    __tablename__ = 'messages'  

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=True)  
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages', lazy=True)
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages', lazy=True)

    media_items = db.relationship('Media', backref='message', cascade='all, delete-orphan')

class Media(db.Model):
    __tablename__ = 'media'
    
    id = db.Column(db.Integer, primary_key=True)
    # This is the crucial link back to the message
    message_id =db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    # Stores the UUID filename, e.g., 'abc-123.png'
    file_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

