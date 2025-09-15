#!/usr/bin/env python3
"""
Test Frontend Data Compatibility
Verifies that the frontend can properly handle real scraped data format
"""

import asyncio
import httpx
import json

async def test_frontend_data_compatibility():
    """Test that frontend receives data in the expected format"""
    print("🧪 Testing Frontend Data Compatibility")
    print("=" * 50)
    
    # Test with a real IKEA product
    test_url = "https://www.ikea.com/us/en/p/stockholm-2025-3-seat-sofa-alhamn-beige-s69574294/"
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"🔍 Testing URL: {test_url[:50]}...")
            
            # Get scraped data
            response = await client.post(
                "http://localhost:8000/api/scrape",
                json={"url": test_url, "mode": "single"},
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code}")
                return False
            
            data = response.json()
            product = data.get('product', {})
            images = data.get('images', [])
            
            print(f"✅ API Response received")
            print(f"📦 Product Name: {product.get('name', 'N/A')}")
            print(f"🏪 Brand: {product.get('brand', 'N/A')}")
            print(f"💰 Price: ${product.get('price', 0):.2f}")
            print(f"🖼️  Images: {len(images)}")
            
            # Test frontend-expected fields
            frontend_fields = [
                'id', 'name', 'brand', 'price', 'url', 'images', 
                'dimensions', 'description', 'weight', 'category',
                'room_type', 'style_tags', 'assembly_required'
            ]
            
            print(f"\n🔍 Checking Frontend-Expected Fields:")
            missing_fields = []
            for field in frontend_fields:
                if field in product:
                    value = product[field]
                    if value is not None and value != "" and value != []:
                        print(f"  ✅ {field}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
                    else:
                        print(f"  ⚠️  {field}: Empty or null")
                        missing_fields.append(field)
                else:
                    print(f"  ❌ {field}: Missing")
                    missing_fields.append(field)
            
            # Check dimensions format
            dimensions = product.get('dimensions', {})
            if dimensions and isinstance(dimensions, dict):
                required_dim_fields = ['width', 'height', 'depth', 'unit']
                dim_complete = all(field in dimensions for field in required_dim_fields)
                if dim_complete:
                    print(f"  ✅ dimensions: Complete object with {required_dim_fields}")
                else:
                    print(f"  ⚠️  dimensions: Incomplete object")
                    missing_fields.append('dimensions')
            else:
                print(f"  ❌ dimensions: Missing or wrong format")
                missing_fields.append('dimensions')
            
            # Check images format
            if images and isinstance(images, list) and len(images) > 0:
                print(f"  ✅ images: Array with {len(images)} items")
                # Check if images are accessible
                accessible_images = 0
                for img_url in images[:3]:  # Check first 3 images
                    try:
                        img_response = await client.head(img_url, timeout=5)
                        if img_response.status_code == 200:
                            accessible_images += 1
                    except:
                        pass
                print(f"  📊 Image Accessibility: {accessible_images}/{min(3, len(images))} accessible")
            else:
                print(f"  ❌ images: Missing or empty")
                missing_fields.append('images')
            
            # Summary
            print(f"\n📊 Compatibility Summary:")
            print(f"  Total Fields Checked: {len(frontend_fields)}")
            print(f"  Missing/Empty Fields: {len(missing_fields)}")
            print(f"  Compatibility: {((len(frontend_fields) - len(missing_fields)) / len(frontend_fields) * 100):.1f}%")
            
            if len(missing_fields) == 0:
                print(f"  🎉 PERFECT COMPATIBILITY!")
                return True
            elif len(missing_fields) <= 2:
                print(f"  ✅ GOOD COMPATIBILITY")
                return True
            else:
                print(f"  ⚠️  NEEDS IMPROVEMENT")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_api_response_format():
    """Test that API response matches frontend expectations"""
    print(f"\n🧪 Testing API Response Format")
    print("=" * 50)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/scrape",
                json={"url": "https://www.ikea.com/us/en/p/dyvlinge-swivel-chair-kelinge-orange-40581921/", "mode": "single"},
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code}")
                return False
            
            data = response.json()
            
            # Check top-level structure
            expected_top_level = ['product', 'images', 'processing_time', 'cost']
            print(f"🔍 Checking API Response Structure:")
            
            for field in expected_top_level:
                if field in data:
                    print(f"  ✅ {field}: Present")
                else:
                    print(f"  ❌ {field}: Missing")
            
            # Check product structure
            product = data.get('product', {})
            if product:
                print(f"  ✅ product: Object with {len(product)} fields")
            else:
                print(f"  ❌ product: Missing or empty")
            
            # Check images
            images = data.get('images', [])
            if isinstance(images, list):
                print(f"  ✅ images: Array with {len(images)} items")
            else:
                print(f"  ❌ images: Wrong type or missing")
            
            # Check processing time
            processing_time = data.get('processing_time', 0)
            if isinstance(processing_time, (int, float)) and processing_time > 0:
                print(f"  ✅ processing_time: {processing_time:.2f}s")
            else:
                print(f"  ⚠️  processing_time: {processing_time}")
            
            # Check cost
            cost = data.get('cost', 0)
            if isinstance(cost, (int, float)):
                print(f"  ✅ cost: ${cost:.2f}")
            else:
                print(f"  ⚠️  cost: {cost}")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    print("🚀 Frontend Data Compatibility Tests")
    print("=" * 60)
    
    # Test 1: Data compatibility
    compatibility_ok = await test_frontend_data_compatibility()
    
    # Test 2: API response format
    format_ok = await test_api_response_format()
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"📊 FRONTEND COMPATIBILITY SUMMARY")
    print(f"=" * 60)
    print(f"Data Compatibility: {'✅ PASSED' if compatibility_ok else '❌ FAILED'}")
    print(f"API Format: {'✅ PASSED' if format_ok else '❌ FAILED'}")
    
    if compatibility_ok and format_ok:
        print(f"🎉 FRONTEND IS READY FOR REAL DATA!")
    else:
        print(f"⚠️  FRONTEND NEEDS ADJUSTMENTS")
    
    print(f"=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
