from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, Page, Browser
from typing import Dict, Any, List, Optional
import logging
import asyncio
import time
import random

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Abstract base class for all retailer scrapers"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.timeout = 30000  # 30 seconds default timeout
        self.rate_limit_delay = 2.0  # seconds between requests
        self.last_request_time = 0
        
    async def initialize(self, headless: bool = True):
        """Initialize browser instance with realistic settings"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-gpu',
                    '--window-size=1920,1080',
                    '--disable-blink-features=AutomationControlled',
                ]
            )
            
            # Create context with realistic settings
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            )
            
            self.page = await context.new_page()
            
            # Set default timeout
            self.page.set_default_timeout(self.timeout)
            
            # Add stealth measures
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
    
    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def _respect_rate_limit(self):
        """Ensure we don't overwhelm the server"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last
            await asyncio.sleep(wait_time)
        self.last_request_time = time.time()
    
    async def _retry_request(self, func, max_retries: int = 3):
        """Retry failed requests with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Max retries exceeded for {func.__name__}: {e}")
                    raise
                
                wait_time = (2 ** attempt) * 1.0  # 1s, 2s, 4s
                await asyncio.sleep(wait_time)
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Check if this scraper can handle the given URL"""
        pass
    
    @abstractmethod
    async def scrape_product(self, url: str) -> Dict[str, Any]:
        """Scrape a single product page"""
        pass
    
    @abstractmethod
    async def scrape_category(self, url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Scrape products from a category/listing page"""
        pass
    
    async def wait_for_page_load(self):
        """Wait for page to be fully loaded with additional wait for dynamic content"""
        await self.page.wait_for_load_state('networkidle')
        # Additional wait for dynamic content
        await asyncio.sleep(random.uniform(1, 3))
    
    async def extract_text(self, selector: str, default: str = "") -> str:
        """Safely extract text from element"""
        try:
            element = await self.page.query_selector(selector)
            if element:
                text = await element.text_content()
                return text.strip() if text else default
            return default
        except:
            return default
    
    async def extract_attribute(self, selector: str, attribute: str, default: str = "") -> str:
        """Safely extract attribute from element"""
        try:
            element = await self.page.query_selector(selector)
            if element:
                value = await element.get_attribute(attribute)
                return value if value else default
            return default
        except:
            return default
    
    async def navigate_to_page(self, url: str) -> bool:
        """Navigate to URL with retry logic and rate limiting"""
        async def _navigate():
            await self._respect_rate_limit()
            await self.page.goto(url, wait_until='networkidle')
            await self.wait_for_page_load()
            return True
        
        try:
            return await self._retry_request(_navigate)
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            raise
    
    async def scroll_to_load_content(self, scrolls: int = 3):
        """Scroll page to load lazy-loaded content"""
        for i in range(scrolls):
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(random.uniform(1, 2))
    
    async def take_screenshot(self, filename: str = None):
        """Take screenshot for debugging purposes"""
        if not filename:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
        
        try:
            await self.page.screenshot(path=filename)
        except:
            pass
    
    def get_retailer_name(self) -> str:
        """Get the name of this retailer"""
        return self.__class__.__name__.replace('Scraper', '').lower()
