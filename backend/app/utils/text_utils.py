import re
from typing import List


def clean_text(text: str) -> str:
    """Clean and normalize text while preserving paragraph structure"""
    if not text:
        return ""
    
    # Split by paragraphs (double newlines)
    paragraphs = text.split('\n\n')
    cleaned_paragraphs = []
    
    for para in paragraphs:
        # Clean each paragraph
        para = para.strip()
        if not para:
            continue
        
        # Remove excessive whitespace within paragraph
        para = re.sub(r'\s+', ' ', para)
        para = para.strip()
        
        # Skip very short paragraphs (likely navigation/UI elements)
        if len(para) < 20:
            continue
        
        # Skip common navigation/UI text patterns
        nav_patterns = [
            r'^(home|about|contact|privacy|terms|menu|navigation|skip|jump).*$',
            r'^cookie.*policy.*$',
            r'^subscribe.*newsletter.*$',
            r'^follow us.*$',
            r'^share.*$',
        ]
        if any(re.match(pattern, para.lower()) for pattern in nav_patterns):
            continue
        
        cleaned_paragraphs.append(para)
    
    # Join with double newlines to preserve paragraph structure
    result = '\n\n'.join(cleaned_paragraphs)
    
    # Final cleanup: remove excessive blank lines
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    return result.strip()


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text"""
    # Simple keyword extraction (can be enhanced with NLP libraries)
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    # Remove common stop words
    stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
    keywords = [w for w in words if w not in stop_words]
    
    # Count frequency and return top keywords
    from collections import Counter
    keyword_counts = Counter(keywords)
    return [word for word, _ in keyword_counts.most_common(max_keywords)]


def estimate_reading_time(text: str) -> int:
    """Estimate reading time in minutes (assuming 200 words per minute)"""
    word_count = len(text.split())
    return max(1, word_count // 200)


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

