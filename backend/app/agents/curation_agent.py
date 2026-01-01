from typing import List, Dict, Any
from app.utils.ai_client import ai_client


class CurationAgent:
    """Agent for curating and organizing resources into a learning journey"""
    
    @staticmethod
    def curate_journey(
        resources: List[Dict[str, Any]],
        topic: str,
        level: str,
        goal: str,
        preferred_format: str = None
    ) -> List[Dict[str, Any]]:
        """
        Curate resources into an organized learning journey
        
        Args:
            resources: List of resource dictionaries
            topic: Learning topic
            level: User level
            goal: Learning goal
            
        Returns:
            Curated list of resources with order and sections
        """
        if not resources:
            return []
        
        # Build resource summary for AI with more context for better curation
        resource_summaries = []
        for idx, resource in enumerate(resources[:40]):  # Allow more resources for AI to choose from
            resource_summaries.append({
                "id": resource.get("id", str(idx)),
                "title": resource.get("title", ""),
                "summary": resource.get("summary", "")[:300],  # More context for better selection
                "type": resource.get("type", "blog"),
                "url": resource.get("url", ""),
                "difficulty": resource.get("difficulty", "intermediate")
            })
        
        # Filter by preferred format if specified (but not for "mixed" or "any")
        # But allow AI to make final selection from a larger pool
        filtered_resources = resource_summaries
        if preferred_format and preferred_format not in ["any", "mixed", "mix"]:
            # Prioritize preferred format but keep some variety
            preferred = [r for r in resource_summaries if r.get("type") == preferred_format]
            other = [r for r in resource_summaries if r.get("type") != preferred_format]
            # If we have preferred format resources, prioritize them (70/30 split)
            if preferred:
                preferred_count = min(len(preferred), int(len(resource_summaries) * 0.7))
                other_count = len(resource_summaries) - preferred_count
                filtered_resources = preferred[:preferred_count] + other[:other_count]
            filtered_resources = filtered_resources[:40]  # Allow AI to choose from more options
        
        # Format note for curation
        if preferred_format and preferred_format.lower() in ["mixed", "mix", "any"]:
            format_note = "User wants a mix of all resource types: videos, articles, documentation, and tutorials. Include diverse formats."
        elif preferred_format:
            format_note = f"User prefers {preferred_format} format."
        else:
            format_note = "Mix resource types appropriately."
        
        # Build format diversity instruction
        format_diversity_note = ""
        if preferred_format in ["any", "mixed", None, ""]:
            format_diversity_note = "\nCRITICAL FORMAT DIVERSITY: User wants a MIX of formats. Ensure you select a BALANCED mix of videos, articles, and documentation. Do NOT select only videos or only articles. Aim for roughly 40% videos, 40% articles/blogs, and 20% documentation when possible."
        elif preferred_format:
            format_diversity_note = f"\nFormat Preference: User prefers {preferred_format} format. Prioritize this format but include some variety (70% preferred, 30% other formats)."
        
        system_prompt = f"""You are an expert learning path curator. Your goal is to create a STREAMLINED, high-quality learning journey that avoids overwhelming learners with too much material.

CRITICAL REQUIREMENTS:
1. QUALITY OVER QUANTITY: Select only the BEST resources that directly contribute to the learning goal
2. STREAMLINED PATH: Create a focused path with 8-12 resources maximum (not 20+)
3. Prerequisites and foundational concepts first
4. Progressive difficulty from beginner to advanced
5. Resource type preferences (prioritize preferred format if specified)
6. Each resource should build on the previous one
7. Remove redundant or overlapping content
8. Prioritize resources with clear, actionable content
{format_diversity_note}

Return ONLY a JSON object with this structure:
{{
    "ordered_resources": ["resource_id1", "resource_id2", ...],  // MAX 12 resources
    "sections": [
        {{
            "name": "Section Name",
            "resources": ["resource_id1", "resource_id2"],
            "description": "What learners will cover"
        }}
    ]
}}"""
        
        # Add format diversity requirement to prompt
        diversity_instruction = ""
        if preferred_format in ["any", "mixed", None, ""]:
            diversity_instruction = "\n\nFORMAT DIVERSITY REQUIREMENT: You MUST select a balanced mix of resource types. Include videos, articles/blogs, and documentation. Do NOT select only one format type. Aim for variety to accommodate different learning styles."
        
        prompt = f"""Topic: {topic}
Level: {level}
Goal: {goal}
{format_note}

Available Resources:
{chr(10).join([f"- {r['title']} ({r['type']}) - {r.get('summary', '')[:100]}..." for r in filtered_resources])}

TASK: Create a STREAMLINED learning journey by selecting ONLY the BEST 8-12 resources that:
1. Directly relate to the topic and goal
2. Provide the most value and clarity
3. Form a logical progression without redundancy
4. Cover all essential concepts efficiently
{diversity_instruction}

IMPORTANT: Do NOT include all resources. Be selective and choose quality over quantity. The goal is a focused, effective learning path, not an exhaustive list."""
        
        try:
            curation = ai_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5
            )
            
            ordered_ids = curation.get("ordered_resources", [])
            sections = curation.get("sections", [])
            
            # Create resource map (use original resources, not filtered summaries)
            resource_map = {r.get("id"): r for r in resources}
            
            # Also filter actual resources by preferred_format (but not for "mixed" or "any")
            if preferred_format and preferred_format not in ["any", "mixed", "mix"]:
                preferred_resources = [r for r in resources if r.get("type") == preferred_format]
                other_resources = [r for r in resources if r.get("type") != preferred_format]
                if preferred_resources:
                    preferred_count = min(len(preferred_resources), int(len(resources) * 0.7))
                    other_count = len(resources) - preferred_count
                    resources = preferred_resources[:preferred_count] + other_resources[:other_count]
                    resource_map = {r.get("id"): r for r in resources}
            
            # Build curated list
            curated = []
            for resource_id in ordered_ids:
                if resource_id in resource_map:
                    curated.append(resource_map[resource_id])
            
            # Add any resources not in the ordered list
            added_ids = set(ordered_ids)
            for resource in resources:
                if resource.get("id") not in added_ids:
                    curated.append(resource)
            
            # Ensure format diversity for "any" or "mixed" preferences
            if preferred_format in ["any", "mixed", None, ""] and len(curated) > 0:
                curated = CurationAgent._ensure_format_diversity(curated, max_resources=12)
            
            # Store sections in metadata (can be used for frontend display)
            for resource in curated:
                resource["_sections"] = sections
            
            # Limit to 12 resources for a streamlined path
            return curated[:12]
        except Exception:
            # Fallback: return top resources in original order (still limit to 12 for streamlined path)
            return resources[:12]
    
    @staticmethod
    def remove_duplicates(resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate or near-duplicate resources"""
        seen_urls = set()
        seen_titles = set()
        unique_resources = []
        
        for resource in resources:
            url = resource.get("url", "")
            title = resource.get("title", "").lower().strip()
            
            # Skip if URL or very similar title already seen
            if url in seen_urls:
                continue
            
            # Simple title similarity check (exact match only for now)
            if title in seen_titles:
                continue
            
            seen_urls.add(url)
            seen_titles.add(title)
            unique_resources.append(resource)
        
        return unique_resources
    
    @staticmethod
    def filter_low_quality(resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out low-quality resources"""
        filtered = []
        
        for resource in resources:
            # Skip if missing essential fields
            if not resource.get("url") or not resource.get("title"):
                continue
            
            # Skip if summary is too short
            summary = resource.get("summary", "")
            if len(summary) < 50:
                continue
            
            filtered.append(resource)
        
        return filtered
    
    @staticmethod
    def _ensure_format_diversity(curated: List[Dict[str, Any]], max_resources: int = 12) -> List[Dict[str, Any]]:
        """Ensure format diversity in curated resources"""
        if len(curated) <= max_resources:
            # Check if we have diversity already
            types = [r.get("type") for r in curated]
            unique_types = set(types)
            if len(unique_types) >= 2:  # Already diverse
                return curated
        
        # Count resources by type
        videos = [r for r in curated if r.get("type") == "video"]
        blogs = [r for r in curated if r.get("type") == "blog"]
        docs = [r for r in curated if r.get("type") == "doc"]
        others = [r for r in curated if r.get("type") not in ["video", "blog", "doc"]]
        
        # Target distribution: 40% videos, 40% blogs, 20% docs/others (minimum 1 of each if available)
        target_videos = max(1, min(len(videos), int(max_resources * 0.4))) if videos else 0
        target_blogs = max(1, min(len(blogs), int(max_resources * 0.4))) if blogs else 0
        target_docs = max(0, min(len(docs), int(max_resources * 0.2))) if docs else 0
        
        # Select diverse resources
        diverse = []
        diverse.extend(videos[:target_videos])
        diverse.extend(blogs[:target_blogs])
        diverse.extend(docs[:target_docs])
        diverse.extend(others[:max(0, max_resources - len(diverse))])
        
        # If we still need more, fill from remaining resources maintaining order
        added_ids = {r.get("id") for r in diverse}
        for resource in curated:
            if len(diverse) >= max_resources:
                break
            if resource.get("id") not in added_ids:
                diverse.append(resource)
                added_ids.add(resource.get("id"))
        
        return diverse[:max_resources]

