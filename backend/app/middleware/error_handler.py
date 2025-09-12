"""
Error handling middleware and custom exceptions
"""

import logging
import traceback
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class PipelineError(Exception):
    """Base exception for pipeline-related errors"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "PIPELINE_ERROR"
        self.details = details or {}
        super().__init__(self.message)

class ScrapingError(PipelineError):
    """Error during product scraping"""
    def __init__(self, message: str, url: str = None, details: dict = None):
        super().__init__(message, "SCRAPING_ERROR", details)
        self.url = url

class ImageProcessingError(PipelineError):
    """Error during image processing"""
    def __init__(self, message: str, product_id: str = None, details: dict = None):
        super().__init__(message, "IMAGE_PROCESSING_ERROR", details)
        self.product_id = product_id

class ModelGenerationError(PipelineError):
    """Error during 3D model generation"""
    def __init__(self, message: str, product_id: str = None, details: dict = None):
        super().__init__(message, "MODEL_GENERATION_ERROR", details)
        self.product_id = product_id

class DatabaseError(PipelineError):
    """Error during database operations"""
    def __init__(self, message: str, operation: str = None, details: dict = None):
        super().__init__(message, "DATABASE_ERROR", details)
        self.operation = operation

class ValidationError(PipelineError):
    """Error during data validation"""
    def __init__(self, message: str, field: str = None, details: dict = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field

class RateLimitError(PipelineError):
    """Error due to rate limiting"""
    def __init__(self, message: str, retry_after: int = None, details: dict = None):
        super().__init__(message, "RATE_LIMIT_ERROR", details)
        self.retry_after = retry_after

def create_error_response(
    error: Exception,
    status_code: int = 500,
    request_id: str = None,
    include_traceback: bool = False
) -> JSONResponse:
    """Create a standardized error response"""
    
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    error_data = {
        "error": {
            "id": request_id,
            "type": error.__class__.__name__,
            "message": str(error),
            "timestamp": datetime.now().isoformat(),
            "status_code": status_code
        }
    }
    
    # Add specific error details
    if isinstance(error, PipelineError):
        error_data["error"]["code"] = error.error_code
        error_data["error"]["details"] = error.details
        
        if hasattr(error, 'url'):
            error_data["error"]["url"] = error.url
        if hasattr(error, 'product_id'):
            error_data["error"]["product_id"] = error.product_id
        if hasattr(error, 'operation'):
            error_data["error"]["operation"] = error.operation
        if hasattr(error, 'field'):
            error_data["error"]["field"] = error.field
        if hasattr(error, 'retry_after'):
            error_data["error"]["retry_after"] = error.retry_after
    
    # Add traceback in development
    if include_traceback:
        error_data["error"]["traceback"] = traceback.format_exc()
    
    return JSONResponse(
        status_code=status_code,
        content=error_data
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    request_id = str(uuid.uuid4())
    
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return create_error_response(exc, exc.status_code, request_id)

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions"""
    request_id = str(uuid.uuid4())
    
    logger.warning(
        f"Validation Error: {exc.errors()}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors()
        }
    )
    
    error_data = {
        "error": {
            "id": request_id,
            "type": "ValidationError",
            "message": "Request validation failed",
            "timestamp": datetime.now().isoformat(),
            "status_code": 422,
            "code": "VALIDATION_ERROR",
            "details": {
                "validation_errors": exc.errors()
            }
        }
    }
    
    return JSONResponse(status_code=422, content=error_data)

async def pipeline_exception_handler(request: Request, exc: PipelineError) -> JSONResponse:
    """Handle pipeline-specific exceptions"""
    request_id = str(uuid.uuid4())
    
    logger.error(
        f"Pipeline Error: {exc.error_code} - {exc.message}",
        extra={
            "request_id": request_id,
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details
        }
    )
    
    # Determine status code based on error type
    status_code = 500
    if isinstance(exc, ValidationError):
        status_code = 400
    elif isinstance(exc, RateLimitError):
        status_code = 429
    elif isinstance(exc, DatabaseError):
        status_code = 503
    
    return create_error_response(exc, status_code, request_id)

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions"""
    request_id = str(uuid.uuid4())
    
    logger.error(
        f"Unhandled Exception: {str(exc)}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "exception_type": exc.__class__.__name__
        },
        exc_info=True
    )
    
    return create_error_response(exc, 500, request_id, include_traceback=True)

def setup_error_handlers(app):
    """Setup all error handlers for the FastAPI app"""
    
    # Add custom exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(PipelineError, pipeline_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers configured successfully")
