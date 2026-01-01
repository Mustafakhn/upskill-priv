from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, JSON
from datetime import datetime
import enum

Base = declarative_base()


class JourneyStatus(enum.Enum):
    PENDING = "pending"
    SCRAPING = "scraping"
    CURATING = "curating"
    READY = "ready"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    free_journeys_used = Column(Integer, default=0, nullable=False)
    is_premium = Column(Integer, default=0, nullable=False)  # 0 = false, 1 = true
    is_admin = Column(Integer, default=0, nullable=False)  # 0 = false, 1 = true
    premium_requested = Column(Integer, default=0, nullable=False)  # 0 = false, 1 = true
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Journey(Base):
    __tablename__ = "journeys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    topic = Column(String(500), nullable=False)
    level = Column(String(50), nullable=False)
    goal = Column(Text, nullable=False)
    preferred_format = Column(String(20), nullable=True)  # video, blog, doc, any
    status = Column(Enum(JourneyStatus), default=JourneyStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class JourneyResource(Base):
    __tablename__ = "journey_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    journey_id = Column(Integer, ForeignKey("journeys.id"), nullable=False, index=True)
    resource_id = Column(String(255), nullable=False)  # MongoDB ObjectId as string
    order_index = Column(Integer, default=0, nullable=False)


class JourneyProgress(Base):
    __tablename__ = "journey_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    journey_id = Column(Integer, ForeignKey("journeys.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resource_id = Column(String(255), nullable=False, index=True)  # MongoDB ObjectId as string
    completed = Column(Integer, default=0, nullable=False)  # 0 = not started, 1 = in progress, 2 = completed
    time_spent_minutes = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    journey_id = Column(Integer, ForeignKey("journeys.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resource_id = Column(String(255), nullable=True, index=True)  # Optional: specific resource quiz
    quiz_type = Column(String(20), nullable=False)  # "mcq" or "short_answer"
    questions = Column(JSON, nullable=False)  # Store quiz questions
    answers = Column(JSON, nullable=True)  # Store user answers
    score = Column(Integer, nullable=True)  # Score percentage
    completed = Column(Integer, default=0, nullable=False)  # 0 = in progress, 1 = completed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )
