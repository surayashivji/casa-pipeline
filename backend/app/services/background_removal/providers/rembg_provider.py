"""
REMBG Provider for Background Removal
Uses the REMBG library with u2net model for high-quality background removal
"""

import asyncio
import time
import logging
from typing import Dict, Any
from io import BytesIO
from PIL import Image
import numpy as np

from ..base_provider import BaseProvider

logger = logging.getLogger(__name__)

class RembgProvider(BaseProvider):
    """REMBG provider using u2net model for product background removal"""
    
    def __init__(self):
        super().__init__()
        self.provider_name = "rembg"
        self.cost_per_image = 0.00  # Free local processing
        self._model = None
        self._model_loaded = False
    
    def is_available(self) -> bool:
        """Check if REMBG is available"""
        try:
            import rembg
            return True
        except ImportError:
            logger.warning("REMBG not available - install with: pip install rembg")
            return False
    
    async def _load_model(self):
        """Load the REMBG model asynchronously"""
        if self._model_loaded:
            return
        
        try:
            import rembg
            # Use u2net model - best for products
            self._model = rembg.new_session('u2net')
            self._model_loaded = True
            logger.info("REMBG u2net model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load REMBG model: {e}")
            raise
    
    async def remove_background(self, image_data: bytes) -> Dict[str, Any]:
        """
        Remove background using REMBG u2net model
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dict with processing results
        """
        start_time = time.time()
        
        try:
            # Load model if not already loaded
            await self._load_model()
            
            if not self._model_loaded:
                return {
                    "success": False,
                    "error": "REMBG model not available",
                    "image_data": image_data,
                    "format": "original",
                    "cost": 0.0,
                    "processing_time": 0.0,
                    "quality_score": 0.0
                }
            
            # Process image in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._process_image_sync, 
                image_data
            )
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "image_data": result["image_data"],
                "format": result["format"],
                "cost": self.cost_per_image,
                "processing_time": processing_time,
                "quality_score": result["quality_score"],
                "transparency_ratio": result["transparency_ratio"]
            }
            
        except Exception as e:
            logger.error(f"REMBG processing failed: {e}")
            processing_time = time.time() - start_time
            
            return {
                "success": False,
                "error": str(e),
                "image_data": image_data,
                "format": "original",
                "cost": 0.0,
                "processing_time": processing_time,
                "quality_score": 0.0
            }
    
    def _process_image_sync(self, image_data: bytes) -> Dict[str, Any]:
        """Synchronous image processing (runs in thread pool)"""
        import rembg
        
        try:
            # Process with REMBG
            output_data = rembg.remove(image_data, session=self._model)
            
            # Load processed image to calculate quality metrics
            processed_img = Image.open(BytesIO(output_data))
            
            # Convert to RGBA if not already
            if processed_img.mode != 'RGBA':
                processed_img = processed_img.convert('RGBA')
            
            # Calculate quality metrics
            quality_score = self._calculate_quality_score(processed_img)
            transparency_ratio = self._calculate_transparency_ratio(processed_img)
            
            # Determine format
            format_name = "PNG"  # REMBG outputs PNG
            
            return {
                "image_data": output_data,
                "format": format_name,
                "quality_score": quality_score,
                "transparency_ratio": transparency_ratio
            }
            
        except Exception as e:
            logger.error(f"REMBG sync processing failed: {e}")
            raise
    
    def _calculate_quality_score(self, image: Image.Image) -> float:
        """
        Calculate quality score based on edge smoothness and transparency
        
        Args:
            image: PIL Image in RGBA mode
            
        Returns:
            float: Quality score between 0.0 and 1.0
        """
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Extract alpha channel
            alpha = img_array[:, :, 3]
            
            # Calculate edge smoothness (gradient magnitude)
            from scipy import ndimage
            grad_x = ndimage.sobel(alpha, axis=1)
            grad_y = ndimage.sobel(alpha, axis=0)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Smooth edges = lower gradient magnitude
            edge_smoothness = 1.0 - (np.mean(gradient_magnitude) / 255.0)
            edge_smoothness = max(0.0, min(1.0, edge_smoothness))
            
            # Calculate transparency ratio
            transparent_pixels = np.sum(alpha < 128)  # Semi-transparent or transparent
            total_pixels = alpha.size
            transparency_ratio = transparent_pixels / total_pixels if total_pixels > 0 else 0
            
            # Combine metrics (weighted average)
            # Edge smoothness is more important than transparency ratio
            quality_score = (edge_smoothness * 0.7) + (transparency_ratio * 0.3)
            
            return min(1.0, max(0.0, quality_score))
            
        except Exception as e:
            logger.warning(f"Quality score calculation failed: {e}")
            # Fallback: basic transparency check
            alpha = np.array(image)[:, :, 3]
            transparent_pixels = np.sum(alpha < 128)
            total_pixels = alpha.size
            return min(1.0, transparent_pixels / total_pixels if total_pixels > 0 else 0.0)
    
    def _calculate_transparency_ratio(self, image: Image.Image) -> float:
        """
        Calculate ratio of transparent/semi-transparent pixels
        
        Args:
            image: PIL Image in RGBA mode
            
        Returns:
            float: Ratio between 0.0 and 1.0
        """
        try:
            alpha = np.array(image)[:, :, 3]
            transparent_pixels = np.sum(alpha < 128)  # Semi-transparent or transparent
            total_pixels = alpha.size
            return transparent_pixels / total_pixels if total_pixels > 0 else 0.0
        except Exception as e:
            logger.warning(f"Transparency ratio calculation failed: {e}")
            return 0.0
