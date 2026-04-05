from typing import List, Dict, Any, Optional
from app.utils.ai_client import ai_client


class AIService:
    """Service for conversational journey-intake AI interactions."""

    VALID_LEVELS = ["beginner", "intermediate", "advanced"]
    VALID_FORMATS = ["video", "blog", "doc", "mixed", "any"]

    def _normalize_level(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        level = str(value).strip().lower()
        aliases = {
            "new": "beginner",
            "novice": "beginner",
            "starter": "beginner",
            "basic": "beginner",
            "complete beginner": "beginner",
            "beginner level": "beginner",
            "mid": "intermediate",
            "medium": "intermediate",
            "experienced": "intermediate",
            "some experience": "intermediate",
            "intermediate level": "intermediate",
            "expert": "advanced",
            "pro": "advanced",
            "advanced level": "advanced",
        }
        level = aliases.get(level, level)
        return level if level in self.VALID_LEVELS else None

    def _normalize_format(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        preferred_format = str(value).strip().lower()
        aliases = {
            "videos": "video",
            "video tutorials": "video",
            "video lessons": "video",
            "tutorials": "video",
            "articles": "blog",
            "article": "blog",
            "blogs": "blog",
            "blog posts": "blog",
            "reading articles": "blog",
            "docs": "doc",
            "documentation": "doc",
            "guides": "doc",
            "documentation and guides": "doc",
            "reading": "blog",
            "mix": "mixed",
            "both": "mixed",
            "mixed learning format": "mixed",
        }
        preferred_format = aliases.get(preferred_format, preferred_format)
        return preferred_format if preferred_format in self.VALID_FORMATS else None

    def _clean_topic(self, value: Optional[str]) -> str:
        if not value:
            return ""
        topic = str(value).strip()
        generic_topics = {"general learning", "learning", "topic", "unknown", "something"}
        return "" if topic.lower() in generic_topics else topic

    def _clean_goal(self, value: Optional[str], topic: str) -> str:
        if value:
            goal = str(value).strip()
            generic_goals = {
                "learn",
                "learn the topic",
                "understand",
                "general learning",
                "get better",
                "improve",
            }
            if goal.lower() not in generic_goals:
                return goal
        return f"Learn {topic}" if topic else ""

    def _validate_intent(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        topic = self._clean_topic(intent.get("topic"))
        level = self._normalize_level(intent.get("level"))
        preferred_format = self._normalize_format(intent.get("preferred_format"))
        goal = self._clean_goal(intent.get("goal"), topic)

        normalized_intent = {
            "topic": topic,
            "level": level,
            "goal": goal,
            "preferred_format": preferred_format,
        }

        missing = []
        if not topic:
            missing.append("topic")
        if not level:
            missing.append("level")
        if not preferred_format:
            missing.append("preferred_format")

        return {
            "missing": missing,
            "is_ready": len(missing) == 0,
            "intent": normalized_intent,
        }

    def _build_fallback_suggestions(self, missing_info: List[str], topic: str = "") -> List[str]:
        if not missing_info:
            return [
                "Build roadmap now",
                "Balanced learning plan",
                "Fastest path",
            ]

        missing = missing_info[0]
        if missing == "topic":
            return [
                "Learn Python",
                "Learn UI design",
                "Learn digital marketing",
                "Learn guitar",
            ]
        if missing == "level":
            return [
                "Complete beginner",
                "Some experience",
                "Intermediate level",
                "Advanced level",
            ]
        if missing == "preferred_format":
            return [
                "Video lessons",
                "Reading articles",
                "Documentation and guides",
                "Mixed learning format",
            ]
        if topic:
            return [
                f"Practical {topic} projects",
                f"Job-ready {topic} skills",
                f"{topic} fundamentals",
            ]
        return ["Help me narrow it down", "Suggest a good starting point", "Give me a balanced plan"]

    def _clean_suggestions(self, suggestions: Any, missing_info: List[str], topic: str = "") -> List[str]:
        if not isinstance(suggestions, list):
            suggestions = []

        cleaned = []
        for suggestion in suggestions:
            if not isinstance(suggestion, str):
                continue
            value = suggestion.strip().strip('"').strip("'").rstrip(".? ")
            for prefix in ["I'm ", "I am ", "I want ", "I'd like ", "I would like ", "I prefer ", "I'd prefer "]:
                if value.lower().startswith(prefix.lower()):
                    value = value[len(prefix):].strip()
                    break
            if value.lower().startswith("to learn "):
                value = value[9:].strip()
            if 3 <= len(value) <= 80 and value not in cleaned:
                cleaned.append(value)

        if not cleaned:
            cleaned = self._build_fallback_suggestions(missing_info, topic)

        return cleaned[:4]

    def generate_chat_turn(
        self,
        conversation_history: List[Dict[str, str]],
        user_message: str,
        asked_questions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate the assistant reply, suggested quick replies, and extracted intent in one AI call.
        """
        if asked_questions is None:
            asked_questions = []

        full_history = conversation_history[-10:] + [{"role": "user", "content": user_message}]
        transcript = "\n".join(
            f"{msg.get('role', 'user').upper()}: {msg.get('content', '')}"
            for msg in full_history
        )
        prior_questions = "\n".join(f"- {question}" for question in asked_questions[-6:])

        system_prompt = """You are a warm, concise learning coach helping a user create a personalized learning journey.

Return ONLY valid JSON with this exact structure:
{
  "response": "string",
  "topic": "string or null",
  "level": "beginner|intermediate|advanced|null",
  "goal": "string or null",
  "preferred_format": "video|blog|doc|mixed|any|null",
  "next_suggestions": ["string", "string", "string"]
}

Rules:
- The response should be 1-3 short sentences, conversational and helpful.
- Sound like a chat, not a form or checklist.
- Briefly react to what the user just said before asking the next thing.
- Actively gather the missing setup info needed for a learning plan.
- Required setup info: topic, learner level, preferred learning format.
- Goal is helpful but optional; if the user gives one, keep it.
- Ask for only one missing thing at a time, prioritizing topic, then level, then preferred_format.
- If all required info is present, confirm you are ready to build the journey.
- Extract only what the user explicitly said or strongly implied.
- Do not invent user preferences.
- next_suggestions must be 3-4 short clickable replies relevant to your response.
- When collecting info, next_suggestions should help answer the exact missing question.
- Keep each suggestion under 10 words when possible.
- Suggestions should be short option labels, not full first-person sentences.
- Do not start suggestions with "I", "I'm", or "I want".
- Avoid repeating the exact same wording across all suggestions.

Good tone examples:
- "Kubernetes and Terraform are a strong combo. What's your current level with them?"
- "Nice, beginner is totally fine here. Do you want videos, written guides, or a mix?"
- "Perfect, mixed works well for this topic. I'll build your learning path now."
"""

        prompt = f"""Conversation:
{transcript}

Previously suggested prompts:
{prior_questions or 'None'}

Generate the next assistant reply, extract the structured learning intent, and provide suggestion chips."""

        try:
            result = ai_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
            )
        except Exception as e:
            print(f"Error in generate_chat_turn: {e}")
            result = {
                "response": "Tell me what you want to learn, your level, and how you like to study.",
                "topic": None,
                "level": None,
                "goal": None,
                "preferred_format": None,
                "next_suggestions": [],
            }

        validation = self._validate_intent(result)
        intent = validation["intent"]
        missing_info = validation["missing"]
        is_ready = validation["is_ready"]
        response = str(result.get("response", "")).strip()

        if not response:
            if not intent["topic"]:
                response = "Tell me what you want to learn, and I'll shape a plan around it."
            elif not intent["level"]:
                response = f"Nice choice. What's your current level in {intent['topic']}?"
            elif not intent["preferred_format"]:
                response = "What kind of material helps you learn best: videos, articles, docs, or mixed?"
            else:
                response = f"Perfect. I have what I need to build your {intent['topic']} learning journey."

        suggestions = self._clean_suggestions(result.get("next_suggestions", []), missing_info, intent["topic"])

        return {
            "response": response,
            "intent": {
                "topic": intent["topic"],
                "level": intent["level"] or "beginner",
                "goal": intent["goal"] or (f"Learn {intent['topic']}" if intent["topic"] else "Learn the topic"),
                "preferred_format": intent["preferred_format"] or "any",
            },
            "missing_info": missing_info,
            "is_ready": is_ready,
            "next_suggestions": suggestions,
        }

    def analyze_conversation(
        self,
        conversation_history: List[Dict[str, str]],
        asked_questions: List[str] = None,
        user_message_count: int = 0
    ) -> Dict[str, Any]:
        """Backward-compatible wrapper around the single-turn generator."""
        if not conversation_history:
            validation = self._validate_intent({})
            return {
                "intent": validation["intent"],
                "missing_info": validation["missing"],
                "is_ready": False,
                "next_suggestions": self._build_fallback_suggestions(validation["missing"]),
            }

        latest_user_message = ""
        prior_history = conversation_history
        if conversation_history[-1].get("role") == "user":
            latest_user_message = conversation_history[-1].get("content", "")
            prior_history = conversation_history[:-1]

        turn = self.generate_chat_turn(prior_history, latest_user_message, asked_questions)
        return {
            "intent": turn["intent"],
            "missing_info": turn["missing_info"],
            "is_ready": turn["is_ready"],
            "next_suggestions": turn["next_suggestions"],
        }

    def generate_chat_response(
        self,
        conversation_history: List[Dict[str, str]],
        user_message: str
    ) -> str:
        """Backward-compatible wrapper for callers that only need the assistant reply."""
        return self.generate_chat_turn(conversation_history, user_message).get("response", "")

    def check_if_ready(self, conversation_history: List[Dict[str, str]]) -> bool:
        user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
        analysis = self.analyze_conversation(conversation_history, asked_questions=[], user_message_count=len(user_messages))
        return analysis["is_ready"]

    def generate_next_question_directly(
        self,
        conversation_history: List[Dict[str, str]],
        asked_questions: List[str]
    ) -> Optional[str]:
        if not conversation_history:
            return "What do you want to learn first?"

        analysis = self.analyze_conversation(
            conversation_history,
            asked_questions,
            len([msg for msg in conversation_history if msg.get("role") == "user"])
        )
        suggestions = analysis.get("next_suggestions", [])
        return suggestions[0] if suggestions else None
