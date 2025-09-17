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

# Import middleware
from app.middleware import (
    setup_logging, 
    setup_error_handlers, 
    RequestLogger,
    metrics_collector
)

# Load environment variables
load_dotenv()

# Configure logging
logger = setup_logging(log_level="INFO")

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
    description="""
    ## 🏠 Room Decorator 3D Pipeline API
    
    A comprehensive API for processing furniture and home goods products into 3D models for iOS room decoration applications.
    
    ### 🚀 Features
    - **Product Scraping**: Extract product data from major retailers (IKEA, Wayfair, etc.)
    - **Image Processing**: AI-powered background removal and image optimization
    - **3D Model Generation**: Convert 2D images to high-quality 3D models using Meshy API
    - **Batch Processing**: Handle multiple products simultaneously with real-time progress tracking
    - **Real-time Updates**: WebSocket support for live progress monitoring
    - **Comprehensive Monitoring**: Health checks, metrics, and detailed logging
    
    ### 🔄 Processing Pipeline
    1. **URL Detection** → Identify retailer and product type
    2. **Product Scraping** → Extract product data and images
    3. **Image Selection** → Choose best images for 3D generation
    4. **Background Removal** → AI-powered image processing
    5. **Image Approval** → Manual review and approval interface
    6. **3D Generation** → Create 3D models from approved images
    7. **Model Optimization** → Generate multiple LOD levels
    8. **Product Saving** → Store final 3D models and metadata
    
    ### 📊 Monitoring & Health
    - Real-time API metrics and performance monitoring
    - Comprehensive error handling and logging
    - Health check endpoints for system status
    - WebSocket connections for live updates
    
    ### 🔧 Development
    - **Base URL**: `http://localhost:8000`
    - **API Documentation**: `/docs` (Swagger UI)
    - **Alternative Docs**: `/redoc` (ReDoc)
    - **WebSocket**: `/ws` for real-time updates
    """,
    version="1.0.0",
    contact={
        "name": "Room Decorator Team",
        "email": "support@roomdecorator.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.roomdecorator.com",
            "description": "Production server"
        }
    ]
)

# Setup error handlers
setup_error_handlers(app)

# Add request logging middleware
app.add_middleware(RequestLogger)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # existing web frontend
        "http://localhost:3000",      # existing
        "http://localhost:8081",      # Expo dev server
        "http://localhost:19000",     # Expo web
        "http://localhost:19001",     # Expo dev tools
        "exp://localhost:8081",       # Expo iOS Simulator
        "https://bec7bf4bc28d.ngrok-free.app",  # ngrok tunnel
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router, prefix="/api", tags=["api"])

# Add static file serving for processed images
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="temp"), name="static")

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
