from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.api.v1.dao.progress_dao import ProgressDAO
from app.api.v1.dao.journey_dao import JourneyDAO


class ProgressService:
    """Service for journey progress operations"""
    
    def __init__(self):
        self.progress_dao = ProgressDAO
        self.journey_dao = JourneyDAO
    
    def get_progress_summary(
        self,
        db: Session,
        journey_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get progress summary for a journey"""
        journey = self.journey_dao.get_by_id(db, journey_id)
        if not journey:
            return None
        
        # Check authorization
        if journey.user_id != user_id:
            return None
        
        # Get total resources count
        from app.api.v1.dao.journey_dao import JourneyDAO
        journey_resources = JourneyDAO.get_resources(db, journey_id)
        total_resources = len(journey_resources)
        
        return self.progress_dao.get_progress_summary(
            db, journey_id, user_id, total_resources
        )
    
    def mark_resource_completed(
        self,
        db: Session,
        journey_id: int,
        user_id: int,
        resource_id: str
    ) -> Dict[str, Any]:
        """Mark a resource as completed"""
        journey = self.journey_dao.get_by_id(db, journey_id)
        if not journey or journey.user_id != user_id:
            raise ValueError("Journey not found or unauthorized")
        
        progress = self.progress_dao.mark_resource_completed(
            db, journey_id, user_id, resource_id
        )
        db.commit()
        # Refresh the progress object to ensure we have the latest state
        db.refresh(progress)
        
        return {
            "resource_id": resource_id,
            "completed": progress.completed,
            "completed_at": progress.completed_at.isoformat() if progress.completed_at else None
        }
    
    def mark_resource_in_progress(
        self,
        db: Session,
        journey_id: int,
        user_id: int,
        resource_id: str
    ) -> Dict[str, Any]:
        """Mark a resource as in progress"""
        journey = self.journey_dao.get_by_id(db, journey_id)
        if not journey or journey.user_id != user_id:
            raise ValueError("Journey not found or unauthorized")
        
        progress = self.progress_dao.mark_resource_in_progress(
            db, journey_id, user_id, resource_id
        )
        db.commit()
        
        return {
            "resource_id": resource_id,
            "completed": progress.completed,
            "last_accessed_at": progress.last_accessed_at.isoformat()
        }
    
    def mark_resource_incomplete(
        self,
        db: Session,
        journey_id: int,
        user_id: int,
        resource_id: str
    ) -> Dict[str, Any]:
        """Mark a resource as incomplete (unmark completion)"""
        journey = self.journey_dao.get_by_id(db, journey_id)
        if not journey or journey.user_id != user_id:
            raise ValueError("Journey not found or unauthorized")
        
        progress = self.progress_dao.mark_resource_incomplete(
            db, journey_id, user_id, resource_id
        )
        db.commit()
        
        return {
            "resource_id": resource_id,
            "completed": progress.completed,
            "completed_at": None
        }
    
    def update_time_spent(
        self,
        db: Session,
        journey_id: int,
        user_id: int,
        resource_id: str,
        time_spent_minutes: int
    ) -> Dict[str, Any]:
        """Update time spent on a resource"""
        journey = self.journey_dao.get_by_id(db, journey_id)
        if not journey or journey.user_id != user_id:
            raise ValueError("Journey not found or unauthorized")
        
        progress = self.progress_dao.update_time_spent(
            db, journey_id, user_id, resource_id, time_spent_minutes
        )
        db.commit()
        
        return {
            "resource_id": resource_id,
            "time_spent_minutes": progress.time_spent_minutes
        }
    
    def get_last_position(
        self,
        db: Session,
        journey_id: int,
        user_id: int
    ) -> Optional[int]:
        """Get the last accessed resource index for a journey"""
        journey = self.journey_dao.get_by_id(db, journey_id)
        if not journey or journey.user_id != user_id:
            return None
        
        last_progress = self.progress_dao.get_last_accessed_resource(
            db, journey_id, user_id
        )
        if not last_progress:
            return None
        
        # Find the index of the last accessed resource
        from app.api.v1.dao.journey_dao import JourneyDAO
        journey_resources = JourneyDAO.get_resources(db, journey_id)
        for idx, jr in enumerate(journey_resources):
            if jr.resource_id == last_progress.resource_id:
                return idx
        
        return None

