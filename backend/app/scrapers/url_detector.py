from typing import Dict, Optional
from urllib.parse import urlparse
import re
import logging

logger = logging.getLogger(__name__)

class URLDetector:
    """Detect retailer and URL type from URLs"""
    
    # Retailer patterns
    RETAILER_PATTERNS = {
        'ikea': [
            r'ikea\.com',
        ],
        'target': [
            r'target\.com',
        ],
        'wayfair': [
            r'wayfair\.com',
        ],
        'westelm': [
            r'westelm\.com',
        ],
        'cb2': [
            r'cb2\.com',
        ],
        'urbanoutfitters': [
            r'urbanoutfitters\.com',
        ],
        'homegoods': [
            r'homegoods\.com',
        ],
        'worldmarket': [
            r'worldmarket\.com',
        ]
    }
    
    # URL type patterns for each retailer
    URL_TYPE_PATTERNS = {
        'ikea': {
            'product': [r'/p/', r'/products/'],
            'category': [r'/cat/', r'/category/'],
            'search': [r'/search/'],
            'room': [r'/rooms/']
        },
        'target': {
            'product': [r'/p/', r'/-/A-\d+'],
            'category': [r'/c/', r'/category/'],
            'search': [r'/s\?', r'/search']
        },
        'wayfair': {
            'product': [r'/p/', r'/product/'],
            'category': [r'/category/', r'/c/'],
            'search': [r'/s\?', r'/search']
        },
        'westelm': {
            'product': [r'/products/', r'/p/'],
            'category': [r'/category/', r'/shop/'],
            'search': [r'/search', r'/s\?']
        },
        'default': {
            'product': [r'/product/', r'/p/', r'/item/'],
            'category': [r'/category/', r'/cat/', r'/collection/'],
            'search': [r'/search', r'/s\?']
        }
    }
    
    @classmethod
    def detect_retailer(cls, url: str) -> Optional[str]:
        """Detect which retailer this URL belongs to"""
        if not url:
            return None
            
        url_lower = url.lower()
        
        for retailer, patterns in cls.RETAILER_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    logger.debug(f"Detected retailer '{retailer}' for URL: {url}")
                    return retailer
        
        logger.warning(f"No retailer detected for URL: {url}")
        return None
    
    @classmethod
    def detect_url_type(cls, url: str, retailer: Optional[str] = None) -> str:
        """Detect if URL is product, category, search, or room"""
        if not url:
            return 'unknown'
            
        if not retailer:
            retailer = cls.detect_retailer(url)
        
        # Get patterns for this retailer (or default)
        patterns = cls.URL_TYPE_PATTERNS.get(retailer, cls.URL_TYPE_PATTERNS['default'])
        
        # Check each type
        for url_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, url):
                    logger.debug(f"Detected URL type '{url_type}' for {retailer}: {url}")
                    return url_type
        
        # Default to 'unknown' if no pattern matches
        logger.warning(f"Unknown URL type for {retailer}: {url}")
        return 'unknown'
    
    @classmethod
    def analyze_url(cls, url: str) -> Dict[str, str]:
        """Full URL analysis"""
        retailer = cls.detect_retailer(url)
        url_type = cls.detect_url_type(url, retailer)
        
        # Determine if supported (has retailer and recognizable type)
        supported = retailer is not None and url_type != 'unknown'
        
        result = {
            'url': url,
            'retailer': retailer or 'unknown',
            'type': url_type,
            'supported': supported
        }
        
        logger.info(f"URL analysis: {result}")
        return result
    
    @classmethod
    def get_supported_retailers(cls) -> list:
        """Get list of all supported retailers"""
        return list(cls.RETAILER_PATTERNS.keys())
    
    @classmethod
    def is_retailer_supported(cls, retailer: str) -> bool:
        """Check if a specific retailer is supported"""
        return retailer in cls.RETAILER_PATTERNS
    
    @classmethod
    def is_url_supported(cls, url: str) -> bool:
        """Check if URL is from a supported retailer with recognizable type"""
        analysis = cls.analyze_url(url)
        return analysis['supported']
