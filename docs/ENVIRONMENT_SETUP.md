# Environment Setup Guide

## Required Environment Variables

Create a `.env` file in the backend directory with the following variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/room_decorator

# Frontend Configuration
FRONTEND_URL=http://localhost:5173

# Backend Configuration
BACKEND_URL=http://localhost:8000

# Development Settings
DEBUG=true
LOG_LEVEL=INFO

# API Keys (for Phase 3+)
# MESHY_API_KEY=your_meshy_api_key_here
# AWS_ACCESS_KEY_ID=your_aws_access_key_here
# AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
# AWS_S3_BUCKET=your_s3_bucket_name_here

# Redis Configuration (for Phase 3+)
REDIS_URL=redis://localhost:6379

# WebSocket Configuration
WEBSOCKET_PORT=8001
```

## Setup Instructions

1. **Copy the environment file:**
   ```bash
   cp docs/ENVIRONMENT_SETUP.md backend/.env
   # Edit the .env file with your actual values
   ```

2. **Start the database:**
   ```bash
   cd docker
   docker-compose up -d postgres redis
   ```

3. **Start the backend:**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

4. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

## Phase 3+ Requirements

When implementing real processing, you'll need:
- Meshy API key for 3D model generation
- AWS credentials for cloud storage
- Redis for task queues
- Proper database migrations
