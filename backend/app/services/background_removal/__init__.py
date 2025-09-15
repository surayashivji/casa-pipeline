"""
Background Removal Service for Casa Pipeline
Provides AI-powered background removal for product images
"""

from .manager import BackgroundRemovalManager
from .base_provider import BaseProvider
from .providers.rembg_provider import RembgProvider

__all__ = [
    'BackgroundRemovalManager',
    'BaseProvider', 
    'RembgProvider'
]
