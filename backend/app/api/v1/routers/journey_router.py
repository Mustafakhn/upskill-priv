from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.mysql import get_db_session
from app.api.v1.services.journey_service import JourneyService
from app.api.v1.services.progress_service import ProgressService
from app.api.v1.services.user_service import UserService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from collections import Counter
from app.db.base import Journey

router = APIRouter(prefix="/journey", tags=["journey"])
security = HTTPBearer()

journey_service = JourneyService()
progress_service = ProgressService()
user_service = UserService()


def get_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get user ID from token"""
    token = credentials.credentials
    user_id = user_service.verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


class JourneyResponse(BaseModel):
    id: int
    user_id: int
    topic: str
    level: str
    goal: str
    status: str
    created_at: str
    resources: List[dict]
    resource_count: int
    sections: Optional[List[dict]] = []


class JourneyListResponse(BaseModel):
    id: int
    topic: str
    level: str
    goal: str
    status: str
    created_at: str


@router.get("/topics/popular")
def get_popular_topics(
    db: Session = Depends(get_db_session),
    limit: int = 8
):
    """Get popular learning topics from existing journeys"""
    try:
        # Get recent journeys and count topics
        all_journeys = db.query(Journey).order_by(Journey.created_at.desc()).limit(500).all()
        
        # Count topics
        topic_counts = Counter()
        for journey in all_journeys:
            if journey.topic:
                topic_counts[journey.topic.lower()] += 1
        
        # Get top topics
        popular_topics = [topic.capitalize() for topic, count in topic_counts.most_common(limit)]
        
        # If we don't have enough, add some defaults
        default_topics = [
            "Learn Python", "Master Guitar", "Italian Cooking", "Digital Marketing",
            "Web Development", "Data Science", "Machine Learning", "Photography",
            "Spanish Language", "Graphic Design", "Music Production", "Cooking Basics"
        ]
        
        # Combine and deduplicate
        all_topics = list(dict.fromkeys(popular_topics + default_topics))[:limit]
        
        return {"topics": all_topics}
    except Exception as e:
        print(f"Error fetching popular topics: {e}")
        # Return defaults on error
        return {
            "topics": [
                "Learn Python", "Master Guitar", "Italian Cooking", "Digital Marketing",
                "Web Development", "Data Science", "Machine Learning", "Photography"
            ]
        }


@router.get("/{journey_id}", response_model=JourneyResponse)
def get_journey(
    journey_id: int,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Get a specific journey with resources"""
    journey = journey_service.get_journey(db, journey_id, user_id)
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    return journey


@router.get("/", response_model=List[JourneyListResponse])
def get_user_journeys(
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Get all journeys for the current user"""
    journeys = journey_service.get_user_journeys(db, user_id)
    return journeys


class MarkResourceRequest(BaseModel):
    resource_id: str


class UpdateTimeSpentRequest(BaseModel):
    resource_id: str
    time_spent_minutes: int


@router.post("/{journey_id}/progress/summary")
def get_progress_summary(
    journey_id: int,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Get progress summary for a journey"""
    summary = progress_service.get_progress_summary(db, journey_id, user_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Journey not found")
    return summary


@router.post("/{journey_id}/progress/complete")
def mark_resource_completed(
    journey_id: int,
    request: MarkResourceRequest,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Mark a resource as completed"""
    try:
        result = progress_service.mark_resource_completed(
            db, journey_id, user_id, request.resource_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{journey_id}/progress/in-progress")
def mark_resource_in_progress(
    journey_id: int,
    request: MarkResourceRequest,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Mark a resource as in progress"""
    try:
        result = progress_service.mark_resource_in_progress(
            db, journey_id, user_id, request.resource_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{journey_id}/progress/incomplete")
def mark_resource_incomplete(
    journey_id: int,
    request: MarkResourceRequest,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Mark a resource as incomplete (unmark completion)"""
    try:
        result = progress_service.mark_resource_incomplete(
            db, journey_id, user_id, request.resource_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{journey_id}/progress/time")
def update_time_spent(
    journey_id: int,
    request: UpdateTimeSpentRequest,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Update time spent on a resource"""
    try:
        result = progress_service.update_time_spent(
            db, journey_id, user_id, request.resource_id, request.time_spent_minutes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{journey_id}/progress/last-position")
def get_last_position(
    journey_id: int,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Get the last accessed resource index"""
    position = progress_service.get_last_position(db, journey_id, user_id)
    return {"last_position": position}

