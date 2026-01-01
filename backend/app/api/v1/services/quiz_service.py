from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from app.api.v1.dao.quiz_dao import QuizDAO
from app.api.v1.dao.journey_dao import JourneyDAO
from app.api.v1.services.companion_service import CompanionService


class QuizService:
    """Service for quiz operations"""
    
    def __init__(self):
        self.quiz_dao = QuizDAO
        self.journey_dao = JourneyDAO
        self.companion_service = CompanionService()
    
    def create_quiz(
        self,
        db: Session,
        journey_id: int,
        user_id: int,
        resource_id: Optional[str] = None,
        quiz_type: str = "mcq",
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """Create a new quiz"""
        journey = self.journey_dao.get_by_id(db, journey_id)
        if not journey or journey.user_id != user_id:
            raise ValueError("Journey not found or unauthorized")
        
        # Generate quiz using companion service
        quiz_data = self.companion_service.generate_quiz(
            db, journey_id, user_id, resource_id, quiz_type, num_questions
        )
        
        # Create quiz attempt
        attempt = self.quiz_dao.create_attempt(
            db, journey_id, user_id, quiz_type, quiz_data["questions"], resource_id
        )
        db.commit()
        
        return {
            "attempt_id": attempt.id,
            "quiz_type": quiz_type,
            "questions": quiz_data["questions"],
            "journey_id": journey_id,
            "resource_id": resource_id
        }
    
    def get_quiz(
        self,
        db: Session,
        attempt_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get quiz attempt"""
        attempt = self.quiz_dao.get_attempt(db, attempt_id, user_id)
        if not attempt:
            return None
        
        return {
            "attempt_id": attempt.id,
            "journey_id": attempt.journey_id,
            "resource_id": attempt.resource_id,
            "quiz_type": attempt.quiz_type,
            "questions": attempt.questions,
            "answers": attempt.answers,
            "score": attempt.score,
            "completed": attempt.completed == 1,
            "created_at": attempt.created_at.isoformat(),
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None
        }
    
    def save_answers(
        self,
        db: Session,
        attempt_id: int,
        user_id: int,
        answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save quiz answers (before submission)"""
        attempt = self.quiz_dao.update_answers(db, attempt_id, user_id, answers)
        if not attempt:
            raise ValueError("Quiz attempt not found")
        db.commit()
        
        return {
            "attempt_id": attempt_id,
            "answers": answers
        }
    
    def submit_quiz(
        self,
        db: Session,
        attempt_id: int,
        user_id: int,
        answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit quiz and calculate score"""
        attempt = self.quiz_dao.get_attempt(db, attempt_id, user_id)
        if not attempt:
            raise ValueError("Quiz attempt not found")
        
        # Calculate score
        questions = attempt.questions
        correct = 0
        total = len(questions)
        
        for idx, question in enumerate(questions):
            if attempt.quiz_type == "mcq":
                user_answer = answers.get(str(idx))
                correct_answer = question.get("correct_answer")
                if user_answer == correct_answer:
                    correct += 1
            # For short_answer, we'd need AI to evaluate, for now just mark as correct if answered
            elif attempt.quiz_type == "short_answer":
                user_answer = answers.get(str(idx))
                if user_answer and user_answer.strip():
                    correct += 1
        
        score = int((correct / total * 100)) if total > 0 else 0
        
        # Submit attempt
        self.quiz_dao.submit_attempt(db, attempt_id, user_id, answers, score)
        db.commit()
        
        return {
            "attempt_id": attempt_id,
            "score": score,
            "correct": correct,
            "total": total,
            "answers": answers,
            "questions": questions,
            "completed": True,
            "journey_id": attempt.journey_id,
            "resource_id": attempt.resource_id,
            "quiz_type": attempt.quiz_type
        }
    
    def get_user_quizzes(
        self,
        db: Session,
        user_id: int,
        journey_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all quiz attempts for a user"""
        attempts = self.quiz_dao.get_user_attempts(db, user_id, journey_id)
        result = []
        for a in attempts:
            quiz_data = {
                "attempt_id": a.id,
                "journey_id": a.journey_id,
                "resource_id": a.resource_id,
                "quiz_type": a.quiz_type,
                "score": a.score,
                "completed": a.completed == 1,
                "created_at": a.created_at.isoformat(),
                "completed_at": a.completed_at.isoformat() if a.completed_at else None
            }
            # Add journey topic if available
            try:
                journey = self.journey_dao.get_by_id(db, a.journey_id)
                if journey:
                    quiz_data["journey_topic"] = journey.topic
            except:
                pass
            result.append(quiz_data)
        return result

