#!/usr/bin/env python3
"""
Clean up duplicate processed images from the database
"""

import sys
sys.path.append('.')

from app.core.database import get_db
from app.models import ProductImage, ProcessingStage
from sqlalchemy.orm import Session
from collections import Counter

def cleanup_duplicates():
    print("=" * 60)
    print("CLEANING UP DUPLICATE PROCESSED IMAGES")
    print("=" * 60)
    
    db = next(get_db())
    try:
        # Get all processed images
        processed_images = db.query(ProductImage).filter(
            ProductImage.image_type == 'processed'
        ).all()
        
        print(f"Total processed images in database: {len(processed_images)}")
        
        # Group by product_id and s3_url
        grouped = {}
        for img in processed_images:
            key = (str(img.product_id), img.s3_url)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(img)
        
        # Find and clean up duplicates
        duplicates_found = 0
        for key, images in grouped.items():
            if len(images) > 1:
                duplicates_found += 1
                product_id, s3_url = key
                print(f"\n❌ DUPLICATE FOUND:")
                print(f"   Product ID: {product_id}")
                print(f"   URL: {s3_url}")
                print(f"   Count: {len(images)}")
                
                # Keep the first one, delete the rest
                keep_image = images[0]
                delete_images = images[1:]
                
                print(f"   Keeping: {keep_image.id}")
                print(f"   Deleting: {[str(img.id) for img in delete_images]}")
                
                for img in delete_images:
                    db.delete(img)
                
                print(f"   ✅ Deleted {len(delete_images)} duplicate(s)")
        
        if duplicates_found == 0:
            print("✅ No duplicates found in database")
        else:
            print(f"\n🧹 Cleaned up {duplicates_found} duplicate groups")
        
        # Also clean up duplicate processing stages
        print(f"\n🔄 Checking for duplicate processing stages...")
        bg_stages = db.query(ProcessingStage).filter(
            ProcessingStage.stage_name == 'background_removal'
        ).all()
        
        # Group by product_id
        stage_groups = {}
        for stage in bg_stages:
            product_id = str(stage.product_id)
            if product_id not in stage_groups:
                stage_groups[product_id] = []
            stage_groups[product_id].append(stage)
        
        # Remove duplicate stages
        duplicate_stages = 0
        for product_id, stages in stage_groups.items():
            if len(stages) > 1:
                duplicate_stages += 1
                print(f"   Product {product_id}: {len(stages)} background removal stages")
                
                # Keep the first one, delete the rest
                keep_stage = stages[0]
                delete_stages = stages[1:]
                
                for stage in delete_stages:
                    db.delete(stage)
                
                print(f"   ✅ Deleted {len(delete_stages)} duplicate stage(s)")
        
        if duplicate_stages == 0:
            print("✅ No duplicate processing stages found")
        else:
            print(f"🧹 Cleaned up {duplicate_stages} duplicate stage groups")
        
        db.commit()
        
        # Final count
        final_count = db.query(ProductImage).filter(
            ProductImage.image_type == 'processed'
        ).count()
        print(f"\n📊 Final processed images count: {final_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_duplicates()
