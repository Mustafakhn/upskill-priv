from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from app.api.v1.services.ai_service import AIService
from app.api.v1.services.agent_service import AgentService
from app.api.v1.services.journey_service import JourneyService
from app.api.v1.services.user_service import UserService
from app.api.v1.services.conversation_service import ConversationService
from app.api.v1.dao.chat_dao import ChatDAO
from sqlalchemy.orm import Session
from app.db.mysql import get_db_session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer()

ai_service = AIService()
agent_service = AgentService()
journey_service = JourneyService()
user_service = UserService()
conversation_service = ConversationService()


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatStartRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []


class ChatStartResponse(BaseModel):
    response: str
    questions: Optional[List[str]] = None
    ready: bool = False
    journey_id: Optional[int] = None
    conversation_id: str  # MongoDB ObjectId as string


class ChatRespondRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage]
    conversation_id: Optional[str] = None  # MongoDB ObjectId as string


class ChatRespondResponse(BaseModel):
    response: str
    questions: Optional[List[str]] = None
    ready: bool = False
    journey_id: Optional[int] = None
    conversation_id: str  # MongoDB ObjectId as string


class ChatHistoryDetailResponse(BaseModel):
    conversation_id: str  # MongoDB ObjectId as string
    messages: List[ChatMessage]
    journey_id: Optional[int] = None


class ConversationSummary(BaseModel):
    id: str  # MongoDB ObjectId as string
    user_id: int
    journey_id: Optional[int] = None
    created_at: str
    updated_at: str


def get_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get user ID from token"""
    token = credentials.credentials
    user_id = user_service.verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


@router.post("/start", response_model=ChatStartResponse)
def start_chat(
    request: ChatStartRequest,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Start a chat session"""
    # Get or create active conversation (MongoDB)
    conversation = conversation_service.get_or_create_active_conversation(user_id)
    conversation_id = conversation["id"]
    
    # Load existing messages if any
    existing_messages = conversation_service.get_conversation_messages(conversation_id, user_id)
    history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in existing_messages
    ]
    
    # Add current message
    history.append({"role": "user", "content": request.message})
    
    # Save user message to MongoDB
    conversation_service.add_message(conversation_id, "user", request.message)
    
    # Generate response
    response_text = ai_service.generate_chat_response(history[:-1], request.message)
    
    # Save assistant response to MongoDB
    conversation_service.add_message(conversation_id, "assistant", response_text)
    
    # Use unified analysis (single AI call for everything)
    user_messages = [msg for msg in history if msg.get("role") == "user"]
    chat = ChatDAO.get_chat(conversation_id)
    asked_questions = chat.get("asked_questions", []) if chat else []
    analysis = ai_service.analyze_conversation(history, asked_questions, len(user_messages))
    ready = analysis["is_ready"]
    intent = analysis["intent"]
    journey_id = None
    
    print(f"[DEBUG] start_chat: is_ready={ready}")
    
    if ready:
        print(f"[DEBUG] start_chat: Creating journey...")
        
        # Check if user can create free journey
        if not user_service.can_create_free_journey(db, user_id):
            return ChatStartResponse(
                response="You've used all your free journeys. Please upgrade to continue.",
                questions=None,
                ready=False,
                journey_id=None,
                conversation_id=conversation_id
            )
        
        # Create journey with preferred format
        journey = journey_service.create_journey(
            db=db,
            user_id=user_id,
            topic=intent["topic"],
            level=intent["level"],
            goal=intent["goal"],
            preferred_format=intent.get("preferred_format", "any")
        )
        
        user_service.increment_free_journeys(db, user_id)
        journey_id = journey["id"]
        
        # Link journey to conversation
        conversation_service.link_journey_to_conversation(conversation_id, journey_id)
        
        response_text = f"Perfect! I've started creating your personalized learning journey for '{intent['topic']}'. This may take a few minutes."
    
    # Get next suggestions if not ready (already computed in analysis above)
    questions = None
    next_suggestions = analysis.get("next_suggestions", [])
    if not ready and next_suggestions and len(next_suggestions) > 0:
        # Save the first suggestion to conversation state (for tracking)
        asked_questions.append(next_suggestions[0])
        ChatDAO.update_asked_questions(conversation_id, asked_questions)
        questions = next_suggestions  # Return all suggestions as array
    
    return ChatStartResponse(
        response=response_text,
        questions=questions,
        ready=ready,
        journey_id=journey_id,
        conversation_id=conversation_id
    )


