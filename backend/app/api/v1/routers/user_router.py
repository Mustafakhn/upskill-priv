from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.db.mysql import get_db_session
from app.api.v1.services.user_service import UserService
from typing import Optional

router = APIRouter(prefix="/user", tags=["user"])
security = HTTPBearer()

user_service = UserService()


def get_user_id_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get user ID from token"""
    token = credentials.credentials
    user_id = user_service.verify_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user_id


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    free_journeys_used: int
    is_premium: bool = False
    is_admin: bool = False
    premium_requested: bool = False


@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db_session)):
    """Register a new user"""
    try:
        user = user_service.create_user(db, user_data.email, user_data.password)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db_session)):
    """Login and get access token and refresh token"""
    user = user_service.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = user_service.create_access_token(user["id"])
    refresh_token = user_service.create_refresh_token(user["id"])
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db_session)):
    """Refresh access token using refresh token"""
    user_id = user_service.verify_refresh_token(request.refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user to return user data
    user = user_service.user_dao.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate new tokens
    access_token = user_service.create_access_token(user_id)
    refresh_token = user_service.create_refresh_token(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "free_journeys_used": user.free_journeys_used,
            "is_premium": user.is_premium == 1,
            "is_admin": user.is_admin == 1,
            "premium_requested": user.premium_requested == 1
        }
    }


@router.get("/me", response_model=UserResponse)
def get_current_user(
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_user_id_from_token)
):
    """Get current user information"""
    user = user_service.user_dao.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {
        "id": user.id,
        "email": user.email,
        "free_journeys_used": user.free_journeys_used,
        "is_premium": user.is_premium == 1,
        "is_admin": user.is_admin == 1,
        "premium_requested": user.premium_requested == 1
    }


def require_admin(user_id: int = Depends(get_user_id_from_token), db: Session = Depends(get_db_session)) -> int:
    """Require admin privileges"""
    if not user_service.is_admin_user(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user_id


# Premium upgrade request
@router.post("/request-premium")
def request_premium(
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_user_id_from_token)
):
    """Request premium upgrade"""
    try:
        result = user_service.request_premium(db, user_id)
        return {"message": "Premium upgrade requested successfully", "user": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Admin endpoints
@router.get("/admin/users", dependencies=[Depends(require_admin)])
def get_all_users(
    db: Session = Depends(get_db_session)
):
    """Get all users (admin only)"""
    users = user_service.get_all_users(db)
    return {"users": users}


@router.get("/admin/premium-requests", dependencies=[Depends(require_admin)])
def get_premium_requests(
    db: Session = Depends(get_db_session)
):
    """Get all premium upgrade requests (admin only)"""
    requests = user_service.get_premium_requests(db)
    return {"requests": requests}


class SetPremiumRequest(BaseModel):
    user_id: int
    is_premium: bool


@router.post("/admin/set-premium", dependencies=[Depends(require_admin)])
def set_premium_status(
    request: SetPremiumRequest,
    db: Session = Depends(get_db_session)
):
    """Set premium status for a user (admin only)"""
    try:
        result = user_service.set_premium_status(db, request.user_id, request.is_premium)
        return {"message": f"Premium status updated successfully", "user": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

