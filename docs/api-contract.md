# API Contract Documentation

## Base URL
Development: `http://localhost:8000`

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
- `WS /ws/batch-updates` - Real-time batch updates

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

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error
