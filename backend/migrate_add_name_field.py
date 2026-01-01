"""
Migration script to add name field to users table
Run this script to add the name column to existing users table
"""
import sys
from sqlalchemy import text
from app.db.mysql import engine

def migrate():
    """Add name column to users table if it doesn't exist"""
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'users'
                AND COLUMN_NAME = 'name'
            """))
            
            if result.fetchone()[0] == 0:
                # Column doesn't exist, add it
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN name VARCHAR(255) NULL
                """))
                conn.commit()
                print("✓ Successfully added 'name' column to users table")
            else:
                print("✓ 'name' column already exists in users table")
                
    except Exception as e:
        print(f"✗ Error migrating database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()

