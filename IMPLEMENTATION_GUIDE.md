# Room Decorator 3D Pipeline - Complete Implementation Guide

## Executive Overview

You're building a pipeline that automatically converts home goods products from retailer websites into 3D models for an iOS virtual room decorator app. The system will scrape product images, process them, generate 3D models, and optimize them for real-time rendering on iOS devices.

### Key Features:
- **Two Modes**: Single product (manual validation) and Batch (automatic processing)
- **GUI-First Development**: Build and validate the interface before backend implementation
- **Multi-Retailer Support**: Starting with IKEA, expanding to Target, West Elm, Urban Outfitters
- **iOS Optimization**: LOD system for smooth performance across all iPhone/iPad models
- **Scalable Architecture**: Local development → Cloud production

## System Architecture

```
┌─────────────────────────────────────┐
│         Your Browser                 │
│  ┌─────────────────────────────┐    │
│  │     React Interface         │    │
│  │  - Mode Selection           │    │
│  │  - Single Product Pipeline  │    │
│  │  - Batch Processing         │    │
│  │  - Results Dashboard        │    │
│  └──────────┬──────────────────┘    │
└─────────────┼───────────────────────┘
              │ HTTP requests
              ↓
┌─────────────────────────────────────┐
│      Backend Server (Python)        │
│  - FastAPI web server               │
│  - URL type detection               │
│  - Playwright scraper               │
│  - RMBG background removal         │
│  - Meshy API integration           │
│  - Batch queue system              │
└──────────┬──────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│         PostgreSQL Database         │
│  - Products table                   │
│  - Images table                     │
│  - Models table                     │
│  - Batch jobs table                │
│  - Analytics table                 │
└─────────────────────────────────────┘
```

## Two Pipeline Modes

### Mode 1: Single Product Pipeline (Manual Control)
For testing, validation, and high-value items where quality matters most.

**Flow**: URL Input → Scrape → Review Data → Select Images → Remove Backgrounds → 
Approve Results → Generate 3D → Review Model → Optimize → Save

**Use Cases**:
- Testing new scrapers
- High-value furniture pieces
- Debugging problematic products
- Training the system

### Mode 2: Batch Pipeline (Automatic Processing)
For processing entire categories or search results with smart defaults.

**Flow**: Category URL → Get Product List → Select Products → Auto-Process All → 
Review Results → Export Models

**Use Cases**:
- Processing entire categories (e.g., all IKEA chairs)
- Daily catalog updates
- Bulk inventory ingestion
- Search result processing

## URL Pattern Detection

The system must detect what type of URL is pasted:

### Product URLs (Single Mode)
- `https://www.ikea.com/us/en/p/stefan-chair-brown-black-00211088/`
- `https://www.urbanoutfitters.com/shop/rhea-swivel-lounge-chair`
- `https://www.westelm.com/products/mid-century-sofa`
- `https://www.target.com/p/item/-/A-54551690`

### Category URLs (Batch Mode)
- `https://www.ikea.com/us/en/cat/chairs-20202/`
- `https://www.urbanoutfitters.com/furniture`
- `https://www.westelm.com/shop/furniture/all-sofas/`
- `https://www.target.com/c/living-room-furniture/`

### Search URLs (Batch Mode)
- `https://www.ikea.com/search/?q=dining+table`
- `https://www.urbanoutfitters.com/search?q=mirror`

### Collection/Room URLs (Batch Mode)
- `https://www.ikea.com/rooms/bedroom/gallery/`
- `https://www.westelm.com/shop/rooms/living-room/`

## Database Schema

