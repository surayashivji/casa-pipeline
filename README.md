# Room Decorator 3D Pipeline

A comprehensive pipeline for converting furniture products from retailer websites into optimized 3D models for iOS room decoration apps.

## Features

- **Two Processing Modes**: Single product (manual validation) and Batch (automatic processing)
- **Multi-Retailer Support**: IKEA, Target, West Elm, Urban Outfitters
- **iOS Optimization**: LOD system for smooth performance across all iPhone/iPad models
- **Scalable Architecture**: Local development → Cloud production

## Quick Start

1. **Start the database and Redis**:
   ```bash
   npm run dev:db
   ```

2. **Start the backend**:
   ```bash
   npm run dev:backend
   ```

3. **Start the frontend**:
   ```bash
   npm run dev:frontend
   ```

4. **Access the applications**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Database Admin: http://localhost:8080

## Development

- Frontend: React + Vite + Tailwind CSS
- Backend: FastAPI + PostgreSQL + Redis
- 3D Processing: Meshy API + RMBG background removal
- Deployment: Docker + AWS

## Project Structure

```
├── frontend/          # React application
├── backend/           # FastAPI application
├── docker/            # Docker configurations
└── docs/              # Documentation
```
