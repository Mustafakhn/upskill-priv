from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.db.base import Journey, JourneyResource, JourneyStatus
from typing import List, Optional
from datetime import datetime


class JourneyDAO:
    """Data Access Object for Journey operations"""
    
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        topic: str,
        level: str,
        goal: str,
        status: JourneyStatus = JourneyStatus.PENDING,
        preferred_format: str = "any"
    ) -> Journey:
        """Create a new learning journey"""
        journey = Journey(
            user_id=user_id,
            topic=topic,
            level=level,
            goal=goal,
            preferred_format=preferred_format,
            status=status
        )
        db.add(journey)
        db.flush()
        return journey
    
    @staticmethod
    def get_by_id(db: Session, journey_id: int) -> Optional[Journey]:
        """Get journey by ID"""
        return db.query(Journey).filter(Journey.id == journey_id).first()
    
    @staticmethod
    def get_by_user(db: Session, user_id: int, limit: int = 100) -> List[Journey]:
        """Get all journeys for a user"""
        return db.query(Journey).filter(
            Journey.user_id == user_id
        ).order_by(desc(Journey.created_at)).limit(limit).all()
    
    @staticmethod
    def update_status(
        db: Session,
        journey_id: int,
        status: JourneyStatus
    ) -> Optional[Journey]:
        """Update journey status"""
        journey = db.query(Journey).filter(Journey.id == journey_id).first()
        if journey:
            journey.status = status
            db.flush()
        return journey
    
    @staticmethod
    def add_resource(
        db: Session,
        journey_id: int,
        resource_id: str,
        order_index: int = 0
    ) -> JourneyResource:
        """Add a resource to a journey"""
        journey_resource = JourneyResource(
            journey_id=journey_id,
            resource_id=resource_id,
            order_index=order_index
        )
        db.add(journey_resource)
        db.flush()
        return journey_resource
    
    @staticmethod
    def get_resources(db: Session, journey_id: int) -> List[JourneyResource]:
        """Get all resources for a journey"""
        return db.query(JourneyResource).filter(
            JourneyResource.journey_id == journey_id
        ).order_by(JourneyResource.order_index).all()
    
    @staticmethod
    def clear_resources(db: Session, journey_id: int):
        """Clear all resources from a journey"""
        db.query(JourneyResource).filter(
            JourneyResource.journey_id == journey_id
        ).delete()
        db.flush()

