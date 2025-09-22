"""
Authentication handlers
"""
from nicegui import app, ui
from file.models import User
from ..services.database import SessionLocal


"""Handle user login"""
def handle_login(username: str, password: str):        
    db = SessionLocal()
    user = db.query(User).filter_by(username=username).first()
    
    if user and user.check_password(password):
        # Set user session
        app.storage.user.update({
            'authenticated': True, 
            'username': user.username, 
            'user_id': user.id
        })
        ui.navigate.to('/')
    else:
        ui.notify('Invalid username or password', color='negative')
        
    db.close()


"""Handle user logout"""
def handle_logout():
    app.storage.user.clear()
    ui.navigate.to('/login')
