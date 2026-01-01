from typing import Dict, Any, List, Optional
from app.api.v1.dao.admin_dao import AdminDAO
from sqlalchemy.orm import Session


class AdminService:
    """Service for admin operations"""
    
    def __init__(self):
        self.admin_dao = AdminDAO
    
    def get_query_logs(
        self,
        limit: int = 100,
        user_id: Optional[int] = None,
        journey_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get query logs"""
        return self.admin_dao.get_query_logs(limit, user_id, journey_id)
    
    def get_ai_usage_stats(
        self,
        user_id: Optional[int] = None,
        journey_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get AI usage statistics"""
        return self.admin_dao.get_ai_usage_stats(user_id, journey_id, days)
    
    def get_user_usage_summary(self, user_id: int) -> Dict[str, Any]:
        """Get usage summary for a user"""
        return self.admin_dao.get_user_usage_summary(user_id)
    
    def get_all_users_usage(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get usage summary for all users"""
        # Get all unique user IDs from query logs
        query_logs = self.admin_dao.get_query_logs(limit=1000)
        user_ids = list(set(log.get("user_id") for log in query_logs if log.get("user_id")))
        
        summaries = []
        for uid in user_ids[:limit]:
            try:
                summary = self.get_user_usage_summary(uid)
                summaries.append(summary)
            except Exception as e:
                print(f"Error getting usage for user {uid}: {e}")
        
        return summaries

