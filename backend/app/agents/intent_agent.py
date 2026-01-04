from typing import Dict, Any
from app.utils.ai_client import ai_client


class IntentAgent:
    """Agent for extracting and structuring user learning intent"""
    
    @staticmethod
    def extract_intent(conversation_history: list) -> Dict[str, Any]:
        """
        Extract structured intent from conversation history
        
        Args:
            conversation_history: List of messages with 'role' and 'content'
            
        Returns:
            Dictionary with topic, level, goal, preferred_format, time_commitment
        """
        # Build conversation context
        context = "\n".join([
            f"{msg.get('role', 'user').upper()}: {msg.get('content', '')}"
            for msg in conversation_history
        ])
        
        system_prompt = """You are an expert at understanding learning goals. Extract structured information 
from the conversation. Return ONLY valid JSON with these exact fields:
{
    "topic": "string (main learning topic)",
    "level": "beginner|intermediate|advanced",
    "goal": "string (what they want to achieve - be specific, e.g. 'learn language features', 'build web apps', 'understand basics')",
    "preferred_format": "video|blog|doc|any",
    "time_commitment": "1-2 hours|half day|full day|week|month"
}

CRITICAL RULES:
- ONLY extract information that the USER explicitly stated or clearly implied
- Do NOT infer goals from assistant questions - if the assistant asks "what's your goal?" and user hasn't answered yet, goal should be "Learn the topic"
- For goal: If they say things like "language features", "basics", "fundamentals", extract those as the goal
- If the user hasn't provided a specific goal yet, return "Learn the topic" (not inferred from questions)
- If information is missing, use default values: "General Learning" for topic, "beginner" for level, "Learn the topic" for goal

FORMAT MAPPING (IMPORTANT):
- If user says "reading", "read", "articles", "article", "blog", "blogs", "text", "written" -> return "blog"
- If user says "video", "videos", "watching", "watch", "tutorial", "tutorials" -> return "video"
- If user says "documentation", "docs", "doc", "official docs", "reference" -> return "doc"
- If user says "mixed", "mix", "any", "both", "all" -> return "any"
- If no preference stated -> return "any"

Be concise."""
        
        prompt = f"""Extract learning intent from this conversation:

{context}"""
        
        try:
            intent = ai_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            # Validate and set defaults
            return {
                "topic": intent.get("topic", "General Learning"),
                "level": intent.get("level", "beginner"),
                "goal": intent.get("goal", "Learn the topic"),
                "preferred_format": intent.get("preferred_format", "any"),
                "time_commitment": intent.get("time_commitment", "1-2 hours")
            }
        except Exception as e:
            # Fallback if AI fails
            return {
                "topic": "General Learning",
                "level": "beginner",
                "goal": "Learn the topic",
                "preferred_format": "any",
                "time_commitment": "1-2 hours"
            }

