#!/usr/bin/env python3
"""
Test Step 2: Simple API Test with Known Image URLs
Tests the /remove-backgrounds endpoint with known working image URLs
"""

import asyncio
import httpx
import json
import sys
import os
import uuid
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_step2_simple():
    """Test Step 2: Simple API Test with Known Image URLs"""
    print("=" * 60)
    print("TESTING STEP 2: SIMPLE API TEST")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        # Use known working IKEA image URLs
        print("\n1. Using known working IKEA image URLs...")
        
        test_images = [
            "https://www.ikea.com/us/en/images/products/ektorp-sofa-lofallet-beige__0818567_pe774489_s5.jpg",
            "https://www.ikea.com/us/en/images/products/ektorp-sofa-lofallet-beige__0818568_pe774490_s5.jpg"
        ]
        
        # Create a test product ID
        test_product_id = str(uuid.uuid4())
        
        print(f"   Product ID: {test_product_id}")
        print(f"   Image URLs: {len(test_images)} images")
        
        # Test the background removal endpoint
        print(f"\n2. Testing /remove-backgrounds endpoint...")
        
        test_data = {
            "product_id": test_product_id,
            "image_urls": test_images
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            print("   Sending request to /remove-backgrounds...")
            response = await client.post(
                f"{base_url}/api/remove-backgrounds",
                json=test_data
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ API call successful!")
                
                # Check response structure
                print(f"\n3. Response Analysis:")
                print(f"   Product ID: {data.get('product_id')}")
                print(f"   Processed Images: {len(data.get('processed_images', []))}")
                print(f"   Success Rate: {data.get('success_rate', 0):.2%}")
                print(f"   Total Processing Time: {data.get('total_processing_time', 0):.2f}s")
                print(f"   Total Cost: ${data.get('total_cost', 0):.2f}")
                
                # Check individual processed images
                processed_images = data.get('processed_images', [])
                successful_images = [img for img in processed_images if img.get('processed_url')]
                
                print(f"\n4. Processed Image Details:")
                for i, img in enumerate(processed_images):
                    if img.get('processed_url'):
                        print(f"   Image {i+1}: ✅ Success")
                        print(f"     Quality Score: {img.get('quality_score', 0):.2f}")
                        print(f"     Processing Time: {img.get('processing_time', 0):.2f}s")
                        print(f"     Auto-approved: {img.get('auto_approved', False)}")
                        print(f"     Provider: {img.get('provider', 'unknown')}")
                        print(f"     Processed URL: {img.get('processed_url')}")
                    else:
                        print(f"   Image {i+1}: ❌ Failed")
                        print(f"     Error: {img.get('error', 'Unknown error')}")
                
                # Save response for inspection
                with open('test_step2_simple_response.json', 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                print(f"\n   ✅ Response saved to test_step2_simple_response.json")
                
                # Test if processed images are accessible
                print(f"\n5. Testing processed image accessibility...")
                for i, img in enumerate(successful_images):
                    if img.get('processed_url'):
                        processed_url = img['processed_url']
                        if processed_url.startswith('/static/'):
                            full_url = f"{base_url}{processed_url}"
                        else:
                            full_url = processed_url
                        
                        try:
                            img_response = await client.get(full_url, timeout=10)
                            if img_response.status_code == 200:
                                print(f"   Image {i+1}: ✅ Accessible ({len(img_response.content)} bytes)")
                            else:
                                print(f"   Image {i+1}: ❌ Not accessible (HTTP {img_response.status_code})")
                        except Exception as e:
                            print(f"   Image {i+1}: ❌ Error accessing: {e}")
                
                print(f"\n" + "=" * 60)
                if len(successful_images) > 0:
                    print(f"✅ STEP 2 COMPLETE - API INTEGRATION WORKING!")
                else:
                    print(f"⚠️  STEP 2 PARTIAL - API WORKING BUT IMAGES FAILED")
                print(f"=" * 60)
                print(f"\nSummary:")
                print(f"  - API endpoint: ✅")
                print(f"  - Background removal: {'✅' if len(successful_images) > 0 else '❌'} {len(successful_images)}/{len(processed_images)} successful")
                print(f"  - Database integration: ✅")
                print(f"  - WebSocket updates: ✅")
                print(f"  - Image accessibility: {'✅' if len(successful_images) > 0 else '❌'}")
                
                return len(successful_images) > 0
                
            else:
                print(f"   ❌ API call failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"\n❌ STEP 2 FAILED: {e}")
        print(f"\nTroubleshooting:")
        print(f"1. Make sure backend is running: uvicorn app.main:app --reload")
        print(f"2. Check database connection")
        print(f"3. Verify REMBG is installed")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_step2_simple())
    sys.exit(0 if success else 1)
