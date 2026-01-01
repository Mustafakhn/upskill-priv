from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.mysql import get_db_session
from app.api.v1.services.quiz_service import QuizService
from app.api.v1.routers.journey_router import get_user_id

router = APIRouter(prefix="/quiz", tags=["quiz"])
quiz_service = QuizService()


class CreateQuizRequest(BaseModel):
    resource_id: Optional[str] = None
    quiz_type: Optional[str] = "mcq"
    num_questions: Optional[int] = 5


class SaveAnswersRequest(BaseModel):
    answers: Dict[str, Any]


class SubmitQuizRequest(BaseModel):
    answers: Dict[str, Any]


@router.post("/{journey_id}/create")
def create_quiz(
    journey_id: int,
    request: CreateQuizRequest,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Create a new quiz"""
    try:
        result = quiz_service.create_quiz(
            db, journey_id, user_id, request.resource_id,
            request.quiz_type, request.num_questions
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{attempt_id}")
def get_quiz(
    attempt_id: int,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Get quiz attempt"""
    quiz = quiz_service.get_quiz(db, attempt_id, user_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("/{attempt_id}/save")
def save_answers(
    attempt_id: int,
    request: SaveAnswersRequest,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Save quiz answers (before submission)"""
    try:
        result = quiz_service.save_answers(db, attempt_id, user_id, request.answers)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{attempt_id}/submit")
def submit_quiz(
    attempt_id: int,
    request: SubmitQuizRequest,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Submit quiz and get results"""
    try:
        result = quiz_service.submit_quiz(db, attempt_id, user_id, request.answers)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/quizzes")
def get_user_quizzes(
    user_id: int,
    journey_id: Optional[int] = None,
    current_user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Get all quiz attempts for a user"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    quizzes = quiz_service.get_user_quizzes(db, user_id, journey_id)
    return {"quizzes": quizzes, "count": len(quizzes)}

