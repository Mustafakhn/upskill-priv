from app.db.mongo import get_mongo_db
from bson import ObjectId
from typing import List, Optional, Dict, Any
from datetime import datetime
from pymongo.collection import Collection


class ChatDAO:
    """Data Access Object for Chat operations (MongoDB)"""
    
    @staticmethod
    def get_collection() -> Collection:
        """Get chats collection"""
        db = get_mongo_db()
        return db.chats
    
    @staticmethod
    def create_chat(
        user_id: int,
        journey_id: Optional[int] = None
    ) -> str:
        """Create a new chat conversation"""
        collection = ChatDAO.get_collection()
        chat = {
            "user_id": user_id,
            "journey_id": journey_id,
            "messages": [],
            "asked_questions": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = collection.insert_one(chat)
        return str(result.inserted_id)
    
    @staticmethod
    def get_chat(chat_id: str) -> Optional[Dict[str, Any]]:
        """Get chat by ID"""
        collection = ChatDAO.get_collection()
        try:
            chat = collection.find_one({"_id": ObjectId(chat_id)})
            if chat:
                chat["id"] = str(chat["_id"])
                del chat["_id"]
            return chat
        except Exception:
            return None
    
    @staticmethod
    def get_chats_by_user(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all chats for a user, sorted by updated_at descending"""
        collection = ChatDAO.get_collection()
        chats = collection.find(
            {"user_id": user_id}
        ).sort("updated_at", -1).limit(limit)
        
        result = []
        for chat in chats:
            chat["id"] = str(chat["_id"])
            del chat["_id"]
            result.append(chat)
        return result
    
    @staticmethod
    def get_active_chat(user_id: int) -> Optional[Dict[str, Any]]:
        """Get the most recent active chat for a user (no journey created yet)"""
        collection = ChatDAO.get_collection()
        chat = collection.find_one(
            {"user_id": user_id, "journey_id": None},
            sort=[("updated_at", -1)]
        )
        if chat:
            chat["id"] = str(chat["_id"])
            del chat["_id"]
        return chat
    
    @staticmethod
    def add_message(
        chat_id: str,
        role: str,
        content: str
    ) -> bool:
        """Add a message to a chat"""
        collection = ChatDAO.get_collection()
        try:
            # First verify the chat exists
            chat = ChatDAO.get_chat(chat_id)
            if not chat:
                print(f"Warning: Chat {chat_id} not found when trying to add message")
                return False
            
            message = {
                "role": role,
                "content": content,
                "created_at": datetime.utcnow()
            }
            result = collection.update_one(
                {"_id": ObjectId(chat_id)},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            if result.modified_count == 0:
                print(f"Warning: Failed to modify chat {chat_id} when adding message (matched_count={result.matched_count})")
                return False
            return True
        except Exception as e:
            print(f"Error adding message to chat {chat_id}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def link_journey(chat_id: str, journey_id: int) -> bool:
        """Link a journey to a chat"""
        collection = ChatDAO.get_collection()
        try:
            result = collection.update_one(
                {"_id": ObjectId(chat_id)},
                {
                    "$set": {
                        "journey_id": journey_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    @staticmethod
    def update_asked_questions(chat_id: str, asked_questions: List[str]) -> bool:
        """Update asked questions list"""
        collection = ChatDAO.get_collection()
        try:
            result = collection.update_one(
                {"_id": ObjectId(chat_id)},
                {
                    "$set": {
                        "asked_questions": asked_questions,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    @staticmethod
    def get_chat_by_journey(user_id: int, journey_id: int) -> Optional[Dict[str, Any]]:
        """Get chat by journey_id and user_id"""
        collection = ChatDAO.get_collection()
        chat = collection.find_one(
            {"user_id": user_id, "journey_id": journey_id},
            sort=[("updated_at", -1)]
        )
        if chat:
            chat["id"] = str(chat["_id"])
            del chat["_id"]
        return chat
    
    @staticmethod
    def get_messages(chat_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a chat"""
        chat = ChatDAO.get_chat(chat_id)
        if chat and "messages" in chat:
            # Convert datetime objects to ISO format strings
            messages = []
            for msg in chat["messages"]:
                msg_dict = {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                if "created_at" in msg and isinstance(msg["created_at"], datetime):
                    msg_dict["created_at"] = msg["created_at"].isoformat()
                messages.append(msg_dict)
            return messages
        return []

