from typing import Dict, Any, List, Optional
from app.utils.ai_client import ai_client
from app.api.v1.dao.resource_dao import ResourceDAO
from app.api.v1.dao.journey_dao import JourneyDAO
from sqlalchemy.orm import Session


class CompanionService:
    """Service for AI Learning Companion features"""
    
    def __init__(self):
        self.resource_dao = ResourceDAO
        self.journey_dao = JourneyDAO
    
    def answer_question(
        self,
        db: Session,
        journey_id: int,
        user_id: int,
        question: str,
        context_resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Answer a question in the context of the learning journey"""
        journey = self.journey_dao.get_by_id(db, journey_id)
        if not journey or journey.user_id != user_id:
            raise ValueError("Journey not found or unauthorized")
        
        # Get journey resources for context
        from app.api.v1.dao.journey_dao import JourneyDAO
        journey_resources = JourneyDAO.get_resources(db, journey_id)
        resource_ids = [jr.resource_id for jr in journey_resources]
        resources = self.resource_dao.get_by_ids(resource_ids) if resource_ids else []
        
        # Get specific resource context if provided
        context_resource = None
        if context_resource_id:
            context_resource = self.resource_dao.get_by_id(context_resource_id)
        
        # Build context
        context_parts = [
            f"Learning Topic: {journey.topic}",
            f"Learning Goal: {journey.goal}",
            f"Skill Level: {journey.level}",
        ]
        
        if context_resource:
            context_parts.append(f"\nCurrent Resource Context:")
            context_parts.append(f"Title: {context_resource.get('title', '')}")
            context_parts.append(f"Summary: {context_resource.get('summary', '')[:500]}")
        
        if resources:
            context_parts.append(f"\nAvailable Resources in Journey:")
            for r in resources[:5]:  # Limit to 5 for context
                context_parts.append(f"- {r.get('title', '')}: {r.get('summary', '')[:200]}")
        
        context = "\n".join(context_parts)
        
        system_prompt = f"""You are an AI learning companion helping a student learn {journey.topic}.
Your role is to:
- Answer questions clearly and concisely
- Adjust explanations to the student's level ({journey.level})
- Provide examples when helpful
- Reference the learning resources when relevant
- Keep responses focused and educational

Student's goal: {journey.goal}
Skill level: {journey.level}

Context about their learning journey:
{context}

Answer the student's question in a helpful, educational way. Be concise but thorough."""
        
        prompt = f"Student question: {question}\n\nProvide a clear, helpful answer:"
        
        try:
            answer = ai_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            return {
                "answer": answer.strip(),
                "context_used": context_resource_id is not None
            }
        except Exception as e:
            raise Exception(f"Failed to generate answer: {str(e)}")
    
    def summarize_resource(
        self,
        resource_id: str,
        level: str = "intermediate"
    ) -> Dict[str, Any]:
        """Generate a summary of a resource"""
        resource = self.resource_dao.get_by_id(resource_id)
        if not resource:
            raise ValueError("Resource not found")
        
        system_prompt = f"""You are a learning assistant. Create a concise summary of this learning resource.
Adjust the summary depth for a {level} level learner.

Focus on:
- Key concepts covered
- Main takeaways
- What the learner will gain
- Prerequisites (if any)

Keep it concise (150-250 words)."""
        
        prompt = f"""Summarize this learning resource:

Title: {resource.get('title', '')}
Current Summary: {resource.get('summary', '')}
Type: {resource.get('type', 'blog')}
Difficulty: {resource.get('difficulty', 'intermediate')}

Create a comprehensive summary:"""
        
        try:
            summary = ai_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=400
            )
            return {
                "summary": summary.strip(),
                "resource_id": resource_id,
                "resource_title": resource.get('title', '')
            }
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")
    
    def simplify_explanation(
        self,
        resource_id: str,
        concept: str,
        level: str = "beginner"
    ) -> Dict[str, Any]:
        """Simplify an explanation for a specific level"""
        resource = self.resource_dao.get_by_id(resource_id)
        if not resource:
            raise ValueError("Resource not found")
        
        system_prompt = f"""You are a learning assistant. Simplify complex explanations for a {level} level learner.

Your task:
- Break down complex concepts into simple terms
- Use analogies and examples
- Avoid jargon or explain it clearly
- Make it easy to understand

Target level: {level}"""
        
        prompt = f"""Simplify this concept from the resource:

Resource: {resource.get('title', '')}
Resource Summary: {resource.get('summary', '')[:500]}

Concept to simplify: {concept}

Provide a simplified explanation suitable for a {level} learner:"""
        
        try:
            explanation = ai_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.6,
                max_tokens=500
            )
            return {
                "explanation": explanation.strip(),
                "concept": concept,
                "level": level
            }
        except Exception as e:
            raise Exception(f"Failed to simplify explanation: {str(e)}")
    
    def generate_examples(
        self,
        resource_id: str,
        concept: str,
        count: int = 3
    ) -> Dict[str, Any]:
        """Generate examples for a concept"""
        resource = self.resource_dao.get_by_id(resource_id)
        if not resource:
            raise ValueError("Resource not found")
        
        system_prompt = """You are a learning assistant. Generate practical examples to help students understand concepts.

Return ONLY valid JSON with this structure:
{
    "examples": [
        {
            "title": "Example title",
            "description": "Detailed example explanation",
            "code_or_demo": "Optional code snippet or demo (if applicable)"
        }
    ]
}"""
        
        prompt = f"""Generate {count} practical examples for this concept:

Resource: {resource.get('title', '')}
Resource Summary: {resource.get('summary', '')[:500]}

Concept: {concept}

Generate {count} clear, practical examples:"""
        
        try:
            result = ai_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            examples = result.get("examples", [])
            return {
                "examples": examples[:count],
                "concept": concept
            }
        except Exception as e:
            raise Exception(f"Failed to generate examples: {str(e)}")
    
    def generate_quiz(
        self,
        db: Session,
        journey_id: int,
        user_id: int,
        resource_id: Optional[str] = None,
        quiz_type: str = "mcq",
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """Generate a quiz (MCQ or short answer)"""
        journey = self.journey_dao.get_by_id(db, journey_id)
        if not journey or journey.user_id != user_id:
            raise ValueError("Journey not found or unauthorized")
        
        # Get context resources
        from app.api.v1.dao.journey_dao import JourneyDAO
        journey_resources = JourneyDAO.get_resources(db, journey_id)
        resource_ids = [jr.resource_id for jr in journey_resources]
        resources = self.resource_dao.get_by_ids(resource_ids) if resource_ids else []
        
        # Focus on specific resource if provided
        if resource_id:
            focus_resource = self.resource_dao.get_by_id(resource_id)
            if focus_resource:
                resources = [focus_resource]
        
        # Build context from resources
        context = f"Learning Topic: {journey.topic}\nLearning Goal: {journey.goal}\nSkill Level: {journey.level}\n\n"
        context += "Resources to quiz on:\n"
        for r in resources[:3]:  # Limit to 3 resources
            context += f"- {r.get('title', '')}: {r.get('summary', '')[:300]}\n"
        
        if quiz_type == "mcq":
            system_prompt = f"""You are a learning assistant creating multiple-choice questions.

Return ONLY valid JSON with this structure:
{{
    "questions": [
        {{
            "question": "Question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Why this answer is correct"
        }}
    ]
}}

Create {num_questions} multiple-choice questions appropriate for a {journey.level} level learner."""
        else:
            system_prompt = f"""You are a learning assistant creating short-answer questions.

Return ONLY valid JSON with this structure:
{{
    "questions": [
        {{
            "question": "Question text",
            "sample_answer": "Example of a good answer",
            "key_points": ["Key point 1", "Key point 2"]
        }}
    ]
}}

Create {num_questions} short-answer questions appropriate for a {journey.level} level learner."""
        
        prompt = f"""Create a quiz based on this learning context:

{context}

Generate {num_questions} {quiz_type.upper()} questions:"""
        
        try:
            result = ai_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.6
            )
            questions = result.get("questions", [])
            return {
                "quiz_type": quiz_type,
                "questions": questions[:num_questions],
                "resource_id": resource_id,
                "journey_id": journey_id
            }
        except Exception as e:
            raise Exception(f"Failed to generate quiz: {str(e)}")

