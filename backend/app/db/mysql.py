from sqlalchemy import create_engine
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
    except Exception as e:
        # Log warning but don't fail - tables might already exist
        print(f"Warning: Database initialization issue: {e}")
        print("Tables may already exist or there may be a connection issue.")
        # Continue anyway


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

