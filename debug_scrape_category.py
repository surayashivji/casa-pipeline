#!/usr/bin/env python3
"""
Debug script for scrape-category endpoint
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.mock_data import MockDataService

def test_generate_mock_product():
    """Test the _generate_mock_product method directly"""
    try:
        print("Testing MockDataService._generate_mock_product...")
        result = MockDataService._generate_mock_product("https://www.ikea.com/us/en/p/test-chair/")
        print("✅ Method works!")
        print(f"Generated product: {result['name']} - ${result['price']}")
        return True
    except Exception as e:
        print(f"❌ Method failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_generate_mock_product()
