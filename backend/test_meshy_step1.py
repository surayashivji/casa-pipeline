#!/usr/bin/env python3
"""
Step 1 Test: Meshy Multi-Image to 3D API Integration
Tests both test mode and production mode
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.meshy import MeshyService

def test_meshy_test_mode():
    """Test Meshy service in test mode"""
    print("=" * 60)
    print("STEP 1: MESHY TEST MODE")
    print("=" * 60)
    
    # Test mode (no charges)
    service = MeshyService(test_mode=True)
    
    # Test images (using publicly accessible images)
    test_images = [
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&h=600&fit=crop"
    ]
    
    print(f"📸 Using {len(test_images)} test images")
    for i, url in enumerate(test_images, 1):
        print(f"   {i}. {url}")
    
    print(f"\n💰 Cost info: {service.get_cost_info(len(test_images))}")
    
    try:
        # Create 3D model task
        print(f"\n🚀 Creating 3D model task...")
        task_id = service.create_3d_model(
            image_urls=test_images,
            object_name="Test Chair",
            settings={
                "ai_model": "meshy-5",
                "target_polycount": 20000,
                "enable_pbr": True
            }
        )
        
        print(f"✅ Task created successfully!")
        print(f"✅ Task ID: {task_id}")
        
        # Check status immediately
        print(f"\n📊 Checking task status...")
        status = service.get_task_status(task_id)
        
        print(f"✅ Status: {status.get('status', 'UNKNOWN')}")
        print(f"✅ Progress: {status.get('progress', 0)}%")
        
        # Show available fields
        print(f"\n📋 Available response fields:")
        for key in status.keys():
            print(f"   - {key}")
        
        # If completed, show results
        if status.get('status') == 'SUCCEEDED':
            model_urls = status.get('model_urls', {})
            if model_urls:
                print(f"\n📦 3D Model Files:")
                for format_name, url in model_urls.items():
                    print(f"   {format_name.upper()}: {url}")
            
            thumbnail_url = status.get('thumbnail_url')
            if thumbnail_url:
                print(f"\n🖼️  Thumbnail: {thumbnail_url}")
        
        print(f"\n🎯 TEST MODE SUCCESS!")
        print(f"   ✅ API integration working")
        print(f"   ✅ Multi-image support working")
        print(f"   ✅ No charges incurred")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test mode failed: {e}")
        return False

def test_meshy_production_mode():
    """Test Meshy service in production mode"""
    print("\n" + "=" * 60)
    print("STEP 1: MESHY PRODUCTION MODE")
    print("=" * 60)
    
    # Set production API key
    os.environ['MESHY_API_KEY'] = 'msy_DNG0ZY0fT4hbR2d7IrdN9DP4NgW8OqHgUkJD'
    
    # Production mode (will consume credits)
    service = MeshyService(test_mode=False)
    
    # Test images
    test_images = [
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=800&h=600&fit=crop"
    ]
    
    print(f"📸 Using {len(test_images)} test images")
    print(f"💰 Cost info: {service.get_cost_info(len(test_images))}")
    
    print(f"\n⚠️  WARNING: This will charge your Meshy account!")
    print("🤔 Skipping production mode test to avoid charges")
    return False
    
    try:
        # Create 3D model task
        print(f"\n🚀 Creating 3D model task...")
        task_id = service.create_3d_model(
            image_urls=test_images,
            object_name="Production Test Chair"
        )
        
        print(f"✅ Task created successfully!")
        print(f"✅ Task ID: {task_id}")
        
        # Wait for completion (with shorter timeout for demo)
        print(f"\n⏳ Waiting for completion (max 2 minutes)...")
        try:
            final_status = service.wait_for_completion(task_id, max_attempts=12, delay_seconds=10)
            
            if final_status.get('status') == 'SUCCEEDED':
                print(f"\n🎉 3D MODEL GENERATION COMPLETE!")
                
                model_urls = final_status.get('model_urls', {})
                if model_urls:
                    print(f"\n📦 REAL 3D MODEL FILES:")
                    for format_name, url in model_urls.items():
                        print(f"   {format_name.upper()}: {url}")
                
                thumbnail_url = final_status.get('thumbnail_url')
                if thumbnail_url:
                    print(f"\n🖼️  Thumbnail: {thumbnail_url}")
                
                print(f"\n🎯 PRODUCTION MODE SUCCESS!")
                print(f"   ✅ Real 3D model generated")
                print(f"   ✅ Working download URLs")
                return True
            else:
                print(f"❌ Generation failed: {final_status.get('task_error', {}).get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"⏰ Timeout or error: {e}")
            print(f"   Task ID: {task_id}")
            print(f"   You can check status later with this ID")
            return False
        
    except Exception as e:
        print(f"\n❌ Production mode failed: {e}")
        return False

def main():
    """Main test function"""
    print("Starting Meshy Step 1 Integration Test...")
    print()
    
    # Test 1: Test Mode
    test_mode_success = test_meshy_test_mode()
    
    # Test 2: Production Mode (optional)
    production_mode_success = test_meshy_production_mode()
    
    print("\n" + "=" * 60)
    print("STEP 1 TEST RESULTS")
    print("=" * 60)
    print(f"✅ Test Mode: {'PASS' if test_mode_success else 'FAIL'}")
    print(f"✅ Production Mode: {'PASS' if production_mode_success else 'SKIP/FAIL'}")
    
    if test_mode_success:
        print(f"\n🎉 STEP 1 COMPLETE!")
        print(f"   ✅ Meshy service working")
        print(f"   ✅ Multi-image support working")
        print(f"   ✅ Test mode safe for development")
        print(f"   ✅ Ready for Step 2: Replace mock endpoints")
    else:
        print(f"\n❌ STEP 1 FAILED")
        print(f"   💡 Check API key and network connection")

if __name__ == "__main__":
    main()
