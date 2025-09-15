#!/usr/bin/env python3
"""
Cleanup script to remove all test products from the database
Deletes in proper order: processing_stages -> product_images -> products
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models import Product, ProductImage, ProcessingStage, Model3D, ModelLOD, BatchJob
from sqlalchemy.orm import Session
from sqlalchemy import text

def cleanup_test_products():
    print("=" * 60)
    print("CLEANING UP TEST PRODUCTS FROM DATABASE")
    print("=" * 60)
    
    db = next(get_db())
    
    try:
        # 1. Find all test products (those with test.example.com URLs)
        print("\n1. Finding test products...")
        test_products = db.query(Product).filter(Product.url.like('%test.example.com%')).all()
        print(f"Found {len(test_products)} test products to delete")
        
        if not test_products:
            print("✅ No test products found - database is clean!")
            return True
        
        # Show what we're about to delete
        for product in test_products:
            print(f"   - {product.id}: {product.name} ({product.url})")
        
        # 2. Delete processing stages first
        print(f"\n2. Deleting processing stages for {len(test_products)} products...")
        product_ids = [p.id for p in test_products]
        
        # Delete processing stages
        processing_stages_deleted = db.query(ProcessingStage).filter(
            ProcessingStage.product_id.in_(product_ids)
        ).delete(synchronize_session=False)
        print(f"✅ Deleted {processing_stages_deleted} processing stages")
        
        # 3. Delete product images and their local files
        print(f"\n3. Deleting product images for {len(test_products)} products...")
        
        # First, let's see what images we have and collect file paths
        images = db.query(ProductImage).filter(ProductImage.product_id.in_(product_ids)).all()
        print(f"Found {len(images)} images to delete")
        
        # Collect local file paths to delete
        local_files_to_delete = []
        for image in images:
            if image.local_path and os.path.exists(image.local_path):
                local_files_to_delete.append(image.local_path)
                print(f"   Will delete local file: {image.local_path}")
        
        # Delete product images from database
        images_deleted = db.query(ProductImage).filter(
            ProductImage.product_id.in_(product_ids)
        ).delete(synchronize_session=False)
        print(f"✅ Deleted {images_deleted} product images from database")
        
        # Delete local files
        if local_files_to_delete:
            print(f"Deleting {len(local_files_to_delete)} local image files...")
            deleted_files = 0
            for file_path in local_files_to_delete:
                try:
                    os.remove(file_path)
                    deleted_files += 1
                except Exception as e:
                    print(f"   ⚠️  Could not delete {file_path}: {e}")
            print(f"✅ Deleted {deleted_files} local image files")
        else:
            print("✅ No local files to delete")
        
        # 4. Delete 3D models and related data
        print(f"\n4. Deleting 3D models for {len(test_products)} products...")
        
        # Delete model LODs first
        models = db.query(Model3D).filter(Model3D.product_id.in_(product_ids)).all()
        model_ids = [m.id for m in models]
        
        if model_ids:
            lods_deleted = db.query(ModelLOD).filter(ModelLOD.model_id.in_(model_ids)).delete(synchronize_session=False)
            print(f"✅ Deleted {lods_deleted} model LODs")
            
            # Delete 3D models
            models_deleted = db.query(Model3D).filter(Model3D.product_id.in_(product_ids)).delete(synchronize_session=False)
            print(f"✅ Deleted {models_deleted} 3D models")
        else:
            print("✅ No 3D models found to delete")
        
        # 5. Check for batch jobs (products reference batch jobs, not the other way around)
        print(f"\n5. Checking batch job references...")
        batch_job_ids = [p.batch_job_id for p in test_products if p.batch_job_id]
        if batch_job_ids:
            print(f"   Found {len(set(batch_job_ids))} unique batch job references")
            print("   (Batch jobs will be cleaned up separately if needed)")
        else:
            print("✅ No batch job references found")
        
        # 6. Finally, delete the products
        print(f"\n6. Deleting {len(test_products)} test products...")
        products_deleted = db.query(Product).filter(Product.id.in_(product_ids)).delete(synchronize_session=False)
        print(f"✅ Deleted {products_deleted} test products")
        
        # 7. Commit all changes
        db.commit()
        print("\n✅ All changes committed to database")
        
        # 8. Verify cleanup
        print(f"\n7. Verifying cleanup...")
        remaining_test_products = db.query(Product).filter(Product.url.like('%test.example.com%')).count()
        remaining_images = db.query(ProductImage).join(Product).filter(Product.url.like('%test.example.com%')).count()
        remaining_stages = db.query(ProcessingStage).join(Product).filter(Product.url.like('%test.example.com%')).count()
        
        print(f"   - Remaining test products: {remaining_test_products}")
        print(f"   - Remaining test images: {remaining_images}")
        print(f"   - Remaining test stages: {remaining_stages}")
        
        if remaining_test_products == 0 and remaining_images == 0 and remaining_stages == 0:
            print("✅ Database cleanup successful - all test data removed!")
        else:
            print("⚠️  Some test data may still remain")
        
        # 9. Show current database stats
        print(f"\n8. Current database statistics:")
        total_products = db.query(Product).count()
        total_images = db.query(ProductImage).count()
        total_stages = db.query(ProcessingStage).count()
        total_models = db.query(Model3D).count()
        
        print(f"   - Total products: {total_products}")
        print(f"   - Total images: {total_images}")
        print(f"   - Total processing stages: {total_stages}")
        print(f"   - Total 3D models: {total_models}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = cleanup_test_products()
    if success:
        print("\n🎉 Database cleanup completed successfully!")
    else:
        print("\n💥 Database cleanup failed!")
        sys.exit(1)
