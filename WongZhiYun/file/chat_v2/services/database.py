"""
Database Service
"""
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from file.chat_v2.chat_config import config

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))

DB_PATH = config.DB_DATABASE   # 👈 use the one from config.py
print(f"[*] NiceGUI using database: {DB_PATH}")
print(">>> DB_PATH =", DB_PATH)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

"""Database service class - manage database connections and sessions"""
class DatabaseService:
    def create_all_tables(self):
        """Create all tables"""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise

    def close_all_connections(self):
        """Close all database connections"""
        if engine:
            engine.dispose()
            logger.info("All database connections closed")

# Create global database service instance
db_service = DatabaseService()
