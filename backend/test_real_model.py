#!/usr/bin/env python3
"""
Test Real Meshy Model Generation
Uses your real API key to generate an actual 3D model you can see
"""

import os
import sys
from pathlib import Path
import time

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.meshy import MeshyService

def test_real_model_generation():
    """Test with real API key to generate actual 3D model"""
    
    print("=" * 70)
    print("TESTING REAL MESHY MODEL GENERATION")
    print("=" * 70)
    
    # Set your real API key
    os.environ['MESHY_API_KEY'] = 'msy_DNG0ZY0fT4hbR2d7IrdN9DP4NgW8OqHgUkJD'
    
    # Create service in production mode
    service = MeshyService(test_mode=False)
    
    # Use simple test images
    test_images = [
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop"
    ]
    
    print(f"🔑 Using real API key: {os.environ['MESHY_API_KEY'][:10]}...")
    print(f"💰 This will cost $15.00 (base + textures)")
    print(f"📸 Using 1 test image: {test_images[0]}")
    
    print(f"\n⚠️  WARNING: This will charge your Meshy account $15.00!")
    print(f"🤔 This is the only way to see actual 3D models")
    
    # Ask for confirmation
    response = input("\nDo you want to proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cancelled. No charges incurred.")
        return False
    
    try:
        # Create 3D model task
        print(f"\n🚀 Creating 3D model task...")
        task_id = service.create_3d_model(
            image_urls=test_images,
            object_name="Real Test Chair",
            settings={
                "ai_model": "meshy-5",
                "target_polycount": 20000,
                "enable_pbr": True
            }
        )
        
        print(f"✅ Task created: {task_id}")
        
        # Wait for completion
        print(f"\n⏳ Waiting for 3D model generation...")
        print(f"   This typically takes 2-5 minutes...")
        
        final_status = service.wait_for_completion(task_id, max_attempts=30, delay_seconds=10)
        
        if final_status.get('status') == 'SUCCEEDED':
            print(f"\n🎉 3D MODEL GENERATION COMPLETE!")
            
            # Get model URLs
            model_urls = final_status.get('model_urls', {})
            thumbnail_url = final_status.get('thumbnail_url')
            
            print(f"\n📦 REAL 3D MODEL FILES:")
            for format_name, url in model_urls.items():
                print(f"   {format_name.upper()}: {url}")
                print(f"      🔗 Click to download: {url}")
            
            if thumbnail_url:
                print(f"\n🖼️  THUMBNAIL:")
                print(f"   {thumbnail_url}")
                print(f"   🔗 Click to view: {thumbnail_url}")
            
            print(f"\n✅ SUCCESS! You now have a real 3D model!")
            print(f"💰 $15.00 charged to your account")
            print(f"🎯 This proves the integration works perfectly!")
            
            return True
        else:
            print(f"❌ Generation failed: {final_status.get('task_error', {}).get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_real_model_generation()
