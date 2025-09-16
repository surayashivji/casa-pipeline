#!/usr/bin/env python3
"""
Download Meshy Test Model Files
Downloads the 3D model files and thumbnail to local files
"""

import requests
import os
from pathlib import Path

def download_file(url, filename):
    """Download a file from URL to local filename"""
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

def download_test_model():
    """Download the test model files from our successful test"""
    
    # Create downloads directory
    download_dir = Path("test_models")
    download_dir.mkdir(exist_ok=True)
    
    # URLs from our successful test run
    model_urls = {
        "model.glb": "https://assets.meshy.ai/dummy-user-for-test-mode/tasks/0199505f-9791-7973-8dca-c77cf716969c/output/model.glb?Expires=1758249267&Signature=L6bOul0OcpykWwmCPqw~weB~tVUyUuhDnn9zpnj92yHwzTvWZV6ofPPlSh0Tl6HP2bulLzid6JhfYwIjjn3zIRbohDuGUtzE0SSGCNqRFrxSj34dzNOYDFmDabroOzhuo9Pev9Ipet7f07P2cYUUQX1xlS1xFYXMvQoE20C65k4Kjegv9VmEpKe~Zj883MgxWZd6zExwAZ2uG57AHgI~bDV8dBnsiHJimeKHnY3kcodCSp~a0sdGAKqyuNNwopN44zcG613uyZdpiSQhCiiiaOYy7uKjze5XLvag4zGKfDpCJD1AJUjNfmEJ4b0zPlfb8ki9DXDuEmNw__&Key-Pair-Id=KL5I0C8H7HX83",
        "model.fbx": "https://assets.meshy.ai/dummy-user-for-test-mode/tasks/0199505f-9791-7973-8dca-c77cf716969c/output/model.fbx?Expires=1758249267&Signature=gsgHe3kyYlCaU2zPeS7iUVSLSbzZ-iTk0uvSfrDoJTWLnIzSUs~fDQym5w~kltjD5CBCLBPcrQbSwvDGGlq7txY9JcPL8EAxFTo0J0bwtQIgG0x~0-F1Fc6s0q1Dwrg6GTp5s7~~KC~RdP675tBBW9Jw58IzWxjned~NDAaOM2Mppk0pGWuUvg5~-JVpKs16bzefbbb7uh8VjlmzRogM-hULw-T3PNlr1PSv4N37FlL7ywRs5mtfaFK122pTDAhXUgoJrpQLdlCmCpAaDIJxgZ0LbJcJFIJCjrJVG067YjdnyFoRFXk790Qg-mJguUlUKD-fwYEPw97zulr66Eiahw__&Key-Pair-Id=KL5I0C8H7HX83",
        "model.usdz": "https://assets.meshy.ai/dummy-user-for-test-mode/tasks/0199505f-9791-7973-8dca-c77cf716969c/output/model.usdz?Expires=1758249267&Signature=hsoWf4iJU5AX4u6EceRpC-ztHUt80c3hPia9Q-Vo-9QyeNBvWXqhTP7Flp3J7s892tzx7k62VtJBPhzv4R~2ECZg5xxwFVzcfoRdq3KHqaHmfuLG3Rc-tD8XUrMGB8hHamMMw8XvyuzFDMbDCn60RvDiFfRtgZ~QCzImjtqX2ADCJXdPg4K~2PtiF3YgLYvQPhiAVAcPJDXGC3fiCnwwHXUXtiWxO5Q9Uyy3Y91XyjRbUJ817ZCB0RGSL5t1OSrsx3GEnbGVZSU0Rpq6Q1f3KDsbI8xE0WFjXRzygBUDgXJNY5MV-gnE5bR5J~O1gJBpGlu~W4ooIM0RaMEQ5xiS6Q__&Key-Pair-Id=KL5I0C8H7HX83",
        "model.obj": "https://assets.meshy.ai/dummy-user-for-test-mode/tasks/0199505f-9791-7973-8dca-c77cf716969c/output/model.obj?Expires=1758249267&Signature=Rvf1WfbFxq6CNQ1DrqpjN8lGgfSEtuFhPwBecNvc6mKUnF5~cU25bo32ZanRzyz8XQwVYOeSJYwNuvH3lxipJm2M~LREhEeh2kEAZBaQ6ibMwH4WE-Ut98M7C7iEb6zTO1Ps6tC7Dau6pNGnPNCpsVSu3CkCGp3sLingSbKLmv8MDm~G1qbCPeCexcv3urq7Q59ldXy1XrlLRJqEa3dtZZv9SMs9POhHAVkLg-XuGq1~U3JYp7Mf5kfTpqK21RbfX9rT0DQU89eUNK-toXk7s3sQIpQXQ1nyZnZzcVi9KfvnSBuBFDs9r3RsYIZ49~Do0Q22enPpWxaUTFnjJT9qXg__&Key-Pair-Id=KL5I0C8H7HX83",
        "model.mtl": "https://assets.meshy.ai/dummy-user-for-test-mode/tasks/0199505f-9791-7973-8dca-c77cf716969c/output/model.mtl?Expires=1758249267&Signature=pJGxfxRaJGlMeqw9QTfhKBRl~2DMaZ8R65nKySlDnVIkCBXdD8M7ufydbRmmrC0N244mylzVHHYk9~5LgR4a9b54gk1ypYCIkXKZakQjxFKID25fnepX-TRAvp7Rr17P4i72WP0eldB1CK6tg238NCi-mG8Hi7Ef-5VKVWgHWM0IauJOdMwkYMLK2nbcztAEIKXi2GrmvxltIULEaNy43dLeGBTp74RRGmzLOhXPUO6gsDhTO8Y-bhl5BThas-TJWhX5TgQ0Ib23fW9P1JoULLs5o-Zl5N14QU8EsBbnvfD3qsDCimpJ0mbxRK1esu4eJzszcWLIjrc1cODT703tNg__&Key-Pair-Id=KL5I0C8H7HX83"
    }
    
    thumbnail_url = "https://assets.meshy.ai/dummy-user-for-test-mode/tasks/0199505f-9791-7973-8dca-c77cf716969c/output/preview.png?Expires=1758249267&Signature=mTKT6SZnTMp3RW4S39cI239CrwTA~tKp4ZbUpDvIUNcX6xRFF75JjgV~CUUNENmEBxG4X73egq4XnWwHR9JDjej4HdQji3yXJEQEiGh3ZjGxIY-Wzdrgf4nsXaI6jFKHJ-ywX7a6a2ZaYH2xPtpMbWPwjbugzKp4~-iOhlPph3l2KI2yRFiTYXA4Uc8ykyANMM3nmMKkhpjhGQjJDtXq8hTrvIZ0ORU3ezWfI~Fz2g~3VGQ4pNTp2sKj5q8BY823WPFaNQloLu9l9ecXWobNUq4o~~B~hPr2AtLXv~5CUUwFF6AsnwmM4swVX~a8zkjwAhhDbTn6CoSTVtN2lNAjUA__&Key-Pair-Id=KL5I0C8H7HX83"
    
    print("=" * 60)
    print("DOWNLOADING MESHY TEST MODEL FILES")
    print("=" * 60)
    
    print(f"📁 Download directory: {download_dir.absolute()}")
    print()
    
    # Download thumbnail
    print("🖼️  Downloading thumbnail...")
    download_file(thumbnail_url, download_dir / "preview.png")
    print()
    
    # Download 3D model files
    print("📦 Downloading 3D model files...")
    success_count = 0
    total_count = len(model_urls)
    
    for filename, url in model_urls.items():
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
    
    else:
        print(f"\n❌ No files were downloaded successfully")
        print(f"   Check your internet connection and try again")

if __name__ == "__main__":
    download_test_model()
