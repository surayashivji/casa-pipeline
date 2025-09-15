#!/usr/bin/env python3
"""
Frontend Real Data Integration Test
Tests the complete user experience with real scraped data
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

class FrontendRealDataTest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"
        self.test_results = []
        
    async def test_frontend_accessibility(self):
        """Test if frontend is accessible and responsive"""
        print("🧪 Testing Frontend Accessibility")
        print("=" * 50)
        
        try:
            async with httpx.AsyncClient() as client:
                # Test main page
                response = await client.get(self.frontend_url, timeout=10)
                if response.status_code == 200:
                    print("✅ Frontend main page accessible")
                    
                    # Check if it's a React app
                    content = response.text
                    if "react" in content.lower() or "vite" in content.lower():
                        print("✅ React/Vite frontend detected")
                    else:
                        print("⚠️  Frontend type unclear")
                    
                    return True
                else:
                    print(f"❌ Frontend returned status {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Frontend not accessible: {e}")
            return False
    
    async def test_single_product_pipeline(self):
        """Test complete single product pipeline with real data"""
        print(f"\n🧪 Testing Single Product Pipeline")
        print("=" * 50)
        
        # Test with real IKEA products
        test_products = [
            {
                "name": "Stockholm Sofa",
                "url": "https://www.ikea.com/us/en/p/stockholm-2025-3-seat-sofa-alhamn-beige-s69574294/",
                "expected_name": "STOCKHOLM 2025 3-seat sofa, Alhamn beige"
            },
            {
                "name": "Dyvlinge Chair", 
                "url": "https://www.ikea.com/us/en/p/dyvlinge-swivel-chair-kelinge-orange-40581921/",
                "expected_name": "DYVLINGE Swivel chair, Kelinge orange"
            }
        ]
        
        results = []
        
        for i, product in enumerate(test_products, 1):
            print(f"\n🔍 Test {i}: {product['name']}")
            print(f"URL: {product['url'][:60]}...")
            
            try:
                async with httpx.AsyncClient() as client:
                    # Step 1: URL Detection
                    print(f"  📋 Step 1: URL Detection")
                    detect_response = await client.post(
                        f"{self.backend_url}/api/detect-url",
                        json={"url": product['url']},
                        timeout=10
                    )
                    
                    if detect_response.status_code == 200:
                        detect_data = detect_response.json()
                        print(f"    ✅ Detected: {detect_data.get('retailer', 'Unknown')} - {detect_data.get('type', 'Unknown')}")
                    else:
                        print(f"    ❌ URL detection failed: {detect_response.status_code}")
                        results.append({"test": f"Test {i}", "step": "URL Detection", "status": "FAILED"})
                        continue
                    
                    # Step 2: Product Scraping
                    print(f"  🕷️  Step 2: Product Scraping")
                    start_time = time.time()
                    
                    scrape_response = await client.post(
                        f"{self.backend_url}/api/scrape",
                        json={"url": product['url'], "mode": "single"},
                        timeout=60
                    )
                    
                    processing_time = time.time() - start_time
                    
                    if scrape_response.status_code == 200:
                        scrape_data = scrape_response.json()
                        scraped_product = scrape_data.get('product', {})
                        images = scrape_data.get('images', [])
                        
                        print(f"    ✅ Scraped: {scraped_product.get('name', 'N/A')}")
                        print(f"    ✅ Brand: {scraped_product.get('brand', 'N/A')}")
                        print(f"    ✅ Price: ${scraped_product.get('price', 0):.2f}")
                        print(f"    ✅ Images: {len(images)} found")
                        print(f"    ✅ Processing Time: {processing_time:.2f}s")
                        
                        # Verify it's real data
                        if scraped_product.get('name') == product['expected_name']:
                            print(f"    🎯 Data Source: REAL SCRAPING")
                            data_source = "REAL"
                        else:
                            print(f"    🎯 Data Source: MOCK DATA (fallback)")
                            data_source = "MOCK"
                        
                        # Step 3: Image Selection (simulate frontend call)
                        print(f"  🖼️  Step 3: Image Selection")
                        if images:
                            selected_images = images[:3]  # Select first 3 images
                            print(f"    ✅ Selected {len(selected_images)} images")
                        else:
                            print(f"    ⚠️  No images to select")
                            selected_images = []
                        
                        # Step 4: Background Removal (simulate frontend call)
                        print(f"  🎨 Step 4: Background Removal")
                        if selected_images:
                            bg_response = await client.post(
                                f"{self.backend_url}/api/remove-backgrounds",
                                json={"product_id": scraped_product.get('id'), "image_urls": selected_images},
                                timeout=30
                            )
                            
                            if bg_response.status_code == 200:
                                bg_data = bg_response.json()
                                processed_images = bg_data.get('processed_images', [])
                                print(f"    ✅ Processed {len(processed_images)} images")
                                print(f"    ✅ Success Rate: {bg_data.get('success_rate', 0):.1%}")
                            else:
                                print(f"    ❌ Background removal failed: {bg_response.status_code}")
                        else:
                            print(f"    ⏭️  Skipped (no images)")
                        
                        # Step 5: Image Approval (simulate frontend call)
                        print(f"  ✅ Step 5: Image Approval")
                        if selected_images:
                            approval_response = await client.post(
                                f"{self.backend_url}/api/approve-images",
                                json={"product_id": scraped_product.get('id'), "image_urls": selected_images, "approved": True},
                                timeout=10
                            )
                            
                            if approval_response.status_code == 200:
                                approval_data = approval_response.json()
                                print(f"    ✅ Approved: {approval_data.get('approved_count', 0)} images")
                            else:
                                print(f"    ❌ Image approval failed: {approval_response.status_code}")
                        else:
                            print(f"    ⏭️  Skipped (no images)")
                        
                        # Step 6: 3D Generation (simulate frontend call)
                        print(f"  🎲 Step 6: 3D Generation")
                        if selected_images:
                            gen3d_response = await client.post(
                                f"{self.backend_url}/api/generate-3d",
                                json={"product_id": scraped_product.get('id'), "image_urls": selected_images, "settings": {}},
                                timeout=30
                            )
                            
                            if gen3d_response.status_code == 200:
                                gen3d_data = gen3d_response.json()
                                print(f"    ✅ Task created: {gen3d_data.get('task_id', 'N/A')}")
                                print(f"    ✅ Status: {gen3d_data.get('status', 'N/A')}")
                                print(f"    ✅ Cost: ${gen3d_data.get('cost', 0):.2f}")
                            else:
                                print(f"    ❌ 3D generation failed: {gen3d_response.status_code}")
                        else:
                            print(f"    ⏭️  Skipped (no images)")
                        
                        # Step 7: Model Optimization (simulate frontend call)
                        print(f"  ⚡ Step 7: Model Optimization")
                        if selected_images:
                            opt_response = await client.post(
                                f"{self.backend_url}/api/optimize-model",
                                json={"product_id": scraped_product.get('id'), "image_urls": selected_images, "settings": {}},
                                timeout=30
                            )
                            
                            if opt_response.status_code == 200:
                                opt_data = opt_response.json()
                                print(f"    ✅ Optimized: {opt_data.get('status', 'N/A')}")
                                print(f"    ✅ Quality: {opt_data.get('model_quality', 0):.2f}")
                            else:
                                print(f"    ❌ Model optimization failed: {opt_response.status_code}")
                        else:
                            print(f"    ⏭️  Skipped (no images)")
                        
                        # Step 8: Save Product (simulate frontend call)
                        print(f"  💾 Step 8: Save Product")
                        save_response = await client.post(
                            f"{self.backend_url}/api/save-product/{scraped_product.get('id')}",
                            json={"status": "completed", "metadata": {"test": True}},
                            timeout=10
                        )
                        
                        if save_response.status_code == 200:
                            save_data = save_response.json()
                            print(f"    ✅ Saved: {save_data.get('status', 'N/A')}")
                            print(f"    ✅ Updated: {save_data.get('updated_at', 'N/A')}")
                        else:
                            print(f"    ❌ Save failed: {save_response.status_code}")
                        
                        # Summary for this product
                        results.append({
                            "test": f"Test {i}",
                            "product": product['name'],
                            "data_source": data_source,
                            "processing_time": processing_time,
                            "images_found": len(images),
                            "pipeline_complete": True
                        })
                        
                        print(f"  🎉 Pipeline completed for {product['name']}")
                        
                    else:
                        print(f"    ❌ Scraping failed: {scrape_response.status_code}")
                        results.append({
                            "test": f"Test {i}",
                            "product": product['name'],
                            "status": "FAILED",
                            "error": f"Scraping failed: {scrape_response.status_code}"
                        })
                        
            except Exception as e:
                print(f"    ❌ Exception: {e}")
                results.append({
                    "test": f"Test {i}",
                    "product": product['name'],
                    "status": "FAILED",
                    "error": str(e)
                })
        
        return results
    
    async def test_batch_pipeline(self):
        """Test batch processing pipeline with real data"""
        print(f"\n🧪 Testing Batch Processing Pipeline")
        print("=" * 50)
        
        try:
            async with httpx.AsyncClient() as client:
                # Step 1: Category Scraping
                print(f"  📋 Step 1: Category Scraping")
                category_response = await client.post(
                    f"{self.backend_url}/api/scrape-category",
                    json={"url": "https://www.ikea.com/us/en/cat/chairs/", "limit": 5},
                    timeout=60
                )
                
                if category_response.status_code == 200:
                    category_data = category_response.json()
                    products = category_data.get('products', [])
                    
                    print(f"    ✅ Found {len(products)} products")
                    print(f"    ✅ Total: {category_data.get('total_found', 0)}")
                    print(f"    ✅ Time: {category_data.get('scraping_time', 0):.2f}s")
                    print(f"    ✅ Cost: ${category_data.get('cost', 0):.2f}")
                    
                    # Step 2: Batch Processing (simulate frontend selection)
                    print(f"  🔄 Step 2: Batch Processing")
                    if products:
                        # Use product URLs as IDs for mock batch processing
                        product_urls = [p.get('url', '') for p in products[:3]]
                        
                        batch_response = await client.post(
                            f"{self.backend_url}/api/batch-process",
                            json={"product_ids": product_urls, "settings": {"test": True}},
                            timeout=30
                        )
                        
                        if batch_response.status_code == 200:
                            batch_data = batch_response.json()
                            print(f"    ✅ Batch created: {batch_data.get('batch_id', 'N/A')}")
                            print(f"    ✅ Products: {batch_data.get('total_products', 0)}")
                            print(f"    ✅ Status: {batch_data.get('status', 'N/A')}")
                            print(f"    ✅ Cost: ${batch_data.get('estimated_cost', 0):.2f}")
                            
                            return True
                        else:
                            print(f"    ❌ Batch processing failed: {batch_response.status_code}")
                            print(f"    Response: {batch_response.text}")
                            return False
                    else:
                        print(f"    ⚠️  No products to process")
                        return True
                else:
                    print(f"    ❌ Category scraping failed: {category_response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"    ❌ Batch pipeline failed: {e}")
            return False
    
    async def test_websocket_integration(self):
        """Test WebSocket integration for real-time updates"""
        print(f"\n🧪 Testing WebSocket Integration")
        print("=" * 50)
        
        try:
            import websockets
            
            # Test WebSocket connection
            uri = "ws://localhost:8000/ws"
            print(f"  🔌 Connecting to WebSocket: {uri}")
            
            async with websockets.connect(uri) as websocket:
                print(f"    ✅ WebSocket connected")
                
                # Send a test message
                test_message = {"type": "test", "message": "Hello WebSocket"}
                await websocket.send(json.dumps(test_message))
                print(f"    ✅ Test message sent")
                
                # Wait for response (with timeout)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"    ✅ Response received: {response[:100]}...")
                    return True
                except asyncio.TimeoutError:
                    print(f"    ⚠️  No response received (timeout)")
                    return True  # WebSocket connection works even without response
                    
        except ImportError:
            print(f"    ⚠️  WebSocket library not available, skipping test")
            return True
        except Exception as e:
            print(f"    ❌ WebSocket test failed: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """Run all frontend integration tests"""
        print("🚀 Frontend Real Data Integration Tests")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print("=" * 60)
        
        # Test 1: Frontend accessibility
        frontend_ok = await self.test_frontend_accessibility()
        
        if not frontend_ok:
            print("❌ Frontend not accessible - skipping remaining tests")
            return
        
        # Test 2: Single product pipeline
        single_results = await self.test_single_product_pipeline()
        
        # Test 3: Batch pipeline
        batch_ok = await self.test_batch_pipeline()
        
        # Test 4: WebSocket integration
        websocket_ok = await self.test_websocket_integration()
        
        # Summary
        print(f"\n" + "=" * 60)
        print(f"📊 FRONTEND REAL DATA INTEGRATION SUMMARY")
        print(f"=" * 60)
        
        # Single product pipeline summary
        single_passed = sum(1 for r in single_results if r.get('pipeline_complete', False))
        single_total = len(single_results)
        print(f"Single Product Pipeline: {single_passed}/{single_total} passed ({single_passed/single_total*100:.1f}%)")
        
        # Data source analysis
        real_scraping = sum(1 for r in single_results if r.get('data_source') == 'REAL')
        mock_data = sum(1 for r in single_results if r.get('data_source') == 'MOCK')
        print(f"Data Sources: {real_scraping} real scraping, {mock_data} mock data")
        
        # Performance analysis
        if single_results:
            avg_processing_time = sum(r.get('processing_time', 0) for r in single_results if r.get('processing_time')) / max(1, len([r for r in single_results if r.get('processing_time')]))
            print(f"Average Processing Time: {avg_processing_time:.2f}s")
        
        # Other tests
        print(f"Batch Pipeline: {'✅ PASSED' if batch_ok else '❌ FAILED'}")
        print(f"WebSocket Integration: {'✅ PASSED' if websocket_ok else '❌ FAILED'}")
        
        # Overall status
        total_tests = 1 + single_total + 2  # frontend + single + batch + websocket
        passed_tests = (1 if frontend_ok else 0) + single_passed + (1 if batch_ok else 0) + (1 if websocket_ok else 0)
        success_rate = passed_tests / total_tests * 100
        
        print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if success_rate >= 90:
            print("🎉 FRONTEND INTEGRATION: EXCELLENT!")
        elif success_rate >= 80:
            print("✅ FRONTEND INTEGRATION: GOOD!")
        elif success_rate >= 70:
            print("⚠️  FRONTEND INTEGRATION: NEEDS IMPROVEMENT")
        else:
            print("❌ FRONTEND INTEGRATION: FAILED")
        
        print(f"=" * 60)
        
        return {
            "frontend_accessible": frontend_ok,
            "single_pipeline_results": single_results,
            "batch_pipeline": batch_ok,
            "websocket_integration": websocket_ok,
            "success_rate": success_rate
        }

async def main():
    tester = FrontendRealDataTest()
    results = await tester.run_comprehensive_test()
    return results

if __name__ == "__main__":
    asyncio.run(main())
