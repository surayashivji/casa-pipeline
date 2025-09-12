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
    UpdateProductStatusRequest, UpdateProductStatusResponse
)
from app.services.mock_data import mock_data
from app.core.database import get_db
from app.models.product import Product
from sqlalchemy.orm import Session
import re
import uuid
from datetime import datetime
from typing import List, Dict, Any

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
