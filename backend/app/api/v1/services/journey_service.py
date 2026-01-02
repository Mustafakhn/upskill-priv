from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.api.v1.dao.journey_dao import JourneyDAO
from app.api.v1.dao.resource_dao import ResourceDAO
from app.db.base import JourneyStatus
from app.api.v1.services.agent_service import AgentService
import threading


class JourneyService:
    """Service for journey operations"""
    
    def __init__(self):
        self.journey_dao = JourneyDAO
        self.resource_dao = ResourceDAO
        self.agent_service = AgentService()
    
    def create_journey(
        self,
        db: Session,
        user_id: int,
        topic: str,
        level: str,
        goal: str,
        preferred_format: str = "any"
    ) -> Dict[str, Any]:
        """Create a new learning journey"""
        # Create journey record
        journey = self.journey_dao.create(
            db=db,
            user_id=user_id,
            topic=topic,
            level=level,
            goal=goal,
            preferred_format=preferred_format,
            status=JourneyStatus.PENDING
        )
        
        # Commit the journey first to ensure it's in the database
        db.commit()
        
        # Small delay to ensure database commit is processed
        import time
        time.sleep(0.1)
        
        # Start background processing (import here to avoid circular import)
        from app.tasks.scrape_tasks import process_journey_sync
        thread = threading.Thread(target=process_journey_sync, args=(journey.id,))
        thread.daemon = True
        thread.start()
        print(f"Started background processing for journey {journey.id}")
        
        return {
            "id": journey.id,
            "topic": journey.topic,
            "level": journey.level,
            "goal": journey.goal,
            "status": journey.status.value,
            "created_at": journey.created_at.isoformat()
        }
    
    def get_journey(self, db: Session, journey_id: int, user_id: int = None) -> Optional[Dict[str, Any]]:
        """Get journey with resources"""
        journey = self.journey_dao.get_by_id(db, journey_id)
        if not journey:
            return None
        
        # Check user authorization
        if user_id and journey.user_id != user_id:
            return None
        
        # Get resources
        journey_resources = self.journey_dao.get_resources(db, journey_id)
        resource_ids = [jr.resource_id for jr in journey_resources]
        
        resources = []
        sections = []
        if resource_ids:
            resources = self.resource_dao.get_by_ids(resource_ids)
            # Sort by order_index
            resource_map = {r["id"]: r for r in resources}
            resources = [
                resource_map[rid] for rid in resource_ids
                if rid in resource_map
            ]
            
            # Extract sections from first resource's metadata if available
            # Sections metadata is stored in _sections field during curation
            for resource in resources:
                if resource.get("_sections"):
                    sections = resource.get("_sections", [])
                    break
        
        # If no sections found in metadata, try to get from journey metadata collection
        if not sections:
            sections = self._get_journey_sections_from_mongo(journey_id)
        
        # Fix sections: map resource titles/IDs to actual resource IDs
        if sections and resources:
            resource_id_map = {r["id"]: r["id"] for r in resources}  # ID to ID mapping
            resource_title_map = {r.get("title", "").lower(): r["id"] for r in resources}  # Title to ID mapping
            
            fixed_sections = []
            for section in sections:
                fixed_section = {
                    "name": section.get("name", ""),
                    "description": section.get("description", ""),
                    "resources": []
                }
                section_resources = section.get("resources", [])
                for resource_ref in section_resources:
                    # resource_ref could be an ID (string) or a title (string)
                    saved_id = None
                    if isinstance(resource_ref, str):
                        # Try as ID first
                        saved_id = resource_id_map.get(resource_ref)
                        # If not found, try as title
                        if not saved_id:
                            saved_id = resource_title_map.get(resource_ref.lower())
                    if saved_id:
                        fixed_section["resources"].append(saved_id)
                if fixed_section["resources"]:  # Only add sections with valid resources
                    fixed_sections.append(fixed_section)
            sections = fixed_sections
        
        return {
            "id": journey.id,
            "user_id": journey.user_id,
            "topic": journey.topic,
            "level": journey.level,
            "goal": journey.goal,
            "status": journey.status.value,
            "created_at": journey.created_at.isoformat(),
            "resources": resources,
            "resource_count": len(resources),
            "sections": sections
        }
    
    def _get_journey_sections_from_mongo(self, journey_id: int) -> List[Dict[str, Any]]:
        """Get sections from MongoDB journey metadata"""
        try:
            from app.db.mongo import get_mongo_db
            db = get_mongo_db()
            metadata = db.journey_metadata.find_one({"journey_id": journey_id})
            if metadata and metadata.get("sections"):
                return metadata.get("sections", [])
        except Exception:
            pass
        return []
    
    def get_user_journeys(self, db: Session, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all journeys for a user"""
        journeys = self.journey_dao.get_by_user(db, user_id, limit)
        
        return [
            {
                "id": journey.id,
                "topic": journey.topic,
                "level": journey.level,
                "goal": journey.goal,
                "status": journey.status.value,
                "created_at": journey.created_at.isoformat()
            }
            for journey in journeys
        ]
    
    def process_journey_sync(
        self,
        db: Session,
        journey_id: int
    ) -> Dict[str, Any]:
        """Process journey synchronously (for background tasks)"""
        journey = self.journey_dao.get_by_id(db, journey_id)
        if not journey:
            return {"success": False, "error": "Journey not found"}
        
        try:
            # Update status to scraping
            self.journey_dao.update_status(db, journey_id, JourneyStatus.SCRAPING)
            db.commit()
            
            # Get preferred format from journey
            preferred_format = journey.preferred_format or "any"
            
            # Create journey using agents
            journey_data = self.agent_service.create_learning_journey(
                topic=journey.topic,
                level=journey.level,
                goal=journey.goal,
                preferred_format=preferred_format,
                journey_id=journey_id,
                user_id=journey.user_id
            )
            
            # Update status to curating
            self.journey_dao.update_status(db, journey_id, JourneyStatus.CURATING)
            db.commit()
            
            # Extract sections from curated resources (stored in _sections metadata)
            sections = []
            if journey_data.get("resources"):
                first_resource = journey_data["resources"][0]
                if first_resource.get("_sections"):
                    sections = first_resource.get("_sections", [])
            
            # Create maps for resource ID and title lookup
            # Map original resource IDs/titles to saved resource IDs
            resource_id_map = {}  # original_id -> saved_id
            resource_title_map = {}  # title -> saved_id
            
            # Save resources to MongoDB and link to journey (with title matching validation)
            print(f"[JOURNEY {journey_id}] Clearing existing resources and saving {len(journey_data.get('resources', []))} new resources...")
            self.journey_dao.clear_resources(db, journey_id)
            saved_count = 0
            topic_lower = journey.topic.lower()
            goal_lower = journey.goal.lower()
            
            for idx, resource in enumerate(journey_data["resources"]):
                # Trust AI curation - resources have already been curated for quality and relevance
                # Only do a basic relevance check on summary/content, not strict title matching
                title = resource.get("title", "").lower()
                summary = resource.get("summary", "").lower()
                
                # Basic relevance check: resource should be somewhat related (AI curation should handle this, but double-check)
                # This is a soft check - if AI curated it, it's likely relevant
                topic_words = [w for w in topic_lower.split() if len(w) > 3]  # Only meaningful words
                goal_keywords = [w for w in goal_lower.split() if len(w) > 3]  # Only meaningful words
                
                # Check if title OR summary contains relevant keywords (more lenient)
                title_relevant = any(word in title for word in topic_words) or any(keyword in title for keyword in goal_keywords)
                summary_relevant = any(word in summary for word in topic_words) or any(keyword in summary for keyword in goal_keywords)
                
                # Only skip if completely irrelevant (both title and summary don't match)
                if not title_relevant and not summary_relevant and len(topic_words) > 0:
                    print(f"[JOURNEY {journey_id}] Skipping resource '{resource.get('title', '')}' - appears irrelevant to topic/goal")
                    continue
                
                # Ensure resource exists (it should from scraping)
                resource_id = resource.get("id")
                if not resource_id:
                    # Get estimated_time - 0 for videos, actual time for text
                    estimated_time = resource.get("estimated_time", 0)
                    if resource.get("type") == "video":
                        estimated_time = 0  # Videos don't have reading time
                    elif estimated_time == 0:
                        estimated_time = 10  # Default for text if missing
                    
                    # Create if missing
                    resource_id = self.resource_dao.create(
                        url=resource.get("url", ""),
                        title=resource.get("title", ""),
                        summary=resource.get("summary", ""),
                        resource_type=resource.get("type", "blog"),
                        difficulty=resource.get("difficulty", "intermediate"),
                        tags=resource.get("tags", []),
                        estimated_time=estimated_time,
                        source=journey.topic
                    )
                
                # Link to journey
                self.journey_dao.add_resource(
                    db=db,
                    journey_id=journey_id,
                    resource_id=resource_id,
                    order_index=idx
                )
                
                # Map original resource ID and title to saved resource ID
                original_id = resource.get("id")
                if original_id:
                    resource_id_map[original_id] = resource_id
                resource_title_map[resource.get("title", "").lower()] = resource_id
                
                saved_count += 1
                if (idx + 1) % 5 == 0:  # Log every 5 resources
                    print(f"[JOURNEY {journey_id}] Saved {idx + 1}/{len(journey_data['resources'])} resources...")
            
            print(f"[JOURNEY {journey_id}] Successfully saved {saved_count} resources")
            
            # Fix sections: map resource IDs/titles to actual saved resource IDs
            if sections:
                fixed_sections = []
                for section in sections:
                    fixed_section = {
                        "name": section.get("name", ""),
                        "description": section.get("description", ""),
                        "resources": []
                    }
                    section_resources = section.get("resources", [])
                    for resource_ref in section_resources:
                        # resource_ref could be an ID (string) or a title (string)
                        saved_id = None
                        if isinstance(resource_ref, str):
                            # Try as ID first
                            saved_id = resource_id_map.get(resource_ref)
                            # If not found, try as title
                            if not saved_id:
                                saved_id = resource_title_map.get(resource_ref.lower())
                        if saved_id:
                            fixed_section["resources"].append(saved_id)
                    if fixed_section["resources"]:  # Only add sections with valid resources
                        fixed_sections.append(fixed_section)
                sections = fixed_sections
                # Store fixed sections in MongoDB
                self._save_journey_sections_to_mongo(journey_id, sections)
            
            # Update status to ready
            print(f"[JOURNEY {journey_id}] Updating status to READY...")
            self.journey_dao.update_status(db, journey_id, JourneyStatus.READY)
            db.commit()  # Commit the status change
            print(f"[JOURNEY {journey_id}] Journey processing completed successfully!")
            
            # Send push notification
            try:
                from app.api.v1.services.push_service import PushService
                push_service = PushService()
                push_service.send_journey_ready_notification(
                    user_id=journey.user_id,
                    journey_id=journey_id,
                    topic=journey.topic
                )
            except Exception as e:
                print(f"Error sending push notification for journey {journey_id}: {e}")
                import traceback
                traceback.print_exc()
            
            return {"success": True, "resource_count": len(journey_data["resources"])}
        except Exception as e:
            self.journey_dao.update_status(db, journey_id, JourneyStatus.FAILED)
            db.commit()  # Commit the failed status
            print(f"Journey {journey_id} processing failed: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def _save_journey_sections_to_mongo(self, journey_id: int, sections: List[Dict[str, Any]]):
        """Save sections to MongoDB journey metadata"""
        try:
            from app.db.mongo import get_mongo_db
            from datetime import datetime
            db = get_mongo_db()
            db.journey_metadata.update_one(
                {"journey_id": journey_id},
                {"$set": {"sections": sections, "updated_at": datetime.utcnow()}},
                upsert=True
            )
        except Exception as e:
            print(f"Warning: Could not save sections to MongoDB: {e}")

