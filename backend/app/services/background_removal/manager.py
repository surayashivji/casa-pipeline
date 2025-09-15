"""
Background Removal Manager
Manages background removal operations and provider selection
"""

import asyncio
import aiohttp
import os
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO

from .providers.rembg_provider import RembgProvider
from .base_provider import BaseProvider

logger = logging.getLogger(__name__)

class BackgroundRemovalManager:
    """Manages background removal operations"""
    
    def __init__(self):
        self.providers: List[BaseProvider] = []
        self._initialize_providers()
        self._ensure_directories()
    
    def _initialize_providers(self):
        """Initialize available providers"""
        # Add REMBG provider
        rembg_provider = RembgProvider()
        if rembg_provider.is_available():
            self.providers.append(rembg_provider)
            logger.info(f"Initialized provider: {rembg_provider.provider_name}")
        else:
            logger.warning("REMBG provider not available")
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs("temp/processed", exist_ok=True)
        logger.info("Created temp/processed directory")
    
    async def process_image(
        self, 
        image_url: str, 
        product_id: str, 
        image_order: int
    ) -> Dict[str, Any]:
        """
        Process a single image for background removal
        
        Args:
            image_url: URL of the image to process
            product_id: ID of the product this image belongs to
            image_order: Order of this image in the product's image set
            
        Returns:
            Dict with processing results
        """
        logger.info(f"Processing image {image_order} for product {product_id}: {image_url}")
        
        try:
            # Download image
            image_data = await self._download_image(image_url)
            if not image_data:
                return {
                    "success": False,
                    "error": "Failed to download image",
                    "original_url": image_url,
                    "processed_url": None,
                    "quality_score": 0.0,
                    "provider": "none"
                }
            
            # Check if image is already transparent
            if await self._is_already_transparent(image_data):
                logger.info(f"Image {image_url} is already transparent, skipping processing")
                return await self._create_skip_result(image_url, product_id, image_order)
            
            # Process with first available provider
            provider = self._get_available_provider()
            if not provider:
                return {
                    "success": False,
                    "error": "No background removal providers available",
                    "original_url": image_url,
                    "processed_url": None,
                    "quality_score": 0.0,
                    "provider": "none"
                }
            
            # Remove background
            result = await provider.remove_background(image_data)
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": result.get("error", "Background removal failed"),
                    "original_url": image_url,
                    "processed_url": None,
                    "quality_score": 0.0,
                    "provider": provider.provider_name
                }
            
            # Save processed image
            processed_url, local_path = await self._save_processed_image(
                result["image_data"],
                product_id,
                image_order,
                result["format"]
            )
            
            return {
                "success": True,
                "original_url": image_url,
                "processed_url": processed_url,
                "local_path": local_path,
                "quality_score": result["quality_score"],
                "transparency_ratio": result.get("transparency_ratio", 0.0),
                "provider": provider.provider_name,
                "processing_time": result["processing_time"],
                "cost": result["cost"]
            }
            
        except Exception as e:
            logger.error(f"Error processing image {image_url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_url": image_url,
                "processed_url": None,
                "quality_score": 0.0,
                "provider": "none"
            }
    
    async def process_batch(
        self, 
        image_urls: List[str], 
        product_id: str,
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Process multiple images in batch with concurrency control
        
        Args:
            image_urls: List of image URLs to process
            product_id: ID of the product
            max_concurrent: Maximum concurrent processing tasks
            
        Returns:
            List of processing results
        """
        logger.info(f"Processing batch of {len(image_urls)} images for product {product_id}")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(url, index):
            async with semaphore:
                # Add small delay between batches to avoid overwhelming
                if index > 0:
                    await asyncio.sleep(0.5)
                return await self.process_image(url, product_id, index)
        
        # Process all images
        tasks = [
            process_with_semaphore(url, index) 
            for index, url in enumerate(image_urls)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Exception processing image {i}: {result}")
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "original_url": image_urls[i],
                    "processed_url": None,
                    "quality_score": 0.0,
                    "provider": "none"
                })
            else:
                processed_results.append(result)
        
        # Log batch summary
        successful = sum(1 for r in processed_results if r.get("success"))
        logger.info(f"Batch processing complete: {successful}/{len(image_urls)} successful")
        
        return processed_results
    
    async def _download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logger.error(f"Failed to download image: HTTP {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error downloading image {url}: {e}")
            return None
    
    async def _is_already_transparent(self, image_data: bytes) -> bool:
        """Check if image already has transparency"""
        try:
            image = Image.open(BytesIO(image_data))
            return image.mode in ('RGBA', 'LA') or 'transparency' in image.info
        except Exception as e:
            logger.warning(f"Error checking transparency: {e}")
            return False
    
    async def _create_skip_result(self, image_url: str, product_id: str, image_order: int) -> Dict[str, Any]:
        """Create result for skipped transparent image"""
        # Still save the original as "processed" for consistency
        filename = f"{product_id}_{image_order}_original.png"
        local_path = f"temp/processed/{filename}"
        processed_url = f"/static/processed/{filename}"
        
        # Save original image to processed directory
        try:
            with open(local_path, 'wb') as f:
                f.write(await self._download_image(image_url))
        except Exception as e:
            logger.warning(f"Failed to save original as processed: {e}")
        
        return {
            "success": True,
            "original_url": image_url,
            "processed_url": processed_url,
            "local_path": local_path,
            "quality_score": 1.0,  # Perfect score for already transparent
            "transparency_ratio": 1.0,
            "provider": "skip",
            "processing_time": 0.0,
            "cost": 0.0,
            "skipped": True
        }
    
    async def _save_processed_image(
        self, 
        image_data: bytes, 
        product_id: str, 
        image_order: int, 
        format_name: str
    ) -> tuple[str, str]:
        """Save processed image and return URL and local path"""
        # Generate filename
        extension = format_name.lower()
        filename = f"{product_id}_{image_order}_processed.{extension}"
        
        # Save locally
        local_path = f"temp/processed/{filename}"
        with open(local_path, 'wb') as f:
            f.write(image_data)
        
        # Return URL and path
        processed_url = f"/static/processed/{filename}"
        return processed_url, local_path
    
    def _get_available_provider(self) -> Optional[BaseProvider]:
        """Get first available provider"""
        for provider in self.providers:
            if provider.is_available():
                return provider
        return None
    
    def get_provider_info(self) -> List[Dict[str, Any]]:
        """Get information about all providers"""
        return [provider.get_provider_info() for provider in self.providers]
