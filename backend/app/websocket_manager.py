"""
WebSocket connection manager for real-time updates
"""

import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}  # Track subscriptions by product/batch ID

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        # Remove from all subscriptions
        for key in list(self.subscriptions.keys()):
            if websocket in self.subscriptions[key]:
                self.subscriptions[key].remove(websocket)
                if not self.subscriptions[key]:  # Remove empty subscription
                    del self.subscriptions[key]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                dead_connections.append(connection)
        
        # Remove dead connections
        for connection in dead_connections:
            self.disconnect(connection)

    async def subscribe_to_product(self, websocket: WebSocket, product_id: str):
        """Subscribe to updates for a specific product"""
        if product_id not in self.subscriptions:
            self.subscriptions[product_id] = []
        if websocket not in self.subscriptions[product_id]:
            self.subscriptions[product_id].append(websocket)
        logger.info(f"WebSocket subscribed to product {product_id}")

    async def subscribe_to_batch(self, websocket: WebSocket, batch_id: str):
        """Subscribe to updates for a specific batch"""
        if batch_id not in self.subscriptions:
            self.subscriptions[batch_id] = []
        if websocket not in self.subscriptions[batch_id]:
            self.subscriptions[batch_id].append(websocket)
        logger.info(f"WebSocket subscribed to batch {batch_id}")

    async def send_product_update(self, product_id: str, update: Dict[str, Any]):
        """Send update to all subscribers of a specific product"""
        message = json.dumps({
            "type": "product_update",
            "product_id": product_id,
            "timestamp": datetime.now().isoformat(),
            **update
        })
        
        if product_id in self.subscriptions:
            dead_connections = []
            for websocket in self.subscriptions[product_id]:
                try:
                    await websocket.send_text(message)
                except:
                    dead_connections.append(websocket)
            
            # Remove dead connections
            for connection in dead_connections:
                self.disconnect(connection)

    async def send_batch_update(self, batch_id: str, update: Dict[str, Any]):
        """Send update to all subscribers of a specific batch"""
        message = json.dumps({
            "type": "batch_update",
            "batch_id": batch_id,
            "timestamp": datetime.now().isoformat(),
            **update
        })
        
        if batch_id in self.subscriptions:
            dead_connections = []
            for websocket in self.subscriptions[batch_id]:
                try:
                    await websocket.send_text(message)
                except:
                    dead_connections.append(websocket)
            
            # Remove dead connections
            for connection in dead_connections:
                self.disconnect(connection)

    async def send_error_update(self, product_id: str, error: str, retry_count: int = 0):
        """Send error update for a specific product"""
        message = json.dumps({
            "type": "error",
            "product_id": product_id,
            "error": error,
            "retry_count": retry_count,
            "timestamp": datetime.now().isoformat()
        })
        
        if product_id in self.subscriptions:
            dead_connections = []
            for websocket in self.subscriptions[product_id]:
                try:
                    await websocket.send_text(message)
                except:
                    dead_connections.append(websocket)
            
            # Remove dead connections
            for connection in dead_connections:
                self.disconnect(connection)

# Create singleton instance
manager = ConnectionManager()
