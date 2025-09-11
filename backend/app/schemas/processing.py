from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Processing Stage Schemas
class ProcessingStageBase(BaseModel):
    stage_name: str
    stage_order: int
    status: str = "pending"
    processing_time_seconds: Optional[float] = None
    cost_usd: float = 0.0
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    metadata: Optional[dict] = None

class ProcessingStageCreate(ProcessingStageBase):
    product_id: UUID

class ProcessingStage(ProcessingStageBase):
    id: UUID
    product_id: UUID
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Product Image Schemas
class ProductImageBase(BaseModel):
    image_type: str  # 'original', 'processed', 'mask', 'preview'
    image_order: int = 0
    s3_url: str
    file_size_bytes: Optional[int] = None
    width_pixels: Optional[int] = None
    height_pixels: Optional[int] = None
    format: Optional[str] = None
    is_primary: bool = False

class ProductImageCreate(ProductImageBase):
    product_id: UUID
    processing_stage_id: Optional[UUID] = None

class ProductImage(ProductImageBase):
    id: UUID
    product_id: UUID
    processing_stage_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# 3D Model Schemas
class Model3DBase(BaseModel):
    meshy_job_id: Optional[str] = None
    model_name: Optional[str] = None
    s3_url: str
    file_size_bytes: Optional[int] = None
    format: str = "glb"
    vertices_count: Optional[int] = None
    triangles_count: Optional[int] = None
    materials_count: Optional[int] = None
    textures_count: Optional[int] = None
    generation_time_seconds: Optional[float] = None
    cost_usd: float = 0.0
    is_optimized: bool = False
    optimization_ratio: Optional[float] = None

class Model3DCreate(Model3DBase):
    product_id: UUID
    processing_stage_id: Optional[UUID] = None

class Model3D(Model3DBase):
    id: UUID
    product_id: UUID
    processing_stage_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Model LOD Schemas
class ModelLODBase(BaseModel):
    lod_level: str  # 'high', 'medium', 'low'
    lod_order: int
    s3_url: str
    file_size_bytes: Optional[int] = None
    vertices_count: Optional[int] = None
    triangles_count: Optional[int] = None
    is_default: bool = False
    target_device: Optional[str] = None

class ModelLODCreate(ModelLODBase):
    model_3d_id: UUID

class ModelLOD(ModelLODBase):
    id: UUID
    model_3d_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Batch Job Schemas
class BatchJobBase(BaseModel):
    job_name: Optional[str] = None
    category: Optional[str] = None
    status: str = "pending"
    total_products: int = 0
    processed_products: int = 0
    successful_products: int = 0
    failed_products: int = 0
    total_cost_usd: float = 0.0
    processing_options: Optional[dict] = None

class BatchJobCreate(BatchJobBase):
    pass

class BatchJob(BatchJobBase):
    id: UUID
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Complete Product with Processing Data
class ProductWithProcessing(BaseModel):
    # Basic product info
    id: UUID
    url: str
    name: str
    brand: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    room_type: Optional[str] = None
    style_tags: Optional[List[str]] = None
    placement_type: Optional[str] = None
    
    # Dimensions
    width_inches: Optional[float] = None
    height_inches: Optional[float] = None
    depth_inches: Optional[float] = None
    weight_kg: Optional[float] = None
    
    # Status
    status: str
    processing_mode: Optional[str] = None
    total_processing_time_seconds: Optional[float] = None
    total_cost_usd: float = 0.0
    
    # Processing data
    processing_stages: List[ProcessingStage] = []
    images: List[ProductImage] = []
    models_3d: List[Model3D] = []
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
