import asyncio
from playwright.async_api import async_playwright

async def test_playwright():
    """Test Playwright installation and basic functionality"""
    print("🧪 Testing Playwright installation...")
    
    try:
        async with async_playwright() as p:
            print("  ✅ Playwright context created successfully")
            
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            print("  ✅ Chromium browser launched successfully")
            
            # Create page
            page = await browser.new_page()
            print("  ✅ New page created successfully")
            
            # Navigate to IKEA
            print("  🌐 Navigating to IKEA website...")
            await page.goto("https://www.ikea.com", wait_until='networkidle')
            title = await page.title()
            print(f"  ✅ Page loaded successfully! Title: {title}")
            
            # Test basic element selection
            print("  🔍 Testing element selection...")
            try:
                # Try to find a common IKEA element
                await page.wait_for_selector('body', timeout=5000)
                print("  ✅ Element selection working")
            except Exception as e:
                print(f"  ⚠️  Element selection test failed: {e}")
            
            # Close browser
            await browser.close()
            print("  ✅ Browser closed successfully")
            
        print("\n🎉 Playwright test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Playwright test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_playwright())
    if success:
        print("\n✅ Playwright is ready for Phase 3 implementation!")
    else:
        print("\n❌ Playwright setup needs attention before proceeding.")
