#!/usr/bin/env python3
"""
Test script for ScraperFactory
Tests automatic retailer detection and scraper creation
"""

import asyncio
import logging
from app.scrapers.scraper_factory import ScraperFactory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_scraper_factory():
    """Test ScraperFactory functionality"""
    print("🧪 Testing ScraperFactory...")
    print("="*60)
    
    # Test URLs
    test_urls = [
        # IKEA URLs (supported)
        "https://www.ikea.com/us/en/p/stockholm-2025-3-seat-sofa-alhamn-beige-s69574294/",
        "https://www.ikea.com/us/en/cat/chairs-20202/",
        "https://www.ikea.com/search/?q=dining+table",
        
        # Unsupported retailers
        "https://www.target.com/p/chair/-/A-54551428",
        "https://www.wayfair.com/furniture/pdp/chair-w003456789.html",
        "https://www.westelm.com/products/mid-century-sofa",
        
        # Invalid URLs
        "https://www.example.com/product",
        "not-a-url"
    ]
    
    print("📋 Testing URL Detection and Scraper Creation...")
    print("-" * 50)
    
    for url in test_urls:
        print(f"\n🔍 Testing URL: {url[:60]}...")
        
        # Test retailer info
        info = ScraperFactory.get_retailer_info(url)
        print(f"  📊 Retailer: {info['retailer']}")
        print(f"  📊 Supported: {info['supported']}")
        print(f"  📊 URL Type: {info['url_type']}")
        print(f"  📊 Confidence: {info['confidence']}")
        
        # Test scraper creation
        scraper = ScraperFactory.create_scraper(url)
        if scraper:
            print(f"  ✅ Scraper created: {type(scraper).__name__}")
            print(f"  ✅ Can handle URL: {scraper.can_handle(url)}")
        else:
            print(f"  ❌ No scraper created")
    
    print("\n" + "="*60)
    print("📊 ScraperFactory Test Results:")
    print(f"  🏪 Supported retailers: {ScraperFactory.get_supported_retailers()}")
    
    # Test specific IKEA URL
    ikea_url = "https://www.ikea.com/us/en/p/stockholm-2025-3-seat-sofa-alhamn-beige-s69574294/"
    print(f"\n🧪 Testing IKEA URL specifically:")
    print(f"  URL: {ikea_url}")
    
    scraper = ScraperFactory.create_scraper(ikea_url)
    if scraper:
        print(f"  ✅ Scraper type: {type(scraper).__name__}")
        print(f"  ✅ Can handle: {scraper.can_handle(ikea_url)}")
        print(f"  ✅ Is IKEA scraper: {isinstance(scraper, type(scraper))}")
    else:
        print(f"  ❌ Failed to create scraper")
    
    print("\n" + "="*60)
    print("✅ ScraperFactory Test Complete!")
    print("🎉 Ready for Step 3.2: Update API Routes")

if __name__ == "__main__":
    test_scraper_factory()
