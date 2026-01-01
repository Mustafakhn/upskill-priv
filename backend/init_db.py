"""
Database initialization script
Run this to create the MySQL database and tables
"""
from app.db.mysql import init_db, engine
from app.config import settings

def main():
    print("Initializing database...")
    print(f"Database URL: {settings.MYSQL_URL}")
    
    try:
        # Create tables
        init_db()
        print("✓ Database tables created successfully!")
        
        # Test connection
        with engine.connect() as conn:
            print("✓ Database connection successful!")
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        print("\nMake sure:")
        print("1. MySQL is running")
        print("2. Database exists (create it manually if needed)")
        print("3. Connection credentials are correct")

if __name__ == "__main__":
    main()

