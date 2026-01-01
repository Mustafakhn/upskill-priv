from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.api.v1.dao.user_dao import UserDAO
from app.db.base import User
from app.config import settings
from app.utils.validators import validate_email


class UserService:
    """Service for user operations"""
    
    def __init__(self):
        self.user_dao = UserDAO
    
    def create_user(self, db: Session, email: str, password: str) -> Dict[str, Any]:
        """Create a new user"""
        # Validate email
        if not validate_email(email):
            raise ValueError("Invalid email format")
        
        # Check if user exists
        existing = self.user_dao.get_by_email(db, email)
        if existing:
            raise ValueError("Email already registered")
        
        # Validate password
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        
        # Create user
        user = self.user_dao.create(db, email, password)
        db.commit()
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "free_journeys_used": user.free_journeys_used,
            "is_premium": user.is_premium == 1,
            "is_admin": user.is_admin == 1,
            "premium_requested": user.premium_requested == 1
        }
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data"""
        user = self.user_dao.get_by_email(db, email)
        if not user:
            return None
        
        if not self.user_dao.verify_password(password, user.password_hash):
            return None
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "free_journeys_used": user.free_journeys_used,
            "is_premium": user.is_premium == 1,
            "is_admin": user.is_admin == 1,
            "premium_requested": user.premium_requested == 1
        }
    
    def update_user_name(self, db: Session, user_id: int, name: str) -> Dict[str, Any]:
        """Update user's name"""
        user = self.user_dao.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        user.name = name.strip() if name else None
        db.commit()
        db.refresh(user)
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "free_journeys_used": user.free_journeys_used,
            "is_premium": user.is_premium == 1,
            "is_admin": user.is_admin == 1,
            "premium_requested": user.premium_requested == 1
        }
    
    def update_user_password(self, db: Session, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """Update user's password"""
        user = self.user_dao.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify old password
        if not self.user_dao.verify_password(old_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Validate new password
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters")
        
        # Update password
        from app.api.v1.dao.user_dao import _hash_password
        user.password_hash = _hash_password(new_password)
        db.commit()
        db.refresh(user)
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "free_journeys_used": user.free_journeys_used,
            "is_premium": user.is_premium == 1,
            "is_admin": user.is_admin == 1,
            "premium_requested": user.premium_requested == 1
        }
    
    def create_access_token(self, user_id: int) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": str(user_id), "exp": expire, "type": "access"}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, user_id: int) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = {"sub": str(user_id), "exp": expire, "type": "refresh"}
        encoded_jwt = jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[int]:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            token_type = payload.get("type", "access")
            if token_type != "access":
                return None  # Only accept access tokens
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return int(user_id)
        except JWTError:
            return None
    
    def verify_refresh_token(self, token: str) -> Optional[int]:
        """Verify refresh token and return user_id"""
        try:
            payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
            token_type = payload.get("type", "refresh")
            if token_type != "refresh":
                return None  # Only accept refresh tokens
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return int(user_id)
        except JWTError:
            return None
    
    def can_create_free_journey(self, db: Session, user_id: int) -> bool:
        """Check if user can create a free journey"""
        user = self.user_dao.get_by_id(db, user_id)
        if not user:
            return False
        # Premium users have unlimited journeys
        if user.is_premium == 1:
            return True
        # Regular users are limited by FREE_JOURNEYS_LIMIT
        return user.free_journeys_used < settings.FREE_JOURNEYS_LIMIT
    
    def is_premium_user(self, db: Session, user_id: int) -> bool:
        """Check if user is premium"""
        user = self.user_dao.get_by_id(db, user_id)
        if not user:
            return False
        return user.is_premium == 1
    
    def is_admin_user(self, db: Session, user_id: int) -> bool:
        """Check if user is admin"""
        user = self.user_dao.get_by_id(db, user_id)
        if not user:
            return False
        return user.is_admin == 1
    
    def request_premium(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Request premium upgrade"""
        user = self.user_dao.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        if user.is_premium == 1:
            raise ValueError("User is already premium")
        user.premium_requested = 1
        db.commit()
        return {
            "id": user.id,
            "email": user.email,
            "premium_requested": user.premium_requested == 1
        }
    
    def set_premium_status(self, db: Session, user_id: int, is_premium: bool) -> Dict[str, Any]:
        """Set premium status for a user (admin only)"""
        user = self.user_dao.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        user.is_premium = 1 if is_premium else 0
        if is_premium:
            user.premium_requested = 0  # Clear request when approved
        db.commit()
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_premium": user.is_premium == 1,
            "premium_requested": user.premium_requested == 1
        }
    
    def get_premium_requests(self, db: Session) -> List[Dict[str, Any]]:
        """Get all users who requested premium (admin only)"""
        users = db.query(User).filter(
            User.premium_requested == 1,
            User.is_premium == 0
        ).all()
        return [
            {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "free_journeys_used": user.free_journeys_used,
                "premium_requested": user.premium_requested == 1,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            for user in users
        ]
    
    def get_all_users(self, db: Session) -> List[Dict[str, Any]]:
        """Get all users (admin only)"""
        users = db.query(User).all()
        return [
            {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "free_journeys_used": user.free_journeys_used,
                "is_premium": user.is_premium == 1,
                "is_admin": user.is_admin == 1,
                "premium_requested": user.premium_requested == 1,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            for user in users
        ]
    
    def increment_free_journeys(self, db: Session, user_id: int):
        """Increment free journeys counter"""
        self.user_dao.increment_free_journeys(db, user_id)
        db.commit()

