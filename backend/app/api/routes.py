from fastapi import APIRouter, HTTPException, Depends
import httpx
from fastapi.responses import Response
from app.schemas.product import (
    URLDetectionRequest, URLDetectionResponse, URLType,
    ScrapeRequest, ScrapeResponse, ImageSelectionRequest, ImageSelectionResponse,
    BackgroundRemovalRequest, BackgroundRemovalResponse, ImageApprovalRequest, ImageApprovalResponse,
    Generate3DRequest, Generate3DResponse, ModelStatusResponse, ProductDimensions
)
from app.schemas.processing import (
    SaveProcessingStageRequest, SaveProcessingStageResponse,
    SaveProductImagesRequest, SaveProductImagesResponse,
    UpdateProductStatusRequest, UpdateProductStatusResponse,
    CategoryScrapeRequest, CategoryScrapeResponse,
    BatchProcessRequest, BatchProcessResponse,
    BatchStatusResponse
)
from app.services.mock_data import mock_data, MockDataService
from app.services.background_removal.manager import BackgroundRemovalManager
from app.core.database import get_db
from app.models import Product, ProductImage, ProcessingStage, Model3D, ModelLOD
from app.scrapers.scraper_factory import ScraperFactory
from sqlalchemy.orm import Session
import re
import uuid
import asyncio
import logging
import os
import pandas as pd
import io
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse
# Import WebSocket manager
from app.websocket_manager import manager
from app.services.meshy.meshy import meshy

# Import monitoring
from app.middleware import metrics_collector

def cleanup_product_files(db: Session, product_id: str) -> int:
    """
    Clean up local files associated with a product.
    Returns the number of files deleted.
    """
    deleted_count = 0
    
    try:
        # Get all images for this product
        images = db.query(ProductImage).filter(ProductImage.product_id == product_id).all()
        
        for image in images:
            if image.local_path and os.path.exists(image.local_path):
                try:
                    os.remove(image.local_path)
                    deleted_count += 1
                    logger.info(f"Deleted local file: {image.local_path}")
                except Exception as e:
                    logger.warning(f"Could not delete {image.local_path}: {e}")
        
        # Get all 3D models for this product
        models = db.query(Model3D).filter(Model3D.product_id == product_id).all()
        
        for model in models:
            # Check for local file path (if it exists)
            local_path = getattr(model, 'file_path', None)
            if local_path and os.path.exists(local_path):
                try:
                    os.remove(local_path)
                    deleted_count += 1
                    logger.info(f"Deleted 3D model file: {local_path}")
                except Exception as e:
                    logger.warning(f"Could not delete {local_path}: {e}")
            
            # Also clean up LOD files
            for lod in model.lods:
                lod_local_path = getattr(lod, 'file_path', None)
                if lod_local_path and os.path.exists(lod_local_path):
                    try:
                        os.remove(lod_local_path)
                        deleted_count += 1
                        logger.info(f"Deleted LOD file: {lod_local_path}")
                    except Exception as e:
                        logger.warning(f"Could not delete {lod_local_path}: {e}")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up files for product {product_id}: {e}")
        return deleted_count

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Room Decorator Pipeline"],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

@router.get("/test")
async def test_endpoint():
    return {"message": "API routes are working"}

@router.post(
    "/detect-url", 
    response_model=URLDetectionResponse,
    summary="Detect URL Type and Retailer",
    description="""
    Analyzes a product URL to determine:
    - **URL Type**: Product page, category page, or search results
    - **Retailer**: IKEA, Wayfair, Amazon, etc.
    - **Confidence**: Detection confidence score (0-1)
    
    This is the first step in the pipeline to understand what type of content we're processing.
    """,
    responses={
        200: {
            "description": "URL successfully analyzed",
            "content": {
                "application/json": {
                    "example": {
                        "type": "product",
                        "retailer": "ikea",
                        "confidence": 0.95,
                        "url": "https://www.ikea.com/us/en/p/stefan-chair-brown-black-00211088/"
                    }
                }
            }
        },
        422: {"description": "Invalid URL format"}
    },
    tags=["URL Detection"]
)
async def detect_url(request: URLDetectionRequest):
    """
    Detect URL type and retailer for a given product URL
    
    **Parameters:**
    - `url`: The product URL to analyze (required)
    
    **Returns:**
    - `type`: Detected URL type (product, category, search)
    - `retailer`: Identified retailer name
    - `confidence`: Detection confidence (0.0-1.0)
    - `url`: Normalized URL
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
        r'ikea\.com.*?/item/',
        r'ikea\.com.*?/cat/'  # Category URLs
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
            # Determine if it's a product or category URL
            url_type = URLType.CATEGORY if '/cat/' in url else URLType.PRODUCT
            return {
                'type': url_type,
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

@router.post(
    "/scrape", 
    response_model=ScrapeResponse,
    summary="Scrape Product Data",
    description="""
    **Step 1 of the Pipeline**: Extract product information from a retailer URL.
    
    This endpoint:
    - Fetches product data (name, price, images, dimensions) using real scrapers
    - Identifies the retailer and product type automatically
    - Stores the product in the database
    - Sends real-time updates via WebSocket
    - Falls back to mock data for unsupported retailers
    
    **Supported Retailers**: IKEA (more coming soon)
    """,
    responses={
        200: {
            "description": "Product successfully scraped",
            "content": {
                "application/json": {
                    "example": {
                        "product": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "name": "STOCKHOLM 2025 3-seat sofa, Alhamn beige",
                            "brand": "IKEA",
                            "price": 1899.0,
                            "url": "https://www.ikea.com/us/en/p/stockholm-2025-3-seat-sofa-alhamn-beige-s69574294/",
                            "images": [
                                "https://www.ikea.com/us/en/images/products/stockholm-2025-3-seat-sofa-alhamn-beige__1362835_pe955331_s5.jpg?f=xl"
                            ],
                            "dimensions": {
                                "width": 95.625,
                                "height": 27.5,
                                "depth": 39.0,
                                "unit": "inches"
                            }
                        },
                        "status": "scraped"
                    }
                }
            }
        },
        404: {"description": "Product not found"},
        422: {"description": "Invalid request data"},
        500: {"description": "Scraping failed"}
    },
    tags=["Single Product Pipeline"]
)
async def scrape_product(request: ScrapeRequest, db: Session = Depends(get_db)):
    """
    Scrape product data from URL using real scrapers
    
    **Parameters:**
    - `url`: Product URL to scrape (required)
    - `mode`: Processing mode - "single" or "batch" (optional, default: "single")
    
    **Returns:**
    - `product`: Complete product information
    - `images`: List of product image URLs
    - `processing_time`: Time taken to scrape (seconds)
    - `cost`: Estimated processing cost
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Starting product scraping for URL: {request.url}")
        
        # Create scraper using factory
        scraper = ScraperFactory.create_scraper(request.url)
        
        if not scraper:
            logger.warning(f"No scraper available for URL: {request.url}, falling back to mock data")
            # Fallback to mock data for unsupported retailers
            return await _scrape_with_mock_data(request, db, start_time)
        
        # Check if scraper can handle this URL
        if not scraper.can_handle(request.url):
            logger.warning(f"Scraper cannot handle URL: {request.url}, falling back to mock data")
            return await _scrape_with_mock_data(request, db, start_time)
        
        # Initialize scraper
        await scraper.initialize(headless=True)
        
        try:
            # Scrape product data
            logger.info(f"Scraping product data from: {request.url}")
            scraped_data = await scraper.scrape_product(request.url)
            
            if not scraped_data:
                logger.error(f"Failed to scrape data from: {request.url}")
                raise HTTPException(status_code=500, detail="Failed to extract product data")
            
            # Check if we got meaningful data (at least name and price)
            if not scraped_data.get('name') or scraped_data.get('name') == 'Unknown Product':
                logger.warning(f"Scraped data appears incomplete for: {request.url}, falling back to mock data")
                return await _scrape_with_mock_data(request, db, start_time)
            
            # Create product in database
            product = _create_product_in_db(scraped_data, request.url, db)
            
            # Send WebSocket update
            processing_time = (datetime.now() - start_time).total_seconds()
            await manager.send_product_update(str(product.id), {
                "stage": "scraping",
                "progress": 100,
                "message": f"Product scraped successfully: {scraped_data['name']}",
                "status": "completed",
                "processing_time": processing_time,
                "cost": 0.05
            })
            
            # Create Product object for response
            product_data = _create_product_response(scraped_data, product, request.url)
            
            logger.info(f"Successfully scraped product: {scraped_data['name']}")
            
            return ScrapeResponse(
                product=product_data,
                images=scraped_data.get('images', []),
                processing_time=processing_time,
                cost=0.05
            )
            
        finally:
            # Always cleanup scraper
            await scraper.cleanup()
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Scraping failed for URL {request.url}: {str(e)}")
        # Only fallback to mock data for certain types of errors
        if "browser" in str(e).lower() or "page" in str(e).lower() or "context" in str(e).lower():
            logger.warning(f"Browser-related error, falling back to mock data: {str(e)}")
            try:
                return await _scrape_with_mock_data(request, db, start_time)
            except Exception as fallback_error:
                logger.error(f"Mock data fallback also failed: {str(fallback_error)}")
                raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")
        else:
            # For other errors, don't fallback - let them fail
            raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

