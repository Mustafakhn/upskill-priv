from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.api.v1.services.push_service import PushService
from app.api.v1.services.user_service import UserService
from app.config import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/push", tags=["push"])
security = HTTPBearer()

push_service = PushService()
user_service = UserService()


class PushSubscription(BaseModel):
    endpoint: str
    keys: Dict[str, str]


class SubscribeRequest(BaseModel):
    subscription: PushSubscription


def get_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get user ID from token"""
    token = credentials.credentials
    user_id = user_service.verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


@router.get("/vapid-public-key")
def get_vapid_public_key():
    """Get VAPID public key for client subscription"""
    if not settings.VAPID_PUBLIC_KEY:
        raise HTTPException(status_code=503, detail="VAPID keys not configured")
    return {"publicKey": settings.VAPID_PUBLIC_KEY}


@router.post("/subscribe")
def subscribe(
    request: SubscribeRequest,
    user_id: int = Depends(get_user_id)
):
    """Subscribe user to push notifications"""
    subscription_dict = {
        "endpoint": request.subscription.endpoint,
        "keys": request.subscription.keys
    }
    
    success = push_service.subscribe_user(user_id, subscription_dict)
    if success:
        return {"success": True, "message": "Subscribed to push notifications"}
    else:
        raise HTTPException(status_code=500, detail="Failed to subscribe")


@router.post("/unsubscribe")
def unsubscribe(user_id: int = Depends(get_user_id)):
    """Unsubscribe user from push notifications"""
    success = push_service.unsubscribe_user(user_id)
    if success:
        return {"success": True, "message": "Unsubscribed from push notifications"}
    else:
        raise HTTPException(status_code=500, detail="Failed to unsubscribe")
