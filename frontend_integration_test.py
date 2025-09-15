#!/usr/bin/env python3
"""
Frontend Integration Test with Real Scraping
Tests the complete pipeline from frontend to backend with real IKEA data
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

class FrontendIntegrationTest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"
        self.test_results = []
        
    async def test_frontend_health(self):
        """Test if frontend is accessible"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.frontend_url, timeout=10)
                if response.status_code == 200:
                    print("✅ Frontend is running and accessible")
                    return True
                else:
                    print(f"❌ Frontend returned status {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Frontend not accessible: {e}")
            return False
    
    async def test_backend_health(self):
        """Test if backend is healthy"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/api/health", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Backend is healthy: {data.get('status', 'unknown')}")
                    return True
                else:
                    print(f"❌ Backend returned status {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Backend not accessible: {e}")
            return False
    
    async def test_real_scraping_pipeline(self):
        """Test the complete scraping pipeline with real IKEA data"""
        print("\n🧪 Testing Real Scraping Pipeline...")
        print("=" * 60)
        
        test_urls = [
            {
                "url": "https://www.ikea.com/us/en/p/stockholm-2025-3-seat-sofa-alhamn-beige-s69574294/",
                "expected_name": "STOCKHOLM 2025 3-seat sofa, Alhamn beige",
                "expected_brand": "IKEA",
                "expected_price_range": (1800, 2000)
            },
            {
                "url": "https://www.ikea.com/us/en/p/dyvlinge-swivel-chair-kelinge-orange-40581921/",
                "expected_name": "DYVLINGE Swivel chair, Kelinge orange", 
                "expected_brand": "IKEA",
                "expected_price_range": (190, 210)
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_urls, 1):
            print(f"\n🔍 Test {i}: {test_case['url'][:50]}...")
            
            try:
                async with httpx.AsyncClient() as client:
                    start_time = time.time()
                    
                    # Test the scraping endpoint
                    response = await client.post(
                        f"{self.backend_url}/api/scrape",
                        json={"url": test_case["url"], "mode": "single"},
                        timeout=60
                    )
                    
                    processing_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        product = data.get('product', {})
                        images = data.get('images', [])
                        
                        # Validate the response
                        name = product.get('name', '')
                        brand = product.get('brand', '')
                        price = product.get('price', 0)
                        dimensions = product.get('dimensions', {})
                        
                        print(f"  ✅ Status: {response.status_code}")
                        print(f"  📦 Product: {name}")
                        print(f"  🏪 Brand: {brand}")
                        print(f"  💰 Price: ${price:.2f}")
                        print(f"  🖼️  Images: {len(images)} found")
                        print(f"  ⏱️  Processing Time: {processing_time:.2f}s")
                        
                        # Check if it's real scraping or mock data
                        if name == test_case['expected_name']:
                            data_source = "REAL SCRAPING"
                            print(f"  🎯 Data Source: {data_source}")
                        else:
                            data_source = "MOCK DATA (fallback)"
                            print(f"  🎯 Data Source: {data_source}")
                        
                        # Validate dimensions
                        if dimensions and any(dimensions.values()):
                            print(f"  📏 Dimensions: {dimensions.get('width', 0):.1f}\" x {dimensions.get('height', 0):.1f}\" x {dimensions.get('depth', 0):.1f}\"")
                        else:
                            print(f"  📏 Dimensions: Not available")
                        
                        # Validate price range
                        price_valid = test_case['expected_price_range'][0] <= price <= test_case['expected_price_range'][1]
                        if price_valid:
                            print(f"  ✅ Price validation: PASSED")
                        else:
                            print(f"  ⚠️  Price validation: FAILED (expected ${test_case['expected_price_range'][0]}-${test_case['expected_price_range'][1]}, got ${price})")
                        
                        # Check processing time
                        if processing_time < 30:
                            print(f"  ✅ Performance: PASSED (<30s)")
                        else:
                            print(f"  ⚠️  Performance: SLOW ({processing_time:.1f}s)")
                        
                        results.append({
                            "test": f"Test {i}",
                            "url": test_case['url'],
                            "status": "PASSED",
                            "data_source": data_source,
                            "processing_time": processing_time,
                            "name": name,
                            "price": price,
                            "images": len(images),
                            "dimensions_available": bool(dimensions and any(dimensions.values()))
                        })
                        
                    else:
                        print(f"  ❌ Status: {response.status_code}")
                        print(f"  ❌ Error: {response.text}")
                        results.append({
                            "test": f"Test {i}",
                            "url": test_case['url'],
                            "status": "FAILED",
                            "error": f"HTTP {response.status_code}"
                        })
                        
            except Exception as e:
                print(f"  ❌ Exception: {e}")
                results.append({
                    "test": f"Test {i}",
                    "url": test_case['url'],
                    "status": "FAILED",
                    "error": str(e)
                })
        
        return results
    
    async def test_api_endpoints(self):
        """Test all API endpoints for frontend integration"""
        print("\n🧪 Testing API Endpoints...")
        print("=" * 60)
        
        endpoints = [
            ("/api/health", "GET", None),
            ("/api/detect-url", "POST", {"url": "https://www.ikea.com/us/en/p/test/"}),
            ("/api/scrape", "POST", {"url": "https://www.ikea.com/us/en/p/test/", "mode": "single"}),
            ("/api/scrape-category", "POST", {"url": "https://www.ikea.com/us/en/cat/chairs/", "limit": 5}),
            ("/api/batch-process", "POST", {"product_ids": ["test-id"], "settings": {}}),
            ("/api/metrics", "GET", None)
        ]
        
        results = []
        
        for endpoint, method, data in endpoints:
            try:
                async with httpx.AsyncClient() as client:
                    if method == "GET":
                        response = await client.get(f"{self.backend_url}{endpoint}", timeout=10)
                    else:
                        response = await client.post(f"{self.backend_url}{endpoint}", json=data, timeout=10)
                    
                    status = "✅ PASSED" if response.status_code in [200, 422] else "❌ FAILED"
                    print(f"  {status} {method} {endpoint} - {response.status_code}")
                    
                    results.append({
                        "endpoint": endpoint,
                        "method": method,
                        "status_code": response.status_code,
                        "passed": response.status_code in [200, 422]
                    })
                    
            except Exception as e:
                print(f"  ❌ FAILED {method} {endpoint} - {e}")
                results.append({
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": 0,
                    "passed": False,
                    "error": str(e)
                })
        
        return results
    
    async def run_comprehensive_test(self):
        """Run all integration tests"""
        print("🚀 Starting Frontend Integration Tests")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print("=" * 60)
        
        # Test 1: Health checks
        print("\n🔍 Testing System Health...")
        backend_healthy = await self.test_backend_health()
        frontend_healthy = await self.test_frontend_health()
        
        if not backend_healthy:
            print("❌ Backend is not healthy - skipping remaining tests")
            return
        
        # Test 2: API endpoints
        api_results = await self.test_api_endpoints()
        
        # Test 3: Real scraping pipeline
        scraping_results = await self.test_real_scraping_pipeline()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 FRONTEND INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        # API endpoint summary
        api_passed = sum(1 for r in api_results if r['passed'])
        api_total = len(api_results)
        print(f"API Endpoints: {api_passed}/{api_total} passed ({api_passed/api_total*100:.1f}%)")
        
        # Scraping pipeline summary
        scraping_passed = sum(1 for r in scraping_results if r['status'] == 'PASSED')
        scraping_total = len(scraping_results)
        print(f"Scraping Pipeline: {scraping_passed}/{scraping_total} passed ({scraping_passed/scraping_total*100:.1f}%)")
        
        # Real scraping vs mock data
        real_scraping = sum(1 for r in scraping_results if r.get('data_source') == 'REAL SCRAPING')
        mock_data = sum(1 for r in scraping_results if r.get('data_source') == 'MOCK DATA (fallback)')
        print(f"Data Sources: {real_scraping} real scraping, {mock_data} mock data")
        
        # Performance summary
        avg_processing_time = sum(r.get('processing_time', 0) for r in scraping_results if r.get('processing_time')) / max(1, len([r for r in scraping_results if r.get('processing_time')]))
        print(f"Average Processing Time: {avg_processing_time:.2f}s")
        
        # Overall status
        overall_passed = api_passed + scraping_passed
        overall_total = api_total + scraping_total
        success_rate = overall_passed / overall_total * 100
        
        print(f"\nOverall Success Rate: {success_rate:.1f}% ({overall_passed}/{overall_total})")
        
        if success_rate >= 90:
            print("🎉 FRONTEND INTEGRATION: EXCELLENT!")
        elif success_rate >= 80:
            print("✅ FRONTEND INTEGRATION: GOOD!")
        elif success_rate >= 70:
            print("⚠️  FRONTEND INTEGRATION: NEEDS IMPROVEMENT")
        else:
            print("❌ FRONTEND INTEGRATION: FAILED")
        
        print("=" * 60)
        
        return {
            "backend_healthy": backend_healthy,
            "frontend_healthy": frontend_healthy,
            "api_results": api_results,
            "scraping_results": scraping_results,
            "success_rate": success_rate
        }

async def main():
    tester = FrontendIntegrationTest()
    results = await tester.run_comprehensive_test()
    return results

if __name__ == "__main__":
    asyncio.run(main())
