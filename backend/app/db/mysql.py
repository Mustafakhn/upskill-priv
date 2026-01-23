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
    """Migrate journeys.status from ENUM to VARCHAR to support SQLAlchemy enum values"""
    try:
        with engine.connect() as conn:
            # Check current column type
            result = conn.execute(
                text("""
                    SELECT COLUMN_TYPE, DATA_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'journeys' 
                    AND COLUMN_NAME = 'status'
                """)
            )
            row = result.fetchone()
            if row:
                column_type = row[0]
                data_type = row[1]
                # If it's an ENUM, convert to VARCHAR
                if data_type == 'enum':
                    print("Migrating journeys.status from ENUM to VARCHAR...")
                    # First, ensure 'completed' is in the enum if it's still ENUM
                    if 'completed' not in column_type.lower():
                        # Add 'completed' to enum first
                        conn.execute(
                            text("""
                                ALTER TABLE journeys 
                                MODIFY COLUMN status ENUM('pending', 'scraping', 'curating', 'ready', 'completed', 'failed') 
                                NOT NULL DEFAULT 'pending'
                            """)
                        )
                        conn.commit()
                    
                    # Convert ENUM to VARCHAR
                    conn.execute(
                        text("""
                            ALTER TABLE journeys 
                            MODIFY COLUMN status VARCHAR(20) 
                            NOT NULL DEFAULT 'pending'
                        """)
                    )
                    conn.commit()
                    print("✓ Successfully migrated journeys.status from ENUM to VARCHAR")
                elif data_type == 'varchar':
                    # Already VARCHAR, just ensure we have the right values
                    print("✓ Journey status is already VARCHAR")
                else:
                    print(f"Warning: Unexpected column type for status: {data_type}")
    except Exception as e:
        # Log but don't fail - migration might not be critical
        print(f"Warning: Could not migrate journey status column: {e}")
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

