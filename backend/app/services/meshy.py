"""
Meshy API Service
Simple integration with Meshy's Multi-Image to 3D API
"""

import os
import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MeshyService:
    def __init__(self, test_mode: bool = True):
        """
        Initialize Meshy service
        
        Args:
            test_mode: If True, uses Meshy's test API key (no charges)
        """
        self.test_mode = test_mode
        self.base_url = "https://api.meshy.ai"
        
        if test_mode:
            # Use Meshy's official test API key
            self.api_key = "msy_dummy_api_key_for_test_mode_12345678"
            logger.info("🧪 Meshy TEST MODE enabled - no charges will occur")
        else:
            # Use production API key from environment
            self.api_key = os.getenv('MESHY_API_KEY')
            if not self.api_key:
                raise ValueError("MESHY_API_KEY environment variable required for production mode")
            logger.info("💰 Meshy PRODUCTION MODE enabled - charges will apply")
    
    def create_3d_model(self, image_urls: List[str], object_name: str = "Product", settings: Optional[Dict] = None) -> str:
        """
        Create 3D model from multiple images
        
        Args:
            image_urls: List of 1-4 image URLs of the same object from different angles
            object_name: Name of the object (for logging)
            settings: Optional settings override
            
        Returns:
            Task ID for tracking the generation progress
        """
        # Validate image count
        if not 1 <= len(image_urls) <= 4:
            raise ValueError(f"Must provide 1-4 images, got {len(image_urls)}")
        
        # Default settings
        default_settings = {
            "ai_model": "meshy-5",
            "topology": "triangle",
            "target_polycount": 30000,
            "symmetry_mode": "auto",
            "should_remesh": True,
            "should_texture": True,
            "enable_pbr": True,
            "moderation": False
        }
        
        # Merge with provided settings
        if settings:
            default_settings.update(settings)
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "image_urls": image_urls,
            **default_settings
        }
        
        logger.info(f"Creating 3D model for '{object_name}' with {len(image_urls)} images")
        logger.debug(f"Payload: {payload}")
        
        try:
            response = requests.post(
                f"{self.base_url}/openapi/v1/multi-image-to-3d",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code not in [200, 202]:
                error_msg = f"Meshy API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            result = response.json()
            task_id = result.get("result")
            
            if not task_id:
                raise Exception("No task ID returned from Meshy API")
            
            logger.info(f"✅ 3D model task created: {task_id}")
            return task_id
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_task_status(self, task_id: str) -> Dict:
        """
        Get the status and results of a 3D model generation task
        
        Args:
            task_id: Task ID returned from create_3d_model
            
        Returns:
            Dictionary with task status, progress, and results
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/openapi/v1/multi-image-to-3d/{task_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = f"Status check failed {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Status check request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def wait_for_completion(self, task_id: str, max_attempts: int = 30, delay_seconds: int = 10) -> Dict:
        """
        Wait for 3D model generation to complete
        
        Args:
            task_id: Task ID to monitor
            max_attempts: Maximum number of status checks
            delay_seconds: Delay between checks
            
        Returns:
            Final task status with results
        """
        import time
        
        logger.info(f"Waiting for 3D model completion: {task_id}")
        
        for attempt in range(max_attempts):
            status = self.get_task_status(task_id)
            current_status = status.get("status", "UNKNOWN")
            progress = status.get("progress", 0)
            
            logger.info(f"Attempt {attempt + 1}/{max_attempts}: {current_status} ({progress}%)")
            
            if current_status in ["SUCCEEDED", "FAILED", "CANCELED"]:
                return status
            
            if attempt < max_attempts - 1:  # Don't sleep on last attempt
                time.sleep(delay_seconds)
        
        raise Exception(f"Task {task_id} did not complete within {max_attempts} attempts")
    
    def get_cost_info(self, num_images: int) -> Dict:
        """
        Get cost information for 3D model generation
        
        Args:
            num_images: Number of images being used
            
        Returns:
            Dictionary with cost breakdown
        """
        if self.test_mode:
            return {
                "base_cost": 0.0,
                "texture_cost": 0.0,
                "total_cost": 0.0,
                "currency": "USD",
                "test_mode": True
            }
        else:
            # Production costs (based on Meshy pricing)
            # Pro Plan: $20/month for 1,000 credits = $0.02 per credit
            # Base model: 5 credits, Texturing: 10 credits = 15 credits total
            base_cost = 0.10  # 5 credits × $0.02
            texture_cost = 0.20  # 10 credits × $0.02
            return {
                "base_cost": base_cost,
                "texture_cost": texture_cost,
                "total_cost": base_cost + texture_cost,
                "currency": "USD",
                "test_mode": False
            }
