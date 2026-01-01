from typing import List, Dict, Any
from app.scraping.query_builder import QueryBuilder
from app.api.v1.services.scrape_service import ScrapeService
from app.utils.ai_client import ai_client


class ScrapeAgent:
    """Agent for intelligently scraping and refining search results"""
    
    def __init__(self):
        self.scrape_service = ScrapeService()
        self.query_builder = QueryBuilder()
    
    def execute_scraping(
        self,
        topic: str,
        level: str,
        goal: str,
        preferred_format: str = None,
        journey_id: int = None,
        user_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Execute intelligent scraping with query refinement
        
        Args:
            topic: Learning topic
            level: User level
            goal: Learning goal
            preferred_format: Preferred format
            journey_id: Optional journey ID for logging
            user_id: Optional user ID for logging
            
        Returns:
            List of scraped resources
        """
        # Build initial queries
        print(f"[SCRAPE AGENT] Building search queries for topic='{topic}', level='{level}', goal='{goal}', format='{preferred_format}'")
        queries = self.query_builder.build_queries(topic, level, goal, preferred_format)
        print(f"[SCRAPE AGENT] Generated {len(queries)} search queries")
        
        # Log queries if journey_id and user_id are provided
        if journey_id and user_id:
            try:
                from app.api.v1.dao.admin_dao import AdminDAO
                AdminDAO.log_query(journey_id, user_id, queries, topic, level, goal)
            except Exception as e:
                print(f"[SCRAPE AGENT] Warning: Could not log queries: {e}")
        
        # Scrape resources with conservative approach to avoid rate limits
        # Run all queries (at least 5) for better coverage
        # Increase max_per_query to get more resources before curation (AI will select best)
        print(f"[SCRAPE AGENT] Executing initial scraping with {len(queries)} queries (all queries will be executed)...")
        max_per_query = 8 if preferred_format in ["any", "mixed", None] else 5  # More resources for mixed/any to ensure diversity
        resources = self.scrape_service.scrape_multiple_queries(queries, max_per_query=max_per_query, preferred_format=preferred_format)
        print(f"[SCRAPE AGENT] Initial scraping complete: Found {len(resources)} resources")
        
        # Don't refine queries if we got any resources - avoid more rate limiting
        # Only refine if we got absolutely nothing
        if len(resources) == 0:
            print(f"[SCRAPE AGENT] No resources found, trying refined queries (this may hit rate limits)...")
            import time
            time.sleep(15)  # Long delay before retry
            refined_queries = self._refine_queries(topic, level, goal, resources)
            refined_queries = refined_queries[:2]  # Only try 2 refined queries
            print(f"[SCRAPE AGENT] Generated {len(refined_queries)} refined queries")
            additional_resources = self.scrape_service.scrape_multiple_queries(
                refined_queries,
                max_per_query=2,  # Reduced from 3 to 2
                preferred_format=preferred_format
            )
            print(f"[SCRAPE AGENT] Refined scraping complete: Found {len(additional_resources)} additional resources")
            resources.extend(additional_resources)
            print(f"[SCRAPE AGENT] Total resources after refinement: {len(resources)}")
        else:
            print(f"[SCRAPE AGENT] Found {len(resources)} resources, skipping refinement to avoid rate limits")
        
        return resources
    
    def _refine_queries(
        self,
        topic: str,
        level: str,
        goal: str,
        existing_resources: List[Dict]
    ) -> List[str]:
        """Refine search queries based on existing results"""
        system_prompt = """You are a search query expert. Generate 3-5 new search queries 
that would complement existing resources. Consider different angles, sources, or sub-topics.

Return ONLY a JSON array of query strings."""
        
        existing_titles = [r.get("title", "") for r in existing_resources[:5]]
        
        prompt = f"""Topic: {topic}
Level: {level}
Goal: {goal}

Existing resources found:
{chr(10).join(existing_titles)}

Generate complementary search queries:"""
        
        try:
            queries = ai_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.8
            )
            
            if isinstance(queries, list):
                return queries[:5]
            
            return []
        except Exception:
            # Fallback queries
            return [
                f"{topic} {level} examples",
                f"{topic} {goal} tutorial",
                f"{topic} best practices"
            ]

