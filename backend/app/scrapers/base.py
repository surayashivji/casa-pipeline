from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..schemas.product import ProductCreate

class BaseScraper(ABC):
    """Base class for all retailer scrapers"""
    
    @abstractmethod
    def scrape_product(self, url: str) -> ProductCreate:
        """Scrape a single product from the given URL"""
        pass
    
    @abstractmethod
    def scrape_category(self, url: str, limit: int = 50) -> List[ProductCreate]:
        """Scrape multiple products from a category/search URL"""
        pass
    
    @abstractmethod
    def detect_url_type(self, url: str) -> str:
        """Detect if URL is product, category, search, or collection"""
        pass
