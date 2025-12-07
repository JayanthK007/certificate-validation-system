"""
Migration script to remove custom blockchain tables (Block, BlockchainEntry).

This script removes the 'blocks' and 'blockchain_entries' tables since
the system now uses Ethereum blockchain only.

Run this script once to clean up the database:
    python -m app.migrations.remove_custom_blockchain_tables
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import DATABASE_URL

def remove_custom_blockchain_tables():
    """Remove Block and BlockchainEntry tables from database."""
    
    print("=" * 80)
    print("Removing Custom Blockchain Tables")
    print("=" * 80)
    print()
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if tables exist and remove them
        tables_to_remove = ['blockchain_entries', 'blocks']
        
        for table_name in tables_to_remove:
            try:
                # Check if table exists (SQLite specific)
                if 'sqlite' in DATABASE_URL:
                    result = conn.execute(text(
                        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
                    ))
                    exists = result.fetchone() is not None
                else:
                    # PostgreSQL
                    result = conn.execute(text(
                        f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')"
                    ))
                    exists = result.fetchone()[0]
                
                if exists:
                    print(f"Removing table: {table_name}...")
                    conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                    conn.commit()
                    print(f"✅ Removed table: {table_name}")
                else:
                    print(f"ℹ️  Table {table_name} does not exist (already removed or never created)")
                    
            except OperationalError as e:
                print(f"⚠️  Error removing table {table_name}: {e}")
                print("   This is okay if the table doesn't exist.")
    
    print()
    print("=" * 80)
    print("Migration Complete!")
    print("=" * 80)
    print()
    print("Custom blockchain tables have been removed.")
    print("The system now uses Ethereum blockchain only.")
    print()
    print("Note: If you have existing data in these tables, it has been deleted.")
    print("      Certificates should be re-issued on Ethereum if needed.")

if __name__ == "__main__":
    remove_custom_blockchain_tables()

