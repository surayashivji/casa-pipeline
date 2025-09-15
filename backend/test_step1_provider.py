#!/usr/bin/env python3
"""
Test Step 1: Provider Architecture
Tests the background removal service with provider pattern
"""

import asyncio
import sys
import os
import logging

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.background_removal.manager import BackgroundRemovalManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_step1():
    """Test Step 1: Provider Architecture"""
    print("=" * 60)
    print("TESTING STEP 1: PROVIDER ARCHITECTURE")
    print("=" * 60)
    
    try:
        # Initialize manager
        print("\n1. Initializing BackgroundRemovalManager...")
        manager = BackgroundRemovalManager()
        print("✅ Manager initialized successfully")
        
        # Check provider info
        print("\n2. Checking available providers...")
        provider_info = manager.get_provider_info()
        for info in provider_info:
            print(f"   Provider: {info['name']}")
            print(f"   Available: {info['available']}")
            print(f"   Cost per image: ${info['cost_per_image']:.2f}")
        
        if not provider_info:
            print("❌ No providers available - check REMBG installation")
            return False
        
        # Test with real IKEA image
        print("\n3. Testing with real IKEA image...")
        test_url = "https://www.ikea.com/us/en/images/products/ektorp-sofa-lofallet-beige__0818567_pe774489_s5.jpg"
        print(f"   Test URL: {test_url}")
        
        result = await manager.process_image(
            image_url=test_url,
            product_id="test_123",
            image_order=0
        )
        
        # Check results
        print(f"\n4. Processing Results:")
        print(f"   Success: {result.get('success')}")
        print(f"   Quality Score: {result.get('quality_score', 0):.2f}")
        print(f"   Provider: {result.get('provider')}")
        print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
        print(f"   Cost: ${result.get('cost', 0):.2f}")
        
        if result.get('success'):
            print(f"   Processed URL: {result.get('processed_url')}")
            print(f"   Local Path: {result.get('local_path')}")
            
            # Check if file exists
            if result.get('local_path'):
                if os.path.exists(result['local_path']):
                    file_size = os.path.getsize(result['local_path'])
                    print(f"   ✅ File exists: {file_size} bytes")
                else:
                    print(f"   ❌ File not found: {result['local_path']}")
        else:
            print(f"   ❌ Processing failed: {result.get('error')}")
            return False
        
        # Test batch processing
        print(f"\n5. Testing batch processing...")
        test_urls = [
            "https://www.ikea.com/us/en/images/products/ektorp-sofa-lofallet-beige__0818567_pe774489_s5.jpg",
            "https://www.ikea.com/us/en/images/products/ektorp-sofa-lofallet-beige__0818568_pe774490_s5.jpg"
        ]
        
        batch_results = await manager.process_batch(
            image_urls=test_urls,
            product_id="test_batch_123",
            max_concurrent=2
        )
        
        successful = sum(1 for r in batch_results if r.get('success'))
        print(f"   Batch Results: {successful}/{len(batch_results)} successful")
        
        for i, result in enumerate(batch_results):
            status = "✅" if result.get('success') else "❌"
            quality = result.get('quality_score', 0)
            print(f"   Image {i+1}: {status} Quality: {quality:.2f}")
        
        print(f"\n" + "=" * 60)
        print(f"✅ STEP 1 COMPLETE - ALL TESTS PASSED!")
        print(f"=" * 60)
        print(f"\nNext Steps:")
        print(f"1. Install REMBG if not already installed: pip install rembg")
        print(f"2. Run: python test_step1_provider.py")
        print(f"3. Proceed to Step 2: API Endpoint Integration")
        
        return True
        
    except Exception as e:
        print(f"\n❌ STEP 1 FAILED: {e}")
        print(f"\nTroubleshooting:")
        print(f"1. Make sure you're in the backend directory")
        print(f"2. Install REMBG: pip install rembg")
        print(f"3. Install Pillow: pip install Pillow")
        print(f"4. Install aiohttp: pip install aiohttp")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_step1())
    sys.exit(0 if success else 1)
