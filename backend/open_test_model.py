#!/usr/bin/env python3
"""
Open Meshy Test Model URLs
Opens the 3D model files and thumbnail in your browser
"""

import webbrowser
import time

def open_test_model():
    """Open the test model URLs from our successful test"""
    
    # URLs from our successful test run
    model_urls = {
        "GLB": "https://assets.meshy.ai/dummy-user-for-test-mode/tasks/0199505f-9791-7973-8dca-c77cf716969c/output/model.glb?Expires=1758249267&Signature=L6bOul0OcpykWwmCPqw~weB~tVUyUuhDnn9zpnj92yHwzTvWZV6ofPPlSh0Tl6HP2bulLzid6JhfYwIjjn3zIRbohDuGUtzE0SSGCNqRFrxSj34dzNOYDFmDabroOzhuo9Pev9Ipet7f07P2cYUUQX1xlS1xFYXMvQoE20C65k4Kjegv9VmEpKe~Zj883MgxWZd6zExwAZ2uG57AHgI~bDV8dBnsiHJimeKHnY3kcodCSp~a0sdGAKqyuNNwopN44zcG613uyZdpiSQhCiiiaOYy7uKjze5XLvag4zGKfDpCJD1AJUjNfmEJ4b0zPlfb8ki9DXDuEmNw__&Key-Pair-Id=KL5I0C8H7HX83",
        "FBX": "https://assets.meshy.ai/dummy-user-for-test-mode/tasks/0199505f-9791-7973-8dca-c77cf716969c/output/model.fbx?Expires=1758249267&Signature=gsgHe3kyYlCaU2zPeS7iUVSLSbzZ-iTk0uvSfrDoJTWLnIzSUs~fDQym5w~kltjD5CBCLBPcrQbSwvDGGlq7txY9JcPL8EAxFTo0J0bwtQIgG0x~0-F1Fc6s0q1Dwrg6GTp5s7~~KC~RdP675tBBW9Jw58IzWxjned~NDAaOM2Mppk0pGWuUvg5~-JVpKs16bzefbbb7uh8VjlmzRogM-hULw-T3PNlr1PSv4N37FlL7ywRs5mtfaFK122pTDAhXUgoJrpQLdlCmCpAaDIJxgZ0LbJcJFIJCjrJVG067YjdnyFoRFXk790Qg-mJguUlUKD-fwYEPw97zulr66Eiahw__&Key-Pair-Id=KL5I0C8H7HX83",
        "USDZ": "https://assets.meshy.ai/dummy-user-for-test-mode/tasks/0199505f-9791-7973-8dca-c77cf716969c/output/model.usdz?Expires=1758249267&Signature=hsoWf4iJU5AX4u6EceRpC-ztHUt80c3hPia9Q-Vo-9QyeNBvWXqhTP7Flp3J7s892tzx7k62VtJBPhzv4R~2ECZg5xxwFVzcfoRdq3KHqaHmfuLG3Rc-tD8XUrMGB8hHamMMw8XvyuzFDMbDCn60RvDiFfRtgZ~QCzImjtqX2ADCJXdPg4K~2PtiF3YgLYvQPhiAVAcPJDXGC3fiCnwwHXUXtiWxO5Q9Uyy3Y91XyjRbUJ817ZCB0RGSL5t1OSrsx3GEnbGVZSU0Rpq6Q1f3KDsbI8xE0WFjXRzygBUDgXJNY5MV-gnE5bR5J~O1gJBpGlu~W4ooIM0RaMEQ5xiS6Q__&Key-Pair-Id=KL5I0C8H7HX83",
        "OBJ": "https://assets.meshy.ai/dummy-user-for-test-mode/tasks/0199505f-9791-7973-8dca-c77cf716969c/output/model.obj?Expires=1758249267&Signature=Rvf1WfbFxq6CNQ1DrqpjN8lGgfSEtuFhPwBecNvc6mKUnF5~cU25bo32ZanRzyz8XQwVYOeSJYwNuvH3lxipJm2M~LREhEeh2kEAZBaQ6ibMwH4WE-Ut98M7C7iEb6zTO1Ps6tC7Dau6pNGnPNCpsVSu3CkCGp3sLingSbKLmv8MDm~G1qbCPeCexcv3urq7Q59ldXy1XrlLRJqEa3dtZZv9SMs9POhHAVkLg-XuGq1~U3JYp7Mf5kfTpqK21RbfX9rT0DQU89eUNK-toXk7s3sQIpQXQ1nyZnZzcVi9KfvnSBuBFDs9r3RsYIZ49~Do0Q22enPpWxaUTFnjJT9qXg__&Key-Pair-Id=KL5I0C8H7HX83"
    }
    
    thumbnail_url = "https://assets.meshy.ai/dummy-user-for-test-mode/tasks/0199505f-9791-7973-8dca-c77cf716969c/output/preview.png?Expires=1758249267&Signature=mTKT6SZnTMp3RW4S39cI239CrwTA~tKp4ZbUpDvIUNcX6xRFF75JjgV~CUUNENmEBxG4X73egq4XnWwHR9JDjej4HdQji3yXJEQEiGh3ZjGxIY-Wzdrgf4nsXaI6jFKHJ-ywX7a6a2ZaYH2xPtpMbWPwjbugzKp4~-iOhlPph3l2KI2yRFiTYXA4Uc8ykyANMM3nmMKkhpjhGQjJDtXq8hTrvIZ0ORU3ezWfI~Fz2g~3VGQ4pNTp2sKj5q8BY823WPFaNQloLu9l9ecXWobNUq4o~~B~hPr2AtLXv~5CUUwFF6AsnwmM4swVX~a8zkjwAhhDbTn6CoSTVtN2lNAjUA__&Key-Pair-Id=KL5I0C8H7HX83"
    
    print("=" * 60)
    print("OPENING MESHY TEST MODEL FILES")
    print("=" * 60)
    
    print("🖼️  Opening thumbnail image...")
    webbrowser.open(thumbnail_url)
    time.sleep(1)
    
    print("\n📦 Opening 3D model files...")
    print("   Note: Some formats may download instead of opening in browser")
    
    for format_name, url in model_urls.items():
        print(f"   Opening {format_name}...")
        webbrowser.open(url)
        time.sleep(0.5)  # Small delay between opens
    
    print(f"\n✅ All model files opened!")
    print(f"\n📋 Model Information:")
    print(f"   • Format: Test mode sample model")
    print(f"   • Generated from: 3 chair images")
    print(f"   • Quality: High (meshy-5 model)")
    print(f"   • Textures: PBR enabled")
    print(f"   • Cost: $0.00 (test mode)")
    
    print(f"\n💡 Tips:")
    print(f"   • GLB: Best for web/Unity/Unreal")
    print(f"   • USDZ: Best for iOS/ARKit")
    print(f"   • FBX: Best for Maya/Blender")
    print(f"   • OBJ: Universal format")
    
    print(f"\n🎯 This shows what real 3D models will look like!")
    print(f"   In production mode, you'll get similar quality models")

if __name__ == "__main__":
    open_test_model()
