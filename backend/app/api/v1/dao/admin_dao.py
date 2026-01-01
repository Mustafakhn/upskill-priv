from app.db.mongo import get_mongo_db
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId


class AdminDAO:
    """Data Access Object for Admin operations"""
    
    @staticmethod
    def get_collection(collection_name: str):
        """Get a MongoDB collection"""
        db = get_mongo_db()
        return getattr(db, collection_name)
    
    @staticmethod
    def log_query(
        journey_id: int,
        user_id: int,
        queries: List[str],
        topic: str,
        level: str,
        goal: str
    ) -> str:
        """Log search queries for a journey"""
        collection = AdminDAO.get_collection("query_logs")
        doc = {
            "journey_id": journey_id,
            "user_id": user_id,
            "queries": queries,
            "topic": topic,
            "level": level,
            "goal": goal,
            "created_at": datetime.utcnow()
        }
        result = collection.insert_one(doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_query_logs(
        limit: int = 100,
        user_id: Optional[int] = None,
        journey_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get query logs"""
        collection = AdminDAO.get_collection("query_logs")
        query = {}
        if user_id:
            query["user_id"] = user_id
        if journey_id:
            query["journey_id"] = journey_id
        
        logs = list(collection.find(query).sort("created_at", -1).limit(limit))
        for log in logs:
            log["id"] = str(log["_id"])
            del log["_id"]
        return logs
    
    @staticmethod
    def log_ai_usage(
        user_id: int,
        journey_id: Optional[int],
        endpoint: str,
        tokens_used: Optional[int] = None,
        cost_estimate: Optional[float] = None
    ) -> str:
        """Log AI API usage"""
        collection = AdminDAO.get_collection("ai_usage_logs")
        doc = {
            "user_id": user_id,
            "journey_id": journey_id,
            "endpoint": endpoint,
            "tokens_used": tokens_used,
            "cost_estimate": cost_estimate,
            "created_at": datetime.utcnow()
        }
        result = collection.insert_one(doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_ai_usage_stats(
        user_id: Optional[int] = None,
        journey_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get AI usage statistics"""
        collection = AdminDAO.get_collection("ai_usage_logs")
        from datetime import timedelta
        
        query = {
            "created_at": {
                "$gte": datetime.utcnow() - timedelta(days=days)
            }
        }
        if user_id:
            query["user_id"] = user_id
        if journey_id:
            query["journey_id"] = journey_id
        
        logs = list(collection.find(query))
        
        total_calls = len(logs)
        total_tokens = sum(log.get("tokens_used", 0) for log in logs)
        total_cost = sum(log.get("cost_estimate", 0) for log in logs)
        
        # Group by endpoint
        endpoint_stats = {}
        for log in logs:
            endpoint = log.get("endpoint", "unknown")
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0
                }
            endpoint_stats[endpoint]["calls"] += 1
            endpoint_stats[endpoint]["tokens"] += log.get("tokens_used", 0)
            endpoint_stats[endpoint]["cost"] += log.get("cost_estimate", 0)
        
        return {
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "total_cost_estimate": round(total_cost, 4),
            "endpoint_stats": endpoint_stats,
            "period_days": days
        }
    
    @staticmethod
    def get_user_usage_summary(user_id: int) -> Dict[str, Any]:
        """Get usage summary for a user"""
        # Get journey count
        from sqlalchemy.orm import Session
        from app.api.v1.dao.journey_dao import JourneyDAO
        # Note: This would need a db session passed in, but for now we'll use MongoDB
        
        # Get AI usage
        ai_stats = AdminDAO.get_ai_usage_stats(user_id=user_id, days=30)
        
        # Get query logs count
        query_logs = AdminDAO.get_query_logs(user_id=user_id, limit=1000)
        
        return {
            "user_id": user_id,
            "journeys_created": len(set(log.get("journey_id") for log in query_logs)),
            "queries_generated": len(query_logs),
            "ai_usage_30_days": ai_stats
        }

