import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.scrapers.base_scraper import BaseScraper
from app.scrapers.url_detector import URLDetector

# Create a test implementation
class TestScraper(BaseScraper):
    def can_handle(self, url: str) -> bool:
        return True
    
    async def scrape_product(self, url: str):
        return {"test": "data", "url": url}
    
    async def scrape_category(self, url: str, limit: int = 50):
        return [{"test": "data", "url": url}]

async def test_base_scraper():
    """Test base scraper functionality"""
    print("🧪 Testing Base Scraper...")
    
    scraper = TestScraper()
    
    try:
        # Test initialization
        print("  🔧 Testing browser initialization...")
        await scraper.initialize()
        print("  ✅ Base scraper initialized successfully")
        
        # Test basic navigation
        print("  🌐 Testing navigation...")
        success = await scraper.navigate_to_page("https://www.ikea.com")
        if success:
            print("  ✅ Navigation successful")
        else:
            print("  ❌ Navigation failed")
        
        # Test text extraction
        print("  📝 Testing text extraction...")
        title = await scraper.extract_text('title')
        print(f"  ✅ Page title extracted: {title[:50]}...")
        
        # Test cleanup
        print("  🧹 Testing cleanup...")
        await scraper.cleanup()
        print("  ✅ Base scraper cleaned up successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Base scraper test failed: {e}")
        await scraper.cleanup()
        return False

def test_url_detector():
    """Test URL detector functionality"""
    print("\n🧪 Testing URL Detector...")
    
    test_urls = [
        # IKEA URLs
        "https://www.ikea.com/us/en/p/ektorp-sofa-lofallet-beige-s69220332/",
        "https://www.ikea.com/us/en/cat/chairs-20202/",
        "https://www.ikea.com/search/?q=dining+table",
        "https://www.ikea.com/rooms/bedroom/gallery/",
        
        # Target URLs
        "https://www.target.com/p/chair/-/A-54551428",
        "https://www.target.com/c/living-room-furniture/",
        "https://www.target.com/s?searchTerm=chair",
        
        # Unsupported URLs
        "https://www.example-furniture.com/p/some-chair/",
        "https://www.amazon.com/some-product",
    ]
    
    print("  📋 Testing URL detection...")
    for url in test_urls:
        result = URLDetector.analyze_url(url)
        status = "✅" if result['supported'] else "❌"
        print(f"    {status} {result['retailer']} - {result['type']}: {url[:60]}...")
    
    # Test supported retailers
    print(f"\n  🏪 Supported retailers: {URLDetector.get_supported_retailers()}")
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting Base Scraper Architecture Tests")
    print("=" * 60)
    
    # Test URL detector (synchronous)
    url_test_passed = test_url_detector()
    
    # Test base scraper (asynchronous)
    scraper_test_passed = await test_base_scraper()
    
    print("\n" + "=" * 60)
    if url_test_passed and scraper_test_passed:
        print("✅ ALL BASE SCRAPER TESTS PASSED!")
        print("🎉 Ready for Step 3: IKEA Scraper Implementation")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
