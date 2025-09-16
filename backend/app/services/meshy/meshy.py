"""
Minimal Meshy API integration
"""
import os
import requests
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MeshyService:
    def __init__(self):
        
        self.api_key = 'msy_dummy_api_key_for_test_mode_12345678'
        self.base_url = "https://api.meshy.ai"
        
        if not self.api_key:
            logger.warning("⚠️ No Meshy API key found - will return mock data")
        else:
            logger.info(f"✅ Meshy initialized with API key: {self.api_key[:10]}...")
    
    def create_task(self, image_urls: List[str]) -> Dict:
        """
        Create a 3D model generation task
        Returns: {"success": bool, "task_id": str, "error": str}
        """
        
        # No API key? Return mock
        if not self.api_key:
            import uuid
            mock_id = f"mock_{uuid.uuid4().hex[:8]}"
            logger.info(f"Returning mock task ID: {mock_id}")
            return {
                "success": True,
                "task_id": mock_id
            }
        
        # Make real API call
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Use first 4 images max (Meshy limit)
            payload = {
                "image_urls": image_urls[:4],
                "ai_model": "meshy-5",  # Use meshy-4 for now
                "topology": "quad",
                "target_polycount": 30000
            }
            
            logger.info(f"Calling Meshy API with {len(image_urls[:4])} images")
            
            response = requests.post(
                f"{self.base_url}/openapi/v1/multi-image-to-3d",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            logger.info(f"Meshy response status: {response.status_code}")
            logger.info(f"Meshy response body: {response.text[:500]}")
            
            if response.status_code in [200, 202]:  # <-- Changed this line
                data = response.json()
                task_id = data.get("result")
                logger.info(f"✅ Created Meshy task: {task_id}")
                return {
                    "success": True,
                    "task_id": task_id
                }
            else:
                error_msg = f"API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "task_id": None,
                    "error": error_msg
                }
                
        except Exception as e:
            logger.error(f"Exception calling Meshy: {e}")
            return {
                "success": False,
                "task_id": None,
                "error": str(e)
            }
    
    def get_status(self, task_id: str) -> Dict:
        """
        Check task status
        Returns the raw Meshy API response
        """
        
        # Mock task? Return mock status
        if task_id.startswith("mock_"):
            return {
                "status": "SUCCEEDED",
                "progress": 100,
                "model_urls": {
                    "glb": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Duck/glTF-Binary/Duck.glb"
                },
                "thumbnail_url": "https://via.placeholder.com/512x512.png?text=Mock+3D+Model"
            }
        
        # No API key? Can't check real status
        if not self.api_key:
            return {
                "status": "FAILED",
                "error": "No API key"
            }
        
        # Check real status
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(
                f"{self.base_url}/openapi/v1/multi-image-to-3d/{task_id}",
                headers=headers,
                timeout=30
            )
            
            logger.info(f"Status check response: {response.status_code}")
            logger.info(f"Response: {response.text}")  # Add this to see what Meshy returns

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Task {task_id}: {data.get('status')} - {data.get('progress')}%")
                return data
            else:
                logger.error(f"Status check failed: {response.text}")
                return {
                    "status": "FAILED",
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"Exception checking status: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }

# Global instance
meshy = MeshyService()