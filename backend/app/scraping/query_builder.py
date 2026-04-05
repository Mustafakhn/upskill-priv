from typing import List, Optional
from app.utils.ai_client import ai_client


class QueryBuilder:
    """Build targeted search queries from user intent."""

    @staticmethod
    def _format_hint(preferred_format: Optional[str]) -> str:
        if preferred_format == "video":
            return "Prefer video-friendly phrasing such as walkthrough, lesson, or explained."
        if preferred_format == "blog":
            return "Prefer article-friendly phrasing such as guide, examples, best practices, or case study."
        if preferred_format == "doc":
            return "Prefer official docs, standards, reference, handbook, or guide phrasing."
        return "Use a balanced mix of query styles without overfocusing on one format."

    @staticmethod
    def _fallback_queries(topic: str, level: str, goal: str, preferred_format: Optional[str] = None) -> List[str]:
        base_goal = goal if goal and goal.lower() != f"learn {topic}".lower() else f"{topic} fundamentals"
        queries = [
            f"{topic} {level} fundamentals",
            f"{topic} {base_goal}",
            f"{topic} practical examples for {level}",
            f"{topic} roadmap for {goal or f'learning {topic}'}",
        ]

        if preferred_format == "doc":
            queries.append(f"{topic} official documentation")
        elif preferred_format == "video":
            queries.append(f"{topic} beginner walkthrough")
        elif preferred_format == "blog":
            queries.append(f"{topic} guide with examples")
        else:
            queries.append(f"{topic} best resources for {level}")

        deduped = []
        seen = set()
        for query in queries:
            normalized = query.lower().strip()
            if normalized not in seen:
                deduped.append(query)
                seen.add(normalized)
        return deduped[:5]

    @staticmethod
    def build_queries(topic: str, level: str, goal: str, preferred_format: str = None) -> List[str]:
        """
        Build multiple focused search queries for scraping.
        """
        format_hint = QueryBuilder._format_hint(preferred_format)

        system_prompt = """You are a search query expert building learning-resource queries.

Generate exactly 5 search queries as a JSON array of strings.

Requirements:
- Every query must stay tightly tied to the topic and the user's goal.
- Avoid generic filler like "common use cases", "advanced concepts", or "best practices" unless anchored to the topic and goal.
- Cover these angles with concrete wording:
  1. foundations
  2. practical examples or projects
  3. goal-specific learning
  4. high-quality reference or official source
  5. one complementary angle based on level
- Keep queries natural and specific.
- Do not produce duplicate or near-duplicate queries.
- Do not include quotation marks or numbering.
Return only a JSON array."""

        prompt = f"""Topic: {topic}
Level: {level}
Goal: {goal}
Preferred format: {preferred_format or 'mixed'}
Format guidance: {format_hint}

Generate 5 focused search queries that will find the most relevant learning resources for this user."""

        try:
            result = ai_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.4
            )

            if isinstance(result, list):
                cleaned = []
                seen = set()
                for item in result:
                    if not isinstance(item, str):
                        continue
                    query = item.strip().strip('"').strip("'")
                    if len(query) < 8:
                        continue
                    normalized = query.lower()
                    if normalized in seen:
                        continue
                    cleaned.append(query)
                    seen.add(normalized)
                if len(cleaned) >= 4:
                    return cleaned[:5]
        except Exception:
            pass

        return QueryBuilder._fallback_queries(topic, level, goal, preferred_format)
