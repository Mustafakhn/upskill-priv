import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:\w)*)?)?$'
    return bool(re.match(pattern, url))


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize user input"""
    # Remove potentially dangerous characters
    text = text.strip()
    if max_length and len(text) > max_length:
        text = text[:max_length]
    return text

