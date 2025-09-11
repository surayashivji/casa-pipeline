from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

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
    in_stock: Optional[bool] = True
    popularity_score: Optional[int] = None
    processing_mode: Optional[str] = None
    status: Optional[str] = "scraped"
    error_message: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
