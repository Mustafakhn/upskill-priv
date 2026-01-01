from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.db.base import QuizAttempt
from typing import List, Optional, Dict, Any
from datetime import datetime


class QuizDAO:
    """Data Access Object for Quiz operations"""
    
    @staticmethod
    def create_attempt(
        db: Session,
        journey_id: int,
        user_id: int,
        quiz_type: str,
        questions: List[Dict[str, Any]],
        resource_id: str = None
    ) -> QuizAttempt:
        """Create a new quiz attempt"""
        attempt = QuizAttempt(
            journey_id=journey_id,
            user_id=user_id,
            resource_id=resource_id,
            quiz_type=quiz_type,
            questions=questions,
            answers=None,
            completed=0
        )
        db.add(attempt)
        db.flush()
        return attempt
    
    @staticmethod
    def get_attempt(
        db: Session,
        attempt_id: int,
        user_id: int
    ) -> Optional[QuizAttempt]:
        """Get quiz attempt by ID"""
        return db.query(QuizAttempt).filter(
            and_(
                QuizAttempt.id == attempt_id,
                QuizAttempt.user_id == user_id
            )
        ).first()
    
    @staticmethod
    def update_answers(
        db: Session,
        attempt_id: int,
        user_id: int,
        answers: Dict[str, Any]
    ) -> Optional[QuizAttempt]:
        """Update quiz answers"""
        attempt = QuizDAO.get_attempt(db, attempt_id, user_id)
        if attempt:
            attempt.answers = answers
            attempt.updated_at = datetime.utcnow()
            db.flush()
        return attempt
    
    @staticmethod
    def submit_attempt(
        db: Session,
        attempt_id: int,
        user_id: int,
        answers: Dict[str, Any],
        score: int
    ) -> Optional[QuizAttempt]:
        """Submit and complete quiz attempt"""
        attempt = QuizDAO.get_attempt(db, attempt_id, user_id)
        if attempt:
            attempt.answers = answers
            attempt.score = score
            attempt.completed = 1
            attempt.completed_at = datetime.utcnow()
            attempt.updated_at = datetime.utcnow()
            db.flush()
        return attempt
    
    @staticmethod
    def get_user_attempts(
        db: Session,
        user_id: int,
        journey_id: Optional[int] = None,
        limit: int = 50
    ) -> List[QuizAttempt]:
        """Get all quiz attempts for a user"""
        query = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id)
        if journey_id:
            query = query.filter(QuizAttempt.journey_id == journey_id)
        return query.order_by(desc(QuizAttempt.created_at)).limit(limit).all()
    
    @staticmethod
    def get_in_progress_attempt(
        db: Session,
        journey_id: int,
        user_id: int,
        resource_id: Optional[str] = None
    ) -> Optional[QuizAttempt]:
        """Get in-progress quiz attempt"""
        query = db.query(QuizAttempt).filter(
            and_(
                QuizAttempt.journey_id == journey_id,
                QuizAttempt.user_id == user_id,
                QuizAttempt.completed == 0
            )
        )
        if resource_id:
            query = query.filter(QuizAttempt.resource_id == resource_id)
        return query.order_by(desc(QuizAttempt.created_at)).first()

