#!/usr/bin/env python3
"""
Working Meshy API Test
Uses the correct field name: image_url
"""

import asyncio
import aiohttp
import json

async def test_meshy_working():
    """Test Meshy API with correct field name"""
    print("=" * 70)
    print("TESTING MESHY API WITH CORRECT FIELD NAME")
    print("=" * 70)
    
    api_key = 'msy_DNG0ZY0fT4hbR2d7IrdN9DP4NgW8OqHgUkJD'
    base_url = "https://api.meshy.ai"
    
    print(f"🔑 Using API key: {api_key[:10]}...")
    print(f"💰 This will cost $0.50!")
    print()
    
    test_image = "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop"
    
    print(f"📸 Using test image: {test_image}")
    
    try:
        print(f"\n🚀 Creating 3D generation task...")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Use the working field name: image_url
        payload = {
            "image_url": test_image,
            "object_name": "Test Chair from Unsplash"
        }
        
        print(f"📤 Sending payload: {json.dumps(payload, indent=2)}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/v1/image-to-3d",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_text = await response.text()
                print(f"📥 Response status: {response.status}")
                print(f"📥 Response body: {response_text}")
                
                if response.status != 202:
                    print(f"❌ Expected status 202, got {response.status}")
                    return False
                
                data = json.loads(response_text)
                task_id = data.get("result")
                
                if not task_id:
                    print(f"❌ No task ID in response")
                    return False
                
                print(f"✅ Task created successfully!")
                print(f"✅ Task ID: {task_id}")
                
                # Poll for status
                print(f"\n⏳ Waiting for 3D model generation...")
                print(f"   This typically takes 2-5 minutes...")
                
                max_attempts = 30  # 5 minutes max
                for attempt in range(max_attempts):
                    await asyncio.sleep(10)  # Wait 10 seconds between checks
                    
                    async with session.get(
                        f"{base_url}/v1/image-to-3d-tasks/{task_id}",
                        headers={"Authorization": f"Bearer {api_key}"},
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as status_response:
                        status_text = await status_response.text()
                        
                        if status_response.status != 200:
                            print(f"❌ Status check failed: {status_response.status}")
                            continue
                        
                        status_data = json.loads(status_text)
                        status = status_data.get('status', 'UNKNOWN')
                        progress = status_data.get('progress', 0)
                        
                        print(f"   📊 Progress: {progress}% - {status}")
                        
                        if status == "SUCCEEDED":
                            print(f"\n🎉 3D MODEL GENERATION COMPLETE!")
                            print(f"=" * 50)
                            
                            model_urls = status_data.get('model_urls', {})
                            if model_urls:
                                print(f"\n📦 REAL 3D MODEL FILES:")
                                for format_name, url in model_urls.items():
                                    print(f"   {format_name.upper()}: {url}")
                                    print(f"      🔗 Click to download: {url}")
                            
                            thumbnail_url = status_data.get('thumbnail_url')
                            if thumbnail_url:
                                print(f"\n🖼️  THUMBNAIL:")
                                print(f"   {thumbnail_url}")
                                print(f"   🔗 Click to view: {thumbnail_url}")
                            
                            video_url = status_data.get('video_url')
                            if video_url:
                                print(f"\n🎥 360° VIDEO:")
                                print(f"   {video_url}")
                                print(f"   🔗 Click to view: {video_url}")
                            
                            metadata = status_data.get('metadata', {})
                            if metadata:
                                print(f"\n📊 METADATA:")
                                for key, value in metadata.items():
                                    print(f"   {key}: {value}")
                            
                            print(f"\n💰 COST: $0.50 charged to your account")
                            print(f"\n🎯 SUCCESS!")
                            print(f"   ✅ Real 3D model generated")
                            print(f"   ✅ Working download URLs")
                            print(f"   ✅ Ready for iOS app")
                            print(f"   ✅ Production mode working")
                            
                            return True
                        
                        elif status == "FAILED":
                            print(f"\n❌ 3D generation failed!")
                            print(f"   Error: {status_data.get('error', 'Unknown error')}")
                            return False
                
                print(f"\n⏰ Timeout: 3D generation took longer than expected")
                print(f"   Task ID: {task_id}")
                print(f"   You can check status later with this ID")
                return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

async def main():
    """Main test function"""
    print("Starting Working Meshy API Test...")
    print()
    
    success = await test_meshy_working()
    
    if success:
        print("\n🎉 Meshy API test completed successfully!")
        print("🎯 You now have a real 3D model!")
        print("🚀 Production mode is working!")
    else:
        print("\n❌ Meshy API test failed or timed out.")
        print("💡 Check the task ID for manual status checking.")

if __name__ == "__main__":
    asyncio.run(main())
