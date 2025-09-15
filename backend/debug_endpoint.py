#!/usr/bin/env python3
"""
Debug the /remove-backgrounds endpoint locally
"""

import asyncio
import sys
import os
import uuid
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.models import Product, ProductImage, ProcessingStage
from app.services.background_removal.manager import BackgroundRemovalManager

async def debug_endpoint():
    """Debug the endpoint logic step by step"""
    print("=" * 60)
    print("DEBUGGING /remove-backgrounds ENDPOINT")
    print("=" * 60)
    
    try:
        # 1. Test database connection
        print("\n1. Testing database connection...")
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        print("   ✅ Database connected")
        
        # 2. Test product creation
        print("\n2. Testing product creation...")
        test_product_id = str(uuid.uuid4())
        product = Product(
            id=test_product_id,
            url=f"https://test.example.com/{test_product_id}",  # Unique URL
            name="Test Product",
            brand="Test",
            status="scraped"
        )
        db.add(product)
        db.commit()
        print(f"   ✅ Product created: {test_product_id}")
        
        # 3. Test BackgroundRemovalManager
        print("\n3. Testing BackgroundRemovalManager...")
        bg_manager = BackgroundRemovalManager()
        print("   ✅ Manager initialized")
        
        # 4. Test image processing
        print("\n4. Testing image processing...")
        test_url = "https://www.ikea.com/us/en/images/products/ektorp-sofa-lofallet-beige__0818567_pe774489_s5.jpg"
        result = await bg_manager.process_image(
            image_url=test_url,
            product_id=test_product_id,
            image_order=0
        )
        print(f"   Result: {result.get('success')}")
        if result.get('success'):
            print(f"   ✅ Image processed successfully")
            print(f"   Quality: {result.get('quality_score', 0):.2f}")
        else:
            print(f"   ❌ Image processing failed: {result.get('error')}")
            return False
        
        # 5. Test ProductImage creation
        print("\n5. Testing ProductImage creation...")
        try:
            processed_image = ProductImage(
                product_id=test_product_id,
                image_type='processed',
                image_order=0,
                s3_url=result.get('processed_url', test_url),
                local_path=result.get('local_path'),
                file_size_bytes=len(result.get('image_data', b'')),
                width_pixels=1400,
                height_pixels=1400,
                format='PNG',
                is_primary=True
            )
            db.add(processed_image)
            db.commit()
            print("   ✅ ProductImage created successfully")
        except Exception as e:
            print(f"   ❌ ProductImage creation failed: {e}")
            return False
        
        # 6. Test ProcessingStage creation
        print("\n6. Testing ProcessingStage creation...")
        try:
            stage = ProcessingStage(
                product_id=test_product_id,
                stage_name="background_removal",
                stage_order=3,
                status="completed",
                processing_time_seconds=result.get('processing_time', 0),
                cost_usd=result.get('cost', 0),
                input_data={"image_count": 1},
                output_data={
                    "successful": 1,
                    "failed": 0,
                    "avg_quality": result.get('quality_score', 0)
                }
            )
            db.add(stage)
            db.commit()
            print("   ✅ ProcessingStage created successfully")
        except Exception as e:
            print(f"   ❌ ProcessingStage creation failed: {e}")
            return False
        
        # 7. Test WebSocket manager
        print("\n7. Testing WebSocket manager...")
        try:
            from app.websocket_manager import manager
            print("   ✅ WebSocket manager imported")
            # Don't actually send - just test import
        except Exception as e:
            print(f"   ❌ WebSocket manager failed: {e}")
            return False
        
        print(f"\n" + "=" * 60)
        print(f"✅ ALL TESTS PASSED - ENDPOINT SHOULD WORK!")
        print(f"=" * 60)
        
        return True
        
    except Exception as e:
        import traceback
        print(f"\n❌ DEBUG FAILED: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = asyncio.run(debug_endpoint())
    sys.exit(0 if success else 1)
