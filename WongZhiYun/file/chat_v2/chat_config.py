"""
Application Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration class - central management of all configurations"""
    
    # ===============================================
    # Application basic configuration
    # ===============================================
    APP_NAME = os.getenv('APP_NAME', 'LOST AND FOUND MMU CHAT APP')
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret_key')
    APP_URL = os.getenv('APP_URL', 'http://localhost:8080')
    
    # Development configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', 'localhost')
    PORT = int(os.getenv('PORT', 8080))
    
    # ===============================================
    # Database configuration (supports multiple databases)
    # ===============================================
    DB_CONNECTION = os.getenv('DB_CONNECTION', 'sqlite')
    DB_DATABASE = os.getenv('DB_DATABASE', 'first.db')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USERNAME = os.getenv('DB_USERNAME', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    @classmethod
    def get_database_url(cls) -> str:
        """Generate database connection URL"""
        if cls.DB_CONNECTION == "sqlite":
            return f"sqlite:///{cls.DB_DATABASE}"
        elif cls.DB_CONNECTION == "mysql":
            return f"mysql+pymysql://{cls.DB_USERNAME}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_DATABASE}"
        elif cls.DB_CONNECTION == "postgresql":
            return f"postgresql://{cls.DB_USERNAME}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_DATABASE}"
        else:
            raise ValueError(f"Unsupported DB_CONNECTION: {cls.DB_CONNECTION}")
    
    # ===============================================
    # Email configuration (SMTP)
    # ===============================================
    EMAIL_NOTIFICATIONS_ENABLED = os.getenv('EMAIL_NOTIFICATIONS_ENABLED', 'True').lower() == 'true'
    EMAIL_NOTIFICATIONS_COOLDOWN = int(os.getenv('EMAIL_NOTIFICATIONS_COOLDOWN', 600)) # 600 seconds = 10 minutes
    
    MAIL_MAILER = os.getenv('MAIL_MAILER', 'smtp')
    MAIL_HOST = os.getenv('MAIL_HOST', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'lostandfoundmmu@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'urpktrgmfooghxme')
    MAIL_ENCRYPTION = os.getenv('MAIL_ENCRYPTION', 'tls')  # tls, ssl, none

    # Force sender to always be lostandfoundmmu@gmail.com
    MAIL_FROM_ADDRESS = "lostandfoundmmu@gmail.com"
    MAIL_FROM_NAME = os.getenv('MAIL_FROM_NAME', APP_NAME)
    
    @classmethod
    def get_mail_config(cls) -> dict:
        """Get mail configuration dictionary"""
        if cls.MAIL_ENCRYPTION.lower() not in ["tls", "ssl", "none"]:
            raise ValueError("MAIL_ENCRYPTION must be 'tls', 'ssl', or 'none'")
        
        return {
            'host': cls.MAIL_HOST,
            'port': cls.MAIL_PORT,
            'username': cls.MAIL_USERNAME,
            'password': cls.MAIL_PASSWORD,
            'use_tls': cls.MAIL_ENCRYPTION.lower() == 'tls',
            'use_ssl': cls.MAIL_ENCRYPTION.lower() == 'ssl',
            'from_address': cls.MAIL_FROM_ADDRESS,
            'from_name': cls.MAIL_FROM_NAME,
        }
    
    # ===============================================
    # UI configuration
    # ===============================================
    FAVICON_PATH = 'static/favicon.ico'
    STYLES_PATH = '/static/styles.css'
    
    STATIC_DIR = 'static'
    STATIC_URL = '/static'

    # ===============================================
    # Log configuration
    # ===============================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')


# Create config instance
config = Config()
