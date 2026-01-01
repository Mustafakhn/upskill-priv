from pymongo import MongoClient
from pymongo.database import Database
from app.config import settings
from typing import Optional

_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_mongo_client() -> MongoClient:
    """Get MongoDB client"""
    global _client
    if _client is None:
        _client = MongoClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000
        )
    return _client


def get_mongo_db() -> Database:
    """Get MongoDB database"""
    global _db
    if _db is None:
        client = get_mongo_client()
        _db = client.get_database("learning_platform")
    return _db


def close_mongo_client():
    """Close MongoDB client"""
    global _client
    if _client is not None:
        _client.close()
        _client = None

