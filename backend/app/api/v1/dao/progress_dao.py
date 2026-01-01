from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.db.base import JourneyProgress
from typing import List, Optional, Dict, Any
from datetime import datetime


class ProgressDAO:
    """Data Access Object for Journey Progress operations"""
    
    @staticmethod
    def get_progress(
        db: Session,
        journey_id: int,
        user_id: int,
        resource_id: str
    ) -> Optional[JourneyProgress]:
        """Get progress for a specific resource in a journey"""
        return db.query(JourneyProgress).filter(
            and_(
                JourneyProgress.journey_id == journey_id,
                JourneyProgress.user_id == user_id,
                JourneyProgress.resource_id == resource_id
            )
        ).first()
    
    @staticmethod
    def get_all_progress(
        db: Session,
        journey_id: int,
        user_id: int
    ) -> List[JourneyProgress]:
        """Get all progress records for a journey"""
        return db.query(JourneyProgress).filter(
            and_(
                JourneyProgress.journey_id == journey_id,
                JourneyProgress.user_id == user_id
            )
        ).all()
    
    @staticmethod
    def upsert_progress(
        db: Session,
        journey_id: int,
        user_id: int,
        resource_id: str,
        completed: int = 0,
        time_spent_minutes: int = 0,
        is_completed: bool = False
    ) -> JourneyProgress:
        """Create or update progress for a resource"""
        progress = ProgressDAO.get_progress(db, journey_id, user_id, resource_id)
        
        if progress:
            # Update existing
            # If is_completed is True, always set to 2 (completed)
            # Otherwise, use the max of current and new completed value, but don't downgrade from 2
            if is_completed:
                progress.completed = 2
            elif progress.completed != 2:  # Only update if not already completed
                # Refresh the progress object to ensure we have the latest state from the database
                db.refresh(progress)
                # Double-check after refresh that it's still not completed
                if progress.completed != 2:
                    progress.completed = max(progress.completed, completed)
            progress.time_spent_minutes += time_spent_minutes
            progress.last_accessed_at = datetime.utcnow()
            if is_completed and progress.completed_at is None:
                progress.completed_at = datetime.utcnow()
            progress.updated_at = datetime.utcnow()
        else:
            # Create new
            progress = JourneyProgress(
                journey_id=journey_id,
                user_id=user_id,
                resource_id=resource_id,
                completed=2 if is_completed else completed,
                time_spent_minutes=time_spent_minutes,
                last_accessed_at=datetime.utcnow(),
                completed_at=datetime.utcnow() if is_completed else None
            )
            db.add(progress)
        
        db.flush()
        return progress
    
    @staticmethod
    def mark_resource_completed(
        db: Session,
        journey_id: int,
        user_id: int,
        resource_id: str
    ) -> JourneyProgress:
        """Mark a resource as completed"""
        return ProgressDAO.upsert_progress(
            db, journey_id, user_id, resource_id,
            completed=2, is_completed=True
        )
    
    @staticmethod
    def mark_resource_in_progress(
        db: Session,
        journey_id: int,
        user_id: int,
        resource_id: str
    ) -> JourneyProgress:
        """Mark a resource as in progress"""
        # Don't overwrite if already completed (completed=2)
        progress = ProgressDAO.get_progress(db, journey_id, user_id, resource_id)
        if progress and progress.completed == 2:
            # Already completed, don't change status
            return progress
        
        return ProgressDAO.upsert_progress(
            db, journey_id, user_id, resource_id,
            completed=1
        )
    
    @staticmethod
    def mark_resource_incomplete(
        db: Session,
        journey_id: int,
        user_id: int,
        resource_id: str
    ) -> JourneyProgress:
        """Mark a resource as incomplete (not completed)"""
        progress = ProgressDAO.get_progress(db, journey_id, user_id, resource_id)
        if progress:
            # Update existing
            progress.completed = 0
            progress.completed_at = None
            progress.last_accessed_at = datetime.utcnow()
            progress.updated_at = datetime.utcnow()
        else:
            # Create new with incomplete status
            progress = JourneyProgress(
                journey_id=journey_id,
                user_id=user_id,
                resource_id=resource_id,
                completed=0,
                time_spent_minutes=0,
                last_accessed_at=datetime.utcnow(),
                completed_at=None
            )
            db.add(progress)
        
        db.flush()
        return progress
    
    @staticmethod
    def update_time_spent(
        db: Session,
        journey_id: int,
        user_id: int,
        resource_id: str,
        time_spent_minutes: int
    ) -> JourneyProgress:
        """Update time spent on a resource"""
        return ProgressDAO.upsert_progress(
            db, journey_id, user_id, resource_id,
            time_spent_minutes=time_spent_minutes
        )
    
    @staticmethod
    def get_last_accessed_resource(
        db: Session,
        journey_id: int,
        user_id: int
    ) -> Optional[JourneyProgress]:
        """Get the last accessed resource for a journey"""
        return db.query(JourneyProgress).filter(
            and_(
                JourneyProgress.journey_id == journey_id,
                JourneyProgress.user_id == user_id
            )
        ).order_by(desc(JourneyProgress.last_accessed_at)).first()
    
    @staticmethod
    def get_progress_summary(
        db: Session,
        journey_id: int,
        user_id: int,
        total_resources: int
    ) -> Dict[str, Any]:
        """Get progress summary for a journey"""
        all_progress = ProgressDAO.get_all_progress(db, journey_id, user_id)
        
        completed_count = sum(1 for p in all_progress if p.completed == 2)
        in_progress_count = sum(1 for p in all_progress if p.completed == 1)
        total_time_spent = sum(p.time_spent_minutes for p in all_progress)
        completion_percentage = (completed_count / total_resources * 100) if total_resources > 0 else 0
        
        return {
            "total_resources": total_resources,
            "completed_count": completed_count,
            "in_progress_count": in_progress_count,
            "not_started_count": total_resources - completed_count - in_progress_count,
            "completion_percentage": round(completion_percentage, 1),
            "total_time_spent_minutes": total_time_spent,
            "progress_by_resource": {
                p.resource_id: {
                    "completed": p.completed,
                    "time_spent_minutes": p.time_spent_minutes,
                    "last_accessed_at": p.last_accessed_at.isoformat() if p.last_accessed_at else None,
                    "completed_at": p.completed_at.isoformat() if p.completed_at else None
                }
                for p in all_progress
            }
        }
