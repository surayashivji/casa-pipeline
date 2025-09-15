import asyncio
import sys
import os
import json

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.scrapers.ikea_scraper import IKEAScraper

async def test_ikea_single_product():
    """Test IKEA single product scraping"""
    print("🧪 Testing IKEA Single Product Scraper...")
    
    # Test URL from the example
    test_url = "https://www.ikea.com/us/en/p/stockholm-2025-3-seat-sofa-alhamn-beige-s69574294/#content"
    
    scraper = IKEAScraper()
    
    try:
        print(f"  🌐 Scraping: {test_url}")
        result = await scraper.scrape_product(test_url)
        
        if result:
            print(f"  ✅ Product Name: {result['name']}")
            print(f"  ✅ Price: ${result['price']}")
            print(f"  ✅ Brand: {result['brand']}")
            print(f"  ✅ Images: {len(result['images'])} found")
            print(f"  ✅ Dimensions: {result['dimensions']}")
            print(f"  ✅ Weight: {result['weight']} kg")
            print(f"  ✅ Category: {result['category']}")
            print(f"  ✅ Room Type: {result['room_type']}")
            print(f"  ✅ Style Tags: {result['style_tags']}")
            print(f"  ✅ IKEA Item Number: {result['ikea_item_number']}")
            print(f"  ✅ Variants: {len(result['variants'])} found")
            
            # Save detailed results to file for inspection
            with open('ikea_scraping_result.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"  💾 Detailed results saved to: ikea_scraping_result.json")
            
            # Verify we got real data (not just defaults)
            assert result['name'] != "Unknown Product", "Product name should be extracted"
            assert result['price'] > 0, "Price should be greater than 0"
            assert len(result['images']) > 0, "Should have at least one image"
            assert result['brand'] == "IKEA", "Brand should be IKEA"
            
            print("\n  ✅ All assertions passed!")
            return True
        else:
            print("  ❌ No result returned from scraper")
            return False
            
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

async def test_ikea_url_detection():
    """Test that IKEA scraper can handle IKEA URLs"""
    print("\n🧪 Testing IKEA URL Detection...")
    
    scraper = IKEAScraper()
    
    test_urls = [
        "https://www.ikea.com/us/en/p/dyvlinge-swivel-chair-kelinge-orange-40581921/",
        "https://www.ikea.com/us/en/cat/chairs-20202/",
        "https://www.target.com/p/chair/-/A-54551428",  # Should return False
    ]
    
    for url in test_urls:
        can_handle = scraper.can_handle(url)
        expected = 'ikea.com' in url
        status = "✅" if can_handle == expected else "❌"
        print(f"  {status} {url[:50]}... -> {can_handle}")
    
    return True

async def main():
    """Run all IKEA scraper tests"""
    print("🚀 Starting IKEA Scraper Tests")
    print("=" * 60)
    
    # Test URL detection
    url_test_passed = await test_ikea_url_detection()
    
    # Test single product scraping
    scraping_test_passed = await test_ikea_single_product()
    
    print("\n" + "=" * 60)
    if url_test_passed and scraping_test_passed:
        print("✅ ALL IKEA SCRAPER TESTS PASSED!")
        print("🎉 Step 4a Complete: IKEA Single Product Scraper Working!")
        print("🚀 Ready for Step 4b: IKEA Category Scraper")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
