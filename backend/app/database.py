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

# ============================================================================
# Database Configuration
# ============================================================================

# Database URL - SQLite for development, can be changed to PostgreSQL for production
# Format: "sqlite:///./certificates.db" or "postgresql://user:pass@localhost/dbname"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./certificates.db")

# ============================================================================
# SQLAlchemy Engine Setup
# ============================================================================

# Create database engine - handles connection pooling and database communication
# For SQLite, we disable thread checking to allow multiple threads
# For PostgreSQL, no special connection args needed
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# ============================================================================
# Session Factory
# ============================================================================

# Create session factory - used to create database sessions
# autocommit=False: Changes require explicit commit
# autoflush=False: Changes are not automatically flushed to DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============================================================================
# Base Model Class
# ============================================================================

# Base class for all SQLAlchemy ORM models
# All database models inherit from this base class
Base = declarative_base()

# ============================================================================
# Database Session Dependency
# ============================================================================

def get_db():
    """
    FastAPI dependency function for getting database sessions.
    
    This function is used as a dependency in FastAPI route handlers.
    It creates a new database session, yields it to the route handler,
    and ensures the session is properly closed after the request completes.
    
    Usage:
        @router.get("/endpoint")
        async def my_endpoint(db: Session = Depends(get_db)):
            # Use db session here
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

# ============================================================================
# Database Initialization
# ============================================================================

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
