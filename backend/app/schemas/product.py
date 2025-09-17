from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from enum import Enum

class ProductBase(BaseModel):
    url: str
    name: str
    brand: Optional[str] = None
    variant_info: Optional[str] = None
    price: Optional[float] = None
    width_inches: Optional[float] = None
    height_inches: Optional[float] = None
    depth_inches: Optional[float] = None
    weight_kg: Optional[float] = None
    category: Optional[str] = None
    room_type: Optional[str] = None
    style_tags: Optional[List[str]] = None
    placement_type: Optional[str] = None
    default_rotation: Optional[int] = None
    retailer_id: Optional[str] = None
    ikea_item_number: Optional[str] = None
    ikea_product_type: Optional[str] = None
    assembly_required: Optional[bool] = None
    package_count: Optional[int] = None
    popularity_score: Optional[int] = None
    processing_mode: Optional[str] = None
    status: Optional[str] = "scraped"
    error_message: Optional[str] = None

class ProductCreate(ProductBase):
    pass

# API Request/Response Models for Product Operations

class URLType(str, Enum):
    PRODUCT = "product"
    CATEGORY = "category"
    SEARCH = "search"
    UNKNOWN = "unknown"

class ProductDimensions(BaseModel):
    width: float
    height: float
    depth: float
    unit: str = "inches"

class Product(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    dimensions: Optional[ProductDimensions] = None
    description: Optional[str] = None
    weight: Optional[float] = None
    
    class Config:
        from_attributes = True

class URLDetectionRequest(BaseModel):
    url: str

class URLDetectionResponse(BaseModel):
    url: str
    type: URLType
    retailer: str
    supported: bool
    confidence: float

class ScrapeRequest(BaseModel):
    url: str
    mode: str = "single"

class ScrapeResponse(BaseModel):
    product: Product  # Use existing Product schema
    images: List[str]  # Simple URLs for frontend
    processing_time: float
    cost: float

class ImageSelectionRequest(BaseModel):
    product_id: UUID
    image_urls: List[str]

class ImageSelectionResponse(BaseModel):
    product_id: UUID
    selected_images: List[str]
    selected_count: int

class BackgroundRemovalRequest(BaseModel):
    product_id: UUID
    image_urls: List[str]

class BackgroundRemovalResponse(BaseModel):
    product_id: UUID
    processed_images: List[Dict[str, Any]]  # Matches frontend expectations
    total_processing_time: float
    total_cost: float
    success_rate: float

class ImageApprovalRequest(BaseModel):
    product_id: UUID
    image_urls: List[str]
    approved: bool

class ImageApprovalResponse(BaseModel):
    product_id: UUID
    status: str
    approved_count: int
    rejected_count: int

class Generate3DRequest(BaseModel):
    product_id: UUID
    image_urls: List[str]
    settings: Optional[Dict[str, Any]] = {}

class Generate3DResponse(BaseModel):
    product_id: UUID
    task_id: str
    status: str
    estimated_completion: datetime
    cost: float

class ModelStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[int] = None
    model_url: Optional[str] = None
    processing_time: Optional[float] = None
    cost: Optional[float] = None
    model_quality: Optional[float] = None
    lods_available: Optional[List[str]] = None
    model_urls: Optional[Dict] = None  
    texture_url: Optional[str] = None 

    class Config:
        protected_namespaces = ()  # Add this to fix the warning
