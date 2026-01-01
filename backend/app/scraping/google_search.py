import requests
from typing import List, Dict, Optional
from app.config import settings
import time
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse, parse_qs
import urllib.parse
import re
import json


class SerpAPISearchProvider:
    """SerpAPI search provider (requires API key)"""
    
    @staticmethod
    def search(query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """Search using SerpAPI"""
        if not settings.SERPAPI_KEY:
            return []
        
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": settings.SERPAPI_KEY,
                "engine": "google",
                "num": min(num_results, 100)
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Parse organic results
            for item in data.get("organic_results", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
            
            return results
        except Exception as e:
            print(f"SerpAPI search failed: {e}")
            return []


class GoogleCustomSearchProvider:
    """Google Custom Search API provider (requires API key and search engine ID)"""
    
    @staticmethod
    def search(query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """Search using Google Custom Search API"""
        if not settings.GOOGLE_CSE_API_KEY or not settings.GOOGLE_CSE_ID:
            return []
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": settings.GOOGLE_CSE_API_KEY,
                "cx": settings.GOOGLE_CSE_ID,
                "q": query,
                "num": min(num_results, 10)  # Google CSE max is 10 per request
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Parse results
            for item in data.get("items", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
            
            return results
        except Exception as e:
            print(f"Google Custom Search failed: {e}")
            return []


class GooglesearchPackageProvider:
    """Google Search using the 'googlesearch' Python package
    
    Based on: https://www.geeksforgeeks.org/python/performing-google-search-using-python-code/
    This is a simple one-liner solution using the googlesearch package.
    """
    
    @staticmethod
    def search(query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """Search using the googlesearch package"""
        try:
            from googlesearch import search as google_search
            
            results = []
            try:
                # Use the googlesearch package - simple one-liner solution
                # The googlesearch-python package uses different parameters than the old 'google' package
                # Based on: https://github.com/MarioVilas/googlesearch
                try:
                    # Try the newer API format first (googlesearch-python package)
                    # Increased pause to 5 seconds to avoid rate limiting
                    search_results = google_search(
                        query,
                        num_results=min(num_results, 5),  # Limit results to reduce requests
                        lang='en',
                        pause=5.0  # Increased from 2.0 to 5.0 seconds
                    )
                except TypeError as e:
                    # Try older API format as fallback
                    try:
                        search_results = google_search(
                            query,
                            num=min(num_results, 5),  # Limit results
                            stop=min(num_results, 5),
                            pause=5  # Increased pause
                        )
                    except TypeError:
                        # Last resort: try without any optional params (may fail, that's ok)
                        search_results = google_search(query)
                
                # Convert URLs to our format
                for url in search_results:
                    results.append({
                        "title": "",  # Package only returns URLs
                        "url": url,
                        "snippet": ""
                    })
                    
                    if len(results) >= num_results:
                        break
                
                # If we got URLs, try to get titles from the pages
                if results:
                    # For now, just return URLs - we can scrape titles separately if needed
                    # The scraper service will handle getting full content
                    return results
            except StopIteration:
                # Iterator exhausted - we got all results
                pass
            except Exception as e:
                print(f"googlesearch package error: {e}")
                return []
            
            return results
        except ImportError:
            # Package not installed
            return []
        except Exception as e:
            print(f"GooglesearchPackageProvider failed: {e}")
            return []


class DuckDuckGoSearchProvider:
    """
    DuckDuckGo Search Provider - supports both text and video searches
    
    Uses the duckduckgo_search library (https://pypi.org/project/duckduckgo-search/)
    Documentation: https://pypi.org/project/duckduckgo-search/
    """
    
    @staticmethod
    def search(query: str, num_results: int = 10, preferred_format: str = "any", region: str = None) -> List[Dict[str, str]]:
        """
        Search using DuckDuckGo (free, no API key needed)
        
        Args:
            query: Search query
            num_results: Maximum number of results
            preferred_format: Preferred format ("video", "videos", "mixed", "mix", or "any")
            region: Region code (e.g., 'us-en', 'wt-wt'). If None, uses 'wt-wt'
        
        Returns:
            List of search results with 'title', 'url', 'snippet'
        """
        if region is None:
            region = 'wt-wt'  # Default: worldwide (no region)
        
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            print("DuckDuckGo library (duckduckgo_search) not installed. Install with: pip install duckduckgo-search")
            return []
        
        # DuckDuckGoSearchProvider now only handles TEXT searches
        # Videos are handled by YouTubeSearchProvider via SearchProvider.search()
        # "mixed" and "any" formats are handled by SearchProvider using YouTube + DuckDuckGo
        
        # Text search (articles, docs, etc.) - for "blog", "doc", or fallback
        # Use multiple backends like the working script for better results
        try:
            with DDGS() as ddgs:
                all_results = []
                seen_urls = set()
                
                # Try multiple backends: html and lite are most reliable (skip bing/auto if they fail)
                backends = ['html', 'bing', 'auto', 'lite']
                
                for backend in backends:
                    try:
                        print(f"      DuckDuckGo: trying backend='{backend}' for query: {query}")
                        text_results = list(ddgs.text(
                            keywords=query,
                            region=region,
                            safesearch='moderate',
                            backend=backend,
                            max_results=20  # Get more results per backend
                        ))
                        
                        if text_results:
                            for r in text_results:
                                url = r.get('href', '')
                                # Skip duplicates
                                if url and url not in seen_urls:
                                    all_results.append({
                                        "title": r.get('title', ''),
                                        "url": url,
                                        "snippet": r.get('body', '')
                                    })
                                    seen_urls.add(url)
                            print(f"      DuckDuckGo: found {len(text_results)} results with backend '{backend}'")
                        
                        # Be nice to the server - delay between backends
                        time.sleep(2)
                        
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "ratelimit" in error_msg or "rate limit" in error_msg:
                            print(f"      DuckDuckGo: backend '{backend}' rate limited")
                        else:
                            # Silently skip backends that don't work - no need to print error details
                            pass
                        time.sleep(1)
                        continue
                
                if all_results:
                    print(f"DuckDuckGo text: returned {len(all_results)} total results from all backends")
                    # Don't limit - return all results found
                    return all_results
        except Exception as e:
            error_msg = str(e).lower()
            if "ratelimit" in error_msg or "rate limit" in error_msg:
                print(f"DuckDuckGo rate limited for query: {query}")
            else:
                print(f"DuckDuckGo text search failed: {e}")
            return []
        
        return []


class GoogleSearchProvider:
    """Google Search via multiple free methods"""
    
    @staticmethod
    def _scrape_google_html(query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """Scrape Google search results directly from HTML (free, no API key needed)
        
        Uses modern CSS selectors based on StackOverflow best practices:
        https://stackoverflow.com/questions/38635419/searching-in-google-with-python
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            params = {
                "q": query,
                "hl": "en",
                "gl": "us",
                "num": min(num_results, 100)  # Google max is 100
            }
            
            response = requests.get("https://www.google.com/search", params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Modern Google search result containers - using current CSS selectors
            # Based on: https://stackoverflow.com/questions/38635419/searching-in-google-with-python
            for result in soup.select(".tF2Cxc, .g", limit=num_results):
                try:
                    # Find title - try multiple selectors for compatibility
                    title_elem = result.select_one(".DKV0Md, h3, .LC20lb, .DKV0Md")
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Find URL - try multiple selectors
                    link_elem = result.select_one(".yuRUbf a, a[href]")
                    if not link_elem:
                        continue
                    
                    url = link_elem.get('href', '')
                    # Clean up Google redirect URLs
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]
                        url = urllib.parse.unquote(url)
                    elif url.startswith('/url?'):
                        parsed = urlparse(url)
                        qs = parse_qs(parsed.query)
                        if 'q' in qs:
                            url = qs['q'][0]
                    
                    # Find snippet - try multiple selectors
                    snippet_elem = result.select_one(".lEBKkf span, .VwiC3b, .st, .aCOpRe")
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    if title and url and url.startswith('http'):
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet
                        })
                        
                        if len(results) >= num_results:
                            break
                except Exception as e:
                    continue  # Skip malformed results
            
            return results
        except Exception as e:
            print(f"Google HTML scrape failed: {e}")
            import traceback
            traceback.print_exc()
            return []


class BingSearchProvider:
    """Bing Search API provider"""
    
    @staticmethod
    def search(query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """Search using Bing Web Search API"""
        if not settings.BING_API_KEY:
            return []
        
        try:
            search_url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": settings.BING_API_KEY}
            params = {
                "q": query,
                "count": num_results,
                "textDecorations": False,
                "textFormat": "Raw"
            }
            
            response = requests.get(search_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            search_results = response.json()
            results = []
            for item in search_results.get("webPages", {}).get("value", []):
                results.append({
                    "title": item.get("name", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("snippet", "")
                })
            return results
        except Exception as e:
            print(f"Bing search failed: {e}")
            return []


class YouTubeSearchProvider:
    """YouTube search provider - searches YouTube for videos"""
    
    @staticmethod
    def search(query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """Search YouTube for videos"""
        try:
            url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code != 200:
                print(f"YouTube search HTTP {resp.status_code}")
                return []
            
            # Extract ytInitialData from the page
            match = re.search(r"var ytInitialData = ({.*?});</script>", resp.text, re.DOTALL)
            if not match:
                print("YouTube: ytInitialData not found")
                return []
            
            data = json.loads(match.group(1))
            
            # Navigate through YouTube's data structure
            try:
                sections = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"] \
                    ["sectionListRenderer"]["contents"]
            except (KeyError, TypeError):
                print("YouTube: Could not parse search results structure")
                return []
            
            results = []
            for section in sections:
                items = section.get("itemSectionRenderer", {}).get("contents", [])
                for item in items:
                    video = item.get("videoRenderer")
                    if video:
                        try:
                            video_id = video["videoId"]
                            title = video["title"]["runs"][0]["text"]
                            results.append({
                                "title": title,
                                "url": f"https://www.youtube.com/watch?v={video_id}",
                                "snippet": ""  # YouTube doesn't provide snippet in this format
                            })
                            if len(results) >= num_results:
                                return results
                        except (KeyError, IndexError, TypeError):
                            continue
            
            return results
        except Exception as e:
            print(f"YouTube search failed: {e}")
            return []


class SearchProvider:
    """
    Main search provider - uses YouTube for videos, DuckDuckGo for text
    
    Strategy:
    - For videos: Use YouTube search (better results)
    - For text content: Use DuckDuckGo library (DDGS)
    - For mixed/any: Use both YouTube and DuckDuckGo
    """
    
    @staticmethod
    def search(query: str, num_results: int = 10, preferred_format: str = "any", region: str = None) -> List[Dict[str, str]]:
        """
        Search using YouTube for videos, DuckDuckGo for text
        
        Args:
            query: Search query
            num_results: Maximum number of results
            preferred_format: "video", "blog", "doc", "any", or "mixed"
                - "any": fetches both videos (YouTube) and articles (DuckDuckGo)
                - "mixed": fetches both videos (YouTube) and articles (DuckDuckGo)
                - "video": fetches only videos from YouTube
                - "blog"/"doc": fetches only articles/text from DuckDuckGo
            region: Region code (optional, for DuckDuckGo)
        """
        preferred_format_lower = (preferred_format or "").lower()
        
        # For videos only: use YouTube
        if preferred_format_lower in ["video", "videos"]:
            results = YouTubeSearchProvider.search(query, num_results)
            if results:
                print(f"YouTube returned {len(results)} video results")
                return results
            print(f"YouTube search failed for query: {query}")
            return []
        
        # For mixed/any: get both YouTube videos and DuckDuckGo text
        if preferred_format_lower in ["mixed", "mix", "any"]:
            all_results = []
            
            # Get videos from YouTube (no limit - get all available)
            try:
                video_results = YouTubeSearchProvider.search(query, num_results=20)  # Get more videos
                for v in video_results:
                    v["type"] = "video"  # Mark as video
                    all_results.append(v)
                print(f"Search (mixed/any): found {len(video_results)} videos from YouTube")
            except Exception as e:
                print(f"YouTube search failed in mixed: {e}")
            
            # Add delay between YouTube and DuckDuckGo searches
            time.sleep(2)
            
            # Get articles/text from DuckDuckGo (no limit - get all available)
            try:
                # Don't limit text results - get all available
                text_results = DuckDuckGoSearchProvider.search(query, num_results=50, preferred_format="blog", region=region)
                for r in text_results:
                    r["type"] = "blog"  # Mark as article/blog
                    all_results.append(r)
                print(f"Search (mixed/any): found {len(text_results)} articles from DuckDuckGo")
            except Exception as e:
                print(f"DuckDuckGo text search failed in mixed: {e}")
            
            if all_results:
                print(f"Search (mixed/any): returned {len(all_results)} total results (videos + articles)")
                # Return all results, no limit
                return all_results
            return []
        
        # Default: text content from DuckDuckGo (for "blog", "doc", or fallback)
        results = DuckDuckGoSearchProvider.search(query, num_results, preferred_format=preferred_format, region=region)
        if results:
            print(f"DuckDuckGo returned {len(results)} text results")
            return results
        
        print(f"DuckDuckGo search failed for query: {query}")
        return []