async def _scrape_with_mock_data(request: ScrapeRequest, db: Session, start_time: datetime):
    """Fallback to mock data when real scraping fails"""
    logger.info(f"Using mock data fallback for URL: {request.url}")
    
    # Get mock product data
    mock_product = mock_data.get_mock_product(request.url)
    if not mock_product:
        # Generate new mock product if not found
        mock_product = mock_data._generate_mock_product(request.url)
    
    # Create product in database
    product = mock_data.create_mock_product_in_db(request.url, db)
    
    # Send WebSocket update
    processing_time = (datetime.now() - start_time).total_seconds()
    await manager.send_product_update(str(product.id), {
        "stage": "scraping",
        "progress": 100,
        "message": f"Product scraped successfully (mock data): {mock_product['name']}",
        "status": "completed",
        "processing_time": processing_time,
        "cost": 0.05
    })
    
    # Create Product object for response
    product_data = Product(
        id=str(product.id),
        url=request.url,
        name=mock_product['name'],
        brand=mock_product['brand'],
        variant_info=mock_product.get('description', ''),
        price=mock_product['price'],
        width_inches=mock_product['dimensions']['width'],
        height_inches=mock_product['dimensions']['height'],
        depth_inches=mock_product['dimensions']['depth'],
        weight_kg=mock_product['weight'],
        category=mock_product['category'],
        room_type=mock_product['room_type'],
        style_tags=mock_product['style_tags'],
        placement_type=mock_product['placement_type'],
        assembly_required=mock_product['assembly_required'],
        retailer_id=mock_product['retailer_id'],
        ikea_item_number=mock_product.get('ikea_item_number'),
        status="scraped",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Add frontend-expected fields
    product_data.description = mock_product.get('description', '')
    product_data.weight = mock_product['weight']
    product_data.dimensions = ProductDimensions(
        width=mock_product['dimensions']['width'],
        height=mock_product['dimensions']['height'],
        depth=mock_product['dimensions']['depth'],
        unit=mock_product['dimensions']['unit']
    )
    
    return ScrapeResponse(
        product=product_data,
        images=mock_product['images'],
        processing_time=processing_time,
        cost=0.05
    )

def _create_product_in_db(scraped_data: dict, url: str, db: Session) -> Product:
    """Create product in database with duplicate handling"""
    try:
        # Check if product already exists
        existing_product = db.query(Product).filter(Product.url == url).first()
        if existing_product:
            logger.info(f"Product already exists, updating: {existing_product.id}")
            # Update existing product
            existing_product.name = scraped_data['name']
            existing_product.brand = scraped_data.get('brand', '')
            existing_product.variant_info = scraped_data.get('description', '')
            existing_product.price = scraped_data.get('price', 0.0)
            existing_product.width_inches = scraped_data.get('dimensions', {}).get('width', 0.0)
            existing_product.height_inches = scraped_data.get('dimensions', {}).get('height', 0.0)
            existing_product.depth_inches = scraped_data.get('dimensions', {}).get('depth', 0.0)
            existing_product.weight_kg = scraped_data.get('weight', 0.0)
            existing_product.category = scraped_data.get('category', '')
            existing_product.room_type = scraped_data.get('room_type', '')
            existing_product.style_tags = scraped_data.get('style_tags', [])
            existing_product.placement_type = scraped_data.get('placement_type', '')
            existing_product.assembly_required = scraped_data.get('assembly_required', False)
            existing_product.retailer_id = scraped_data.get('retailer_id', '')
            existing_product.ikea_item_number = scraped_data.get('ikea_item_number', '')
            existing_product.status = "scraped"
            existing_product.updated_at = datetime.now()
            
            db.commit()
            return existing_product
        
        # Create new product
        product = Product(
            id=uuid.uuid4(),
            url=url,
            name=scraped_data['name'],
            brand=scraped_data.get('brand', ''),
            variant_info=scraped_data.get('description', ''),
            price=scraped_data.get('price', 0.0),
            width_inches=scraped_data.get('dimensions', {}).get('width', 0.0),
            height_inches=scraped_data.get('dimensions', {}).get('height', 0.0),
            depth_inches=scraped_data.get('dimensions', {}).get('depth', 0.0),
            weight_kg=scraped_data.get('weight', 0.0),
            category=scraped_data.get('category', ''),
            room_type=scraped_data.get('room_type', ''),
            style_tags=scraped_data.get('style_tags', []),
            placement_type=scraped_data.get('placement_type', ''),
            assembly_required=scraped_data.get('assembly_required', False),
            retailer_id=scraped_data.get('retailer_id', ''),
            ikea_item_number=scraped_data.get('ikea_item_number', ''),
            status="scraped",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(product)
        db.flush()  # Get the ID without committing yet
        
        # Save images to product_images table
        images = scraped_data.get('images', [])
        logger.info(f"Saving {len(images)} images to database for product {product.id}")
        
        for i, image_url in enumerate(images):
            img = ProductImage(
                product_id=product.id,
                image_type="original",
                image_order=i,
                s3_url=image_url,
                width_pixels=1024,  # Default, could be extracted from image
                height_pixels=1024,  # Default, could be extracted from image
                format="jpg",
                is_primary=(i == 0)
            )
            db.add(img)
        
        # Create initial processing stage
        stage = ProcessingStage(
            product_id=product.id,
            stage_name="scraping",
            stage_order=1,
            status="completed",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            processing_time_seconds=2.5,
            cost_usd=0.05,
            input_data={"url": url},
            output_data={"images_found": len(images)},
            stage_metadata={"retailer": scraped_data.get('retailer', 'unknown')}
        )
        db.add(stage)
        
        db.commit()
        db.refresh(product)
        
        logger.info(f"Created product in database: {product.id} with {len(images)} images")
        return product
        
    except Exception as e:
        logger.error(f"Failed to create product in database: {str(e)}")
        db.rollback()
        raise

def _create_product_response(scraped_data: dict, product: Product, url: str) -> Product:
    """Create Product response object from scraped data"""
    # Create Product object for response
    product_data = Product(
        id=product.id,
        url=url,
        name=scraped_data['name'],
        brand=scraped_data.get('brand', ''),
        variant_info=scraped_data.get('description', ''),
        price=scraped_data.get('price', 0.0),
        width_inches=scraped_data.get('dimensions', {}).get('width', 0.0),
        height_inches=scraped_data.get('dimensions', {}).get('height', 0.0),
        depth_inches=scraped_data.get('dimensions', {}).get('depth', 0.0),
        weight_kg=scraped_data.get('weight', 0.0),
        category=scraped_data.get('category', ''),
        room_type=scraped_data.get('room_type', ''),
        style_tags=scraped_data.get('style_tags', []),
        placement_type=scraped_data.get('placement_type', ''),
        assembly_required=scraped_data.get('assembly_required', False),
        retailer_id=scraped_data.get('retailer_id', ''),
        ikea_item_number=scraped_data.get('ikea_item_number', ''),
        status="scraped",
        created_at=product.created_at,
        updated_at=product.updated_at
    )
    
    # Add frontend-expected fields
    product_data.description = scraped_data.get('description', '')
    product_data.weight = scraped_data.get('weight', 0.0)
    
    # Add dimensions in frontend format
    dimensions = scraped_data.get('dimensions', {})
    logger.info(f"Dimensions from scraped_data: {dimensions}")
    logger.info(f"Individual fields - width: {product_data.width_inches}, height: {product_data.height_inches}, depth: {product_data.depth_inches}")
    
    if dimensions and any(dimensions.values()):  # Check if dimensions exist and are not all zero
        product_data.dimensions = ProductDimensions(
            width=dimensions.get('width', 0.0),
            height=dimensions.get('height', 0.0),
            depth=dimensions.get('depth', 0.0),
            unit=dimensions.get('unit', 'inches')
        )
        logger.info(f"Created dimensions from scraped_data: {product_data.dimensions}")
    else:
        # Fallback: create dimensions from individual fields if dimensions object is missing
        if product_data.width_inches or product_data.height_inches or product_data.depth_inches:
            product_data.dimensions = ProductDimensions(
                width=product_data.width_inches or 0.0,
                height=product_data.height_inches or 0.0,
                depth=product_data.depth_inches or 0.0,
                unit='inches'
            )
            logger.info(f"Created dimensions from individual fields: {product_data.dimensions}")
        else:
            logger.warning("No dimensions found in scraped data")
    
    return product_data

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
        selected_images = request.image_urls[:min(5, len(request.image_urls))]
        
        # Create processing stage
        stage = mock_data.create_processing_stage(
            product_id=request.product_id,
            stage_name="image_selection",
            input_data={"total_images": len(request.image_urls)},
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
            product_id=request.product_id,
            selected_images=selected_images,
            selected_count=len(selected_images)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image selection failed: {str(e)}")

@router.post("/remove-backgrounds", response_model=BackgroundRemovalResponse)
async def remove_backgrounds(request: BackgroundRemovalRequest, db: Session = Depends(get_db)):
    """
    Step 3: Remove backgrounds from selected images using real AI processing
    """
    try:
        # Get product from database
        product = db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            # For testing purposes, create a minimal product if it doesn't exist
            logger.warning(f"Product {request.product_id} not found, creating minimal product for testing")
            product = Product(
                id=request.product_id,
                url=f"https://test.example.com/{request.product_id}",
                name="Test Product",
                brand="Test",
                status="scraped"
            )
            db.add(product)
            db.commit()
        
        # Initialize background removal manager
        bg_manager = BackgroundRemovalManager()
        
        # Send WebSocket update - processing started
        await manager.send_product_update(str(request.product_id), {
            "stage": "background_removal",
            "progress": 0,
            "message": f"Starting background removal for {len(request.image_urls)} images",
            "status": "processing"
        })
        
        # Check if processed images already exist for this product
        existing_processed = db.query(ProductImage).filter(
            ProductImage.product_id == request.product_id,
            ProductImage.image_type == 'processed'
        ).all()
        
        if existing_processed:
            logger.warning(f"Processed images already exist for product {request.product_id}, returning existing results")
            # Return existing processed images
            existing_results = []
            for img in existing_processed:
                # Construct the full URL for the processed image
                processed_url = f"http://localhost:8000{img.local_path}" if img.local_path else img.s3_url
                existing_results.append({
                    "original_url": img.s3_url,  # This is the original URL
                    "processed_url": processed_url,  # This is the processed image URL
                    "quality_score": getattr(img, 'quality_score', 0.85),
                    "processing_time": 0,
                    "auto_approved": True,
                    "provider": "rembg"
                })
            
            return BackgroundRemovalResponse(
                product_id=request.product_id,
                processed_images=existing_results,
                total_processing_time=0.0,
                total_cost=0.0,
                success_rate=1.0
            )
        
        # Get original images from database
        original_images = db.query(ProductImage).filter(
            ProductImage.product_id == request.product_id,
            ProductImage.image_type == 'original'
        ).all()
        
        # Process images with real background removal
        processed_images = []
        successful_count = 0
        total_processing_time = 0.0
        total_cost = 0.0
        
        for i, image_url in enumerate(request.image_urls):
            try:
                # Process single image
                result = await bg_manager.process_image(
                    image_url=image_url,
                    product_id=str(request.product_id),
                    image_order=i
                )
                
                if result.get('success'):
                    # Get actual file size from local file
                    file_size = 0
                    if result.get('local_path') and os.path.exists(result['local_path']):
                        file_size = os.path.getsize(result['local_path'])
                    
                    # Create new ProductImage record for processed image
                    processed_image = ProductImage(
                        product_id=request.product_id,
                        image_type='processed',
                        image_order=i,
                        s3_url=result.get('processed_url', image_url),  # Use processed URL
                        local_path=result.get('local_path'),
                        file_size_bytes=file_size,
                        width_pixels=1400,  # REMBG outputs 1400x1400
                        height_pixels=1400,
                        format='PNG',
                        is_primary=(i == 0)  # First image is primary
                    )
                    
                    db.add(processed_image)
                    db.commit()
                    
                    # Add to response
                    processed_images.append({
                        "original_url": image_url,
                        "processed_url": result.get('processed_url'),
                        "quality_score": result.get('quality_score', 0),
                        "processing_time": result.get('processing_time', 0),
                        "auto_approved": result.get('quality_score', 0) > 0.85,
                        "provider": result.get('provider', 'rembg')
                    })
                    
                    successful_count += 1
                    total_processing_time += result.get('processing_time', 0)
                    total_cost += result.get('cost', 0)
                    
                    # Send progress update
                    progress = int((i + 1) / len(request.image_urls) * 100)
                    await manager.send_product_update(str(request.product_id), {
                        "stage": "background_removal",
                        "progress": progress,
                        "message": f"Processed image {i + 1}/{len(request.image_urls)} - Quality: {result.get('quality_score', 0):.2f}",
                        "status": "processing"
                    })
                    
                else:
                    # Handle failed processing
                    logger.error(f"Background removal failed for image {i}: {result.get('error')}")
                    processed_images.append({
                        "original_url": image_url,
                        "processed_url": None,
                        "error": result.get('error', 'Processing failed'),
                        "processing_time": 0,
                        "quality_score": 0
                    })
                    
            except Exception as e:
                logger.error(f"Error processing image {i}: {e}")
                processed_images.append({
                    "original_url": image_url,
                    "processed_url": None,
                    "error": str(e),
                    "processing_time": 0,
                    "quality_score": 0
                })
        
        # Create processing stage record
        stage = ProcessingStage(
            product_id=request.product_id,
            stage_name="background_removal",
            stage_order=3,
            status="completed" if successful_count > 0 else "failed",
            processing_time_seconds=total_processing_time,
            cost_usd=total_cost,
            input_data={"image_count": len(request.image_urls)},
            output_data={
                "successful": successful_count,
                "failed": len(request.image_urls) - successful_count,
                "avg_quality": sum(img.get('quality_score', 0) for img in processed_images if img.get('quality_score', 0) > 0) / max(successful_count, 1)
            }
        )
        
        db.add(stage)
        db.commit()
        
        # Send completion update
        await manager.send_product_update(str(request.product_id), {
            "stage": "background_removal",
            "progress": 100,
            "message": f"Background removal complete: {successful_count}/{len(request.image_urls)} successful",
            "status": "completed" if successful_count > 0 else "failed"
        })
        
        return BackgroundRemovalResponse(
            product_id=request.product_id,
            processed_images=processed_images,
            total_processing_time=total_processing_time,
            total_cost=total_cost,
            success_rate=successful_count / len(request.image_urls) if request.image_urls else 0
        )
        
    except Exception as e:
        import traceback
        logger.error(f"Background removal endpoint failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
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
            input_data={"approved": request.approved, "image_count": len(request.image_urls)},
            output_data={"approved_images": request.image_urls if request.approved else []},
            db=db
        )
        
        return ImageApprovalResponse(
            product_id=request.product_id,
            status="approved" if request.approved else "rejected",
            approved_count=len(request.image_urls) if request.approved else 0,
            rejected_count=len(request.image_urls) if not request.approved else 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image approval failed: {str(e)}")

@router.post("/generate-3d", response_model=Generate3DResponse)
async def generate_3d_model(request: Generate3DRequest, db: Session = Depends(get_db)):
    """
    Step 5: Generate 3D model from processed images
    NOW USING REAL MESHY API!
    """
    try:
        # Get product info
        product = db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check test mode from environment
        test_mode = os.getenv("MESHY_TEST_MODE", "true").lower() == "true"
        
        if test_mode:
            logger.info("🧪 TEST MODE: Replacing with test images")
            logger.info(f"(Ignoring {len(request.image_urls)} provided images)")
            image_urls = [
                "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
                "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=800"
            ]
        else:
            logger.info("🚀 PRODUCTION MODE: Using real product images")
            image_urls = request.image_urls
            if not image_urls:
                raise HTTPException(status_code=400, detail="No images provided")
            logger.info(f"Creating 3D model for {product.name} with {len(image_urls)} images")

        # Call Meshy API
        result = meshy.create_task(image_urls)
        
        if not result["success"]:
            logger.error(f"Meshy API failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get("error", "Meshy API failed"))
        
        task_id = result["task_id"]
        logger.info(f"Meshy task created: {task_id}")
        
        # Store in database
        model_3d = Model3D(
            product_id=request.product_id,
            meshy_task_id=task_id,
            status="processing",
            s3_url="",  # Will be updated when complete
            generation_method="meshy",
            is_test_mode=test_mode
        )
        db.add(model_3d)
        
        # Also update ProcessingStage
        stage = mock_data.create_processing_stage(
            product_id=request.product_id,
            stage_name="3d_generation",
            input_data={"images": image_urls, "image_count": len(image_urls)},
            output_data={"meshy_task_id": task_id},
            db=db
        )
        
        db.commit()
        
        # Send WebSocket update
        await manager.send_product_update(str(request.product_id), {
            "stage": "3d_generation",
            "progress": 0,
            "message": f"Started 3D generation with {len(image_urls)} images",
            "status": "processing"
        })
        
        # Return same format as before (so frontend doesn't need changes)
        # Test mode is faster, production takes longer
        estimated_time = 30 if test_mode else 180  # 30 seconds test, 3 minutes production
        cost = 0.00 if test_mode else 0.50  # Free for test, charge for production
        
        return Generate3DResponse(
            product_id=request.product_id,
            task_id=task_id,
            status="processing",
            estimated_completion=datetime.now() + timedelta(seconds=estimated_time),
            cost=cost
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"3D generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/model-status/{task_id}", response_model=ModelStatusResponse)
async def get_model_status(task_id: str, db: Session = Depends(get_db)):
    """
    Check status of 3D model generation
    NOW USING REAL MESHY API!
    """
    try:
        # Get status from Meshy
        logger.info(f"Checking status for task: {task_id}")
        status_data = meshy.get_status(task_id)
        
        # Extract Meshy status
        meshy_status = status_data.get("status", "PENDING")
        progress = status_data.get("progress", 0)
        
        # Map Meshy status to our format
        if meshy_status == "SUCCEEDED":
            status = "completed"
            progress = 100
        elif meshy_status == "FAILED":
            status = "failed"
            progress = 0
        elif meshy_status in ["PENDING", "IN_PROGRESS"]:
            status = "processing"
            # Ensure progress shows something even if 0
            progress = max(progress, 10)
        else:
            status = "processing"
        
        logger.info(f"Task {task_id}: {meshy_status} ({progress}%) -> {status}")
        
        # Update database if we have the record
        model_3d = db.query(Model3D).filter(Model3D.meshy_task_id == task_id).first()
        if model_3d:
            if meshy_status == "SUCCEEDED" and model_3d.status != "completed":
                # Update model record
                model_3d.status = "completed"
                model_3d.model_url = status_data.get("model_urls", {}).get("glb")

                model_3d.model_urls = status_data.get("model_urls", {})

                # Save texture URL
                texture_urls = status_data.get("texture_urls", [])
                if texture_urls and len(texture_urls) > 0:
                    model_3d.base_texture_url = texture_urls[0].get("base_color", "")

                model_3d.thumbnail_url = status_data.get("thumbnail_url")
                model_3d.completed_at = datetime.now()
                
                # Update processing stage
                stage = db.query(ProcessingStage).filter(
                    ProcessingStage.product_id == model_3d.product_id,
                    ProcessingStage.stage_name == "3d_generation"
                ).first()
                if stage:
                    stage.status = "completed"
                    stage.completed_at = datetime.now()
                    stage.output_data = {
                        "model_url": model_3d.model_url,
                        "thumbnail_url": model_3d.thumbnail_url
                    }
                
                db.commit()
                
                # Send WebSocket update
                await manager.send_product_update(str(model_3d.product_id), {
                    "stage": "3d_generation",
                    "progress": 100,
                    "message": "3D model completed!",
                    "status": "completed",
                    "model_url": model_3d.model_url,
                    "thumbnail_url": model_3d.thumbnail_url
                })
                
                logger.info(f"✅ Model completed for product {model_3d.product_id}")
            
            elif meshy_status == "FAILED" and model_3d.status != "failed":
                model_3d.status = "failed"
                model_3d.error_message = status_data.get("message", "Generation failed")
                db.commit()
                
                logger.error(f"❌ Model generation failed for product {model_3d.product_id}")
        
        # Return response in same format as before
        return ModelStatusResponse(
            task_id=task_id,
            status=status,
            progress=progress,
            model_url=status_data.get("model_urls", {}).get("glb") if status == "completed" else None,
            model_urls=status_data.get("model_urls", {}) if status == "completed" else None,  # NEW
            texture_url=model_3d.base_texture_url if model_3d and status == "completed" else None,  # NEW
            thumbnail_url=status_data.get("thumbnail_url") if status == "completed" else None,
            processing_time=30.0 if status == "completed" else None,
            cost=0.00,
            model_quality=0.95 if status == "completed" else None,
            lods_available=["high"] if status == "completed" else None
        )
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return ModelStatusResponse(
            task_id=task_id,
            status="failed",
            progress=0,
            error=str(e)
        )

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
            input_data={"image_count": len(request.image_urls), "settings": request.settings},
            output_data={"lod_versions": lod_versions},
            db=db
        )
        
        return ModelStatusResponse(
            task_id=f"opt_{uuid.uuid4().hex[:8]}",
            status="completed",
            progress=100,
            model_url="https://s3.amazonaws.com/models/optimized-model.glb",
            processing_time=12.8,
            cost=0.10,
            model_quality=0.98,
            lods_available=["high", "medium", "low"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model optimization failed: {str(e)}")

@router.post("/save-product/{product_id}", response_model=UpdateProductStatusResponse)
async def save_product(product_id: str, request: UpdateProductStatusRequest, db: Session = Depends(get_db)):
    """
    Step 7: Save final product to database
    """
    try:
        # Get product from database
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Update product status
        product.status = request.status
        product.updated_at = datetime.now()
        db.commit()
        
        # Create final processing stage
        stage = mock_data.create_processing_stage(
            product_id=product_id,
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
            product_data = MockDataService._generate_mock_product(f"{request.url}/product-{i+1}")
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
# ADMIN ENDPOINTS
# ============================================================================

@router.get(
    "/products",
    summary="Get All Products",
    description="""
    **Admin Endpoint**: Retrieve all products from the database with pagination and filtering.
    
    **Features**:
    - Pagination support (limit/offset)
    - Filter by status, retailer, or date range
    - Include related images and processing stages
    - Sort by creation date, name, or price
    
    **Use Cases**:
    - Admin panel product listing
    - Debugging scraped data
    - Monitoring pipeline performance
    """,
    responses={
        200: {
            "description": "Products retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "products": [
                            {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "name": "STOCKHOLM 2025 3-seat sofa",
                                "brand": "IKEA",
                                "price": 1899.0,
                                "status": "scraped",
                                "created_at": "2024-01-15T10:30:00Z",
                                "image_count": 5,
                                "processing_stages": 3
                            }
                        ],
                        "total": 25,
                        "limit": 20,
                        "offset": 0
                    }
                }
            }
        }
    },
    tags=["Admin"]
)
async def get_products(
    limit: int = 20,
    offset: int = 0,
    status: str = None,
    retailer: str = None,
    include_images: bool = False,
    include_stages: bool = False,
    include_models_3d: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get all products with optional filtering and pagination
    """
    try:
        # Build query
        query = db.query(Product)
        
        # Apply filters
        if status:
            query = query.filter(Product.status == status)
        if retailer:
            query = query.filter(Product.brand.ilike(f"%{retailer}%"))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        products = query.order_by(Product.created_at.desc()).offset(offset).limit(limit).all()
        
        # Build response
        product_list = []
        for product in products:
            product_data = {
                "id": str(product.id),
                "name": product.name,
                "brand": product.brand,
                "price": product.price,
                "url": product.url,
                "status": product.status,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None,
                "dimensions": {
                    "width": product.width_inches,
                    "height": product.height_inches,
                    "depth": product.depth_inches
                },
                "weight_kg": product.weight_kg,
                "category": product.category,
                "room_type": product.room_type,
                "assembly_required": product.assembly_required,
                "retailer_id": product.retailer_id,
                "ikea_item_number": product.ikea_item_number
            }
            
            # Include image count
            image_count = db.query(ProductImage).filter(ProductImage.product_id == product.id).count()
            product_data["image_count"] = image_count
            
            # Include processing stage count
            stage_count = db.query(ProcessingStage).filter(ProcessingStage.product_id == product.id).count()
            product_data["processing_stages"] = stage_count
            
            # Include actual images if requested
            if include_images:
                images = db.query(ProductImage).filter(ProductImage.product_id == product.id).order_by(ProductImage.image_order).all()
                product_data["images"] = [
                    {
                        "id": str(img.id),
                        "s3_url": img.s3_url,
                        "image_type": img.image_type,
                        "image_order": img.image_order,
                        "is_primary": img.is_primary,
                        "width_pixels": img.width_pixels,
                        "height_pixels": img.height_pixels,
                        "format": img.format
                    } for img in images
                ]
            
            # Include processing stages if requested
            if include_stages:
                stages = db.query(ProcessingStage).filter(ProcessingStage.product_id == product.id).order_by(ProcessingStage.stage_order).all()
                product_data["stages"] = [
                    {
                        "id": str(stage.id),
                        "stage_name": stage.stage_name,
                        "stage_order": stage.stage_order,
                        "status": stage.status,
                        "started_at": stage.started_at.isoformat() if stage.started_at else None,
                        "completed_at": stage.completed_at.isoformat() if stage.completed_at else None,
                        "processing_time_seconds": stage.processing_time_seconds,
                        "cost_usd": stage.cost_usd,
                        "error_message": stage.error_message
                    } for stage in stages
                ]
            
            # Include 3D models if requested
            if include_models_3d:
                models_3d = db.query(Model3D).filter(Model3D.product_id == product.id).all()
                product_data["models_3d"] = [
                    {
                        "id": str(model.id),
                        "meshy_task_id": model.meshy_task_id,
                        "model_name": model.model_name,
                        "model_url": model.model_url,
                        "model_urls": model.model_urls,
                        "base_texture_url": model.base_texture_url,
                        "thumbnail_url": model.thumbnail_url,
                        "status": model.status,
                        "generation_method": model.generation_method,
                        "is_test_mode": model.is_test_mode,
                        "format": model.format,
                        "vertices_count": model.vertices_count,
                        "triangles_count": model.triangles_count,
                        "file_size_bytes": model.file_size_bytes,
                        "generation_time_seconds": model.generation_time_seconds,
                        "cost_usd": model.cost_usd,
                        "is_optimized": model.is_optimized,
                        "optimization_ratio": model.optimization_ratio,
                        "completed_at": model.completed_at.isoformat() if model.completed_at else None,
                        "created_at": model.created_at.isoformat() if model.created_at else None
                    } for model in models_3d
                ]
            
            product_list.append(product_data)
        
        return {
            "products": product_list,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
        
    except Exception as e:
        logger.error(f"Failed to get products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve products: {str(e)}")

@router.get(
    "/products/{product_id}",
    summary="Get Single Product",
    description="""
    **Admin Endpoint**: Retrieve a specific product with all related data.
    
    **Includes**:
    - Complete product information
    - All associated images
    - All processing stages
    - Error messages and metadata
    """,
    responses={
        200: {"description": "Product retrieved successfully"},
        404: {"description": "Product not found"}
    },
    tags=["Admin"]
)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """
    Get a specific product by ID with all related data
    """
    try:
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get images
        images = db.query(ProductImage).filter(ProductImage.product_id == product.id).order_by(ProductImage.image_order).all()
        
        # Get processing stages
        stages = db.query(ProcessingStage).filter(ProcessingStage.product_id == product.id).order_by(ProcessingStage.stage_order).all()
        
        # Build response
        product_data = {
            "id": str(product.id),
            "name": product.name,
            "brand": product.brand,
            "price": product.price,
            "url": product.url,
            "status": product.status,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None,
            "dimensions": {
                "width": product.width_inches,
                "height": product.height_inches,
                "depth": product.depth_inches
            },
            "weight_kg": product.weight_kg,
            "category": product.category,
            "room_type": product.room_type,
            "style_tags": product.style_tags,
            "placement_type": product.placement_type,
            "assembly_required": product.assembly_required,
            "retailer_id": product.retailer_id,
            "ikea_item_number": product.ikea_item_number,
            "error_message": product.error_message,
            "images": [
                {
                    "id": str(img.id),
                    "s3_url": img.s3_url,
                    "image_type": img.image_type,
                    "image_order": img.image_order,
                    "is_primary": img.is_primary,
                    "width_pixels": img.width_pixels,
                    "height_pixels": img.height_pixels,
                    "format": img.format,
                    "file_size_bytes": img.file_size_bytes,
                    "created_at": img.created_at.isoformat() if img.created_at else None
                } for img in images
            ],
            "processing_stages": [
                {
                    "id": str(stage.id),
                    "stage_name": stage.stage_name,
                    "stage_order": stage.stage_order,
                    "status": stage.status,
                    "started_at": stage.started_at.isoformat() if stage.started_at else None,
                    "completed_at": stage.completed_at.isoformat() if stage.completed_at else None,
                    "processing_time_seconds": stage.processing_time_seconds,
                    "cost_usd": stage.cost_usd,
                    "input_data": stage.input_data,
                    "output_data": stage.output_data,
                    "error_message": stage.error_message,
                    "stage_metadata": stage.stage_metadata
                } for stage in stages
            ]
        }
        
        return product_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve product: {str(e)}")

@router.get(
    "/images",
    summary="Get All Images",
    description="""
    **Admin Endpoint**: Retrieve all product images with filtering options.
    
    **Features**:
    - Filter by product ID, image type, or date range
    - Pagination support
    - Include product information
    - Sort by creation date or image order
    """,
    responses={
        200: {"description": "Images retrieved successfully"}
    },
    tags=["Admin"]
)
async def get_images(
    product_id: str = None,
    image_type: str = None,
    limit: int = 50,
    offset: int = 0,
    include_product: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get all images with optional filtering
    """
    try:
        # Build query
        query = db.query(ProductImage)
        
        # Apply filters
        if product_id:
            query = query.filter(ProductImage.product_id == product_id)
        if image_type:
            query = query.filter(ProductImage.image_type == image_type)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        images = query.order_by(ProductImage.created_at.desc()).offset(offset).limit(limit).all()
        
        # Build response
        image_list = []
        for img in images:
            image_data = {
                "id": str(img.id),
                "product_id": str(img.product_id),
                "s3_url": img.s3_url,
                "image_type": img.image_type,
                "image_order": img.image_order,
                "is_primary": img.is_primary,
                "width_pixels": img.width_pixels,
                "height_pixels": img.height_pixels,
                "format": img.format,
                "file_size_bytes": img.file_size_bytes,
                "created_at": img.created_at.isoformat() if img.created_at else None
            }
            
            # Include product information if requested
            if include_product:
                product = db.query(Product).filter(Product.id == img.product_id).first()
                if product:
                    image_data["product"] = {
                        "name": product.name,
                        "brand": product.brand,
                        "url": product.url
                    }
            
            image_list.append(image_data)
        
        return {
            "images": image_list,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
        
    except Exception as e:
        logger.error(f"Failed to get images: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve images: {str(e)}")

@router.get(
    "/processing-stages",
    summary="Get All Processing Stages",
    description="""
    **Admin Endpoint**: Retrieve all processing stages with filtering options.
    
    **Features**:
    - Filter by product ID, stage name, or status
    - Pagination support
    - Include product information
    - Sort by creation date or stage order
    """,
    responses={
        200: {"description": "Processing stages retrieved successfully"}
    },
    tags=["Admin"]
)
async def get_processing_stages(
    product_id: str = None,
    stage_name: str = None,
    status: str = None,
    limit: int = 50,
    offset: int = 0,
    include_product: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get all processing stages with optional filtering
    """
    try:
        # Build query
        query = db.query(ProcessingStage)
        
        # Apply filters
        if product_id:
            query = query.filter(ProcessingStage.product_id == product_id)
        if stage_name:
            query = query.filter(ProcessingStage.stage_name == stage_name)
        if status:
            query = query.filter(ProcessingStage.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        stages = query.order_by(ProcessingStage.created_at.desc()).offset(offset).limit(limit).all()
        
        # Build response
        stage_list = []
        for stage in stages:
            stage_data = {
                "id": str(stage.id),
                "product_id": str(stage.product_id),
                "stage_name": stage.stage_name,
                "stage_order": stage.stage_order,
                "status": stage.status,
                "started_at": stage.started_at.isoformat() if stage.started_at else None,
                "completed_at": stage.completed_at.isoformat() if stage.completed_at else None,
                "processing_time_seconds": stage.processing_time_seconds,
                "cost_usd": stage.cost_usd,
                "input_data": stage.input_data,
                "output_data": stage.output_data,
                "error_message": stage.error_message,
                "stage_metadata": stage.stage_metadata,
                "created_at": stage.created_at.isoformat() if stage.created_at else None
            }
            
            # Include product information if requested
            if include_product:
                product = db.query(Product).filter(Product.id == stage.product_id).first()
                if product:
                    stage_data["product"] = {
                        "name": product.name,
                        "brand": product.brand,
                        "url": product.url
                    }
            
            stage_list.append(stage_data)
        
        return {
            "stages": stage_list,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
        
    except Exception as e:
        logger.error(f"Failed to get processing stages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve processing stages: {str(e)}")

# ============================================================================
# BATCH CSV PROCESSING ENDPOINTS
# ============================================================================

@router.post("/batch/validate-csv-data")
async def validate_csv_data(file: UploadFile = File(...)):
    """
    Validate CSV file and return parsed data with validation results
    """
    try:
        # Check file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        # Read CSV content
        content = await file.read()
        csv_string = content.decode('utf-8')
        
        # Parse CSV
        df = pd.read_csv(io.StringIO(csv_string))
        
        # Required columns
        required_columns = [
            'name', 'brand', 'price', 'url', 'image_urls',
            'width_inches', 'height_inches', 'depth_inches', 'weight_kg',
            'category', 'room_type', 'style_tags', 'placement_type',
            'assembly_required', 'retailer_id', 'ikea_item_number'
        ]
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return {
                "isValid": False,
                "errorCount": len(missing_columns),
                "errors": [f"Missing required column: {col}" for col in missing_columns],
                "data": []
            }
        
        # Validate data types and required fields
        errors = []
        valid_rows = []
        
        for index, row in df.iterrows():
            row_errors = []
            
            # Check required fields
            if pd.isna(row['name']) or str(row['name']).strip() == '':
                row_errors.append(f"Row {index + 1}: Name is required")
            
            if pd.isna(row['brand']) or str(row['brand']).strip() == '':
                row_errors.append(f"Row {index + 1}: Brand is required")
            
            if pd.isna(row['price']) or not isinstance(row['price'], (int, float)) or row['price'] < 0:
                row_errors.append(f"Row {index + 1}: Price must be a positive number")
            
            if pd.isna(row['url']) or str(row['url']).strip() == '':
                row_errors.append(f"Row {index + 1}: URL is required")
            
            # Parse image URLs
            image_urls = []
            if not pd.isna(row['image_urls']):
                try:
                    # Handle comma-separated URLs
                    urls_str = str(row['image_urls']).strip()
                    if urls_str:
                        image_urls = [url.strip() for url in urls_str.split(',') if url.strip()]
                except:
                    row_errors.append(f"Row {index + 1}: Invalid image URLs format")
            
            # Parse style tags
            style_tags = []
            if not pd.isna(row['style_tags']):
                try:
                    tags_str = str(row['style_tags']).strip()
                    if tags_str:
                        style_tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                except:
                    row_errors.append(f"Row {index + 1}: Invalid style tags format")
            
            # Convert numeric fields
            try:
                price = float(row['price']) if not pd.isna(row['price']) else 0.0
                width = float(row['width_inches']) if not pd.isna(row['width_inches']) else 0.0
                height = float(row['height_inches']) if not pd.isna(row['height_inches']) else 0.0
                depth = float(row['depth_inches']) if not pd.isna(row['depth_inches']) else 0.0
                weight = float(row['weight_kg']) if not pd.isna(row['weight_kg']) else 0.0
                assembly_required = bool(row['assembly_required']) if not pd.isna(row['assembly_required']) else False
            except (ValueError, TypeError) as e:
                row_errors.append(f"Row {index + 1}: Invalid numeric values - {str(e)}")
                continue
            
            if row_errors:
                errors.extend(row_errors)
            else:
                # Create valid row data
                valid_row = {
                    'name': str(row['name']).strip(),
                    'brand': str(row['brand']).strip(),
                    'price': price,
                    'url': str(row['url']).strip(),
                    'image_urls': image_urls,
                    'width_inches': width,
                    'height_inches': height,
                    'depth_inches': depth,
                    'weight_kg': weight,
                    'category': str(row['category']).strip() if not pd.isna(row['category']) else '',
                    'room_type': str(row['room_type']).strip() if not pd.isna(row['room_type']) else '',
                    'style_tags': style_tags,
                    'placement_type': str(row['placement_type']).strip() if not pd.isna(row['placement_type']) else '',
                    'assembly_required': assembly_required,
                    'retailer_id': str(row['retailer_id']).strip() if not pd.isna(row['retailer_id']) else '',
                    'ikea_item_number': str(row['ikea_item_number']).strip() if not pd.isna(row['ikea_item_number']) else ''
                }
                valid_rows.append(valid_row)
        
        return {
            "isValid": len(errors) == 0,
            "validRows": len(valid_rows),
            "errorCount": len(errors),
            "errors": errors[:10],  # Limit to first 10 errors
            "data": valid_rows
        }
        
    except Exception as e:
        logger.error(f"CSV validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate CSV: {str(e)}")

@router.post("/batch/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload and validate CSV file - NO DATABASE STORAGE
    This just validates the CSV and returns the data for frontend processing
    """
    try:
        # Read file content once
        content = await file.read()
        csv_string = content.decode('utf-8')
        
        # Parse CSV
        df = pd.read_csv(io.StringIO(csv_string))
        
        # Required columns
        required_columns = [
            'name', 'brand', 'price', 'url', 'image_urls',
            'width_inches', 'height_inches', 'depth_inches', 'weight_kg',
            'category', 'room_type', 'style_tags', 'placement_type',
            'assembly_required', 'retailer_id', 'ikea_item_number'
        ]
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Validate data types and required fields
        errors = []
        valid_rows = []
        
        for index, row in df.iterrows():
            row_errors = []
            
            # Check required fields
            if pd.isna(row['name']) or str(row['name']).strip() == '':
                row_errors.append(f"Row {index + 1}: Name is required")
            
            if pd.isna(row['brand']) or str(row['brand']).strip() == '':
                row_errors.append(f"Row {index + 1}: Brand is required")
            
            if pd.isna(row['price']) or not isinstance(row['price'], (int, float)) or row['price'] < 0:
                row_errors.append(f"Row {index + 1}: Price must be a positive number")
            
            if pd.isna(row['url']) or str(row['url']).strip() == '':
                row_errors.append(f"Row {index + 1}: URL is required")
            
            # Parse image URLs
            image_urls = []
            if not pd.isna(row['image_urls']):
                try:
                    # Handle comma-separated URLs
                    urls_str = str(row['image_urls']).strip()
                    if urls_str:
                        image_urls = [url.strip() for url in urls_str.split(',') if url.strip()]
                except:
                    row_errors.append(f"Row {index + 1}: Invalid image URLs format")
            
            # Parse style tags
            style_tags = []
            if not pd.isna(row['style_tags']):
                try:
                    tags_str = str(row['style_tags']).strip()
                    if tags_str:
                        style_tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                except:
                    row_errors.append(f"Row {index + 1}: Invalid style tags format")
            
            # Convert numeric fields
            try:
                price = float(row['price']) if not pd.isna(row['price']) else 0.0
                width = float(row['width_inches']) if not pd.isna(row['width_inches']) else 0.0
                height = float(row['height_inches']) if not pd.isna(row['height_inches']) else 0.0
                depth = float(row['depth_inches']) if not pd.isna(row['depth_inches']) else 0.0
                weight = float(row['weight_kg']) if not pd.isna(row['weight_kg']) else 0.0
                assembly_required = bool(row['assembly_required']) if not pd.isna(row['assembly_required']) else False
            except (ValueError, TypeError) as e:
                row_errors.append(f"Row {index + 1}: Invalid numeric values - {str(e)}")
                continue
            
            if row_errors:
                errors.extend(row_errors)
            else:
                # Create valid row data
                valid_row = {
                    'name': str(row['name']).strip(),
                    'brand': str(row['brand']).strip(),
                    'price': price,
                    'url': str(row['url']).strip(),
                    'image_urls': image_urls,
                    'width_inches': width,
                    'height_inches': height,
                    'depth_inches': depth,
                    'weight_kg': weight,
                    'category': str(row['category']).strip() if not pd.isna(row['category']) else '',
                    'room_type': str(row['room_type']).strip() if not pd.isna(row['room_type']) else '',
                    'style_tags': style_tags,
                    'placement_type': str(row['placement_type']).strip() if not pd.isna(row['placement_type']) else '',
                    'assembly_required': assembly_required,
                    'retailer_id': str(row['retailer_id']).strip() if not pd.isna(row['retailer_id']) else '',
                    'ikea_item_number': str(row['ikea_item_number']).strip() if not pd.isna(row['ikea_item_number']) else ''
                }
                valid_rows.append(valid_row)
        
        if errors:
            raise HTTPException(
                status_code=400, 
                detail=f"CSV validation failed: {len(errors)} errors found"
            )
        
        # Return validated data WITHOUT storing in database
        return {
            "isValid": True,
            "validRows": len(valid_rows),
            "errorCount": 0,
            "errors": [],
            "data": valid_rows,
            "message": f"CSV validated successfully - {len(valid_rows)} products ready for processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CSV validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate CSV: {str(e)}")

@router.get("/batch/download-template")
async def download_template():
    """
    Download CSV template file
    """
    try:
        # Create template CSV content
        template_data = {
            'name': ['STOCKHOLM 2025 3-seat sofa', 'EKTORP 3-seat sofa'],
            'brand': ['IKEA', 'IKEA'],
            'price': [1899.0, 899.0],
            'url': [
                'https://www.ikea.com/us/en/p/stockholm-2025-3-seat-sofa-alhamn-beige-s69574294/',
                'https://www.ikea.com/us/en/p/ektorp-3-seat-sofa-lofallet-beige-s69220332/'
            ],
            'image_urls': [
                'https://www.ikea.com/us/en/images/products/stockholm-2025-3-seat-sofa-alhamn-beige__1362835_pe955331_s5.jpg?f=xl,https://www.ikea.com/us/en/images/products/stockholm-2025-3-seat-sofa-alhamn-beige__1362835_pe955331_s6.jpg?f=xl',
                'https://www.ikea.com/us/en/images/products/ektorp-3-seat-sofa-lofallet-beige__s69220332_pe955331_s5.jpg?f=xl,https://www.ikea.com/us/en/images/products/ektorp-3-seat-sofa-lofallet-beige__s69220332_pe955331_s6.jpg?f=xl'
            ],
            'width_inches': [95.625, 88.625],
            'height_inches': [27.5, 25.625],
            'depth_inches': [39.0, 35.0],
            'weight_kg': [45.0, 35.0],
            'category': ['seating', 'seating'],
            'room_type': ['living', 'living'],
            'style_tags': ['modern,scandinavian', 'classic,comfortable'],
            'placement_type': ['floor', 'floor'],
            'assembly_required': [False, True],
            'retailer_id': ['S69574294', 'S69220332'],
            'ikea_item_number': ['S69574294', 'S69220332']
        }
        
        df = pd.DataFrame(template_data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        
        # Create response
        response = StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=batch_products_template.csv"}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Template download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate template: {str(e)}")

# ============================================================================
# MONITORING AND HEALTH ENDPOINTS
# ============================================================================

@router.get(
    "/health",
    summary="System Health Check",
    description="""
    Comprehensive health check endpoint that provides:
    - **System Status**: Overall API health
    - **Database Status**: Database connectivity and performance
    - **WebSocket Status**: Active connection count
    - **Memory Usage**: Current memory consumption
    - **Uptime**: System uptime information
    - **Version**: API version and build info
    
    This endpoint is used by monitoring systems and load balancers.
    """,
    responses={
        200: {
            "description": "System is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "version": "1.0.0",
                        "uptime": "2d 5h 30m",
                        "database": {
                            "status": "connected",
                            "response_time_ms": 12
                        },
                        "websocket": {
                            "active_connections": 5
                        },
                        "memory": {
                            "used_mb": 128.5,
                            "total_mb": 512.0
                        }
                    }
                }
            }
        },
        503: {"description": "System is unhealthy"}
    },
    tags=["Monitoring & Health"]
)
async def health_check():
    """
    Health check endpoint with detailed system status
    
    **Returns:**
    - `status`: Overall system health (healthy/unhealthy)
    - `timestamp`: Current timestamp
    - `version`: API version
    - `uptime`: System uptime
    - `database`: Database status and performance
    - `websocket`: WebSocket connection info
    - `memory`: Memory usage statistics
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

@router.delete("/products/{product_id}")
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    """Delete a product and clean up all associated files"""
    try:
        # Check if product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Clean up local files first
        deleted_files = cleanup_product_files(db, product_id)
        
        # Delete processing stages
        stages_deleted = db.query(ProcessingStage).filter(
            ProcessingStage.product_id == product_id
        ).delete(synchronize_session=False)
        
        # Delete product images
        images_deleted = db.query(ProductImage).filter(
            ProductImage.product_id == product_id
        ).delete(synchronize_session=False)
        
        # Delete 3D models and LODs
        models = db.query(Model3D).filter(Model3D.product_id == product_id).all()
        model_ids = [m.id for m in models]
        
        if model_ids:
            # Delete LODs first
            lods_deleted = db.query(ModelLOD).filter(
                ModelLOD.model_3d_id.in_(model_ids)
            ).delete(synchronize_session=False)
            
            # Delete 3D models
            models_deleted = db.query(Model3D).filter(
                Model3D.product_id == product_id
            ).delete(synchronize_session=False)
        else:
            lods_deleted = 0
            models_deleted = 0
        
        # Finally, delete the product
        product_deleted = db.query(Product).filter(Product.id == product_id).delete(synchronize_session=False)
        
        # Commit all changes
        db.commit()
        
        return {
            "message": "Product deleted successfully",
            "product_id": product_id,
            "deleted_files": deleted_files,
            "deleted_stages": stages_deleted,
            "deleted_images": images_deleted,
            "deleted_models": models_deleted,
            "deleted_lods": lods_deleted
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

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


@router.get("/proxy-model")
async def proxy_model(url: str):
    """Proxy external model files to avoid CORS issues"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return Response(
                content=response.content,
                media_type="model/gltf-binary",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Cache-Control": "public, max-age=3600"
                }
            )
    except Exception as e:
        logger.error(f"Failed to proxy model: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch model")
