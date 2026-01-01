from typing import Optional, Dict
from app.config import settings
import time


class PlaywrightScraper:
    """Scraper for JavaScript-heavy pages using Playwright"""
    
    def __init__(self, timeout: int = None):
        self.timeout = timeout or (settings.SCRAPE_TIMEOUT * 2)
        self._browser = None
    
    def _get_browser(self):
        """Get or create browser instance"""
        if self._browser is None:
            try:
                from playwright.sync_api import sync_playwright
                self._playwright = sync_playwright().start()
                self._browser = self._playwright.chromium.launch(headless=True)
            except ImportError:
                raise Exception("Playwright not installed. Install with: pip install playwright && playwright install chromium")
        return self._browser
    
    def scrape(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape a JavaScript-heavy page
        
        Returns:
            Dictionary with 'title', 'content', 'html', or None if failed
        """
        try:
            browser = self._get_browser()
            page = browser.new_page()
            
            # Navigate to page
            page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
            
            # Wait a bit for dynamic content
            time.sleep(2)
            
            # Get page content
            title = page.title()
            html = page.content()
            
            # Extract text content
            content = page.evaluate("""
                () => {
                    // Remove script and style elements
                    const scripts = document.querySelectorAll('script, style, nav, header, footer');
                    scripts.forEach(el => el.remove());
                    
                    const main = document.querySelector('main') || 
                                 document.querySelector('article') || 
                                 document.querySelector('[role="main"]') ||
                                 document.body;
                    
                    return main ? main.innerText : '';
                }
            """)
            
            page.close()
            
            return {
                "title": title or url,
                "content": content,
                "html": html,
                "url": url
            }
        except Exception as e:
            print(f"Playwright scraping failed for {url}: {e}")
            return None
    
    def close(self):
        """Close browser"""
        if self._browser:
            self._browser.close()
            self._browser = None
        if hasattr(self, '_playwright'):
            self._playwright.stop()

