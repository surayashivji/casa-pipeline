"""
ScraperFactory for Room Decorator 3D Pipeline
Automatically detects retailers and returns appropriate scrapers
"""

import logging
from typing import Optional, Dict, Any
from .base_scraper import BaseScraper
from .url_detector import URLDetector
from .ikea_scraper import IKEAScraper

logger = logging.getLogger(__name__)

class ScraperFactory:
    """Factory class for creating appropriate scrapers based on URL"""
    
    # Registry of available scrapers
    _scrapers: Dict[str, type] = {
        'ikea': IKEAScraper,
        # Future scrapers will be added here
        # 'target': TargetScraper,
        # 'wayfair': WayfairScraper,
        # 'westelm': WestElmScraper,
        # 'cb2': CB2Scraper,
        # 'urbanoutfitters': UrbanOutfittersScraper,
        # 'homegoods': HomeGoodsScraper,
        # 'worldmarket': WorldMarketScraper
    }
    
    @classmethod
    def create_scraper(cls, url: str) -> Optional[BaseScraper]:
        """
        Create appropriate scraper based on URL
        
        Args:
            url: Product or category URL to scrape
            
        Returns:
            Scraper instance or None if unsupported retailer
        """
        try:
            # Detect retailer from URL
            analysis = URLDetector.analyze_url(url)
            retailer = analysis.get('retailer', '').lower()
            
            if not retailer:
                logger.warning(f"Could not detect retailer from URL: {url}")
                return None
            
            # Check if we have a scraper for this retailer
            if retailer not in cls._scrapers:
                logger.warning(f"No scraper available for retailer: {retailer}")
                return None
            
            # Create scraper instance
            scraper_class = cls._scrapers[retailer]
            scraper = scraper_class()
            
            logger.info(f"Created {retailer} scraper for URL: {url}")
            return scraper
            
        except Exception as e:
            logger.error(f"Error creating scraper for URL {url}: {e}")
            return None
    
    @classmethod
    def get_supported_retailers(cls) -> list:
        """Get list of supported retailers"""
        return list(cls._scrapers.keys())
    
    @classmethod
    def is_supported(cls, url: str) -> bool:
        """Check if URL is supported by any scraper"""
        analysis = URLDetector.analyze_url(url)
        retailer = analysis.get('retailer', '').lower()
        return retailer in cls._scrapers
    
    @classmethod
    def get_retailer_info(cls, url: str) -> Dict[str, Any]:
        """Get detailed information about the retailer for a URL"""
        analysis = URLDetector.analyze_url(url)
        retailer = analysis.get('retailer', '').lower()
        
        return {
            'url': url,
            'retailer': retailer,
            'supported': retailer in cls._scrapers,
            'scraper_available': retailer in cls._scrapers,
            'url_type': analysis.get('type', 'unknown'),
            'confidence': analysis.get('confidence', 0)
        }
