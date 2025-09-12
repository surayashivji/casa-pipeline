"""
Logging configuration for the pipeline API
"""

import logging
import logging.config
import sys
from pathlib import Path
from datetime import datetime
import json
from fastapi import Request

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup comprehensive logging configuration"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Default log file
    if log_file is None:
        log_file = log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": str(log_file),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": str(log_dir / "errors.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False
            },
            "app": {  # App-specific logger
                "handlers": ["console", "file", "error_file"],
                "level": "DEBUG",
                "propagate": False
            },
            "app.api": {  # API logger
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
            "app.websocket_manager": {  # WebSocket logger
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
            "app.services": {  # Services logger
                "handlers": ["console", "file"],
                "level": "DEBUG",
                "propagate": False
            },
            "uvicorn": {  # Uvicorn logger
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.error": {  # Uvicorn error logger
                "handlers": ["console", "file", "error_file"],
                "level": "ERROR",
                "propagate": False
            }
        }
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Get logger
    logger = logging.getLogger("app")
    logger.info(f"Logging configured - Level: {log_level}, File: {log_file}")
    
    return logger

class RequestLogger:
    """Middleware for logging HTTP requests"""
    
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger("app.api")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        request_id = str(uuid.uuid4())
        
        # Log request start
        start_time = datetime.now()
        self.logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "start_time": start_time.isoformat()
            }
        )
        
        # Process request
        response_sent = False
        
        async def send_wrapper(message):
            nonlocal response_sent
            if not response_sent:
                response_sent = True
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Log request completion
                self.logger.info(
                    f"Request completed: {request.method} {request.url.path}",
                    extra={
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "duration_seconds": duration,
                        "end_time": end_time.isoformat(),
                        "status_code": message.get("status", "unknown")
                    }
                )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

# Import uuid for RequestLogger
import uuid
