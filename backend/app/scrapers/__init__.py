# Scrapers package for Room Decorator 3D Pipeline
# This package contains all retailer-specific scrapers

from .base_scraper import BaseScraper
from .url_detector import URLDetector

# ScraperFactory will be imported when we create it in Step 5
# from .scraper_factory import ScraperFactory

__all__ = [
    'BaseScraper',
    'URLDetector'
    # 'ScraperFactory'  # Will be added in Step 5
]