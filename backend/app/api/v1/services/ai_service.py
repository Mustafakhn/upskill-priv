from typing import List, Dict, Any, Optional
from app.utils.ai_client import ai_client
from app.agents.intent_agent import IntentAgent


class AIService:
    """Service for AI interactions"""

    def __init__(self):
        self.intent_agent = IntentAgent()

    def _validate_intent(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate intent and determine missing info, readiness, all from a single intent dict
        This avoids multiple AI calls by reusing extracted intent
        """
        missing = []
        
        # Check for topic - only topic is truly required
        topic = intent.get("topic", "").lower().strip()
        generic_topics = ["general learning", "learning", "topic", "unknown"]
        if not topic or topic in generic_topics or len(topic) < 2:
            missing.append("topic")
        
        # Level is optional - default to "beginner" if not specified (don't mark as missing)
        level = intent.get("level")
        if level:
            level = str(level).lower().strip()
            if level not in ["beginner", "intermediate", "advanced"]:
                # Invalid level, default to beginner
                intent["level"] = "beginner"
        else:
            # No level specified, default to beginner silently
            intent["level"] = "beginner"
        
        # Goal is optional - use topic as goal if not specified (don't mark as missing)
        goal = intent.get("goal", "").lower().strip()
        generic_goals = ["learn the topic", "learn", "understand", "general learning", "topic", "acquire a new skill", "just to acquire a new skill", "acquire new skill"]
        if not goal or goal in generic_goals:
            # Use topic as goal if goal is generic or missing
            topic_for_goal = intent.get("topic", "").strip()
            if topic_for_goal and topic_for_goal.lower() not in generic_topics:
                intent["goal"] = f"Learn {topic_for_goal}"
            else:
                intent["goal"] = "Learn the topic"
        
        # Preferred format is optional - default to "any" if not specified
        preferred_format = intent.get("preferred_format") or ""
        if preferred_format:
            preferred_format = str(preferred_format).lower().strip()
        # Accept: video, blog, doc, any, mixed
        valid_formats = ["video", "blog", "doc", "any", "mixed"]
        # If not specified or invalid, default to "any" (don't add to missing)
        if not preferred_format or preferred_format not in valid_formats:
            preferred_format = "any"
            # Update intent with default
            intent["preferred_format"] = "any"
        
        # Determine readiness - need all info AND at least 2 user messages (checked separately)
        is_ready = len(missing) == 0
        
        return {
            "missing": missing,
            "is_ready": is_ready,
            "intent": intent
        }

    def analyze_conversation(
        self,
        conversation_history: List[Dict[str, str]],
        asked_questions: List[str] = None,
        user_message_count: int = 0
    ) -> Dict[str, Any]:
        """
        Unified method that does everything in ONE AI call:
        - Extracts intent
        - Determines missing info
        - Checks readiness
        - Generates next question/suggestion (if needed)
        
        Returns dict with: intent, missing_info, is_ready, next_suggestion
        """
        if asked_questions is None:
            asked_questions = []
        
        # Single AI call to extract intent AND generate suggestion if needed
        context = "\n".join([
            f"{msg.get('role', 'user').upper()}: {msg.get('content', '')}"
            for msg in conversation_history[-8:]  # Last 8 messages
        ])
        
        asked_context = ""
        if asked_questions:
            asked_context = f"\n\nQuestions already asked:\n" + "\n".join([f"- {q}" for q in asked_questions[-5:]])  # Last 5 questions
        
        system_prompt = """You are a helpful learning assistant. Analyze the conversation and extract structured information.

Return ONLY valid JSON with these exact fields:
{
    "topic": "string (main learning topic, or 'General Learning' if not specified)",
    "level": "beginner|intermediate|advanced|null (DO NOT default to 'beginner' - return null if user hasn't specified)",
    "goal": "string (what they want to achieve - be specific, or 'Learn the topic' if not specified)",
    "preferred_format": "video|blog|doc|any|mixed (default: any)",
    "next_suggestions": "array of 3-4 strings (SHORT user-friendly suggestions the user could click to provide missing info, or empty array if all info collected. Each suggestion 8-12 words max, written as if the USER is saying it, not as an AI question. Provide multiple options for variety)"
}

CRITICAL RULES for extraction:
- ONLY extract information that the USER explicitly stated or clearly implied
- Do NOT infer goals from assistant questions
- Do NOT ask questions proactively - only provide suggestions if user explicitly asks for help
- If topic not specified: return null (don't create journey)
- If goal not specified: return null (use topic as goal if topic is clear)
- If level not specified: return null (default to "beginner" silently, don't ask)
- If preferred_format not specified: return "any" (this is optional and can default)
- IMPORTANT: Default to null/empty for missing info - don't ask questions unless user explicitly requests help

CRITICAL RULES for next_suggestions:
- Return empty array [] by default - DO NOT proactively ask questions
- ONLY return suggestions if the user explicitly asks for help or clarification
- If topic is missing: return empty array [] (don't create journey, but don't ask either)
- If level is missing: return empty array [] (default to "beginner" silently)
- If goal is missing: return empty array [] (use topic as goal if topic is clear)
- If preferred_format is missing: return empty array [] (default to "any" silently)
- ONLY provide suggestions if user explicitly requests them (e.g., "help me", "what do I need", "what else")
- Write as if they're QUICK SUGGESTIONS for the USER to click, NOT questions from the AI
- ALWAYS start with "I" (first person from user's perspective)
- NEVER use question format (no "What", "How", "Do you", "Can you", etc.)
- NEVER frame as AI asking the user (no "Tell me", "Share", "Let me know")
- Make each SHORT (8-12 words max)
- Focus on what the USER wants to learn or achieve
- Use simple, everyday language
- NO technical jargon, NO frameworks

Be concise and accurate."""
        
        prompt = f"""Analyze this conversation and extract the learning intent. Do NOT ask questions - only extract what the user has explicitly stated:

{context}{asked_context}

Return JSON with: topic, level, goal, preferred_format, next_suggestion"""
        
        try:
            result = ai_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            # Extract intent from AI response - apply defaults silently
            topic = result.get("topic", "").strip() if result.get("topic") else ""
            level = result.get("level", "").strip() if result.get("level") else ""
            goal = result.get("goal", "").strip() if result.get("goal") else ""
            
            # Apply defaults silently (don't ask questions)
            if not level:
                level = "beginner"
            if not goal and topic:
                goal = f"Learn {topic}"
            elif not goal:
                goal = "Learn the topic"
            
            intent = {
                "topic": topic,
                "level": level,
                "goal": goal,
                "preferred_format": result.get("preferred_format", "any").strip() if result.get("preferred_format") else "any",
                "time_commitment": result.get("time_commitment", "1-2 hours")
            }
            
            # Validate using code-based checks (not AI-based)
            validation = self._validate_intent(intent)
            
            # Determine readiness - only topic is required, level and goal have defaults
            # Only need topic and at least 1 user message (not 2)
            is_ready = len(validation["missing"]) == 0 and user_message_count >= 1
            
            # Get next suggestions from AI response, or generate them if missing and needed
            next_suggestions = result.get("next_suggestions", [])
            # Handle legacy single suggestion format
            if not isinstance(next_suggestions, list):
                if result.get("next_suggestion"):
                    next_suggestions = [result.get("next_suggestion")]
                else:
                    next_suggestions = []
            
            # Don't generate suggestions proactively - only if user explicitly asks
            # Only generate suggestions if topic is missing (required field)
            if not is_ready and len(next_suggestions) == 0 and validation["missing"]:
                # Only suggest if topic is missing (the only truly required field)
                if "topic" in validation["missing"]:
                    next_suggestions = ["I want to learn Python", "I'm interested in web development", "I'd like to learn data science", "I want to learn product management"]
                # For other missing fields, don't ask - use defaults silently
            
            # Clean up suggestions
            cleaned_suggestions = []
            for suggestion in next_suggestions:
                if not suggestion or not isinstance(suggestion, str):
                    continue
                    
                suggestion = suggestion.strip().strip('"').strip("'").rstrip('?').rstrip('.').rstrip()
                
                # Clean up suggestion to ensure it's user-to-AI format
                suggestion_lower = suggestion.lower()
                
                # Remove question words at the start
                question_starters = ["what", "how", "do you", "can you", "tell me", "share", "let me know", "would you"]
                for starter in question_starters:
                    if suggestion_lower.startswith(starter):
                        # Convert question to statement
                        if "your" in suggestion_lower or "you" in suggestion_lower:
                            suggestion = suggestion.replace("your", "my").replace("Your", "My")
                            suggestion = suggestion[len(starter):].strip().capitalize()
                            if not suggestion.lower().startswith("i "):
                                suggestion = "I " + suggestion.lower()
                        break
                
                # Ensure it starts with "I" if it's a user statement
                if not suggestion.lower().startswith("i ") and not suggestion.lower().startswith("i'm") and not suggestion.lower().startswith("i'd"):
                    if "you" in suggestion.lower() or "your" in suggestion.lower():
                        suggestion = suggestion.replace("you", "I").replace("You", "I").replace("your", "my").replace("Your", "My")
                        if not suggestion.lower().startswith("i "):
                            suggestion = "I " + suggestion.lower()
                
                if len(suggestion) >= 3 and len(suggestion) <= 100:
                    cleaned_suggestions.append(suggestion)
            
            next_suggestions = cleaned_suggestions[:4]  # Limit to 4 suggestions
            
            return {
                "intent": intent,
                "missing_info": validation["missing"],
                "is_ready": is_ready,
                "next_suggestions": next_suggestions
            }
        except Exception as e:
            print(f"Error in analyze_conversation: {e}")
            import traceback
            traceback.print_exc()
            # Fallback
            intent = {
                "topic": "General Learning",
                "level": None,  # Don't default level
                "goal": "Learn the topic",
                "preferred_format": None,
                "time_commitment": None
            }
            validation = self._validate_intent(intent)
            return {
                "intent": intent,
                "missing_info": validation["missing"],
                "is_ready": False,
                "next_suggestions": ["I want to learn Python", "I'm interested in web development", "I'd like to learn data science"]
            }

    def _determine_missing_info(self, conversation_history: List[Dict[str, str]]) -> List[str]:
        """
        Determine what information is still missing from the conversation
        
        Returns a list of missing information types we need to collect
        """
        # Debug: print conversation history
        print(f"  [DEBUG] _determine_missing_info called with {len(conversation_history)} messages")
        
        intent = self.intent_agent.extract_intent(conversation_history)
        print(f"  [DEBUG] Extracted intent: topic={intent.get('topic')}, level={intent.get('level')}, goal={intent.get('goal')}")
        
        missing = []
        
        # Check for topic
        topic = intent.get("topic", "").lower().strip()
        generic_topics = ["general learning", "learning", "topic", "unknown"]
        if not topic or topic in generic_topics or len(topic) < 2:
            missing.append("topic")
            print(f"  [DEBUG] Topic missing: '{topic}'")
        else:
            print(f"  [DEBUG] Topic found: '{topic}'")
        
        # Check for level - be strict, don't accept defaults
        level = intent.get("level")
        if not level:
            missing.append("experience level")
            print(f"  [DEBUG] Level missing: None")
        else:
            level = str(level).lower().strip()
            if level not in ["beginner", "intermediate", "advanced"]:
                missing.append("experience level")
                print(f"  [DEBUG] Level missing: '{level}'")
            else:
                print(f"  [DEBUG] Level found: '{level}'")
        
        # Check for goal - reject very generic goals
        goal = intent.get("goal", "").lower().strip()
        generic_goals = ["learn the topic", "learn", "understand", "general learning", "topic", "acquire a new skill", "just to acquire a new skill", "acquire new skill"]
        if not goal or goal in generic_goals:
            missing.append("learning goal or what they want to achieve")
            print(f"  [DEBUG] Goal missing: '{goal}'")
        else:
            print(f"  [DEBUG] Goal found: '{goal}'")
        
        # Preferred format is required - accept "mixed" as valid
        preferred_format = intent.get("preferred_format") or ""
        if preferred_format:
            preferred_format = str(preferred_format).lower().strip()
        valid_formats = ["video", "blog", "doc", "any", "mixed"]
        if not preferred_format or preferred_format not in valid_formats:
            missing.append("preferred learning format (videos, articles, docs, mixed, or any)")
            print(f"  [DEBUG] Preferred format missing: '{preferred_format}'")
        else:
            print(f"  [DEBUG] Preferred format found: '{preferred_format}'")
        
        print(f"  [DEBUG] Missing info result: {missing}")
        return missing

    def _has_required_info(self, conversation_history: List[Dict[str, str]]) -> bool:
        """
        Check if we have all REQUIRED information to create a journey
        
        Required: topic, level, goal
        Optional: preferred_format, time_commitment
        """
        missing = self._determine_missing_info(conversation_history)
        return len(missing) == 0

    def generate_chat_response(
        self,
        conversation_history: List[Dict[str, str]],
        user_message: str
    ) -> str:
        """
        Generate AI chat response - conversational, one question at a time

        Args:
            conversation_history: Previous messages
            user_message: Current user message

        Returns:
            AI response text
        """
        # Note: This still makes a separate AI call for chat response generation
        # We could optimize further by combining with analyze_conversation, but keeping separate
        # for now to maintain clear separation of concerns
        
        # Quick check for missing info (no AI call, just validation)
        intent = self.intent_agent.extract_intent(conversation_history + [{"role": "user", "content": user_message}])
        validation = self._validate_intent(intent)
        has_required = validation["is_ready"]
        missing_info = validation["missing"]
        
        # Build dynamic instructions - don't ask questions proactively
        if has_required:
            # We have everything we need - confirm and offer to create journey
            instructions = "You have all the required information (topic, level, goal). Acknowledge their last response and confirm you're ready to create their personalized learning journey. Be concise and friendly."
        elif missing_info:
            # Only topic is required - if missing, acknowledge but don't ask questions
            if "topic" in missing_info:
                instructions = "Acknowledge their message. Do NOT ask questions. Simply acknowledge what they said. If they provided a topic, confirm it. If not, just acknowledge their message without asking for more information."
            else:
                # Topic is present, other info missing - use defaults silently, don't ask
                instructions = "Acknowledge their message and confirm you understand. Do NOT ask questions. Use defaults silently (beginner level, learn the topic as goal). Be concise and friendly."
        else:
            instructions = "You have enough information. If appropriate, acknowledge what they said and confirm you're ready to create their learning journey."
        
        system_prompt = f"""You are a helpful, friendly learning assistant. Your goal is to understand what the user wants to learn and create a personalized learning journey.

IMPORTANT RULES:
- Respond naturally and conversationally (1-2 sentences max - be concise!)
- DO NOT ask questions proactively - only acknowledge what the user said
- Be friendly and engaging, like talking to a friend
- If the user provides a topic, acknowledge it and confirm you'll create a journey
- Use defaults silently (beginner level, learn the topic as goal) - don't ask about these
- Once you have a topic, confirm you're ready to create the journey

{instructions}

Once you have a topic, say something like: Perfect! I'll create a personalized learning journey for you."""

        # Build conversation context (last 8 messages for context)
        messages = conversation_history[-8:] + [
            {"role": "user", "content": user_message}
        ]

        context = "\n".join([
            f"{msg.get('role', 'user').upper()}: {msg.get('content', '')}"
            for msg in messages
        ])

        prompt = f"""Continue this conversation naturally as the learning assistant:

{context}

ASSISTANT:"""

        try:
            response = ai_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.8,
                max_tokens=150  # Shorter responses - be concise!
            )
            return response.strip()
        except Exception as e:
            return f"I apologize, but I'm having trouble right now. Could you please rephrase your question? Error: {str(e)}"

    def check_if_ready(self, conversation_history: List[Dict[str, str]]) -> bool:
        """Check if we have enough information to create a journey - use analyze_conversation for efficiency"""
        user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
        analysis = self.analyze_conversation(conversation_history, asked_questions=[], user_message_count=len(user_messages))
        return analysis["is_ready"]

    def generate_next_question_directly(
        self,
        conversation_history: List[Dict[str, str]],
        asked_questions: List[str]
    ) -> Optional[str]:
        """
        Generate the next single question - now uses analyze_conversation for efficiency
        """
        if not conversation_history:
            return "What topic would you like to learn about?"
        
        user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
        analysis = self.analyze_conversation(conversation_history, asked_questions, len(user_messages))
        
        if analysis["is_ready"]:
            return None  # We have everything we need
        
        return analysis["next_suggestion"]
