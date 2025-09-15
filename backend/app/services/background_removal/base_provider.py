"""
Base Provider for Background Removal Services
Abstract base class that all background removal providers must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ProviderType(Enum):
    """Available background removal providers"""
    REMBG = "rembg"
    REMOVE_BG = "remove_bg"
    CLIPDROP = "clipdrop"
    PHOTOROOM = "photoroom"

class BaseProvider(ABC):
    """Abstract base class for background removal providers"""
    
    def __init__(self):
        self.provider_name: str = ""
        self.cost_per_image: float = 0.0
    
    @abstractmethod
    async def remove_background(self, image_data: bytes) -> Dict[str, Any]:
        """
        Remove background from image data
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dict containing:
                - success: bool
                - image_data: bytes (processed image)
                - format: str (image format)
                - cost: float (processing cost)
                - processing_time: float (seconds)
                - quality_score: float (0-1)
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this provider is available for use
        
        Returns:
            bool: True if provider can be used
        """
        pass
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            "name": self.provider_name,
            "cost_per_image": self.cost_per_image,
            "available": self.is_available()
        }
