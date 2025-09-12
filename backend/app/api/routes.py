from fastapi import APIRouter, HTTPException
from app.schemas.product import URLDetectionRequest, URLDetectionResponse, URLType
from app.services.mock_data import mock_data
import re

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
