from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.api.v1.services.admin_service import AdminService
from app.api.v1.services.user_service import UserService
from app.api.v1.routers.journey_router import get_user_id
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()
admin_service = AdminService()
user_service = UserService()


def check_admin(user_id: int) -> bool:
    """Check if user is admin (for now, allow all authenticated users - can be enhanced)"""
    # TODO: Add proper admin role checking
    return True


@router.get("/queries")
def get_query_logs(
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = Query(None),
    journey_id: Optional[int] = Query(None),
    current_user_id: int = Depends(get_user_id)
):
    """Get query logs (admin only)"""
    if not check_admin(current_user_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    logs = admin_service.get_query_logs(limit, user_id, journey_id)
    return {"logs": logs, "count": len(logs)}


@router.get("/usage/ai")
def get_ai_usage(
    user_id: Optional[int] = Query(None),
    journey_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    current_user_id: int = Depends(get_user_id)
):
    """Get AI usage statistics (admin only)"""
    if not check_admin(current_user_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    stats = admin_service.get_ai_usage_stats(user_id, journey_id, days)
    return stats


@router.get("/usage/user/{user_id}")
def get_user_usage(
    user_id: int,
    current_user_id: int = Depends(get_user_id)
):
    """Get usage summary for a specific user (admin only)"""
    if not check_admin(current_user_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    summary = admin_service.get_user_usage_summary(user_id)
    return summary


@router.get("/usage/all")
def get_all_users_usage(
    limit: int = Query(100, ge=1, le=1000),
    current_user_id: int = Depends(get_user_id)
):
    """Get usage summary for all users (admin only)"""
    if not check_admin(current_user_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    summaries = admin_service.get_all_users_usage(limit)
    return {"users": summaries, "count": len(summaries)}

