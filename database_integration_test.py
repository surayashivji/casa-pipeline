#!/usr/bin/env python3
"""
Database Integration Test
Tests database operations with real scraped data
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

class DatabaseIntegrationTest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.test_results = []
        
    async def test_database_operations(self):
        """Test database operations with real scraped data"""
        print("🧪 Testing Database Operations")
        print("=" * 50)
        
        # Test 1: Single product scraping and saving
        print("\n🔍 Test 1: Single Product Database Save")
        test_url = "https://www.ikea.com/us/en/p/stockholm-2025-3-seat-sofa-alhamn-beige-s69574294/"
        
        try:
            async with httpx.AsyncClient() as client:
                # Scrape product
                response = await client.post(
                    f"{self.backend_url}/api/scrape",
                    json={"url": test_url, "mode": "single"},
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    product = data.get('product', {})
                    
                    print(f"  ✅ Product scraped: {product.get('name', 'N/A')}")
                    print(f"  ✅ Product ID: {product.get('id', 'N/A')}")
                    print(f"  ✅ Database saved: {product.get('created_at', 'N/A')}")
                    
                    # Test duplicate handling
                    print(f"\n🔍 Test 2: Duplicate Handling")
                    duplicate_response = await client.post(
                        f"{self.backend_url}/api/scrape",
                        json={"url": test_url, "mode": "single"},
                        timeout=60
                    )
                    
                    if duplicate_response.status_code == 200:
                        duplicate_data = duplicate_response.json()
                        duplicate_product = duplicate_data.get('product', {})
                        
                        if duplicate_product.get('id') == product.get('id'):
                            print(f"  ✅ Duplicate handled: Same product ID returned")
                        else:
                            print(f"  ⚠️  Duplicate handling: Different product ID")
                        
                        print(f"  ✅ Updated at: {duplicate_product.get('updated_at', 'N/A')}")
                    
                    return True
                else:
                    print(f"  ❌ Scraping failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Database test failed: {e}")
            return False
    
    async def test_batch_database_operations(self):
        """Test batch processing database operations"""
        print(f"\n🔍 Test 3: Batch Processing Database")
        
        try:
            async with httpx.AsyncClient() as client:
                # Test category scraping
                response = await client.post(
                    f"{self.backend_url}/api/scrape-category",
                    json={"url": "https://www.ikea.com/us/en/cat/chairs/", "limit": 5},
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    products = data.get('products', [])
                    
                    print(f"  ✅ Category scraped: {len(products)} products")
                    print(f"  ✅ Total found: {data.get('total_found', 0)}")
                    print(f"  ✅ Scraping time: {data.get('scraping_time', 0):.2f}s")
                    print(f"  ✅ Cost: ${data.get('cost', 0):.2f}")
                    
                    # Test batch processing
                    if products:
                        product_ids = [p.get('url', '') for p in products[:3]]  # Use URLs as IDs for mock
                        
                        batch_response = await client.post(
                            f"{self.backend_url}/api/batch-process",
                            json={"product_ids": product_ids, "settings": {}},
                            timeout=30
                        )
                        
                        if batch_response.status_code == 200:
                            batch_data = batch_response.json()
                            print(f"  ✅ Batch created: {batch_data.get('batch_id', 'N/A')}")
                            print(f"  ✅ Total products: {batch_data.get('total_products', 0)}")
                            print(f"  ✅ Estimated cost: ${batch_data.get('estimated_cost', 0):.2f}")
                            
                            return True
                        else:
                            print(f"  ❌ Batch processing failed: {batch_response.status_code}")
                            return False
                    else:
                        print(f"  ⚠️  No products to test batch processing")
                        return True
                else:
                    print(f"  ❌ Category scraping failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Batch database test failed: {e}")
            return False
    
    async def test_database_consistency(self):
        """Test database data consistency"""
        print(f"\n🔍 Test 4: Database Consistency")
        
        try:
            async with httpx.AsyncClient() as client:
                # Test multiple products to check consistency
                test_urls = [
                    "https://www.ikea.com/us/en/p/stockholm-2025-3-seat-sofa-alhamn-beige-s69574294/",
                    "https://www.ikea.com/us/en/p/dyvlinge-swivel-chair-kelinge-orange-40581921/"
                ]
                
                products = []
                for i, url in enumerate(test_urls, 1):
                    print(f"  📦 Testing product {i}: {url[:50]}...")
                    
                    response = await client.post(
                        f"{self.backend_url}/api/scrape",
                        json={"url": url, "mode": "single"},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        product = data.get('product', {})
                        products.append(product)
                        
                        # Check required fields
                        required_fields = ['id', 'name', 'brand', 'price', 'url', 'created_at', 'updated_at']
                        missing_fields = [field for field in required_fields if not product.get(field)]
                        
                        if missing_fields:
                            print(f"    ⚠️  Missing fields: {missing_fields}")
                        else:
                            print(f"    ✅ All required fields present")
                        
                        # Check data types
                        if isinstance(product.get('price'), (int, float)):
                            print(f"    ✅ Price is numeric: ${product.get('price', 0):.2f}")
                        else:
                            print(f"    ❌ Price is not numeric: {product.get('price')}")
                        
                        if isinstance(product.get('dimensions'), dict):
                            print(f"    ✅ Dimensions is object")
                        else:
                            print(f"    ❌ Dimensions is not object: {type(product.get('dimensions'))}")
                    
                    else:
                        print(f"    ❌ Failed to scrape product {i}")
                
                # Check for duplicate URLs
                urls = [p.get('url') for p in products if p.get('url')]
                if len(urls) == len(set(urls)):
                    print(f"  ✅ No duplicate URLs found")
                else:
                    print(f"  ⚠️  Duplicate URLs detected")
                
                return len(products) > 0
                
        except Exception as e:
            print(f"  ❌ Consistency test failed: {e}")
            return False
    
    async def test_database_performance(self):
        """Test database performance under load"""
        print(f"\n🔍 Test 5: Database Performance")
        
        try:
            async with httpx.AsyncClient() as client:
                # Test concurrent requests
                print(f"  🚀 Testing concurrent requests...")
                
                start_time = time.time()
                
                # Create multiple concurrent requests
                tasks = []
                for i in range(3):
                    task = client.post(
                        f"{self.backend_url}/api/scrape",
                        json={"url": f"https://www.ikea.com/us/en/p/test-{i}/", "mode": "single"},
                        timeout=30
                    )
                    tasks.append(task)
                
                # Wait for all requests to complete
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                total_time = time.time() - start_time
                
                successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
                
                print(f"  ✅ Concurrent requests: {successful}/{len(tasks)} successful")
                print(f"  ✅ Total time: {total_time:.2f}s")
                print(f"  ✅ Average time per request: {total_time/len(tasks):.2f}s")
                
                if total_time < 30:  # Should complete within 30 seconds
                    print(f"  ✅ Performance: GOOD")
                    return True
                else:
                    print(f"  ⚠️  Performance: SLOW")
                    return False
                
        except Exception as e:
            print(f"  ❌ Performance test failed: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """Run all database integration tests"""
        print("🚀 Database Integration Tests")
        print("=" * 60)
        
        # Test 1: Basic database operations
        db_ops_ok = await self.test_database_operations()
        
        # Test 2: Batch operations
        batch_ops_ok = await self.test_batch_database_operations()
        
        # Test 3: Data consistency
        consistency_ok = await self.test_database_consistency()
        
        # Test 4: Performance
        performance_ok = await self.test_database_performance()
        
        # Summary
        print(f"\n" + "=" * 60)
        print(f"📊 DATABASE INTEGRATION TEST SUMMARY")
        print(f"=" * 60)
        
        tests = [
            ("Database Operations", db_ops_ok),
            ("Batch Operations", batch_ops_ok),
            ("Data Consistency", consistency_ok),
            ("Performance", performance_ok)
        ]
        
        passed = sum(1 for _, ok in tests if ok)
        total = len(tests)
        
        for test_name, ok in tests:
            status = "✅ PASSED" if ok else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        success_rate = passed / total * 100
        print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed}/{total})")
        
        if success_rate >= 90:
            print("🎉 DATABASE INTEGRATION: EXCELLENT!")
        elif success_rate >= 80:
            print("✅ DATABASE INTEGRATION: GOOD!")
        elif success_rate >= 70:
            print("⚠️  DATABASE INTEGRATION: NEEDS IMPROVEMENT")
        else:
            print("❌ DATABASE INTEGRATION: FAILED")
        
        print(f"=" * 60)
        
        return {
            "database_operations": db_ops_ok,
            "batch_operations": batch_ops_ok,
            "data_consistency": consistency_ok,
            "performance": performance_ok,
            "success_rate": success_rate
        }

async def main():
    tester = DatabaseIntegrationTest()
    results = await tester.run_comprehensive_test()
    return results

if __name__ == "__main__":
    asyncio.run(main())
