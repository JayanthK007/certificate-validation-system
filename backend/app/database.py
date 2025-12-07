"""
Database Configuration and Session Management Module

This module handles all database-related configuration including:
- Database engine creation (SQLite for dev, PostgreSQL for production)
- Session factory setup for SQLAlchemy ORM
- Database session dependency injection for FastAPI
- Database initialization (table creation)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./certificates.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    FastAPI dependency function for getting database sessions.
    
    This function is used as a dependency in FastAPI route handlers.
    It creates a new database session, yields it to the route handler,
    and ensures the session is properly closed after the request completes.
    
    Usage:
        @router.get("/endpoint")
        async def my_endpoint(db: Session = Depends(get_db)):
            pass
    
    Yields:
        Session: SQLAlchemy database session
    
    Note:
        The session is automatically closed in the finally block,
        ensuring no connection leaks even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database by creating all tables defined in models.
    
    This function creates all database tables based on the SQLAlchemy models
    that inherit from Base. It's called once during application startup.
    
    Note:
        - In production, use database migrations (Alembic) instead
        - This function will not drop existing tables, only create missing ones
        - Safe to call multiple times (idempotent)
    """
    Base.metadata.create_all(bind=engine)
