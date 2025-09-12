"""
Middleware package for error handling, logging, and monitoring
"""

from .error_handler import (
    PipelineError,
    ScrapingError,
    ImageProcessingError,
    ModelGenerationError,
    DatabaseError,
    ValidationError as PipelineValidationError,
    RateLimitError,
    setup_error_handlers
)

from .logging_config import setup_logging, RequestLogger

from .monitoring import metrics_collector, MetricsCollector

__all__ = [
    "PipelineError",
    "ScrapingError", 
    "ImageProcessingError",
    "ModelGenerationError",
    "DatabaseError",
    "PipelineValidationError",
    "RateLimitError",
    "setup_error_handlers",
    "setup_logging",
    "RequestLogger",
    "metrics_collector",
    "MetricsCollector"
]
