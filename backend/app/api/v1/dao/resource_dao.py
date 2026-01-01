from app.db.mongo import get_mongo_db
from bson import ObjectId
from typing import List, Optional, Dict, Any
from datetime import datetime
from pymongo.collection import Collection


class ResourceDAO:
    """Data Access Object for Resource operations (MongoDB)"""
    
    @staticmethod
    def get_collection() -> Collection:
        """Get resources collection"""
        db = get_mongo_db()
        return db.resources
    
    @staticmethod
    def get_raw_scrapes_collection() -> Collection:
        """Get raw scrapes collection"""
        db = get_mongo_db()
        return db.raw_scrapes
    
    @staticmethod
    def create(
        url: str,
        title: str,
        summary: str,
        resource_type: str,
        difficulty: str,
        tags: List[str],
        estimated_time: int,
        source: str,
        content: str = None,
        **kwargs
    ) -> str:
        """Create a new resource"""
        collection = ResourceDAO.get_collection()
        resource = {
            "url": url,
            "title": title,
            "summary": summary,
            "type": resource_type,
            "difficulty": difficulty,
            "tags": tags,
            "estimated_time": estimated_time,
            "source": source,
            "scraped_at": datetime.utcnow(),
            **kwargs
        }
        if content:
            resource["content"] = content
        result = collection.insert_one(resource)
        return str(result.inserted_id)
    
    @staticmethod
    def update(
        resource_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update a resource"""
        collection = ResourceDAO.get_collection()
        try:
            result = collection.update_one(
                {"_id": ObjectId(resource_id)},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    @staticmethod
    def get_by_id(resource_id: str) -> Optional[Dict[str, Any]]:
        """Get resource by ID"""
        collection = ResourceDAO.get_collection()
        try:
            resource = collection.find_one({"_id": ObjectId(resource_id)})
            if resource:
                resource["id"] = str(resource["_id"])
                del resource["_id"]
            return resource
        except Exception:
            return None
    
    @staticmethod
    def get_by_ids(resource_ids: List[str]) -> List[Dict[str, Any]]:
        """Get multiple resources by IDs"""
        collection = ResourceDAO.get_collection()
        try:
            object_ids = [ObjectId(rid) for rid in resource_ids]
            resources = list(collection.find({"_id": {"$in": object_ids}}))
            for resource in resources:
                resource["id"] = str(resource["_id"])
                del resource["_id"]
            return resources
        except Exception:
            return []
    
    @staticmethod
    def get_by_url(url: str) -> Optional[Dict[str, Any]]:
        """Get resource by URL"""
        collection = ResourceDAO.get_collection()
        resource = collection.find_one({"url": url})
        if resource:
            resource["id"] = str(resource["_id"])
            del resource["_id"]
        return resource
    
    @staticmethod
    def save_raw_scrape(url: str, html: str) -> str:
        """Save raw HTML scrape"""
        collection = ResourceDAO.get_raw_scrapes_collection()
        doc = {
            "url": url,
            "html": html,
            "scraped_at": datetime.utcnow()
        }
        result = collection.insert_one(doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_raw_scrape(url: str) -> Optional[str]:
        """Get raw HTML scrape by URL"""
        collection = ResourceDAO.get_raw_scrapes_collection()
        doc = collection.find_one({"url": url}, sort=[("scraped_at", -1)])
        return doc.get("html") if doc else None
    
    @staticmethod
    def search_resources(query: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        """Search resources with query"""
        collection = ResourceDAO.get_collection()
        resources = list(collection.find(query).limit(limit))
        for resource in resources:
            resource["id"] = str(resource["_id"])
            del resource["_id"]
        return resources
