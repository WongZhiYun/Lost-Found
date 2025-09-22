"""
Database Models
"""
import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from services.database import Base

# --- Model definition ---
class User(Base):
    __tablename__ = 'users' 
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    sent_messages = relationship('Message', foreign_keys='Message.sender_id', back_populates='sender')
    received_messages = relationship('Message', foreign_keys='Message.receiver_id', back_populates='receiver')

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(str(self.password), password)

    def get_avatar(self):
        return f'https://robohash.org/{self.username}.png'

class Message(Base):
    __tablename__ = 'messages'  

    id = Column(Integer, primary_key=True)
    content = Column(String(500), nullable=True)  
    created_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    sender_id = Column(Integer, ForeignKey('users.id')) 
    receiver_id = Column(Integer, ForeignKey('users.id'))

    sender = relationship('User', foreign_keys=[sender_id], back_populates='sent_messages')
    receiver = relationship('User', foreign_keys=[receiver_id], back_populates='received_messages')

    media_items = relationship('Media', back_populates='message', cascade='all, delete-orphan')

    def __init__(self, sender_id, receiver_id, content=None):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content

class Media(Base):
    __tablename__ = 'media'
    
    id = Column(Integer, primary_key=True)
    # This is the crucial link back to the message
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    # Stores the UUID filename, e.g., 'abc-123.png'
    file_url = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Establishes the other side of the relationship
    message = relationship('Message', back_populates='media_items')

    def __init__(self, message_id, file_url):
        self.message_id = message_id
        self.file_url = file_url