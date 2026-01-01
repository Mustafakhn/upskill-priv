from typing import Dict, Any, List
from app.agents.intent_agent import IntentAgent
from app.agents.scrape_agent import ScrapeAgent
from app.agents.summarization_agent import SummarizationAgent
from app.agents.curation_agent import CurationAgent


class AgentService:
    """Service for orchestrating AI agents"""
    
    def __init__(self):
        self.intent_agent = IntentAgent()
        self.scrape_agent = ScrapeAgent()
        self.summarization_agent = SummarizationAgent()
        self.curation_agent = CurationAgent()
    
    def process_conversation_to_intent(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract structured intent from conversation"""
        return self.intent_agent.extract_intent(conversation_history)
    
    def create_learning_journey(
        self,
        topic: str,
        level: str,
        goal: str,
        preferred_format: str = None,
        journey_id: int = None,
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        Create a complete learning journey using agents
        
        Returns:
            Dictionary with journey information and resources
        """
        print(f"[AGENT PIPELINE] Starting learning journey creation for: topic='{topic}', level='{level}', goal='{goal}', format='{preferred_format}'")
        
        # Step 1: Scrape resources
        print(f"[AGENT PIPELINE] Step 1: Scraping resources...")
        resources = self.scrape_agent.execute_scraping(
            topic=topic,
            level=level,
            goal=goal,
            preferred_format=preferred_format,
            journey_id=journey_id,
            user_id=user_id
        )
        print(f"[AGENT PIPELINE] Step 1 complete: Found {len(resources)} resources")
        
        # Log unfiltered resources by type
        resource_types = {}
        for resource in resources:
            rtype = resource.get("type", "unknown")
            resource_types[rtype] = resource_types.get(rtype, 0) + 1
        print(f"[AGENT PIPELINE] Unfiltered resources by type: {resource_types}")
        print(f"[AGENT PIPELINE] Sample unfiltered resources:")
        for idx, resource in enumerate(resources[:10]):  # Show first 10
            print(f"  {idx+1}. [{resource.get('type', 'unknown')}] {resource.get('title', 'No title')[:60]} - Content: {'Yes' if resource.get('content') and len(resource.get('content', '')) > 100 else 'No/Short'}")
        
        # Step 2: Enrich resources with summaries and tags (batch processing)
        print(f"[AGENT PIPELINE] Step 2: Enriching resources with summaries and tags (batch mode)...")
        from app.api.v1.dao.resource_dao import ResourceDAO
        
        # Batch enrich all resources at once
        enriched_resources = self.summarization_agent.enrich_resources_batch(resources, level)
        
        # Update MongoDB for all resources
        for resource in enriched_resources:
            resource_id = resource.get("id")
            if resource_id:
                ResourceDAO.update(resource_id, {
                    "summary": resource.get("summary", ""),
                    "tags": resource.get("tags", []),
                    "difficulty": resource.get("difficulty", level)
                })
        
        print(f"[AGENT PIPELINE] Step 2 complete: Enriched {len(enriched_resources)} resources (batch mode)")
        
        # Step 3: Filter and curate
        print(f"[AGENT PIPELINE] Step 3: Filtering and curating resources...")
        filtered = self.curation_agent.filter_low_quality(enriched_resources)
        print(f"[AGENT PIPELINE] Step 3a: Filtered to {len(filtered)} high-quality resources")
        unique = self.curation_agent.remove_duplicates(filtered)
        print(f"[AGENT PIPELINE] Step 3b: Removed duplicates, {len(unique)} unique resources")
        curated = self.curation_agent.curate_journey(
            unique,
            topic=topic,
            level=level,
            goal=goal,
            preferred_format=preferred_format
        )
        print(f"[AGENT PIPELINE] Step 3c: Curated to {len(curated)} final resources")
        print(f"[AGENT PIPELINE] Pipeline complete: Returning {len(curated)} curated resources")
        
        return {
            "resources": curated,
            "total_resources": len(curated),
            "topic": topic,
            "level": level,
            "goal": goal
        }

