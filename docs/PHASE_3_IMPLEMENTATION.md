# Phase 3+ Implementation Guide

## Overview

Phase 3+ will implement real processing functionality while maintaining the existing architecture. The frontend is already set up to call the correct API functions.

## Implementation Steps

### 1. Background Removal Implementation

**Backend Changes:**
```python
# In app/api/routes.py - remove_backgrounds endpoint
async def remove_backgrounds(request: BackgroundRemovalRequest, db: Session = Depends(get_db)):
    # Replace mock response with real RMBG processing
    processed_images = []
    for image_url in request.image_urls:
        # Download image
        image_data = download_image(image_url)
        
        # Remove background using RMBG
        processed_image = remove_background(image_data)
        
        # Upload to cloud storage
        processed_url = upload_to_s3(processed_image)
        
        processed_images.append({
            "original_url": image_url,
            "processed_url": processed_url,
            "mask_url": generate_mask_url(processed_image)
        })
    
    return BackgroundRemovalResponse(
        product_id=request.product_id,
        processed_images=processed_images,
        total_processing_time=processing_time,
        total_cost=calculate_cost(processed_images),
        success_rate=1.0
    )
```

**Frontend Changes:**
- No changes needed! The frontend already calls `removeBackgrounds()` correctly.

### 2. 3D Model Generation Implementation

**Backend Changes:**
```python
# In app/api/routes.py - generate_3d_model endpoint
async def generate_3d_model(request: Generate3DRequest, db: Session = Depends(get_db)):
    # Replace mock response with real Meshy API call
    meshy_response = call_meshy_api(
        images=request.image_urls,
        settings=request.settings
    )
    
    # Store task in database
    task = create_processing_task(
        product_id=request.product_id,
        task_type="3d_generation",
        external_task_id=meshy_response.task_id,
        status="processing"
    )
    
    return Generate3DResponse(
        product_id=request.product_id,
        task_id=meshy_response.task_id,
        status="processing",
        estimated_completion=meshy_response.estimated_time,
        cost=meshy_response.cost
    )
```

**Frontend Changes:**
- No changes needed! The frontend already calls `generate3DModel()` correctly.

### 3. Model Optimization Implementation

**Backend Changes:**
```python
# In app/api/routes.py - optimize_model endpoint
async def optimize_model(request: Generate3DRequest, db: Session = Depends(get_db)):
    # Replace mock response with real optimization
    optimized_model = optimize_3d_model(
        model_url=request.model_url,
        settings=request.settings
    )
    
    return OptimizeModelResponse(
        product_id=request.product_id,
        optimized_model_url=optimized_model.url,
        lods=optimized_model.lods,
        cost=optimized_model.cost
    )
```

**Frontend Changes:**
- No changes needed! The frontend already calls `optimizeModel()` correctly.

## Removing Mock Responses

### In productProcessing.js

Replace mock responses with real API calls:

```javascript
// Before (Phase 2)
console.log('Using mock image selection for Phase 2');
const mockSelectedImages = (result.images || product.images || []).slice(0, 3);

// After (Phase 3+)
const selectedImages = await selectImages(result.id, result.images);
const selectedImageUrls = selectedImages.selected_images;
```

### In Individual Components

The single pipeline components already call real APIs, so no changes needed there.

## Database Schema Updates

Add tables for:
- Processing tasks
- External API responses
- Cost tracking
- Performance metrics

## Environment Variables

Add to `.env`:
```bash
MESHY_API_KEY=your_meshy_api_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=your_bucket_name
REDIS_URL=redis://localhost:6379
```

## Testing Strategy

1. **Unit Tests**: Test individual API functions
2. **Integration Tests**: Test full pipeline with real APIs
3. **End-to-End Tests**: Test frontend-backend integration
4. **Performance Tests**: Test with large datasets

## Rollout Plan

1. **Phase 3a**: Implement background removal
2. **Phase 3b**: Implement 3D model generation
3. **Phase 3c**: Implement model optimization
4. **Phase 3d**: Add monitoring and analytics
5. **Phase 4**: Production deployment

## Monitoring

Add monitoring for:
- API response times
- Processing success rates
- Cost tracking
- Error rates
- User satisfaction
