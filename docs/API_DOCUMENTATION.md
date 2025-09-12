# 🏠 Room Decorator 3D Pipeline API Documentation

## Overview

The Room Decorator 3D Pipeline API is a comprehensive system for processing furniture and home goods products into 3D models for iOS room decoration applications. It provides a complete pipeline from URL detection to 3D model generation with real-time monitoring and WebSocket support.

## 🚀 Quick Start

### Base URLs
- **Development**: `http://localhost:8000`
- **Production**: `https://api.roomdecorator.com`

### Interactive Documentation
- **Swagger UI**: `/docs` - Interactive API explorer
- **ReDoc**: `/redoc` - Alternative documentation format

### Authentication
Currently no authentication required for development. Production will use JWT tokens.

## 📋 API Endpoints

### 🔍 URL Detection

#### `POST /api/detect-url`
Analyzes a product URL to determine retailer and content type.

**Request:**
```json
{
  "url": "https://www.ikea.com/us/en/p/stefan-chair-brown-black-00211088/"
}
```

**Response:**
```json
{
  "type": "product",
  "retailer": "ikea",
  "confidence": 0.95,
  "url": "https://www.ikea.com/us/en/p/stefan-chair-brown-black-00211088/"
}
```

**Supported Retailers:**
- IKEA
- Wayfair
- Amazon
- West Elm
- Pottery Barn

---

### 🏠 Single Product Pipeline

#### `POST /api/scrape`
**Step 1**: Extract product data from URL.

**Request:**
```json
{
  "url": "https://www.ikea.com/us/en/p/stefan-chair-brown-black-00211088/",
  "mode": "single"
}
```

**Response:**
```json
{
  "product": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "STEFAN Chair",
    "brand": "IKEA",
    "price": 99.99,
    "url": "https://www.ikea.com/us/en/p/stefan-chair-brown-black-00211088/",
    "images": [
      "https://www.ikea.com/us/en/images/products/stefan-chair-brown-black__0737165_pe740136_s5.jpg"
    ],
    "dimensions": {
      "width": 20.5,
      "height": 33.5,
      "depth": 20.5
    }
  },
  "status": "scraped"
}
```

#### `POST /api/select-images`
**Step 2**: Select best images for 3D generation.

**Request:**
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "selected_images": [
    "https://www.ikea.com/us/en/images/products/stefan-chair-brown-black__0737165_pe740136_s5.jpg"
  ]
}
```

#### `POST /api/remove-backgrounds`
**Step 3**: Process background removal on selected images.

**Request:**
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "image_urls": [
    "https://www.ikea.com/us/en/images/products/stefan-chair-brown-black__0737165_pe740136_s5.jpg"
  ]
}
```

#### `POST /api/approve-images`
**Step 4**: Approve processed images for 3D generation.

**Request:**
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "approved_images": [
    {
      "url": "https://processed-images.com/chair_no_bg.jpg",
      "quality_score": 0.92
    }
  ]
}
```

#### `POST /api/generate-3d`
**Step 5**: Generate 3D model from approved images.

**Request:**
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "approved_images": [
    "https://processed-images.com/chair_no_bg.jpg"
  ],
  "quality": "high"
}
```

**Response:**
```json
{
  "task_id": "task_12345",
  "status": "processing",
  "estimated_completion": "2024-01-15T10:35:00Z"
}
```

#### `GET /api/model-status/{task_id}`
**Step 6**: Check 3D model generation status.

**Response:**
```json
{
  "task_id": "task_12345",
  "status": "completed",
  "progress": 100,
  "model_url": "https://models.roomdecorator.com/chair_3d.glb",
  "quality": "high",
  "file_size_mb": 2.5
}
```

#### `POST /api/optimize-model`
**Step 7**: Optimize 3D model and generate LOD levels.

#### `POST /api/save-product`
**Step 8**: Save final product with 3D model.

---

### 📦 Batch Processing

#### `POST /api/scrape-category`
Scrape multiple products from a category or search.

**Request:**
```json
{
  "category_url": "https://www.ikea.com/us/en/cat/chairs-114/",
  "max_products": 10,
  "filters": {
    "price_min": 50,
    "price_max": 200
  }
}
```

