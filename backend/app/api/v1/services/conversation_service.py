from typing import List, Dict, Any, Optional
from datetime import datetime
from app.api.v1.dao.chat_dao import ChatDAO


class ConversationService:
    """Service for conversation operations (MongoDB-based)"""

    def __init__(self):
        self.chat_dao = ChatDAO

    def get_or_create_active_conversation(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """Get active conversation or create a new one"""
        chat = self.chat_dao.get_active_chat(user_id)

        if not chat:
            chat_id = self.chat_dao.create_chat(user_id)
            chat = self.chat_dao.get_chat(chat_id)

        return {
            "id": chat["id"],
            "user_id": chat["user_id"],
            "journey_id": chat.get("journey_id"),
            "created_at": chat["created_at"].isoformat() if isinstance(chat["created_at"], datetime) else chat["created_at"],
            "updated_at": chat["updated_at"].isoformat() if isinstance(chat["updated_at"], datetime) else chat["updated_at"]
        }

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str
    ) -> Dict[str, Any]:
        """Add a message to a conversation"""
        try:
            success = self.chat_dao.add_message(conversation_id, role, content)
            
            if success:
                return {
                    "conversation_id": conversation_id,
                    "role": role,
                    "content": content
                }
            else:
                print(f"Warning: add_message returned False for conversation_id={conversation_id}")
                # Don't raise exception, just return the dict anyway - message might have been added
                return {
                    "conversation_id": conversation_id,
                    "role": role,
                    "content": content
                }
        except Exception as e:
            print(f"Error adding message to conversation {conversation_id}: {e}")
            import traceback
            traceback.print_exc()
            # Still return the dict so the conversation can continue
            return {
                "conversation_id": conversation_id,
                "role": role,
                "content": content
            }

    def get_conversation_messages(
        self,
        conversation_id: str,
        user_id: int = None
    ) -> List[Dict[str, Any]]:
        """Get all messages for a conversation"""
        # Verify the chat belongs to the user if user_id is provided
        if user_id:
            chat = self.chat_dao.get_chat(conversation_id)
            if not chat or chat.get("user_id") != user_id:
                return []
        
        messages = self.chat_dao.get_messages(conversation_id)
        return messages

    def get_user_conversations(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Get all conversations for a user"""
        chats = self.chat_dao.get_chats_by_user(user_id)
        
        result = []
        for chat in chats:
            result.append({
                "id": chat["id"],
                "user_id": chat["user_id"],
                "journey_id": chat.get("journey_id"),
                "created_at": chat["created_at"].isoformat() if isinstance(chat["created_at"], datetime) else chat["created_at"],
                "updated_at": chat["updated_at"].isoformat() if isinstance(chat["updated_at"], datetime) else chat["updated_at"]
            })
        return result

    def link_journey_to_conversation(
        self,
        conversation_id: str,
        journey_id: int
    ):
        """Link a journey to a conversation"""
        self.chat_dao.link_journey(conversation_id, journey_id)
    
    def get_conversation_by_journey(
        self,
        user_id: int,
        journey_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get conversation by journey_id"""
        chat = self.chat_dao.get_chat_by_journey(user_id, journey_id)
        if not chat:
            return None
        
        return {
            "id": chat["id"],
            "user_id": chat["user_id"],
            "journey_id": chat.get("journey_id"),
            "created_at": chat["created_at"].isoformat() if isinstance(chat["created_at"], datetime) else chat["created_at"],
            "updated_at": chat["updated_at"].isoformat() if isinstance(chat["updated_at"], datetime) else chat["updated_at"]
        }