@router.post("/respond", response_model=ChatRespondResponse)
def respond_to_chat(
    request: ChatRespondRequest,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Respond to chat message"""
    # Get or create conversation
    if request.conversation_id:
        conversation_id = request.conversation_id
    else:
        conversation = conversation_service.get_or_create_active_conversation(user_id)
        conversation_id = conversation["id"]
    
    # Load existing messages
    existing_messages = conversation_service.get_conversation_messages(conversation_id, user_id)
    history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in existing_messages
    ]
    
    # Add current message
    history.append({"role": "user", "content": request.message})
    
    # Save user message to MongoDB
    conversation_service.add_message(conversation_id, "user", request.message)
    
    # Generate response
    response_text = ai_service.generate_chat_response(history[:-1], request.message)
    
    # Save assistant response to MongoDB
    conversation_service.add_message(conversation_id, "assistant", response_text)
    
    # Use unified analysis method (single AI call for everything)
    user_messages = [msg for msg in history if msg.get("role") == "user"]
    analysis = ai_service.analyze_conversation(history, asked_questions=[], user_message_count=len(user_messages))
    ready = analysis["is_ready"]
    intent = analysis["intent"]
    journey_id = None
    
    print(f"[DEBUG] respond_to_chat: is_ready={ready}")
    
    if ready:
        print(f"[DEBUG] respond_to_chat: Creating journey...")
        
        # Check if user can create free journey
        if not user_service.can_create_free_journey(db, user_id):
            return ChatRespondResponse(
                response="You've used all your free journeys. Please upgrade to continue.",
                ready=False,
                questions=None,
                journey_id=None,
                conversation_id=conversation_id
            )
        
        # Create journey with preferred format
        journey = journey_service.create_journey(
            db=db,
            user_id=user_id,
            topic=intent["topic"],
            level=intent["level"],
            goal=intent["goal"],
            preferred_format=intent.get("preferred_format", "any")
        )
        
        user_service.increment_free_journeys(db, user_id)
        journey_id = journey["id"]
        
        # Link journey to conversation
        conversation_service.link_journey_to_conversation(conversation_id, journey_id)
        
        response_text = f"Perfect! I've started creating your personalized learning journey for '{intent['topic']}'. This may take a few minutes."
    
    # Get next suggestions if not ready (already computed in analysis above)
    questions = None
    if not ready:
        chat = ChatDAO.get_chat(conversation_id)
        asked_questions = chat.get("asked_questions", []) if chat else []
        
        # Use the suggestions from the analysis (already computed, no additional AI call)
        next_suggestions = analysis.get("next_suggestions", [])
        if next_suggestions and len(next_suggestions) > 0:
            # Save the first suggestion to conversation state (for tracking)
            asked_questions.append(next_suggestions[0])
            ChatDAO.update_asked_questions(conversation_id, asked_questions)
            questions = next_suggestions  # Return all suggestions as array
    
    return ChatRespondResponse(
        response=response_text,
        questions=questions,
        ready=ready,
        journey_id=journey_id,
        conversation_id=conversation_id
    )


@router.get("/history/{conversation_id}", response_model=ChatHistoryDetailResponse)
def get_chat_history(
    conversation_id: str,
    user_id: int = Depends(get_user_id)
):
    """Get chat history for a conversation"""
    chat = ChatDAO.get_chat(conversation_id)
    
    if not chat or chat.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = conversation_service.get_conversation_messages(conversation_id, user_id)
    
    return ChatHistoryDetailResponse(
        conversation_id=conversation_id,
        journey_id=chat.get("journey_id"),
        messages=[
            ChatMessage(role=msg["role"], content=msg["content"])
            for msg in messages
        ]
    )


@router.get("/history", response_model=List[ConversationSummary])
def get_user_conversations(
    user_id: int = Depends(get_user_id)
):
    """Get all conversations for the current user"""
    conversations = conversation_service.get_user_conversations(user_id)
    return conversations
