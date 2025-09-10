"""
Authentication handlers
"""
from nicegui import app, ui
from models import User
from services.database import SessionLocal


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


"""Handle user registration"""
def handle_register(username: str, email: str, password: str):
    db = SessionLocal()
    
    # Check if username already exists
    if db.query(User).filter_by(username=username).first():
        ui.notify('Username already exists', color='negative')
        db.close()
        return
        
    if db.query(User).filter_by(email=email).first():
        ui.notify('Email already exists', color='negative')
        db.close()
        return

    # Create new user
    try:
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.add(new_user)
        db.commit()

        app.storage.user.update({
            'authenticated': True, 
            'username': new_user.username, 
            'user_id': new_user.id,
            'show_success_message': 'Registration successful!'  # Store success message
        })
        ui.navigate.to('/')
    except Exception as e:
        db.rollback()
        ui.notify(f'Registration failed: {str(e)}', color='negative')
    finally:
        db.close()


"""Handle user logout"""
def handle_logout():
    app.storage.user.clear()
    ui.navigate.to('/login')
