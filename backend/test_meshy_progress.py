"""
Test Meshy with detailed progress tracking
"""
import os
import time
import json
from datetime import datetime

# Use test API key
os.environ['MESHY_API_KEY'] = 'msy_dummy_api_key_for_test_mode_12345678'

from app.services.meshy.meshy import meshy

def test_progress_tracking():
    print("="*60)
    print("MESHY PROGRESS TRACKING TEST")
    print("="*60)
    
    # Test images
    test_images = [
        "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
        "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=800"
    ]
    
    # Step 1: Create task
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Creating task...")
    result = meshy.create_task(test_images)
    
    if not result["success"]:
        print(f"❌ Failed: {result.get('error')}")
        return
    
    task_id = result["task_id"]
    print(f"✅ Task created: {task_id}")
    
    # Step 2: Poll for progress
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting progress tracking...")
    print("-" * 40)
    
    max_polls = 20  # Poll up to 20 times
    poll_interval = 3  # Every 3 seconds
    
    previous_progress = -1
    
    for i in range(max_polls):
        # Check status
        status_data = meshy.get_status(task_id)
        
        # Extract info
        status = status_data.get("status", "UNKNOWN")
        progress = status_data.get("progress", 0)
        
        # Print update if progress changed
        if progress != previous_progress:
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Progress bar visualization
            bar_length = 30
            filled = int(bar_length * progress / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            print(f"[{timestamp}] {bar} {progress:3}% - {status}")
            
            previous_progress = progress
        
        # Check if complete
        if status == "SUCCEEDED":
            print("-" * 40)
            print(f"\n✅ COMPLETED at {datetime.now().strftime('%H:%M:%S')}")
            
            # Show results
            model_urls = status_data.get("model_urls", {})
            if model_urls:
                print("\n📦 Generated Models:")
                print(f"  GLB:  {model_urls.get('glb', 'N/A')[:80]}...")
                print(f"  FBX:  {model_urls.get('fbx', 'N/A')[:80]}...")
                print(f"  USDZ: {model_urls.get('usdz', 'N/A')[:80]}...")
            
            thumbnail = status_data.get("thumbnail_url")
            if thumbnail:
                print(f"\n🖼️ Thumbnail: {thumbnail[:80]}...")
            
            # Show full response for debugging
            print("\n📋 Full Response:")
            print(json.dumps(status_data, indent=2)[:500])
            
            break
            
        elif status == "FAILED":
            print(f"\n❌ Task failed: {status_data.get('message', 'Unknown error')}")
            break
        
        # Wait before next poll
        time.sleep(poll_interval)
    
    else:
        print(f"\n⏱️ Timeout after {max_polls * poll_interval} seconds")
        print(f"Last status: {status}")
        print(f"Last progress: {progress}%")

if __name__ == "__main__":
    test_progress_tracking()