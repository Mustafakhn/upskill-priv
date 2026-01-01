from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.base import User
from typing import Optional
import bcrypt

# Use bcrypt directly to avoid passlib version issues
def _hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Bcrypt has a 72 byte limit, so truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


class UserDAO:
    """Data Access Object for User operations"""
    
    @staticmethod
    def create(db: Session, email: str, password: str) -> User:
        """Create a new user"""
        password_hash = _hash_password(password)
        user = User(
            email=email,
            password_hash=password_hash,
            free_journeys_used=0
        )
        db.add(user)
        db.flush()
        return user
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return _verify_password(plain_password, hashed_password)
    
    @staticmethod
    def increment_free_journeys(db: Session, user_id: int) -> User:
        """Increment free journeys counter"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.free_journeys_used += 1
            db.flush()
        return user

