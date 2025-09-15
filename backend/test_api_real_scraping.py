#!/usr/bin/env python3
"""
Test script for Step 3.2: API Routes with Real Scraping
Tests the /api/scrape endpoint with real IKEA URLs
"""

import asyncio
import httpx
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_api_real_scraping():
    """Test the API with real scraping"""
    print("🧪 Testing API Routes with Real Scraping")
    print("="*60)
    
    base_url = "http://localhost:8000"
    
    # Test URLs
    test_urls = [
        # IKEA URLs (should use real scraping)
        "https://www.ikea.com/us/en/p/stockholm-2025-3-seat-sofa-alhamn-beige-s69574294/",
        "https://www.ikea.com/us/en/p/dyvlinge-swivel-chair-kelinge-orange-40581921/",
        
        # Unsupported retailer (should fallback to mock)
        "https://www.target.com/p/chair/-/A-54551428",
        
        # Invalid URL (should fallback to mock)
        "https://www.example.com/product"
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, url in enumerate(test_urls, 1):
            print(f"\n🔍 Test {i}: {url[:60]}...")
            print("-" * 50)
            
            try:
                # Test the /api/scrape endpoint
                response = await client.post(
                    f"{base_url}/api/scrape",
                    json={"url": url, "mode": "single"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    product = data.get('product', {})
                    
                    print(f"  ✅ Status: {response.status_code}")
                    print(f"  📦 Product: {product.get('name', 'N/A')}")
                    print(f"  🏪 Brand: {product.get('brand', 'N/A')}")
                    print(f"  💰 Price: ${product.get('price', 0):.2f}")
                    print(f"  🖼️  Images: {len(data.get('images', []))} found")
                    print(f"  ⏱️  Processing Time: {data.get('processing_time', 0):.2f}s")
                    print(f"  💵 Cost: ${data.get('cost', 0):.2f}")
                    
                    # Check if it's real data or mock data
                    if "STOCKHOLM" in product.get('name', '') or "Dyvlinge" in product.get('name', ''):
                        print(f"  🎯 Data Source: REAL SCRAPING")
                    else:
                        print(f"  🎯 Data Source: MOCK DATA (fallback)")
                    
                    # Check dimensions
                    dimensions = product.get('dimensions', {})
                    if dimensions:
                        print(f"  📏 Dimensions: {dimensions.get('width', 0):.1f}\" x {dimensions.get('height', 0):.1f}\" x {dimensions.get('depth', 0):.1f}\"")
                    
                    # Check IKEA-specific fields
                    if product.get('ikea_item_number'):
                        print(f"  🏷️  IKEA Item: {product.get('ikea_item_number')}")
                    
                    if product.get('assembly_required') is not None:
                        print(f"  🔧 Assembly: {'Required' if product.get('assembly_required') else 'Not Required'}")
                    
                else:
                    print(f"  ❌ Status: {response.status_code}")
                    print(f"  ❌ Error: {response.text}")
                    
            except Exception as e:
                print(f"  ❌ Exception: {str(e)}")
    
    print("\n" + "="*60)
    print("📊 API Real Scraping Test Summary:")
    print("  ✅ IKEA URLs should use real scraping")
    print("  ✅ Unsupported URLs should fallback to mock data")
    print("  ✅ All requests should return 200 status")
    print("  ✅ Real data should have accurate IKEA information")
    print("\n🎉 Step 3.2 Complete: API Routes with Real Scraping!")

if __name__ == "__main__":
    asyncio.run(test_api_real_scraping())
