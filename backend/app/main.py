from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
import json
import asyncio
from typing import List, Dict, Any
from datetime import datetime

# Import API routes and WebSocket manager
from app.api import routes
from app.websocket_manager import manager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket manager is now imported from websocket_manager.py

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Room Decorator Pipeline API...")
    yield
    # Shutdown
    logger.info("Shutting down Room Decorator Pipeline API...")

# Create FastAPI app
app = FastAPI(
    title="Room Decorator Pipeline API",
    description="API for processing furniture products into 3D models for iOS room decoration apps",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router, prefix="/api", tags=["api"])

@app.get("/")
async def root():
    return {
        "message": "Room Decorator Pipeline API", 
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "connections": len(manager.active_connections)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                # Handle subscription requests
                if message.get("type") == "subscribe_product":
                    product_id = message.get("product_id")
                    if product_id:
                        await manager.subscribe_to_product(websocket, product_id)
                        await manager.send_personal_message(json.dumps({
                            "type": "subscription_confirmed",
                            "product_id": product_id,
                            "message": f"Subscribed to product {product_id}"
                        }), websocket)
                
                elif message.get("type") == "subscribe_batch":
                    batch_id = message.get("batch_id")
                    if batch_id:
                        await manager.subscribe_to_batch(websocket, batch_id)
                        await manager.send_personal_message(json.dumps({
                            "type": "subscription_confirmed",
                            "batch_id": batch_id,
                            "message": f"Subscribed to batch {batch_id}"
                        }), websocket)
                
                elif message.get("type") == "ping":
                    await manager.send_personal_message(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }), websocket)
                
                else:
                    # Echo back unknown messages
                    await manager.send_personal_message(json.dumps({
                        "type": "echo",
                        "message": f"Received: {data}",
                        "timestamp": datetime.now().isoformat()
                    }), websocket)
                    
            except json.JSONDecodeError:
                # Handle non-JSON messages
                await manager.send_personal_message(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                }), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
