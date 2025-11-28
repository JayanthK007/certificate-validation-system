"""
Database initialization script
Run this to initialize the database with tables
"""
from app.database import init_db, engine
from app.models.db_models import Base

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    print("Tables created:")
    for table in Base.metadata.tables:
        print(f"  - {table}")

