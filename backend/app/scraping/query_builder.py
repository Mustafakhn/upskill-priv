from typing import List
from app.utils.ai_client import ai_client


class QueryBuilder:
    """Build search queries from user intent"""
    
    @staticmethod
    def build_queries(topic: str, level: str, goal: str, preferred_format: str = None) -> List[str]:
        """
        Build multiple search queries for scraping
        
        Args:
            topic: Learning topic
            level: User level (beginner/intermediate/advanced)
            goal: Learning goal
            preferred_format: Preferred format (video/blog/doc)
            
        Returns:
            List of search query strings
        """
        # Don't restrict queries by material type - let the search engine find everything
        # Generate diverse, general queries that cover different learning angles
        system_prompt = """You are a search query expert. Generate at least 5 diverse, general search queries 
(aim for 5-8 queries) that would help someone learn the given topic. 

IMPORTANT: Do NOT include material type keywords like "video", "blog", "tutorial", "documentation" in queries.
Just use general, natural search queries about the topic itself.

Consider different learning angles:
- Fundamentals and basics
- Practical examples and projects
- Official resources and references
- Best practices and patterns
- Common use cases
- Advanced concepts

Return ONLY a JSON array of query strings, nothing else.
Example: ["python basics", "python examples", "python best practices", "python web development", ...]"""
        
        prompt = f"""Topic: {topic}
Level: {level}
Goal: {goal}

Generate general search queries (do NOT include material type keywords like "video", "blog", "tutorial"):

Generate search queries:"""
        
        try:
            result = ai_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            if isinstance(result, list):
                # Ensure at least 5 queries, but don't limit maximum
                if len(result) < 5:
                    # If we got fewer than 5, add some fallback queries
                    fallback_queries = [
                        f"{topic} {level} tutorial",
                        f"{topic} {level} guide",
                        f"{topic} documentation",
                        f"learn {topic} {level}",
                        f"{topic} {goal} {level}"
                    ]
                    # Add fallbacks that aren't already in result
                    for fb_query in fallback_queries:
                        if fb_query.lower() not in [q.lower() for q in result]:
                            result.append(fb_query)
                            if len(result) >= 5:
                                break
                return result  # Return all queries (at least 5)
            
            # Fallback if response is not a list
            return [
                f"{topic} {level} tutorial",
                f"{topic} {level} guide",
                f"{topic} documentation",
                f"learn {topic} {level}",
                f"{topic} {goal}"
            ]
        except Exception:
            # Fallback queries if AI fails
            return [
                f"{topic} {level} tutorial",
                f"{topic} {level} guide",
                f"{topic} documentation",
                f"learn {topic} {level}",
                f"{topic} {goal}"
            ]

