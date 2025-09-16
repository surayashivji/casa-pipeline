"""
Simple test to verify Meshy works
"""
import os
import time

# Use Meshy's official test API key - FREE!
os.environ['MESHY_API_KEY'] = 'msy_dummy_api_key_for_test_mode_12345678'

from app.services.meshy.meshy import meshy

def test_meshy():
    print("="*60)
    print("TESTING MESHY SERVICE")
    print("="*60)
    print("🧪 Using Meshy's test API key (FREE)")
    print("="*60)
    
    # Can use any images - they'll be ignored in test mode
    test_images = [
        "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
        "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=800"
    ]
    
    # Step 1: Create task
    print("\n1. Creating task with test API key...")
    result = meshy.create_task(test_images)
    
    if not result["success"]:
        print(f"❌ Failed: {result.get('error')}")
        return
    
    task_id = result["task_id"]
    print(f"✅ Task ID: {task_id}")
    
    # Step 2: Check status
    print("\n2. Checking status...")
    status = meshy.get_status(task_id)
    print(f"Status: {status.get('status')}")
    print(f"Progress: {status.get('progress')}%")
    
    # Step 3: If test returns sample data immediately
    if status.get("status") == "SUCCEEDED":
        print("\n✅ Test mode returned sample data immediately!")
        model_urls = status.get("model_urls", {})
        if model_urls:
            print(f"Sample GLB: {model_urls.get('glb')}")
            print(f"Sample Thumbnail: {status.get('thumbnail_url')}")
    else:
        # Might need to poll
        print("\n3. Checking if we need to poll...")
        for i in range(3):  # Just check a few times
            time.sleep(2)
            status = meshy.get_status(task_id)
            print(f"  Status: {status.get('status')}")
            if status.get("status") == "SUCCEEDED":
                print(f"\n✅ Got sample response!")
                print(f"Sample GLB: {status.get('model_urls', {}).get('glb')}")
                break

if __name__ == "__main__":
    test_meshy()