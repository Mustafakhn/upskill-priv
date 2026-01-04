from typing import Dict, Any, List
from app.utils.ai_client import ai_client
from app.api.v1.dao.resource_dao import ResourceDAO


class SummarizationAgent:
    """Agent for summarizing and enriching scraped resources"""
    
    @staticmethod
    def summarize_resource(resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate or improve summary for a resource
        
        Args:
            resource: Resource dictionary
            
        Returns:
            Updated resource with improved summary
        """
        url = resource.get("url", "")
        title = resource.get("title", "")
        existing_summary = resource.get("summary", "")
        content = resource.get("content", "")
        
        # If summary is already good, skip
        if existing_summary and len(existing_summary) > 200:
            return resource
        
        system_prompt = """You are a content summarizer. Create a concise, informative summary 
(150-250 words) of the resource. Focus on:
- What the resource teaches
- Key topics covered
- Who it's for (beginner/intermediate/advanced)
- What learners will gain

Return ONLY the summary text, no additional commentary."""
        
        prompt = f"""Summarize this learning resource:

Title: {title}
URL: {url}
Existing Summary: {existing_summary}
Content Preview: {content[:1000] if content else "Not available"}

Create a detailed summary:"""
        
        try:
            summary = ai_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=300
            )
            
            resource["summary"] = summary.strip()
            return resource
        except Exception:
            # Keep existing summary if AI fails
            return resource
    
    @staticmethod
    def enrich_resources_batch(resources: List[Dict[str, Any]], topic_level: str) -> List[Dict[str, Any]]:
        """
        Enrich multiple resources at once (batch processing with AI)
        
        Args:
            resources: List of resource dictionaries
            topic_level: Default difficulty level
            
        Returns:
            List of enriched resources
        """
        if not resources:
            return resources
        
        # Build batch prompt for all resources (limit to reasonable number for AI context)
        resources_to_process = resources[:15]  # Process up to 15 at once
        resources_data = []
        for idx, resource in enumerate(resources_to_process):
            resources_data.append({
                "id": idx,
                "title": resource.get("title", ""),
                "summary": resource.get("summary", "")[:200] or resource.get("title", ""),
                "url": resource.get("url", ""),
                "content": resource.get("content", "")[:300] if resource.get("content") else ""
            })
        
        system_prompt = """You are a resource enrichment assistant. For each resource, generate:
1. A concise summary (100-150 words)
2. 5-8 relevant tags (lowercase, no duplicates)
3. Difficulty level (beginner/intermediate/advanced)

Return ONLY valid JSON with this structure:
{
    "resources": [
        {
            "id": 0,
            "summary": "detailed summary text",
            "tags": ["tag1", "tag2"],
            "difficulty": "beginner"
        }
    ]
}"""
        
        resources_text = "\n\n".join([
            f"Resource {r['id']}:\nTitle: {r['title']}\nURL: {r['url']}\nSummary: {r['summary']}\nContent: {r['content']}"
            for r in resources_data
        ])
        
        prompt = f"""Enrich these learning resources:

{resources_text}

Default difficulty: {topic_level}

Generate summaries, tags, and difficulty for each resource:"""
        
        try:
            result = ai_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5
            )
            
            enriched_map = {}
            if isinstance(result, dict) and "resources" in result:
                for enriched in result["resources"]:
                    enriched_map[enriched.get("id")] = enriched
            
            # Apply enrichments to processed resources
            for idx, resource in enumerate(resources_to_process):
                if idx in enriched_map:
                    enriched = enriched_map[idx]
                    resource["summary"] = enriched.get("summary", resource.get("summary", resource.get("title", "")))
                    resource["tags"] = enriched.get("tags", [])
                    resource["difficulty"] = enriched.get("difficulty", topic_level)
                else:
                    # Fallback for resources not in batch result
                    if not resource.get("summary"):
                        resource["summary"] = resource.get("title", "")
                    if not resource.get("tags"):
                        resource["tags"] = []
                    if not resource.get("difficulty"):
                        resource["difficulty"] = SummarizationAgent.determine_difficulty(resource, topic_level)
            
            # For resources beyond the batch limit, apply basic enrichment
            for resource in resources[15:]:
                if not resource.get("summary"):
                    resource["summary"] = resource.get("title", "")
                if not resource.get("tags"):
                    resource["tags"] = []
                if not resource.get("difficulty"):
                    resource["difficulty"] = SummarizationAgent.determine_difficulty(resource, topic_level)
            
            return resources
        except Exception as e:
            print(f"Batch enrichment failed: {e}, using fallback enrichment")
            # Fallback: ensure all resources have basic fields
            for resource in resources:
                if not resource.get("summary"):
                    resource["summary"] = resource.get("title", "")
                if not resource.get("tags"):
                    resource["tags"] = []
                if not resource.get("difficulty"):
                    resource["difficulty"] = SummarizationAgent.determine_difficulty(resource, topic_level)
            return resources
    
    @staticmethod
    def extract_tags(resource: Dict[str, Any]) -> List[str]:
        """Extract relevant tags from resource"""
        title = resource.get("title", "")
        summary = resource.get("summary", "")
        content = resource.get("content", "")
        
        system_prompt = """You are a tag extractor. Extract 5-8 relevant tags from the content.
Return ONLY a JSON array of tag strings, lowercase, no duplicates.

Example: ["python", "tutorial", "beginner", "web-development"]"""
        
        prompt = f"""Extract tags from this resource:

Title: {title}
Summary: {summary}
Content: {content[:500] if content else ""}

Extract tags:"""
        
        try:
            tags = ai_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            if isinstance(tags, list):
                return [str(tag).lower() for tag in tags[:8]]
            
            return []
        except Exception:
            return []
    
    @staticmethod
    def determine_difficulty(resource: Dict[str, Any], topic_level: str) -> str:
        """Determine resource difficulty level"""
        title = resource.get("title", "").lower()
        summary = resource.get("summary", "").lower()
        
        # Simple keyword-based detection
        beginner_keywords = ["beginner", "introduction", "getting started", "basics", "first steps"]
        advanced_keywords = ["advanced", "expert", "deep dive", "master", "complex"]
        
        content_lower = f"{title} {summary}".lower()
        
        if any(kw in content_lower for kw in advanced_keywords):
            return "advanced"
        if any(kw in content_lower for kw in beginner_keywords):
            return "beginner"
        
        return topic_level  # Default to topic level

