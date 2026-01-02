from typing import Dict, Any, Optional
from app.db.mongo import get_mongo_db
from datetime import datetime


class PushDAO:
    """Data Access Object for Push Notification subscriptions"""
    
    @staticmethod
    def get_collection():
        """Get push subscriptions collection"""
        db = get_mongo_db()
        return db.push_subscriptions
    
    @staticmethod
    def save_subscription(user_id: int, subscription: Dict[str, Any]) -> bool:
        """Save or update push subscription for a user"""
        try:
            collection = PushDAO.get_collection()
            collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "subscription": subscription,
                        "updated_at": datetime.utcnow()
                    },
                    "$setOnInsert": {
                        "user_id": user_id,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error saving push subscription: {e}")
            return False
    
    @staticmethod
    def get_subscription(user_id: int) -> Optional[Dict[str, Any]]:
        """Get push subscription for a user"""
        try:
            collection = PushDAO.get_collection()
            doc = collection.find_one({"user_id": user_id})
            if doc and doc.get("subscription"):
                return doc["subscription"]
            return None
        except Exception as e:
            print(f"Error getting push subscription: {e}")
            return None
    
    @staticmethod
    def delete_subscription(user_id: int) -> bool:
        """Delete push subscription for a user"""
        try:
            collection = PushDAO.get_collection()
            collection.delete_one({"user_id": user_id})
            return True
        except Exception as e:
            print(f"Error deleting push subscription: {e}")
            return False

