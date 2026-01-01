from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.db.mysql import get_db_session
from app.api.v1.services.companion_service import CompanionService
from app.api.v1.services.user_service import UserService
from app.api.v1.routers.journey_router import get_user_id

router = APIRouter(prefix="/companion", tags=["companion"])
companion_service = CompanionService()


class QuestionRequest(BaseModel):
    question: str
    context_resource_id: Optional[str] = None


class SimplifyRequest(BaseModel):
    resource_id: str
    concept: str
    level: Optional[str] = "beginner"


class ExamplesRequest(BaseModel):
    resource_id: str
    concept: str
    count: Optional[int] = 3


class QuizRequest(BaseModel):
    resource_id: Optional[str] = None
    quiz_type: Optional[str] = "mcq"  # "mcq" or "short_answer"
    num_questions: Optional[int] = 5


@router.post("/{journey_id}/question")
def answer_question(
    journey_id: int,
    request: QuestionRequest,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Answer a question in the context of a learning journey"""
    try:
        result = companion_service.answer_question(
            db, journey_id, user_id, request.question, request.context_resource_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resource/{resource_id}/summarize")
def summarize_resource(
    resource_id: str,
    user_id: int = Depends(get_user_id)
):
    """Generate a summary of a resource"""
    try:
        result = companion_service.summarize_resource(resource_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resource/simplify")
def simplify_explanation(
    request: SimplifyRequest,
    user_id: int = Depends(get_user_id)
):
    """Simplify an explanation for a specific level"""
    try:
        result = companion_service.simplify_explanation(
            request.resource_id, request.concept, request.level
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resource/examples")
def generate_examples(
    request: ExamplesRequest,
    user_id: int = Depends(get_user_id)
):
    """Generate examples for a concept"""
    try:
        result = companion_service.generate_examples(
            request.resource_id, request.concept, request.count
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{journey_id}/quiz")
def generate_quiz(
    journey_id: int,
    request: QuizRequest,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Generate a quiz for a journey or specific resource"""
    try:
        result = companion_service.generate_quiz(
            db, journey_id, user_id, request.resource_id,
            request.quiz_type, request.num_questions
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

