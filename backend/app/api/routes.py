from fastapi import APIRouter, HTTPException, Depends
from app.schemas.product import (
    URLDetectionRequest, URLDetectionResponse, URLType,
    ScrapeRequest, ScrapeResponse, ImageSelectionRequest, ImageSelectionResponse,
    BackgroundRemovalRequest, BackgroundRemovalResponse, ImageApprovalRequest, ImageApprovalResponse,
    Generate3DRequest, Generate3DResponse, ModelStatusResponse
)
from app.schemas.processing import (
    SaveProcessingStageRequest, SaveProcessingStageResponse,
    SaveProductImagesRequest, SaveProductImagesResponse,
    UpdateProductStatusRequest, UpdateProductStatusResponse,
    CategoryScrapeRequest, CategoryScrapeResponse,
    BatchProcessRequest, BatchProcessResponse,
    BatchStatusResponse
)
from app.services.mock_data import mock_data
from app.core.database import get_db
from app.models.product import Product
from sqlalchemy.orm import Session
import re
import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Any# Import WebSocket manager
from app.websocket_manager import manager

# Import monitoring
from app.middleware import metrics_collector

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    return {"message": "API routes are working"}

@router.post("/detect-url", response_model=URLDetectionResponse)
async def detect_url(request: URLDetectionRequest):
    """
    Detect URL type and retailer for a given product URL
    """
    try:
        url = request.url.strip()
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Detect retailer and URL type
        detection_result = _detect_url_type(url)
        
        return URLDetectionResponse(
            url=url,
            type=detection_result['type'],
            retailer=detection_result['retailer'],
            supported=detection_result['supported'],
            confidence=detection_result['confidence']
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"URL detection failed: {str(e)}")

def _detect_url_type(url: str) -> dict:
    """
    Detect the type and retailer of a product URL
    """
    # IKEA detection patterns
    ikea_patterns = [
        r'ikea\.com.*?/p/',
        r'ikea\.com.*?/products/',
        r'ikea\.com.*?/item/'
    ]
    
    # Target detection patterns
    target_patterns = [
        r'target\.com.*?/p/',
        r'target\.com.*?/product/',
        r'target\.com.*?/-/A-'
    ]
    
    # West Elm detection patterns
    west_elm_patterns = [
        r'westelm\.com.*?/products/',
        r'westelm\.com.*?/p/'
    ]
    
    # Urban Outfitters detection patterns
    urban_outfitters_patterns = [
        r'urbanoutfitters\.com.*?/products/',
        r'urbanoutfitters\.com.*?/p/'
    ]
    
    # Check for IKEA
    for pattern in ikea_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return {
                'type': URLType.PRODUCT,
                'retailer': 'IKEA',
                'supported': True,
                'confidence': 0.95
            }
    
    # Check for Target
    for pattern in target_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return {
                'type': URLType.PRODUCT,
                'retailer': 'Target',
                'supported': True,
                'confidence': 0.90
            }
    
    # Check for West Elm
    for pattern in west_elm_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return {
                'type': URLType.PRODUCT,
                'retailer': 'West Elm',
                'supported': True,
                'confidence': 0.90
            }
    
    # Check for Urban Outfitters
    for pattern in urban_outfitters_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return {
                'type': URLType.PRODUCT,
                'retailer': 'Urban Outfitters',
                'supported': True,
                'confidence': 0.90
            }
    
    # Check for category URLs
    category_patterns = [
        r'ikea\.com.*?/categories/',
        r'target\.com.*?/c/',
        r'westelm\.com.*?/categories/',
        r'urbanoutfitters\.com.*?/categories/'
    ]
    
    for pattern in category_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return {
                'type': URLType.CATEGORY,
                'retailer': 'Unknown',
                'supported': True,
                'confidence': 0.70
            }
    
    # Check for search URLs
    search_patterns = [
        r'ikea\.com.*?/search',
        r'target\.com.*?/search',
        r'westelm\.com.*?/search',
        r'urbanoutfitters\.com.*?/search'
    ]
    
    for pattern in search_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return {
                'type': URLType.SEARCH,
                'retailer': 'Unknown',
                'supported': True,
                'confidence': 0.60
            }
    
    # Unknown URL type
    return {
        'type': URLType.UNKNOWN,
        'retailer': 'Unknown',
        'supported': False,
        'confidence': 0.0
    }

