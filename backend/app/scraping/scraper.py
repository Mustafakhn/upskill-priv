import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
from app.config import settings
from app.utils.text_utils import clean_text, estimate_reading_time
from urllib.parse import urljoin, urlparse
import time
import re


class WebScraper:
    """Web scraper using requests and BeautifulSoup"""
    
    def __init__(self, timeout: int = None):
        self.timeout = timeout or settings.SCRAPE_TIMEOUT
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def scrape(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape a web page
        
        Returns:
            Dictionary with 'title', 'content', 'html', or None if failed
        """
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Check if it's HTML
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                return None
            
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_content(soup, title)
            
            if not content and not title:
                return None
            
            return {
                "title": title or url,
                "content": clean_text(content),
                "html": html,
                "url": url
            }
        except Exception as e:
            print(f"Scraping failed for {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try various title sources
        if soup.title:
            return soup.title.string or ""
        
        # Try Open Graph title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]
        
        # Try h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text()
        
        return ""
    
    def _extract_content(self, soup: BeautifulSoup, page_title: str = "") -> str:
        """Extract main content from page with better formatting"""
        # Remove unwanted elements
        unwanted_tags = ["script", "style", "nav", "header", "footer", "aside", 
                        "menu", "menubar", "sidebar", "advertisement", "ads",
                        "comment", "comments", "social", "share", "breadcrumb",
                        "breadcrumbs", "navigation", "nav-menu", "cookie",
                        "cookie-banner", "newsletter", "subscribe", "related"]
        
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove elements with common non-content classes/ids
        unwanted_classes = ["nav", "menu", "sidebar", "header", "footer", "ad", 
                           "advertisement", "social", "share", "breadcrumb",
                           "cookie", "newsletter", "related", "comments",
                           "comment-section", "author-box", "tags", "meta"]
        
        for class_name in unwanted_classes:
            for element in soup.find_all(class_=lambda x: x and any(c in str(x).lower() for c in [class_name])):
                element.decompose()
            for element in soup.find_all(id=lambda x: x and any(c in str(x).lower() for c in [class_name])):
                element.decompose()
        
        # Try to find main content areas (prioritize article tag)
        main_content = None
        
        # First try article tag
        article = soup.find("article")
        if article:
            main_content = article
        else:
            # Try main tag
            main = soup.find("main")
            if main:
                main_content = main
            else:
                # Try content divs
                content_divs = soup.find_all("div", class_=lambda x: x and any(
                    keyword in str(x).lower() for keyword in 
                    ["content", "main", "post", "article", "entry", "body", "text", "prose"]
                ))
                if content_divs:
                    # Find the largest content div
                    main_content = max(content_divs, key=lambda x: len(x.get_text()))
                else:
                    # Fallback to body
                    main_content = soup.find("body")
        
        if not main_content:
            return ""
        
        # Extract text with better paragraph preservation
        paragraphs = []
        seen_text = set()  # Track seen text to remove duplicates
        
        # Extract paragraphs from common content tags
        for element in main_content.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "pre", "code"]):
            text = element.get_text(separator=" ", strip=True)
            # Clean up the text
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # Skip if too short, empty, or duplicate
            if len(text) < 20:
                continue
            
            # Skip navigation-like text
            nav_keywords = ["home", "about", "contact", "privacy", "terms", "cookie", 
                          "menu", "navigation", "skip to", "jump to", "table of contents"]
            if any(keyword in text.lower() for keyword in nav_keywords) and len(text) < 50:
                continue
            
            # Create a normalized version for duplicate detection
            normalized = text.lower()[:100]  # Use first 100 chars for comparison
            if normalized in seen_text:
                continue
            seen_text.add(normalized)
            
            paragraphs.append(text)
        
        # If we didn't get good paragraphs, fall back to getting all text
        if len(paragraphs) < 3:
            full_text = main_content.get_text(separator="\n", strip=True)
            # Split by double newlines or long whitespace
            paragraphs = [p.strip() for p in re.split(r'\n\s*\n+', full_text) if len(p.strip()) > 50]
        
        # Join paragraphs with double newlines
        content = "\n\n".join(paragraphs)
        
        # Remove repeated headers/titles (common issue)
        lines = content.split("\n")
        cleaned_lines = []
        seen_lines = set()
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                cleaned_lines.append("")
                continue
            
            # Skip if this exact line appeared recently (within last 5 lines)
            line_lower = line_stripped.lower()
            if line_lower in seen_lines:
                continue
            
            # Add to seen (keep last 10 lines in memory)
            seen_lines.add(line_lower)
            if len(seen_lines) > 10:
                # Remove oldest entry (simple approach: clear if too many)
                if len(seen_lines) > 20:
                    seen_lines = set(list(seen_lines)[-10:])
            
            cleaned_lines.append(line_stripped)
        
        content = "\n".join(cleaned_lines)
        
        # Remove excessive blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Remove repeated title/header at the beginning
        if page_title:
            title_variations = [
                page_title,
                page_title.lower(),
                page_title.upper(),
                page_title.title(),
            ]
            lines = content.split('\n')
            # Remove first few lines if they match the title
            while lines:
                first_line = lines[0].strip()
                if not first_line:
                    lines.pop(0)
                    continue
                # Check if first line is a variation of the title
                if any(var and (first_line.startswith(var) or var in first_line[:min(50, len(first_line))]) 
                       for var in title_variations if var):
                    lines.pop(0)
                else:
                    break
            content = '\n'.join(lines)
        
        # Remove common repeated patterns at start (like "Documentation Tutorials...")
        lines = content.split('\n')
        filtered_lines = []
        skip_patterns = [
            r'^documentation\s+tutorials?',
            r'^tutorials?\s+documentation',
            r'^home\s+>\s+',
            r'^breadcrumb',
        ]
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                filtered_lines.append("")
                continue
            
            # Skip lines that match skip patterns
            if any(re.match(pattern, line_stripped.lower()) for pattern in skip_patterns):
                continue
            
            # Skip very short lines that are likely navigation
            if len(line_stripped) < 30 and line_stripped.lower() in ['documentation', 'tutorials', 'tutorial']:
                continue
            
            filtered_lines.append(line_stripped)
        
        content = '\n'.join(filtered_lines)
        
        # Final cleanup
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = content.strip()
        
        return content
    
    def detect_type(self, url: str, content: str = None) -> str:
        """Detect resource type from URL and content"""
        url_lower = url.lower()
        
        # Check URL patterns
        if any(domain in url_lower for domain in ["youtube.com", "youtu.be", "vimeo.com"]):
            return "video"
        if any(domain in url_lower for domain in ["github.com", "gitlab.com"]):
            return "doc"
        if any(ext in url_lower for ext in [".pdf", ".doc", ".docx"]):
            return "doc"
        
        # Check content if available
        if content:
            content_lower = content.lower()
            if "video" in content_lower or "watch" in content_lower:
                return "video"
            if "tutorial" in content_lower or "guide" in content_lower:
                return "blog"
            if "documentation" in content_lower or "api" in content_lower:
                return "doc"
        
        # Default to blog
        return "blog"