```sql
-- Products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100),
    variant_info VARCHAR(255),
    price DECIMAL(10,2),
    
    -- Dimensions for virtual room scaling
    width_inches DECIMAL(10,2),
    height_inches DECIMAL(10,2),
    depth_inches DECIMAL(10,2),
    weight_kg DECIMAL(10,2),
    
    -- iOS Room Designer specific
    category VARCHAR(50),  -- 'seating', 'tables', 'storage', 'decor'
    room_type VARCHAR(50),  -- 'living', 'bedroom', 'kitchen', 'bathroom'
    style_tags TEXT[],  -- ['modern', 'scandinavian', 'minimal']
    placement_type VARCHAR(20),  -- 'floor', 'wall', 'tabletop', 'ceiling'
    default_rotation INTEGER,  -- 0, 90, 180, 270 degrees
    
    -- Retailer specific
    retailer_id VARCHAR(100),  -- Store's internal product ID
    ikea_item_number VARCHAR(20),  -- "004.110.88"
    ikea_product_type VARCHAR(50),  -- "chair", "table", etc.
    assembly_required BOOLEAN,
    package_count INTEGER,
    
    -- Status tracking
    in_stock BOOLEAN DEFAULT true,
    popularity_score INTEGER,
    processing_mode VARCHAR(20),  -- 'single' or 'batch'
    batch_job_id UUID REFERENCES batch_jobs(id),
    status VARCHAR(50) DEFAULT 'scraped',
    error_message TEXT,
    last_scraped_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Batch jobs table
CREATE TABLE batch_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_url TEXT NOT NULL,
    source_type VARCHAR(50),  -- 'category', 'search', 'collection', 'room'
    total_products INTEGER,
    processed_count INTEGER DEFAULT 0,
    successful_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    status VARCHAR(50),  -- 'pending', 'processing', 'completed', 'failed'
    settings JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Product images table
CREATE TABLE product_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    image_url TEXT NOT NULL,
    image_type VARCHAR(50),  -- 'original', 'processed'
    is_transparent BOOLEAN DEFAULT false,
    transparency_score DECIMAL(3,2),
    is_approved BOOLEAN DEFAULT false,
    auto_approved BOOLEAN DEFAULT false,
    local_path TEXT,
    s3_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3D models table
CREATE TABLE product_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    model_url TEXT NOT NULL,
    lod_level VARCHAR(20),  -- 'high', 'medium', 'low', 'original'
    polygon_count INTEGER,
    file_size_bytes BIGINT,
    format VARCHAR(20),  -- 'glb', 'usdz', 'reality'
    generation_method VARCHAR(50),  -- 'meshy', 'manual'
    generation_time_seconds INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Processing analytics table
CREATE TABLE processing_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    step_name VARCHAR(50),  -- 'scraping', 'bg_removal', '3d_generation'
    duration_seconds INTEGER,
    success BOOLEAN,
    error_details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Room templates table
CREATE TABLE room_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100),
    room_type VARCHAR(50),
    style VARCHAR(50),
    product_ids UUID[],
    thumbnail_url TEXT,
    popularity_score INTEGER
);

-- Product combinations table
CREATE TABLE product_combinations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    primary_product_id UUID REFERENCES products(id),
    recommended_products UUID[],
    usage_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

# STEP-BY-STEP IMPLEMENTATION PLAN

## Phase 0: Environment Setup & Architecture Validation (Week 0)

**Goal**: Establish consistent development environment and validate stack

### Deliverables:
- [ ] Development environment with Node.js, Python 3.9+, PostgreSQL
- [ ] Project structure created
- [ ] Git repository initialized with .gitignore
- [ ] React app boilerplate (Create React App or Vite)
- [ ] FastAPI project structure
- [ ] Docker Compose for local PostgreSQL
- [ ] Environment variables configuration (.env files)
- [ ] API contract documentation (OpenAPI/Swagger)
- [ ] Basic CI/CD pipeline skeleton

### Success Criteria:
- Can run React app locally
- Can run FastAPI server locally
- PostgreSQL accessible via Docker
- Hot reload working for both frontend and backend

## Phase 1: Build Complete GUI with Mock Data (Week 1)

**Goal**: Create the entire interface with both Single and Batch modes using mock data

### Deliverables:
- [ ] React app with mode selector toggle
- [ ] Single Product Pipeline UI:
  - [ ] URL input with validation
  - [ ] Product data review card
  - [ ] Image selector grid (multi-select)
  - [ ] Background removal before/after viewer
  - [ ] Approval interface with quality scores
  - [ ] 3D model preview (using Three.js)
  - [ ] LOD comparison viewer
  - [ ] Save confirmation screen
- [ ] Batch Processing UI:
  - [ ] Category URL input
  - [ ] Product grid with checkboxes
  - [ ] Selection controls (select all, filter, sort)
  - [ ] Processing queue with real-time status
  - [ ] Progress tracker with percentage
  - [ ] Results summary dashboard
  - [ ] Bulk export interface
- [ ] Mock data for all scenarios:
  - [ ] 5 real IKEA products (manually extracted)
  - [ ] Simulated processing states
  - [ ] Error scenarios
- [ ] Responsive design for desktop/tablet
- [ ] Loading states and error boundaries

### Key Components to Build:
```
src/
├── components/
│   ├── ModeSelector/
│   ├── SinglePipeline/
│   │   ├── URLInput/
│   │   ├── ProductReview/
│   │   ├── ImageSelector/
│   │   ├── BackgroundRemoval/
│   │   ├── ModelViewer/
│   │   └── LODComparison/
│   ├── BatchPipeline/
│   │   ├── CategoryInput/
│   │   ├── ProductGrid/
│   │   ├── ProcessingQueue/
│   │   └── ResultsDashboard/
│   └── shared/
│       ├── ProgressBar/
│       ├── StatusIndicator/
│       └── ErrorDisplay/
```

### Success Criteria:
- Can click through both modes completely
- All UI states are visible and functional
- Mock data covers happy path and error cases
- UI is intuitive without documentation

## Phase 2: Create Backend API Structure (Week 2)

**Goal**: Build FastAPI backend with all endpoints using mock data

### Deliverables:
- [ ] FastAPI server with CORS configuration
- [ ] URL type detection endpoint
- [ ] Single product endpoints
- [ ] Batch processing endpoints
- [ ] WebSocket support for real-time updates
- [ ] Mock data responses matching frontend
- [ ] API documentation (auto-generated)
- [ ] Request validation with Pydantic
- [ ] Error handling middleware
- [ ] Logging configuration

### API Endpoints:

#### URL Detection
```http
POST /api/detect-url
Request: {"url": "string"}
Response: {"type": "product|category|search", "retailer": "ikea"}
```

#### Single Product Pipeline
```http
POST /api/scrape
Request: {"url": "string", "mode": "single"}
Response: {"product": {...}, "images": [...]}