#### `POST /api/batch-process`
Start batch processing for multiple products.

**Request:**
```json
{
  "product_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001"
  ],
  "settings": {
    "max_images_per_product": 4,
    "auto_approve_threshold": 0.85,
    "quality": "standard"
  }
}
```

**Response:**
```json
{
  "batch_id": "batch_67890",
  "status": "processing",
  "total_products": 2,
  "estimated_completion": "2024-01-15T11:00:00Z"
}
```

#### `GET /api/batch-status/{batch_id}`
Get batch processing status.

**Response:**
```json
{
  "batch_id": "batch_67890",
  "status": "processing",
  "progress": 65,
  "completed_products": 1,
  "total_products": 2,
  "failed_products": 0,
  "current_stage": "generate_3d",
  "estimated_completion": "2024-01-15T11:00:00Z"
}
```

#### `POST /api/batch-cancel/{batch_id}`
Cancel a running batch process.

#### `GET /api/batch-history`
Get batch processing history.

---

### 🔌 WebSocket Support

#### `WS /ws`
Real-time updates for product and batch processing.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

**Subscribe to Product Updates:**
```json
{
  "type": "subscribe_product",
  "product_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Subscribe to Batch Updates:**
```json
{
  "type": "subscribe_batch",
  "batch_id": "batch_67890"
}
```

**Ping/Pong:**
```json
{
  "type": "ping"
}
```

**WebSocket Message Types:**
- `product_update`: Product processing progress
- `batch_update`: Batch processing progress
- `subscription_confirmed`: Subscription confirmation
- `error`: Error notifications
- `pong`: Ping response

---

### 📊 Monitoring & Health

#### `GET /api/health`
Comprehensive system health check.

**Response:**
```json
{
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
```

#### `GET /api/metrics`
Real-time API metrics and performance data.

**Response:**
```json
{
  "total_requests": 1250,
  "successful_requests": 1180,
  "error_requests": 70,
  "error_rate": 0.056,
  "average_response_time_ms": 245.5,
  "requests_per_minute": 12.5,
  "endpoints": {
    "/api/scrape": {
      "requests": 150,
      "avg_response_time_ms": 320.5,
      "error_rate": 0.02
    }
  }
}
```

#### `GET /api/metrics/reset`
Reset metrics counters.

#### `GET /api/logs`
Get recent application logs.

---

## 🔄 Processing Pipeline Flow

```mermaid
graph TD
    A[URL Input] --> B[URL Detection]
    B --> C[Product Scraping]
    C --> D[Image Selection]
    D --> E[Background Removal]
    E --> F[Image Approval]
    F --> G[3D Generation]
    G --> H[Model Optimization]
    H --> I[Product Saving]
    
    J[Batch Processing] --> K[Multiple Products]
    K --> C
    
    L[WebSocket] --> M[Real-time Updates]
    M --> N[Progress Tracking]
```

## 📝 Error Handling

### Error Response Format
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Invalid request data
- `PRODUCT_NOT_FOUND`: Product not found
- `PROCESSING_ERROR`: Processing failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error
- `503` - Service Unavailable

## 🛠️ Development

### Running the API
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/roomdecorator

# Redis (for Celery)
REDIS_URL=redis://localhost:6379

# Meshy API
MESHY_API_KEY=your_meshy_api_key

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/pipeline.log
```

### Testing
```bash
# Run tests
pytest tests/

# Test specific endpoint
curl -X POST "http://localhost:8000/api/detect-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.ikea.com/us/en/p/stefan-chair-brown-black-00211088/"}'
```

## 📚 Additional Resources

- [API Contract](./api-contract.md) - Detailed API specifications
- [Frontend Integration Guide](../frontend/README.md) - Frontend integration examples
- [Database Schema](../backend/app/models/) - Database models and relationships
- [WebSocket Guide](./websocket-guide.md) - WebSocket implementation details

## 🤝 Support

For questions or issues:
- **Email**: support@roomdecorator.com
- **Documentation**: `/docs` endpoint
- **Health Check**: `/api/health` endpoint
