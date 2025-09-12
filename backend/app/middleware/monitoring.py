"""
Monitoring and metrics collection for the pipeline API
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import asyncio
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class Metrics:
    """Metrics collection for the pipeline API"""
    
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    request_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    # Pipeline metrics
    products_processed: int = 0
    products_successful: int = 0
    products_failed: int = 0
    batches_processed: int = 0
    batches_successful: int = 0
    batches_failed: int = 0
    
    # Processing stage metrics
    scraping_requests: int = 0
    image_selection_requests: int = 0
    background_removal_requests: int = 0
    image_approval_requests: int = 0
    model_generation_requests: int = 0
    model_optimization_requests: int = 0
    product_save_requests: int = 0
    
    # Error metrics
    error_counts: Dict[str, int] = field(default_factory=dict)
    
    # WebSocket metrics
    websocket_connections: int = 0
    websocket_messages_sent: int = 0
    websocket_subscriptions: int = 0
    
    # Cost tracking
    total_cost: float = 0.0
    cost_by_stage: Dict[str, float] = field(default_factory=dict)
    
    # Performance metrics
    average_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    
    def update_response_time(self, response_time: float):
        """Update response time metrics"""
        self.request_times.append(response_time)
        self.average_response_time = sum(self.request_times) / len(self.request_times)
        
        if len(self.request_times) >= 10:
            sorted_times = sorted(self.request_times)
            self.p95_response_time = sorted_times[int(len(sorted_times) * 0.95)]
            self.p99_response_time = sorted_times[int(len(sorted_times) * 0.99)]
    
    def record_error(self, error_type: str):
        """Record an error occurrence"""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    def record_cost(self, stage: str, cost: float):
        """Record cost for a processing stage"""
        self.total_cost += cost
        self.cost_by_stage[stage] = self.cost_by_stage.get(stage, 0.0) + cost
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        success_rate = (self.successful_requests / max(self.total_requests, 1)) * 100
        error_rate = (self.failed_requests / max(self.total_requests, 1)) * 100
        
        return {
            "status": "healthy" if error_rate < 10 else "degraded" if error_rate < 25 else "unhealthy",
            "success_rate": round(success_rate, 2),
            "error_rate": round(error_rate, 2),
            "total_requests": self.total_requests,
            "average_response_time": round(self.average_response_time, 3),
            "p95_response_time": round(self.p95_response_time, 3),
            "p99_response_time": round(self.p99_response_time, 3),
            "total_cost": round(self.total_cost, 2),
            "websocket_connections": self.websocket_connections,
            "error_counts": dict(self.error_counts)
        }

class MetricsCollector:
    """Singleton metrics collector"""
    
    _instance = None
    _metrics = Metrics()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def metrics(self) -> Metrics:
        return self._metrics
    
    def record_request(self, method: str, path: str, status_code: int, response_time: float):
        """Record a request"""
        self._metrics.total_requests += 1
        
        if 200 <= status_code < 400:
            self._metrics.successful_requests += 1
        else:
            self._metrics.failed_requests += 1
            self.record_error(f"HTTP_{status_code}")
        
        self._metrics.update_response_time(response_time)
        
        logger.info(
            f"Request recorded: {method} {path} - {status_code} ({response_time:.3f}s)",
            extra={
                "method": method,
                "path": path,
                "status_code": status_code,
                "response_time": response_time
            }
        )
    
    def record_pipeline_stage(self, stage: str, success: bool, cost: float = 0.0):
        """Record a pipeline stage execution"""
        stage_attr = f"{stage}_requests"
        if hasattr(self._metrics, stage_attr):
            setattr(self._metrics, stage_attr, getattr(self._metrics, stage_attr) + 1)
        
        if success:
            self._metrics.products_successful += 1
        else:
            self._metrics.products_failed += 1
            self.record_error(f"PIPELINE_{stage.upper()}")
        
        if cost > 0:
            self._metrics.record_cost(stage, cost)
    
    def record_batch_processing(self, success: bool, product_count: int):
        """Record batch processing"""
        self._metrics.batches_processed += 1
        self._metrics.products_processed += product_count
        
        if success:
            self._metrics.batches_successful += 1
            self._metrics.products_successful += product_count
        else:
            self._metrics.batches_failed += 1
            self._metrics.products_failed += product_count
            self.record_error("BATCH_PROCESSING")
    
    def record_websocket_event(self, event_type: str, count: int = 1):
        """Record WebSocket events"""
        if event_type == "connection":
            self._metrics.websocket_connections += count
        elif event_type == "message":
            self._metrics.websocket_messages_sent += count
        elif event_type == "subscription":
            self._metrics.websocket_subscriptions += count
    
    def record_error(self, error_type: str):
        """Record an error"""
        self._metrics.record_error(error_type)
        logger.warning(f"Error recorded: {error_type}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics"""
        return {
            "requests": {
                "total": self._metrics.total_requests,
                "successful": self._metrics.successful_requests,
                "failed": self._metrics.failed_requests,
                "success_rate": round((self._metrics.successful_requests / max(self._metrics.total_requests, 1)) * 100, 2)
            },
            "performance": {
                "average_response_time": round(self._metrics.average_response_time, 3),
                "p95_response_time": round(self._metrics.p95_response_time, 3),
                "p99_response_time": round(self._metrics.p99_response_time, 3)
            },
            "pipeline": {
                "products_processed": self._metrics.products_processed,
                "products_successful": self._metrics.products_successful,
                "products_failed": self._metrics.products_failed,
                "batches_processed": self._metrics.batches_processed,
                "batches_successful": self._metrics.batches_successful,
                "batches_failed": self._metrics.batches_failed
            },
            "stages": {
                "scraping": self._metrics.scraping_requests,
                "image_selection": self._metrics.image_selection_requests,
                "background_removal": self._metrics.background_removal_requests,
                "image_approval": self._metrics.image_approval_requests,
                "model_generation": self._metrics.model_generation_requests,
                "model_optimization": self._metrics.model_optimization_requests,
                "product_save": self._metrics.product_save_requests
            },
            "websocket": {
                "connections": self._metrics.websocket_connections,
                "messages_sent": self._metrics.websocket_messages_sent,
                "subscriptions": self._metrics.websocket_subscriptions
            },
            "costs": {
                "total": round(self._metrics.total_cost, 2),
                "by_stage": {k: round(v, 2) for k, v in self._metrics.cost_by_stage.items()}
            },
            "errors": dict(self._metrics.error_counts),
            "health": self._metrics.get_health_status()
        }

# Global metrics collector instance
metrics_collector = MetricsCollector()