POST /api/select-images
Request: {"product_id": "uuid", "image_ids": ["uuid"]}
Response: {"selected_count": 3}

POST /api/remove-backgrounds
Request: {"image_ids": ["uuid"]}
Response: {"processed_images": [...]}

POST /api/approve-images
Request: {"image_ids": ["uuid"], "approved": true}
Response: {"status": "approved"}

POST /api/generate-3d
Request: {"product_id": "uuid", "settings": {...}}
Response: {"task_id": "string", "status": "pending"}

GET /api/model-status/{task_id}
Response: {"status": "completed", "model_url": "string"}
```

#### Batch Processing
```http
POST /api/scrape-category
Request: {"url": "string", "limit": 50}
Response: {"products": [...], "total": 150}

POST /api/batch-process
Request: {"product_ids": ["uuid"], "settings": {...}}
Response: {"batch_id": "uuid", "status": "processing"}

GET /api/batch-status/{batch_id}
Response: {"processed": 25, "total": 50, "failed": 2}
```

#### WebSocket
```http
WS /ws/batch-updates
Message: {"batch_id": "uuid", "product_id": "uuid", "status": "string"}
```

### Success Criteria:
- All endpoints return appropriate mock data
- WebSocket sends simulated updates
- API documentation accessible at /docs
- Frontend can connect to all endpoints

## Phase 3: Implement Real Scraping - IKEA First (Week 3)

**Goal**: Replace mock scraping with actual Playwright scrapers, starting with IKEA

### Week 3a: IKEA Single Product Scraper (Days 1-2)
- [ ] Playwright installed and configured
- [ ] IKEA product URL parser
- [ ] Extract product JSON data
- [ ] Download all product images (high-res)
- [ ] Parse dimensions and specifications
- [ ] Handle product variants
- [ ] Error handling for missing data

### Week 3b: IKEA Category Scraper (Days 3-4)
- [ ] Category page parser
- [ ] Pagination handling
- [ ] Product list extraction
- [ ] Filtering and sorting options
- [ ] Handle lazy loading
- [ ] Rate limiting (1 request/second)

### Week 3c: Urban Outfitters Scraper (Days 5-7)
- [ ] Handle React-based site
- [ ] Dynamic content loading
- [ ] Extract product data from DOM
- [ ] Image gallery extraction
- [ ] Handle missing dimensions

### Scraper Requirements:
```python
class IKEAScraper:
    def scrape_product(url: str) -> Product:
        # Extract from embedded JSON
        # Get all image URLs
        # Parse dimensions
        # Return structured data
    
    def scrape_category(url: str, limit: int) -> List[Product]:
        # Parse category page
        # Handle pagination
        # Extract product URLs
        # Return product list
