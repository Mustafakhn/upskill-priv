from typing import List, Dict, Optional
from app.scraping.google_search import SearchProvider
from app.scraping.scraper import WebScraper
from app.scraping.playwright_scraper import PlaywrightScraper
from app.api.v1.dao.resource_dao import ResourceDAO
from app.utils.text_utils import truncate_text, estimate_reading_time
import time


class ScrapeService:
    """Service for scraping web resources"""
    
    def __init__(self):
        self.web_scraper = WebScraper()
        self._playwright_scraper = None  # Lazy initialization
    
    def search_and_scrape(
        self,
        query: str,
        max_results: int = 10,
        use_playwright: bool = False,
        preferred_format: str = "any"
    ) -> List[Dict]:
        """
        Search for resources and scrape them
        
        Args:
            query: Search query
            max_results: Maximum number of results to scrape
            use_playwright: Whether to use Playwright for JS-heavy pages
            preferred_format: Preferred format (video, blog, doc, any, mixed)
            
        Returns:
            List of scraped resource dictionaries
        """
        try:
            print(f"[SCRAPE SERVICE] === Starting search_and_scrape ===")
            print(f"[SCRAPE SERVICE] Parameters: query='{query}', max_results={max_results}, use_playwright={use_playwright}, preferred_format='{preferred_format}'")
            
            # Search for URLs
            print(f"[SCRAPE SERVICE] Calling SearchProvider.search with query='{query}', max_results={max_results * 2}, preferred_format='{preferred_format}'")
            search_results = SearchProvider.search(query, num_results=max_results * 2, preferred_format=preferred_format)  # Get more to ensure mix
            print(f"[SCRAPE SERVICE] SearchProvider.search returned {len(search_results) if search_results else 0} results")
            
            if not search_results:
                print(f"[SCRAPE SERVICE] No search results returned, exiting early")
                return []
            
            # Log sample of results to debug
            if search_results:
                print(f"[SCRAPE SERVICE] Sample result structure: {list(search_results[0].keys()) if search_results else 'N/A'}")
                print(f"[SCRAPE SERVICE] First result type: {search_results[0].get('type', 'NO TYPE') if search_results else 'N/A'}")
            
            scraped_resources = []
            
            # For mixed/any formats, ensure we process both videos and articles
            # Separate videos and articles to ensure diversity
            if preferred_format in ["any", "mixed", "mix"]:
                videos = [r for r in search_results if r.get("type", "").lower() == "video"]
                articles = [r for r in search_results if r.get("type", "").lower() in ["blog", "article", "doc"]]
                
                # Process videos and articles separately to ensure mix
                # Take up to max_results/2 of each type (or all if fewer available)
                video_limit = min(len(videos), max(1, max_results // 2))
                article_limit = min(len(articles), max(1, max_results // 2))
                
                results_to_process = videos[:video_limit] + articles[:article_limit]
                print(f"[SCRAPE SERVICE] Separated results: {len(videos)} videos, {len(articles)} articles. Processing {video_limit} videos + {article_limit} articles = {len(results_to_process)} total")
            else:
                # For specific formats, process in order
                results_to_process = search_results[:max_results]
                print(f"[SCRAPE SERVICE] Processing {len(results_to_process)} results for format: {preferred_format}")
            
            if not results_to_process:
                print(f"[SCRAPE SERVICE] WARNING: No results to process after filtering!")
                return []
            
            print(f"[SCRAPE SERVICE] Starting to process {len(results_to_process)} resources...")
            for idx, result in enumerate(results_to_process):
                print(f"[SCRAPE SERVICE] Processing resource {idx + 1}/{len(results_to_process)}: {result.get('url', 'NO URL')[:80]}...")
                url = result.get("url", "")
                if not url:
                    continue
                
                # Check if already scraped
                existing = ResourceDAO.get_by_url(url)
                if existing:
                    scraped_resources.append(existing)
                    continue
                
                # Detect resource type - prefer the type field from SearchProvider, fallback to URL check
                result_type = result.get("type", "").lower()
                is_video = (
                    result_type == "video" or 
                    "youtube.com" in url.lower() or 
                    "youtu.be" in url.lower() or 
                    "vimeo.com" in url.lower()
                )
                
                scraped_data = None  # Initialize for delay logic
                
                # For videos: Don't scrape content, just use search result data
                if is_video:
                    resource_id = ResourceDAO.create(
                        url=url,
                        title=result.get("title", url),
                        summary=result.get("snippet", "")[:300],  # Use snippet from search
                        resource_type="video",
                        difficulty="intermediate",  # Will be refined by curation agent
                        tags=[],
                        estimated_time=0,  # Videos don't have reading time
                        source=query,
                        content=""  # Don't store content for videos
                    )
                else:
                    # For text content: Try to scrape the page
                    # Use regular scraper first (faster), then Playwright if needed
                    print(f"[SCRAPE SERVICE] Attempting to scrape article: {url[:80]}...")
                    scraped_data = None
                    
                    # Try regular scraper first (faster, works for most sites)
                    # Add timeout protection - regular scraper can also hang
                    try:
                        import threading
                        regular_result = [None]
                        regular_exception = [None]
                        
                        def scrape_regular():
                            try:
                                regular_result[0] = self._scrape_url(url, use_playwright=False)
                            except Exception as e:
                                regular_exception[0] = e
                        
                        regular_thread = threading.Thread(target=scrape_regular)
                        regular_thread.daemon = True
                        regular_thread.start()
                        regular_thread.join(timeout=30)  # 30 second timeout for regular scraper
                        
                        if regular_thread.is_alive():
                            print(f"[SCRAPE SERVICE] Regular scraper timed out for {url[:60]}...")
                            regular_data = None
                        elif regular_exception[0]:
                            raise regular_exception[0]
                        else:
                            regular_data = regular_result[0]
                        
                        if regular_data and len(regular_data.get("content", "")) >= 200:
                            scraped_data = regular_data
                            print(f"[SCRAPE SERVICE] Successfully scraped with regular scraper: {url[:60]}... ({len(scraped_data.get('content', ''))} chars)")
                    except Exception as e:
                        print(f"[SCRAPE SERVICE] Regular scraper failed for {url[:60]}...: {str(e)[:100]}")
                    
                    # Only try Playwright if regular scraper failed or returned minimal content
                    if (not scraped_data or len(scraped_data.get("content", "")) < 200) and use_playwright:
                        try:
                            print(f"[SCRAPE SERVICE] Trying Playwright for {url[:60]}...")
                            playwright_data = self._scrape_url(url, use_playwright=True)
                            if playwright_data and len(playwright_data.get("content", "")) > len(scraped_data.get("content", "") if scraped_data else ""):
                                scraped_data = playwright_data
                                print(f"[SCRAPE SERVICE] Successfully scraped with Playwright: {url[:60]}... ({len(scraped_data.get('content', ''))} chars)")
                        except Exception as e:
                            print(f"[SCRAPE SERVICE] Playwright scraper failed for {url[:60]}...: {str(e)[:100]}")
                    
                    # If scraping fails, use search result data as fallback (like videos)
                    if not scraped_data or len(scraped_data.get("content", "")) < 100:
                        print(f"[SCRAPE SERVICE] Using fallback (snippet only) for {url[:80]}...")
                        # Fallback: Create resource from search result data
                        # This ensures articles/blogs are not skipped when scraping fails
                        resource_id = ResourceDAO.create(
                            url=url,
                            title=result.get("title", url),
                            summary=result.get("snippet", "")[:300],  # Use snippet from search
                            resource_type="blog",  # Default to blog for text content
                            difficulty="intermediate",  # Will be refined by curation agent
                            tags=[],
                            estimated_time=0,  # Can't estimate without content
                            source=query,
                            content=""  # No content available
                        )
                    else:
                        # Scraping succeeded - use scraped data
                        # Save raw HTML
                        ResourceDAO.save_raw_scrape(url, scraped_data["html"])
                        
                        # Create resource with scraped content
                        resource_type = self.web_scraper.detect_type(url, scraped_data.get("content", ""))
                        estimated_time = estimate_reading_time(scraped_data.get("content", ""))
                        
                        resource_id = ResourceDAO.create(
                            url=url,
                            title=scraped_data.get("title", result.get("title", url)),
                            summary=truncate_text(scraped_data.get("content", result.get("snippet", "")), 300),
                            resource_type=resource_type,
                            difficulty="intermediate",  # Will be refined by curation agent
                            tags=[],
                            estimated_time=estimated_time,
                            source=query,
                            content=scraped_data.get("content", "")
                        )
                
                resource = ResourceDAO.get_by_id(resource_id)
                if resource:
                    scraped_resources.append(resource)
                
                # Be polite - shorter delay between scraping individual pages (skip delay for videos)
                # Only delay if we actually attempted scraping and succeeded (not for videos or failed scrapes)
                if not is_video and scraped_data:
                    time.sleep(1)  # Reduced from 3 to 1 second to speed up processing
                
                print(f"[SCRAPE SERVICE] Completed processing resource {idx + 1}/{len(results_to_process)}")
            
            print(f"[SCRAPE SERVICE] === Finished search_and_scrape: {len(scraped_resources)} resources ===\n")
            return scraped_resources
        
        except Exception as e:
            print(f"[SCRAPE SERVICE] ERROR in search_and_scrape: {str(e)}")
            import traceback
            traceback.print_exc()
            return scraped_resources if 'scraped_resources' in locals() else []
    
    def _scrape_url(self, url: str, use_playwright: bool = False) -> Optional[Dict]:
        """Scrape a single URL with timeout protection"""
        if use_playwright:
            # Try Playwright for better content extraction (especially for JS-heavy sites)
            if self._playwright_scraper is None:
                self._playwright_scraper = PlaywrightScraper()
            
            try:
                # Add timeout protection - Playwright can hang
                import threading
                
                result = [None]
                exception = [None]
                
                def scrape_with_timeout():
                    try:
                        result[0] = self._playwright_scraper.scrape(url)
                    except Exception as e:
                        exception[0] = e
                
                thread = threading.Thread(target=scrape_with_timeout)
                thread.daemon = True
                thread.start()
                thread.join(timeout=15)  # 15 second timeout for Playwright
                
                if thread.is_alive():
                    print(f"[SCRAPE SERVICE] Playwright scraping timed out for {url[:60]}...")
                    return None
                
                if exception[0]:
                    raise exception[0]
                
                playwright_data = result[0]
                if playwright_data and len(playwright_data.get("content", "")) > 200:
                    return playwright_data
            except Exception as e:
                print(f"[SCRAPE SERVICE] Playwright scraping failed for {url[:60]}...: {str(e)[:100]}")
        
        # Regular scraper (faster, works for most sites)
        try:
            scraped_data = self.web_scraper.scrape(url)
            if scraped_data and len(scraped_data.get("content", "")) > 200:
                return scraped_data
        except Exception as e:
            print(f"[SCRAPE SERVICE] Regular scraping failed for {url[:60]}...: {str(e)[:100]}")
        
        return None
    
    def scrape_multiple_queries(self, queries: List[str], max_per_query: int = 5, preferred_format: str = "any") -> List[Dict]:
        """Scrape resources for multiple search queries with conservative rate limiting"""
        all_resources = []
        seen_urls = set()
        
        # Run all generated queries (no limit)
        print(f"[SCRAPE SERVICE] Will execute {len(queries)} queries (all generated queries)")
        
        for idx, query in enumerate(queries):
            # Add significant delay between queries to avoid rate limiting
            if idx > 0:
                delay = 10  # 10 seconds between queries
                print(f"[SCRAPE SERVICE] Waiting {delay} seconds before next query to avoid rate limits...")
                time.sleep(delay)
            
            print(f"[SCRAPE SERVICE] Searching for query {idx + 1}/{len(queries)}: '{query}' (format: {preferred_format})")
            resources = self.search_and_scrape(query, max_results=max_per_query, use_playwright=True, preferred_format=preferred_format)
            
            for resource in resources:
                url = resource.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_resources.append(resource)
        
        print(f"[SCRAPE SERVICE] Total resources found: {len(all_resources)}")
        return all_resources

