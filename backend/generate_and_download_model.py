#!/usr/bin/env python3
"""
Generate Fresh Meshy Model and Download
Creates a new 3D model task and downloads the results
"""

import os
import sys
from pathlib import Path
import time

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.meshy import MeshyService

def download_file(url, filename):
    """Download a file from URL to local filename"""
    import requests
    try:
        print(f"📥 Downloading {filename}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        file_size = os.path.getsize(filename)
        print(f"   ✅ Downloaded {filename} ({file_size:,} bytes)")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to download {filename}: {e}")
        return False

def generate_and_download_model():
    """Generate a fresh 3D model and download it"""
    
    print("=" * 60)
    print("GENERATING FRESH MESHY MODEL")
    print("=" * 60)
    
    # Create downloads directory
    download_dir = Path("fresh_test_models")
    download_dir.mkdir(exist_ok=True)
    
    # Test images
    test_images = [
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&h=600&fit=crop"
    ]
    
    print(f"📸 Using {len(test_images)} test images")
    for i, url in enumerate(test_images, 1):
        print(f"   {i}. {url}")
    
    # Create Meshy service in test mode
    service = MeshyService(test_mode=True)
    print(f"\n💰 Cost info: {service.get_cost_info(len(test_images))}")
    
    try:
        # Generate fresh 3D model
        print(f"\n🚀 Creating fresh 3D model task...")
        task_id = service.create_3d_model(
            image_urls=test_images,
            object_name="Fresh Test Chair",
            settings={
                "ai_model": "meshy-5",
                "target_polycount": 20000,
                "enable_pbr": True
            }
        )
        
        print(f"✅ Task created: {task_id}")
        
        # Wait for completion
        print(f"\n⏳ Waiting for completion...")
        final_status = service.wait_for_completion(task_id, max_attempts=6, delay_seconds=5)
        
        if final_status.get('status') == 'SUCCEEDED':
            print(f"\n🎉 3D MODEL GENERATION COMPLETE!")
            
            # Get model URLs
            model_urls = final_status.get('model_urls', {})
            thumbnail_url = final_status.get('thumbnail_url')
            
            if not model_urls:
                print(f"❌ No model URLs in response")
                return False
            
            print(f"\n📦 Downloading model files...")
            print(f"📁 Save directory: {download_dir.absolute()}")
            
            success_count = 0
            total_count = len(model_urls) + (1 if thumbnail_url else 0)
            
            # Download thumbnail
            if thumbnail_url:
                if download_file(thumbnail_url, download_dir / "preview.png"):
                    success_count += 1
                print()
            
            # Download model files
            for format_name, url in model_urls.items():
                filename = f"model.{format_name.lower()}"
                if download_file(url, download_dir / filename):
                    success_count += 1
                print()
            
            print("=" * 60)
            print("DOWNLOAD RESULTS")
            print("=" * 60)
            print(f"✅ Successfully downloaded: {success_count}/{total_count} files")
            print(f"📁 Files saved to: {download_dir.absolute()}")
            
            if success_count > 0:
                print(f"\n📋 Downloaded files:")
                for file_path in download_dir.iterdir():
                    if file_path.is_file():
                        size = file_path.stat().st_size
                        print(f"   • {file_path.name} ({size:,} bytes)")
                
                print(f"\n💡 How to view the models:")
                print(f"   • GLB: Use Blender, Unity, or online GLB viewers")
                print(f"   • USDZ: Open in iOS Files app or ARKit")
                print(f"   • FBX: Use Maya, Blender, or 3ds Max")
                print(f"   • OBJ: Universal format, works in most 3D software")
                print(f"   • PNG: Thumbnail preview image")
                
                print(f"\n🎯 This shows the quality of 3D models from Meshy!")
                print(f"   In production, you'll get similar quality from your product images")
                
                return True
            else:
                print(f"\n❌ No files were downloaded successfully")
                return False
                
        else:
            print(f"❌ Generation failed: {final_status.get('task_error', {}).get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    generate_and_download_model()