```

### Success Criteria:
- Successfully scrape 10 diverse IKEA products
- Category scraper handles pagination
- Rate limiting prevents blocking
- Graceful handling of missing data

## Phase 4: Add PostgreSQL Database (Week 4)

**Goal**: Set up database and connect all endpoints

### Deliverables:
- [ ] PostgreSQL running in Docker
- [ ] All tables created with migrations
- [ ] SQLAlchemy ORM models
- [ ] Database connection pooling
- [ ] Products saving with upsert logic
- [ ] Batch job tracking
- [ ] Image metadata storage
- [ ] Transaction handling
- [ ] Database indexes for performance

### Database Operations:
```python
# Key operations to implement
- upsert_product(product_data)
- create_batch_job(source_url, settings)
- update_batch_progress(batch_id, product_id, status)
- store_image_metadata(product_id, images)
- get_products_by_status(status)
- get_batch_job_details(batch_id)
```

### Success Criteria:
- All CRUD operations working
- Concurrent updates handled properly
- No duplicate products (URL is unique)
- Batch progress accurately tracked

## Phase 5: Integrate Background Removal (Week 5)

**Goal**: Implement RMBG for background removal

### Deliverables:
- [ ] RMBG installed with model downloaded
- [ ] Single image processing endpoint
- [ ] Batch image processing with queue
- [ ] Transparency validation (score calculation)
- [ ] Quality scoring system
- [ ] Auto-approval logic (score > 0.85)
- [ ] Before/after image storage
- [ ] Skip already-transparent images (IKEA)

### Processing Pipeline:
```python
def process_image(image_path):
    # Check if already transparent
    if has_transparency(image_path):
        return image_path, 1.0
    
    # Remove background
    result = remove_background(image_path)
    
    # Calculate transparency score
    score = calculate_transparency_score(result)
    
    # Auto-approve if high quality
    auto_approved = score > 0.85
    
    return result, score, auto_approved
```

### Image Quality Gates:
- Minimum resolution: 1024x1024
- Maximum file size: 10MB
- Aspect ratio: 1:3 to 3:1 max
- Color space: RGB only
- Transparency score minimum: 0.80

### Success Criteria:
- 90% of IKEA images process successfully
- Average processing time < 5 seconds/image
- Transparency scores are accurate
- Failed removals are detected

## Phase 6: Connect Meshy API (Week 6-7)

**Goal**: Generate real 3D models from processed images

### Deliverables:
- [ ] Meshy API credentials configured
- [ ] Single product 3D generation
- [ ] Batch generation queue
- [ ] Task status polling
- [ ] Error handling and retries
- [ ] Cost tracking per model
- [ ] Model URL storage
- [ ] Webhook support (if available)

### Meshy Integration:
```python
class MeshyClient:
    def create_task(images: List[str], settings: dict) -> str:
        # Submit to Meshy API
        # Return task_id
    
    def check_status(task_id: str) -> dict:
        # Poll for completion
        # Return status and URL
    
    def batch_process(products: List[Product]) -> List[Task]:
        # Queue multiple products
        # Handle rate limits
        # Return task list
