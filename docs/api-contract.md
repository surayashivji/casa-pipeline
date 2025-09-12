# API Contract Documentation

## Overview
This document provides the complete API contract for the Room Decorator 3D Pipeline API. For interactive documentation, visit `/docs` (Swagger UI) or `/redoc`.

## Base URLs
- **Development**: `http://localhost:8000`
- **Production**: `https://api.roomdecorator.com`

## Authentication
Currently no authentication required for development. Production will use JWT tokens.

## Rate Limiting
- **Default**: 100 requests per minute per IP
- **Burst**: 200 requests per minute for short periods
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Endpoints

### URL Detection
- `POST /api/detect-url`
- Determines URL type and retailer

### Single Product Pipeline
- `POST /api/scrape` - Scrape single product
- `POST /api/select-images` - Select images for processing
- `POST /api/remove-backgrounds` - Process background removal
- `POST /api/approve-images` - Approve processed images
- `POST /api/generate-3d` - Generate 3D model
- `GET /api/model-status/{task_id}` - Check model generation status

### Batch Processing
- `POST /api/scrape-category` - Scrape category/search results
- `POST /api/batch-process` - Start batch processing
- `GET /api/batch-status/{batch_id}` - Get batch status

### WebSocket
- `WS /ws` - Real-time updates for products and batches

### Monitoring & Health
- `GET /api/health` - System health check with detailed status
- `GET /api/metrics` - Real-time API metrics and performance
- `GET /api/metrics/reset` - Reset metrics counters
- `GET /api/logs` - Get recent application logs

## Request/Response Examples

### URL Detection
```json
POST /api/detect-url
{
  "url": "https://www.ikea.com/us/en/p/stefan-chair-brown-black-00211088/"
}

Response:
{
  "type": "product",
  "retailer": "ikea",
  "confidence": 0.95
}
```

### Single Product Scraping
```json
POST /api/scrape
{
  "url": "https://www.ikea.com/us/en/p/stefan-chair-brown-black-00211088/",
  "mode": "single"
}

Response:
{
  "product": {
    "id": "uuid",
    "name": "STEFAN Chair",
    "brand": "IKEA",
    "price": 99.99,
    "images": ["url1", "url2", "url3"],
    "dimensions": {
      "width": 20.5,
      "height": 33.5,
      "depth": 20.5
    }
  },
  "status": "scraped"
}
```

### Batch Processing
```json
POST /api/batch-process
{
  "product_ids": ["uuid1", "uuid2", "uuid3"],
  "settings": {
    "max_images_per_product": 4,
    "auto_approve_threshold": 0.85,
    "quality": "standard"
  }
}

Response:
{
  "batch_id": "uuid",
  "status": "processing",
  "total_products": 3,
  "estimated_completion": "2024-01-15T10:30:00Z"
}
```

### Health Check
```json
GET /api/health

Response:
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

### Metrics
```json
GET /api/metrics

Response:
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

### WebSocket Messages
```json
// Subscribe to product updates
{
  "type": "subscribe_product",
  "product_id": "550e8400-e29b-41d4-a716-446655440000"
}

// Subscribe to batch updates
{
  "type": "subscribe_batch",
  "batch_id": "batch_67890"
}

// Ping/Pong
{
  "type": "ping"
}

// Product update message
{
  "type": "product_update",
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "stage": "generate_3d",
  "progress": 75,
  "message": "Generating 3D model..."
}
```

## Error Responses

All endpoints return consistent error responses:

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

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error
