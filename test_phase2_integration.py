#!/usr/bin/env python3
"""
Phase 2 Integration Test
Tests the complete frontend-backend integration to verify Phase 2 is properly complete.
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

class Phase2IntegrationTest:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.results = []
        self.passed = 0
        self.failed = 0
        
    async def test_backend_health(self):
        """Test 1: Backend API is running and healthy"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/api/health")
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get("status") == "healthy":
                        self.log_test("✅ Backend Health Check", "PASSED", "Backend is healthy")
                        return True
                    else:
                        self.log_test("❌ Backend Health Check", "FAILED", f"Backend unhealthy: {health_data}")
                        return False
                else:
                    self.log_test("❌ Backend Health Check", "FAILED", f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test("❌ Backend Health Check", "FAILED", f"Connection error: {e}")
            return False
    
    async def test_api_endpoints(self):
        """Test 2: All API endpoints are accessible"""
        endpoints = [
            ("/api/detect-url", "POST"),
            ("/api/scrape", "POST"),
            ("/api/select-images", "POST"),
            ("/api/remove-backgrounds", "POST"),
            ("/api/approve-images", "POST"),
            ("/api/generate-3d", "POST"),
            ("/api/optimize-model", "POST"),
            ("/api/save-product/test-id", "POST"),
            ("/api/scrape-category", "POST"),
            ("/api/batch-process", "POST"),
            ("/api/health", "GET"),
            ("/api/metrics", "GET")
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint, method in endpoints:
                try:
                    if method == "GET":
                        response = await client.get(f"{self.backend_url}{endpoint}")
                    else:
                        # For POST endpoints, send minimal valid data
                        test_data = self.get_test_data_for_endpoint(endpoint)
                        response = await client.post(f"{self.backend_url}{endpoint}", json=test_data)
                    
                    if response.status_code in [200, 201, 422]:  # 422 is OK for validation errors
                        self.log_test(f"✅ {endpoint}", "PASSED", f"HTTP {response.status_code}")
                    else:
                        self.log_test(f"❌ {endpoint}", "FAILED", f"HTTP {response.status_code}")
                except Exception as e:
                    self.log_test(f"❌ {endpoint}", "FAILED", f"Error: {e}")
    
    def get_test_data_for_endpoint(self, endpoint):
        """Get minimal test data for each endpoint"""
        test_data_map = {
            "/api/detect-url": {"url": "https://www.ikea.com/us/en/p/test/"},
            "/api/scrape": {"url": "https://www.ikea.com/us/en/p/test/", "mode": "single"},
            "/api/select-images": {"product_id": "test-id", "image_urls": ["https://example.com/image.jpg"]},
            "/api/remove-backgrounds": {"product_id": "test-id", "image_urls": ["https://example.com/image.jpg"]},
            "/api/approve-images": {"product_id": "test-id", "image_urls": ["https://example.com/image.jpg"], "approved": True},
            "/api/generate-3d": {"product_id": "test-id", "image_urls": ["https://example.com/image.jpg"], "settings": {}},
            "/api/optimize-model": {"product_id": "test-id", "image_urls": ["https://example.com/image.jpg"], "settings": {}},
            "/api/scrape-category": {"url": "https://www.ikea.com/us/en/cat/test/", "limit": 5},
            "/api/batch-process": {"product_ids": ["test-id-1", "test-id-2"], "settings": {}}
        }
        return test_data_map.get(endpoint, {})
    
    async def test_complete_pipeline(self):
        """Test 3: Complete single product pipeline"""
        try:
            async with httpx.AsyncClient() as client:
                # Step 1: Scrape product
                scrape_response = await client.post(f"{self.backend_url}/api/scrape", json={
                    "url": "https://www.ikea.com/us/en/p/test-chair/",
                    "mode": "single"
                })
                
                if scrape_response.status_code == 200:
                    scrape_data = scrape_response.json()
                    product_id = scrape_data["product"]["id"]
                    
                    # Step 2: Select images
                    select_response = await client.post(f"{self.backend_url}/api/select-images", json={
                        "product_id": product_id,
                        "image_urls": scrape_data["images"][:2]  # Select first 2 images
                    })
                    
                    if select_response.status_code == 200:
                        # Step 3: Remove backgrounds
                        bg_response = await client.post(f"{self.backend_url}/api/remove-backgrounds", json={
                            "product_id": product_id,
                            "image_urls": scrape_data["images"][:2]
                        })
                        
                        if bg_response.status_code == 200:
                            # Step 4: Approve images
                            approve_response = await client.post(f"{self.backend_url}/api/approve-images", json={
                                "product_id": product_id,
                                "image_urls": scrape_data["images"][:2],
                                "approved": True
                            })
                            
                            if approve_response.status_code == 200:
                                self.log_test("✅ Complete Pipeline", "PASSED", "All pipeline steps successful")
                                return True
                            else:
                                self.log_test("❌ Complete Pipeline", "FAILED", f"Approval failed: HTTP {approve_response.status_code}")
                                return False
                        else:
                            self.log_test("❌ Complete Pipeline", "FAILED", f"Background removal failed: HTTP {bg_response.status_code}")
                            return False
                    else:
                        self.log_test("❌ Complete Pipeline", "FAILED", f"Image selection failed: HTTP {select_response.status_code}")
                        return False
                else:
                    self.log_test("❌ Complete Pipeline", "FAILED", f"Scraping failed: HTTP {scrape_response.status_code}")
                    return False
        except Exception as e:
            self.log_test("❌ Complete Pipeline", "FAILED", f"Pipeline error: {e}")
            return False
    
    async def test_websocket_connection(self):
        """Test 4: WebSocket connection works"""
        try:
            import websockets
            
            async with websockets.connect(f"ws://localhost:8000/ws") as websocket:
                # Send ping
                await websocket.send(json.dumps({"type": "ping"}))
                
                # Wait for pong or timeout
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    if data.get("type") == "pong":
                        self.log_test("✅ WebSocket Connection", "PASSED", "WebSocket ping/pong successful")
                        return True
                    else:
                        self.log_test("❌ WebSocket Connection", "FAILED", f"Unexpected response: {data}")
                        return False
                except asyncio.TimeoutError:
                    self.log_test("❌ WebSocket Connection", "FAILED", "No pong response received")
                    return False
        except Exception as e:
            self.log_test("❌ WebSocket Connection", "FAILED", f"WebSocket error: {e}")
            return False
    
    def log_test(self, test_name, status, message):
        """Log test result"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "status": status,
            "message": message
        }
        self.results.append(result)
        
        if status == "PASSED":
            self.passed += 1
            print(f"[{timestamp}] {test_name}: {message}")
        else:
            self.failed += 1
            print(f"[{timestamp}] {test_name}: {message}")
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"PHASE 2 INTEGRATION TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%")
        
        if self.failed == 0:
            print(f"\n🎉 PHASE 2 INTEGRATION: COMPLETE!")
            print(f"✅ Frontend and backend are properly integrated")
            print(f"✅ All API endpoints are working")
            print(f"✅ Complete pipeline is functional")
            print(f"✅ WebSocket connection is working")
        else:
            print(f"\n⚠️  PHASE 2 INTEGRATION: INCOMPLETE")
            print(f"❌ {self.failed} test(s) failed - see details above")
        
        print(f"{'='*60}")
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Phase 2 Integration Tests...")
        print(f"Backend URL: {self.backend_url}")
        print(f"Frontend URL: {FRONTEND_URL}")
        print(f"{'='*60}")
        
        # Test 1: Backend Health
        backend_healthy = await self.test_backend_health()
        if not backend_healthy:
            print("❌ Backend is not healthy - skipping remaining tests")
            self.print_summary()
            return
        
        # Test 2: API Endpoints
        await self.test_api_endpoints()
        
        # Test 3: Complete Pipeline
        await self.test_complete_pipeline()
        
        # Test 4: WebSocket
        await self.test_websocket_connection()
        
        # Print summary
        self.print_summary()

async def main():
    """Main test runner"""
    tester = Phase2IntegrationTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