# ============================================================================
# SINGLE PRODUCT PIPELINE ENDPOINTS
# ============================================================================

@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_product(request: ScrapeRequest, db: Session = Depends(get_db)):
    """
    Step 1: Scrape product data from URL using mock data service
    """
    try:
        # Get mock product data
        mock_product = mock_data.get_mock_product(request.url)
        if not mock_product:
            # Generate new mock product if not found
            mock_product = mock_data._generate_mock_product(request.url)
        
        # Create product in database
        product = mock_data.create_mock_product_in_db(request.url, db)
        
        # Send WebSocket update
        await manager.send_product_update(str(product.id), {
            "stage": "scraping",
            "progress": 100,
            "message": f"Product scraped successfully: {mock_product['name']}",
            "status": "completed",
            "processing_time": 2.5,
            "cost": 0.05
        })
        
        return ScrapeResponse(
            product_id=str(product.id),
            url=request.url,
            name=mock_product['name'],
            brand=mock_product['brand'],
            price=mock_product['price'],
            description=mock_product['description'],
            dimensions=mock_product['dimensions'],
            weight=mock_product['weight'],
            category=mock_product['category'],
            room_type=mock_product['room_type'],
            style_tags=mock_product['style_tags'],
            placement_type=mock_product['placement_type'],
            assembly_required=mock_product['assembly_required'],
            in_stock=mock_product['in_stock'],
            images=mock_product['images'],
            retailer_id=mock_product['retailer_id'],
            ikea_item_number=mock_product.get('ikea_item_number'),
            processing_time=2.5,
            cost=0.05,
            status="completed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.post("/select-images", response_model=ImageSelectionResponse)
async def select_images(request: ImageSelectionRequest, db: Session = Depends(get_db)):
    """
    Step 2: Select best images for 3D generation
    """
    try:
        # Get product from database
        product = db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Mock image selection logic (select first 3-5 images)
        selected_images = request.images[:min(5, len(request.images))]
        
        # Create processing stage
        stage = mock_data.create_processing_stage(
            product_id=request.product_id,
            stage_name="image_selection",
            input_data={"total_images": len(request.images)},
            output_data={"selected_images": len(selected_images)},
            db=db
        )
        
        # Send WebSocket update
        await manager.send_product_update(str(request.product_id), {
            "stage": "image_selection",
            "progress": 100,
            "message": f"Selected {len(selected_images)} images for 3D generation",
            "status": "completed",
            "processing_time": 1.2,
            "cost": 0.0
        })
        
        return ImageSelectionResponse(
            product_id=str(request.product_id),
            selected_images=selected_images,
            total_available=len(request.images),
            selection_criteria=["quality", "angle", "lighting"],
            processing_time=1.2,
            cost=0.0,
            status="completed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image selection failed: {str(e)}")

@router.post("/remove-backgrounds", response_model=BackgroundRemovalResponse)
async def remove_backgrounds(request: BackgroundRemovalRequest, db: Session = Depends(get_db)):
    """
    Step 3: Remove backgrounds from selected images
    """
    try:
        # Get product from database
        product = db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Mock background removal (generate processed image URLs)
        processed_images = []
        for i, image_url in enumerate(request.images):
            processed_images.append({
                "original_url": image_url,
                "processed_url": f"https://s3.amazonaws.com/processed-{uuid.uuid4().hex[:8]}.png",
                "mask_url": f"https://s3.amazonaws.com/mask-{uuid.uuid4().hex[:8]}.png",
                "processing_time": 3.5 + i * 0.5
            })
        
        # Create processing stage
        stage = mock_data.create_processing_stage(
            product_id=request.product_id,
            stage_name="background_removal",
            input_data={"images": request.images},
            output_data={"processed_images": processed_images},
            db=db
        )
        
        return BackgroundRemovalResponse(
            product_id=str(request.product_id),
            processed_images=processed_images,
            total_processed=len(processed_images),
            processing_time=sum(img["processing_time"] for img in processed_images),
            cost=0.15 * len(processed_images),
            status="completed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Background removal failed: {str(e)}")

@router.post("/approve-images", response_model=ImageApprovalResponse)
async def approve_images(request: ImageApprovalRequest, db: Session = Depends(get_db)):
    """
    Step 4: User approval of processed images
    """
    try:
        # Get product from database
        product = db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Create processing stage
        stage = mock_data.create_processing_stage(
            product_id=request.product_id,
            stage_name="image_approval",
            input_data={"approved": request.approved, "feedback": request.feedback},
            output_data={"approved_images": request.approved_images if request.approved else []},
            db=db
        )
        
        return ImageApprovalResponse(
            product_id=str(request.product_id),
            approved=request.approved,
            approved_images=request.approved_images if request.approved else [],
            feedback=request.feedback,
            processing_time=0.5,
            cost=0.0,
            status="completed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image approval failed: {str(e)}")

@router.post("/generate-3d", response_model=Generate3DResponse)
async def generate_3d_model(request: Generate3DRequest, db: Session = Depends(get_db)):
    """
    Step 5: Generate 3D model from approved images
    """
    try:
        # Get product from database
        product = db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Mock 3D generation
        model_data = {
            "model_url": f"https://s3.amazonaws.com/model-{uuid.uuid4().hex[:8]}.glb",
            "preview_url": f"https://s3.amazonaws.com/preview-{uuid.uuid4().hex[:8]}.jpg",
            "file_size": 2.5 * 1024 * 1024,  # 2.5MB
            "vertices_count": 15420,
            "triangles_count": 30840,
            "materials_count": 3,
            "textures_count": 2,
            "generation_time": 45.2,
            "quality_score": 0.87
        }
        
        # Create processing stage
        stage = mock_data.create_processing_stage(
            product_id=request.product_id,
            stage_name="model_generation",
            input_data={"images": request.images},
            output_data=model_data,
            db=db
        )
        
        # Send WebSocket update
        await manager.send_product_update(str(request.product_id), {
            "stage": "model_generation",
            "progress": 100,
            "message": f"3D model generated successfully (Quality: {model_data['quality_score']:.2f})",
            "status": "completed",
            "processing_time": model_data["generation_time"],
            "cost": 0.50,
            "model_url": model_data["model_url"],
            "quality_score": model_data["quality_score"]
        })
        
        return Generate3DResponse(
            product_id=str(request.product_id),
            model_url=model_data["model_url"],
            preview_url=model_data["preview_url"],
            file_size=model_data["file_size"],
            vertices_count=model_data["vertices_count"],
            triangles_count=model_data["triangles_count"],
            materials_count=model_data["materials_count"],
            textures_count=model_data["textures_count"],
            generation_time=model_data["generation_time"],
            quality_score=model_data["quality_score"],
            cost=0.50,
            status="completed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"3D generation failed: {str(e)}")

@router.post("/optimize-model", response_model=ModelStatusResponse)
async def optimize_model(request: Generate3DRequest, db: Session = Depends(get_db)):
    """
    Step 6: Optimize 3D model and create LOD versions for iOS
    """
    try:
        # Get product from database
        product = db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Mock LOD optimization
        lod_versions = [
            {
                "lod_level": "high",
                "lod_order": 1,
                "model_url": f"https://s3.amazonaws.com/model-high-{uuid.uuid4().hex[:8]}.glb",
                "file_size": 2.5 * 1024 * 1024,
                "vertices_count": 15420,
                "triangles_count": 30840,
                "optimization_ratio": 1.0
            },
            {
                "lod_level": "medium",
                "lod_order": 2,
                "model_url": f"https://s3.amazonaws.com/model-medium-{uuid.uuid4().hex[:8]}.glb",
                "file_size": 1.2 * 1024 * 1024,
                "vertices_count": 7710,
                "triangles_count": 15420,
                "optimization_ratio": 0.5
            },
            {
                "lod_level": "low",
                "lod_order": 3,
                "model_url": f"https://s3.amazonaws.com/model-low-{uuid.uuid4().hex[:8]}.glb",
                "file_size": 0.6 * 1024 * 1024,
                "vertices_count": 3855,
                "triangles_count": 7710,
                "optimization_ratio": 0.25
            }
        ]
        
        # Create processing stage
        stage = mock_data.create_processing_stage(
            product_id=request.product_id,
            stage_name="optimization",
            input_data={"original_model": request.model_url},
            output_data={"lod_versions": lod_versions},
            db=db
        )
        
        return ModelStatusResponse(
            product_id=str(request.product_id),
            model_url=request.model_url,
            lod_versions=lod_versions,
            total_optimization_time=12.8,
            total_cost=0.10,
            status="completed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model optimization failed: {str(e)}")

@router.post("/save-product", response_model=UpdateProductStatusResponse)
async def save_product(request: UpdateProductStatusRequest, db: Session = Depends(get_db)):
    """
    Step 7: Save final product to database
    """
    try:
        # Get product from database
        product = db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Update product status
        product.status = request.status
        product.updated_at = datetime.now()
        db.commit()
        
        # Create final processing stage
        stage = mock_data.create_processing_stage(
            product_id=request.product_id,
            stage_name="saving",
            input_data={"status": request.status},
            output_data={"saved": True, "metadata": request.metadata},
            db=db
        )
        
        return UpdateProductStatusResponse(
            id=str(product.id),
            status=product.status,
            updated_at=product.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product saving failed: {str(e)}")

# ============================================================================
# BATCH PROCESSING ENDPOINTS
# ============================================================================

@router.post("/scrape-category", response_model=CategoryScrapeResponse)
async def scrape_category(request: CategoryScrapeRequest, db: Session = Depends(get_db)):
    """
    Scrape multiple products from a category URL
    """
    try:
        # Detect URL type first
        detection_result = _detect_url_type(request.url)
        if not detection_result['supported']:
            raise HTTPException(status_code=400, detail="Unsupported category URL")
        
        # Generate mock products for the category
        mock_products = []
        for i in range(min(request.limit, 10)):  # Limit to 10 for testing
            product_data = mock_data._generate_mock_product(f"{request.url}/product-{i+1}")
            mock_products.append({
                "url": product_data['url'],
                "name": product_data['name'],
                "brand": product_data['brand'],
                "price": product_data['price'],
                "category": product_data['category'],
                "room_type": product_data['room_type'],
                "images": product_data['images'][:3]  # Limit images for batch
            })
        
        # Note: In real implementation, this would create a processing stage
        # For now, we'll skip database operations for category scraping
        
        return CategoryScrapeResponse(
            category_url=request.url,
            total_found=len(mock_products),
            products=mock_products,
            scraping_time=5.2,
            cost=0.10 * len(mock_products)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Category scraping failed: {str(e)}")

@router.post("/batch-process", response_model=BatchProcessResponse)
async def batch_process(request: BatchProcessRequest, db: Session = Depends(get_db)):
    """
    Process multiple products through the entire pipeline
    """
    try:
        # Create batch job
        batch_job = mock_data.create_mock_batch_job(
            product_ids=request.product_ids,
            settings=request.settings
        )
        
        # Simulate batch processing
        total_products = len(request.product_ids)
        successful_products = int(total_products * 0.85)  # 85% success rate
        failed_products = total_products - successful_products
        
        # Note: In real implementation, this would create a processing stage
        # For now, we'll skip database operations for batch processing
        
        # Send WebSocket update for batch start
        await manager.send_batch_update(batch_job['id'], {
            "stage": "batch_started",
            "progress": 0,
            "message": f"Batch processing started for {total_products} products",
            "status": "processing",
            "processed": 0,
            "total": total_products,
            "successful": 0,
            "failed": 0,
            "estimated_time_minutes": total_products * 2.5,
            "estimated_cost": total_products * 0.75
        })
        
        return BatchProcessResponse(
            batch_id=batch_job['id'],
            total_products=total_products,
            estimated_completion=datetime.now().replace(microsecond=0),  # Mock completion time
            estimated_cost=total_products * 0.75,  # $0.75 per product
            status="processing"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@router.get("/batch-status/{batch_id}", response_model=BatchStatusResponse)
async def get_batch_status(batch_id: str, db: Session = Depends(get_db)):
    """
    Get the status of a batch processing job
    """
    try:
        # Mock batch status (in real implementation, this would query the database)
        mock_status = {
            "batch_id": batch_id,
            "status": "processing",
            "progress": 65,
            "processed": 13,
            "total": 20,
            "successful": 11,
            "failed": 2,
            "progress_percentage": 65,
            "estimated_completion": "2024-01-15T14:30:00Z",
            "current_cost": 15.50
        }
        
        return BatchStatusResponse(
            batch_id=mock_status["batch_id"],
            status=mock_status["status"],
            progress=mock_status["progress"],
            processed=mock_status["processed"],
            total=mock_status["total"],
            successful=mock_status["successful"],
            failed=mock_status["failed"],
            progress_percentage=mock_status["progress_percentage"],
            estimated_completion=datetime.fromisoformat(mock_status["estimated_completion"].replace('Z', '+00:00')),
            current_cost=mock_status["current_cost"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get batch status: {str(e)}")

@router.post("/batch-cancel/{batch_id}")
async def cancel_batch(batch_id: str, db: Session = Depends(get_db)):
    """
    Cancel a running batch processing job
    """
    try:
        # Mock batch cancellation
        return {
            "batch_id": batch_id,
            "status": "cancelled",
            "message": "Batch processing cancelled successfully",
            "cancelled_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel batch: {str(e)}")

@router.get("/batch-history")
async def get_batch_history(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    """
    Get history of batch processing jobs
    """
    try:
        # Mock batch history
        mock_history = []
        for i in range(min(limit, 5)):  # Return up to 5 mock entries
            mock_history.append({
                "batch_id": f"batch_{uuid.uuid4().hex[:8]}",
                "status": ["completed", "processing", "failed", "cancelled"][i % 4],
                "total_products": 10 + i * 5,
                "successful_products": 8 + i * 4,
                "failed_products": 2 + i,
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat() if i % 2 == 0 else None,
                "total_cost": 15.50 + i * 5.25
            })
        
        return {
            "batches": mock_history,
            "total": len(mock_history),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get batch history: {str(e)}")

# ============================================================================
# MONITORING AND HEALTH ENDPOINTS
# ============================================================================

@router.get("/health")
async def health_check():
    """
    Health check endpoint with detailed status
    """
    try:
        health_status = metrics_collector.metrics.get_health_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "uptime": "running",
            "metrics": health_status
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.get("/metrics")
async def get_metrics():
    """
    Get detailed metrics and statistics
    """
    try:
        metrics_summary = metrics_collector.get_metrics_summary()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics_summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/metrics/reset")
async def reset_metrics():
    """
    Reset all metrics (for testing purposes)
    """
    try:
        # Reset metrics
        metrics_collector._metrics = metrics_collector.Metrics()
        
        return {
            "message": "Metrics reset successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset metrics: {str(e)}")

@router.get("/logs")
async def get_recent_logs(limit: int = 100):
    """
    Get recent log entries (for debugging)
    """
    try:
        # This would typically read from log files
        # For now, return a mock response
        return {
            "message": "Log retrieval not implemented in this version",
            "timestamp": datetime.now().isoformat(),
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")
