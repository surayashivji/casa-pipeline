from abc import ABC, abstractmethod
from typing import List
from ..schemas.product import ProductCreate

class BaseScraper(ABC):
    """Base class for all retailer scrapers"""
    
    @abstractmethod
    def detect_url_type(self, url: str) -> str:
        """Detect URL type: product, category, search, collection"""
        pass
    
    @abstractmethod
    def scrape_product(self, url: str) -> ProductCreate:
        """Scrape a single product"""
        pass
    
    @abstractmethod
    def scrape_category(self, url: str, limit: int = 50) -> List[ProductCreate]:
        """Scrape a category page"""
        pass