```

### Meshy Settings:
```python
SINGLE_MODE_SETTINGS = {
    "quality": "high",
    "enable_pbr": True,
    "auto_orient": True,
    "target_polycount": 30000
}

BATCH_MODE_SETTINGS = {
    "quality": "standard",  # Faster, lower cost
    "enable_pbr": True,
    "auto_orient": True,
    "target_polycount": 15000
}
```

### Success Criteria:
- 3D models generating successfully
- Polling system works reliably
- Failed tasks are retried (up to 3x)
- Cost tracking is accurate

## Phase 7: Add Model Optimization (Week 8)

**Goal**: Create LOD versions for different iOS devices

### Deliverables:
- [ ] Trimesh library integrated
- [ ] LOD generation pipeline
- [ ] Polygon reduction algorithm
- [ ] Texture resizing
- [ ] File format conversion (GLB, USDZ)
- [ ] Compression and optimization
- [ ] Validation of outputs

### LOD Targets for iOS:
```python
LOD_CONFIGS = {
    "high": {
        "polygons": 30000,
        "texture_size": 2048,
        "devices": ["iPad Pro", "iPhone 14 Pro"]
    },
    "medium": {
        "polygons": 10000,
        "texture_size": 1024,
        "devices": ["iPhone 12", "iPhone 13"]
    },
    "low": {
        "polygons": 3000,
        "texture_size": 512,
        "devices": ["iPhone SE", "iPhone 11"]
    }
}
```

### iOS Performance Budgets:
```python
ROOM_LIMITS = {
    "iPhone_14_Pro": {
        "max_polygons_total": 200000,
        "max_textures_mb": 100,
        "max_objects": 50
    },
    "iPhone_12": {
        "max_polygons_total": 100000,
        "max_textures_mb": 75,
        "max_objects": 30
    },
    "iPhone_SE": {
        "max_polygons_total": 50000,
        "max_textures_mb": 50,
        "max_objects": 20
    }
}
```

### Success Criteria:
- All 3 LOD levels generating
- USDZ files working on iOS
- File sizes appropriate for mobile
- Models maintain visual quality

## Phase 8: Implement Batch Processing System (Week 9)

**Goal**: Enable parallel processing of multiple products

### Deliverables:
- [ ] Queue system (Redis or database-based)
- [ ] Worker pool for parallel processing
- [ ] Progress tracking per product
- [ ] Real-time WebSocket updates
- [ ] Error recovery and retry logic
- [ ] Batch results summary
- [ ] Export functionality
- [ ] Priority queue support

### Batch Processing Features:
```python
class BatchProcessor:
    def __init__(self, max_workers=4):
        self.queue = Queue()
        self.workers = []
        
    def process_batch(batch_id: str, products: List[Product]):
        # Add to queue with priority
        # Start workers
        # Track progress
        # Handle failures
        # Generate summary
```

### Smart Defaults for Batch:
- Maximum 4 images per product
- Skip lifestyle shots with people
- Auto-approve if transparency > 0.85
- Retry failed products up to 3 times
- Continue batch even if individuals fail

### Success Criteria:
- Can process 50 products in parallel
- Real-time updates working
- Failed products don't stop batch
- Memory usage stays stable

## Phase 9: Add Multi-Retailer Support (Week 10)

**Goal**: Expand beyond IKEA to other furniture retailers

### Retailer Priority Order:
1. **IKEA** ✅ (Week 3)
2. **Target** (Has API, structured data)
3. **West Elm** (Premium furniture, good images)
4. **Urban Outfitters** (Complex scraping)

### Deliverables:
- [ ] Target scraper (API-based)
- [ ] West Elm scraper
- [ ] Scraper factory pattern
- [ ] Retailer-specific parsers
- [ ] Universal data normalizer
- [ ] Error handling per retailer

### Scraper Factory:
```python
class ScraperFactory:
    @staticmethod
    def get_scraper(url: str) -> BaseScraper:
        if "ikea.com" in url:
            return IKEAScraper()
        elif "target.com" in url:
            return TargetScraper()
        elif "westelm.com" in url:
            return WestElmScraper()
        else:
            raise UnknownRetailerError(url)
