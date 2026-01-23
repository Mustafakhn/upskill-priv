from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from app.config import settings
from app.db.base import Base

engine = create_engine(
    settings.MYSQL_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables - creates tables if they don't exist"""
    try:
        # Create all tables defined in Base.metadata
        Base.metadata.create_all(bind=engine)
        
        # Migrate journey status enum to include 'completed' if needed
        _migrate_journey_status_enum()
    except Exception as e:
        # Log warning but don't fail - tables might already exist
        print(f"Warning: Database initialization issue: {e}")
        print("Tables may already exist or there may be a connection issue.")
        # Continue anyway


def _migrate_journey_status_enum():
    """Add 'completed' status to journeys.status enum if it doesn't exist"""
    try:
        with engine.connect() as conn:
            # Check current enum values
            result = conn.execute(
                text("""
                    SELECT COLUMN_TYPE 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'journeys' 
                    AND COLUMN_NAME = 'status'
                """)
            )
            row = result.fetchone()
            if row:
                enum_type = row[0]
                # Check if 'completed' is already in the enum
                if 'completed' not in enum_type.lower():
                    print("Migrating journeys.status enum to include 'completed'...")
                    # Alter the enum to add 'completed'
                    # MySQL requires us to recreate the enum with all values
                    conn.execute(
                        text("""
                            ALTER TABLE journeys 
                            MODIFY COLUMN status ENUM('pending', 'scraping', 'curating', 'ready', 'completed', 'failed') 
                            NOT NULL DEFAULT 'pending'
                        """)
                    )
                    conn.commit()
                    print("✓ Successfully added 'completed' status to journeys table")
                else:
                    print("✓ Journey status enum already includes 'completed'")
    except Exception as e:
        # Log but don't fail - migration might not be critical
        print(f"Warning: Could not migrate journey status enum: {e}")
        import traceback
        traceback.print_exc()


@contextmanager
def get_db() -> Session:
    """Get database session with context manager"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session():
    """Get database session (use with dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

