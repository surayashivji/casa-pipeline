#!/usr/bin/env python3
"""
Test script for admin endpoints
"""
import asyncio
import httpx
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminEndpointTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []

    async def _run_test(self, test_name, method, endpoint, params=None, expected_status=200):
        logger.info(f"\n🔍 Test: {test_name}")
        logger.info(f"   {method} {endpoint}")
        if params:
            logger.info(f"   Params: {params}")
        
        try:
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(f"{self.base_url}{endpoint}", params=params, timeout=30)
                else:
                    response = await client.request(method, f"{self.base_url}{endpoint}", json=params, timeout=30)
                
                logger.info(f"   Status: {response.status_code}")
                
                if response.status_code == expected_status:
                    data = response.json()
                    logger.info(f"   ✅ Success: {test_name}")
                    
                    # Log some key data
                    if isinstance(data, dict):
                        if 'products' in data:
                            logger.info(f"   📦 Products: {len(data['products'])}")
                        if 'images' in data:
                            logger.info(f"   🖼️  Images: {len(data['images'])}")
                        if 'stages' in data:
                            logger.info(f"   ⚙️  Stages: {len(data['stages'])}")
                        if 'total' in data:
                            logger.info(f"   📊 Total: {data['total']}")
                    
                    self.test_results.append(True)
                else:
                    logger.error(f"   ❌ Failed: Expected {expected_status}, got {response.status_code}")
                    logger.error(f"   Response: {response.text}")
                    self.test_results.append(False)
                    
        except Exception as e:
            logger.error(f"   ❌ Exception: {e}")
            self.test_results.append(False)

    async def run_tests(self):
        print("🧪 Testing Admin Endpoints")
        print("=" * 50)
        
        # Test 1: Get all products (basic)
        await self._run_test(
            "Get All Products (Basic)",
            "GET",
            "/api/products"
        )
        
        # Test 2: Get products with pagination
        await self._run_test(
            "Get Products with Pagination",
            "GET",
            "/api/products",
            {"limit": 5, "offset": 0}
        )
        
        # Test 3: Get products with filters
        await self._run_test(
            "Get Products with Filters",
            "GET",
            "/api/products",
            {"status": "scraped", "retailer": "IKEA"}
        )
        
        # Test 4: Get products with images included
        await self._run_test(
            "Get Products with Images",
            "GET",
            "/api/products",
            {"include_images": True, "limit": 3}
        )
        
        # Test 5: Get all images
        await self._run_test(
            "Get All Images",
            "GET",
            "/api/images"
        )
        
        # Test 6: Get images with filters
        await self._run_test(
            "Get Images with Filters",
            "GET",
            "/api/images",
            {"image_type": "original", "limit": 10}
        )
        
        # Test 7: Get all processing stages
        await self._run_test(
            "Get All Processing Stages",
            "GET",
            "/api/processing-stages"
        )
        
        # Test 8: Get processing stages with filters
        await self._run_test(
            "Get Processing Stages with Filters",
            "GET",
            "/api/processing-stages",
            {"status": "completed", "limit": 10}
        )
        
        # Test 9: Get specific product (if any exist)
        # First get a product ID
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/products", params={"limit": 1})
                if response.status_code == 200:
                    data = response.json()
                    if data.get('products') and len(data['products']) > 0:
                        product_id = data['products'][0]['id']
                        await self._run_test(
                            f"Get Specific Product ({product_id[:8]}...)",
                            "GET",
                            f"/api/products/{product_id}"
                        )
                    else:
                        logger.info("   ⚠️  No products found for specific product test")
                else:
                    logger.info("   ⚠️  Could not get products for specific product test")
        except Exception as e:
            logger.info(f"   ⚠️  Could not test specific product: {e}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Admin Endpoints Test Summary:")
        passed = sum(self.test_results)
        total = len(self.test_results)
        print(f"   ✅ Passed: {passed}/{total}")
        print(f"   ❌ Failed: {total - passed}/{total}")
        print(f"   📈 Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 All admin endpoints are working!")
        else:
            print(f"\n⚠️  {total - passed} endpoint(s) need attention")

if __name__ == "__main__":
    tester = AdminEndpointTester()
    asyncio.run(tester.run_tests())