```

### Success Criteria:
- All 4 retailers working
- Data normalized across retailers
- Graceful fallback for missing data
- Retailer-specific features preserved

## Phase 10: Production Optimization (Week 11-12)

**Goal**: Prepare for scale and production deployment

### Deliverables:
- [ ] Redis caching layer
- [ ] S3 storage for images/models
- [ ] CloudFront CDN setup
- [ ] Database query optimization
- [ ] API rate limiting
- [ ] Authentication system
- [ ] Monitoring (Sentry, DataDog)
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Load testing

### Production Architecture:
```yaml
# docker-compose.prod.yml
services:
  frontend:
    image: room-decorator-frontend
    ports: ["3000:3000"]
  
  backend:
    image: room-decorator-backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL
      - REDIS_URL
      - S3_BUCKET
      - MESHY_API_KEY
  
  postgres:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    ports: ["6379:6379"]
  
  worker:
    image: room-decorator-backend
    command: celery worker
    scale: 4
```

### Monitoring & Observability:
- Processing success rate by retailer
- Average time per pipeline step
- Cost per model tracking
- API usage and limits
- Error rate by step
- Queue depth and processing speed

### Success Criteria:
- Handle 1000+ products per day
- 99% uptime
- < 5 minute average processing time
- Auto-scaling working
- Costs optimized (< $0.75/model)

## Error Recovery Strategy

### Scraping Failures:
```python
SCRAPING_STRATEGY = {
    "max_retries": 3,
    "retry_delay": [5, 30, 300],  # seconds
    "user_agents": [...],  # Rotate on retry
    "proxy_rotation": True,
    "screenshot_on_failure": True,
    "fallback_to_cached": True
}
```

### Background Removal Failures:
```python
BG_REMOVAL_STRATEGY = {
    "max_retries": 2,
    "fallback_quality": "lower",
    "skip_if_transparent": True,
    "manual_review_queue": True
}
```

### 3D Generation Failures:
```python
MESHY_STRATEGY = {
    "max_retries": 3,
    "retry_with_fewer_images": True,
    "fallback_to_lower_quality": True,
    "try_alternative_angles": True,
    "queue_for_manual_review": True
}
```

### Batch Processing Failures:
```python
BATCH_STRATEGY = {
    "continue_on_error": True,
    "retry_failed_at_end": True,
    "max_failure_percentage": 20,  # Abort if >20% fail
    "notification_threshold": 10,  # Alert if >10% fail
}
```

## Key Performance Indicators (KPIs)

### Quality Metrics:
- **Model Quality Score**: > 85% pass automated checks
- **Transparency Score**: > 80% achieve 0.85+ score
- **Dimension Accuracy**: Within 5% of actual size
- **Texture Quality**: 90% maintain original colors

### Performance Metrics:
- **Processing Speed**: 90% complete in < 3 minutes
- **Batch Throughput**: 50 products/hour minimum
- **API Response Time**: < 500ms for 95% of requests
- **iOS Load Time**: Room with 20 objects loads in < 3 seconds
- **Frame Rate**: Maintain 60fps with 30 objects on iPhone 12

### Cost Metrics:
- **Cost Per Model**: < $0.75 (all steps included)
- **Meshy API Efficiency**: < $0.50 per successful model
- **Storage Costs**: < $0.10 per product
- **Bandwidth**: < $0.05 per model download

### Business Metrics:
- **Success Rate**: > 95% of products process successfully
- **Retailer Coverage**: 95% of products from supported sites
- **Daily Volume**: 500+ products processed
- **Model Variety**: 1000+ unique models in database
- **User Satisfaction**: 4.5+ star rating for model quality

### Error Metrics:
- **Scraping Failure Rate**: < 5%
- **BG Removal Failure Rate**: < 10%
- **3D Generation Failure Rate**: < 5%
- **Batch Failure Rate**: < 2%
- **System Downtime**: < 1% monthly

## Testing Strategy

### Phase 1-2 Testing (GUI + Mock API):
- Test both pipeline modes completely
- Validate all UI states and transitions
- Ensure mock data covers edge cases
- Test WebSocket connections
- Validate responsive design

### Phase 3-5 Testing (Scraping + Processing):
```python
TEST_PRODUCTS = [
    "IKEA sofa with variants",
    "IKEA chair with assembly",
    "Target lamp with multiple angles",
    "Urban Outfitters unique decor",
    "Product with missing dimensions",
    "Product with lifestyle images",
    "Out of stock product",
    "Product with 20+ images",
    "Modular furniture set",
    "Glass/transparent product"
]
```

### Phase 6-8 Testing (3D Generation + Batch):
- Process 50 products in single batch
- Test batch failure recovery
- Validate cost tracking
- Monitor memory usage
- Test concurrent batches

### Phase 9-10 Testing (Scale + Production):
- Load test with 500+ products
- Test all 4 retailers simultaneously
- Benchmark processing speeds
- Validate CDN performance
- Test auto-scaling

### Edge Cases to Test:
- Products with 20+ images
- Products with no dimensions
- Discontinued/out of stock products
- Complex modular furniture
- Transparent/glass products
- Products with people in images
- Corrupted/invalid images
- Network interruptions
- API rate limit hitting

## Budget Considerations

### Development Costs (One-time):
- Meshy API testing: $50-100
- AWS setup: $100
- Domain/hosting: $50
- Development tools: $50

### Running Costs (Monthly):
- Meshy API: $0.50 × daily volume
- AWS S3: $50-100
- AWS RDS (PostgreSQL): $50-100
- AWS EC2 (workers): $100-200
- CloudFront CDN: $50-100
- Monitoring tools: $50

### Cost Optimization Strategies:
- Use "standard" quality for batch mode
- Cache aggressively (24hr for scraping)
- Skip products under $50
- Limit to top 3 variants per product
- Daily processing caps
- Reuse existing models when possible

## Quick Start Checklist

### Week 0 - Environment Setup:
- [ ] Install Node.js 18+, Python 3.9+
- [ ] Install Docker Desktop
- [ ] Create GitHub repository
- [ ] Set up project folders
- [ ] Install React and FastAPI
- [ ] Configure PostgreSQL in Docker
- [ ] Create .env files
- [ ] Test basic connectivity

### Week 1 - GUI Sprint:
- [ ] Create React app with routing
- [ ] Build mode selector
- [ ] Implement single pipeline UI
- [ ] Implement batch pipeline UI
- [ ] Add mock data for IKEA products
- [ ] Test complete user flows
- [ ] Document component structure

### Week 2 - API Sprint:
- [ ] Set up FastAPI project
- [ ] Create all endpoints
- [ ] Add mock responses
- [ ] Implement WebSocket
- [ ] Generate API docs
- [ ] Connect frontend to API
- [ ] Test all integrations

## Success Milestones

### MVP Success (Week 4):
- [ ] GUI fully functional with mock data
- [ ] Can scrape real IKEA products
- [ ] Data persisted to PostgreSQL
- [ ] Both modes working end-to-end

### Core Pipeline Success (Week 7):
- [ ] Background removal working
- [ ] 3D models generating via Meshy
- [ ] LODs created successfully
- [ ] < 10% failure rate
- [ ] 10+ products processed successfully

### Production Success (Week 12):
- [ ] Batch processing 50+ products
- [ ] 4 retailers supported
- [ ] < 5% failure rate
- [ ] < 5 minutes average processing time
- [ ] 500+ products in database
- [ ] Running in production environment

---

**This document serves as your complete implementation guide. Each phase builds on the previous one, with clear deliverables and success criteria. Start with Phase 0 (environment setup) and Phase 1 (GUI with mock data) to validate the concept before building the complex backend systems.**
