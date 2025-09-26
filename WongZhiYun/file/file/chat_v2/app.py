"""
Chat App - Main Application

This is a modern chat application based on NiceGUI
Features include: user authentication, chat, email notifications
"""
from nicegui import app, ui
from config import config
from pages.main import main_page
from pages.chat import direct_chat_page
from pages.auth import show_login_page
from core.startup_checker import run_startup_checks
from core.middleware import AuthMiddleware
from services.database import db_service

#Setup application routes
def setup_routes():
    # Main page route
    ui.page('/')(main_page)
    
    # Direct chat page route
    ui.page('/chat/{partner_id}')(direct_chat_page)
    
    # Login page route
    ui.page('/login')(show_login_page)



#Main application entry point
def main():
    # Run startup checks
    if not run_startup_checks():
        print("Startup checks failed. Please check your .env file configuration.")
        print("See README.md for configuration examples.")
        return
        
    # Setup routes
    setup_routes()
    
    # Add middleware
    app.add_middleware(AuthMiddleware)

    # Setup static files
    app.add_static_files(config.STATIC_URL, config.STATIC_DIR)
    
    # Start application
    ui.run(
        storage_secret=config.SECRET_KEY,
        title=config.APP_NAME,
        favicon=config.FAVICON_PATH,
        host=config.HOST,
        port=config.PORT
    )
    
if __name__ in {"__main__", "__mp_main__"}:
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Close database connections
        db_service.close_all_connections()
