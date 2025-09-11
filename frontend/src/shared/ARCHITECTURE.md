# Architecture Overview

## Frontend Structure
```
src/
├── components/
│   ├── single/           # Single product pipeline (8 steps)
│   ├── batch/            # Batch processing pipeline (3 steps)
│   └── layout/           # Layout components
├── shared/
│   ├── components/       # Reusable UI components
│   └── utils/           # Shared processing logic
└── data/                # Mock data
```

## Key Components

### Single Product Pipeline
- **URLInput** - Product URL validation
- **ProductReview** - Scraped data verification
- **ImageSelector** - Multi-select interface
- **BackgroundRemoval** - AI processing simulation
- **ApprovalInterface** - Quality review
- **ModelGeneration** - 3D model creation
- **ModelViewer** - Interactive 3D viewer
- **SaveConfirmation** - Database save

### Batch Processing Pipeline
- **CategoryInput** - Category URL input
- **ProductGrid** - Product selection
- **BatchProcessingDashboard** - Real-time processing & results

### Shared Components
- **PipelineStageDisplay** - Shows individual stage data
- **ProductPipelineView** - Full product pipeline view

## Data Flow
```
GUI Component → Stage Processor → Database Helper → Backend API → Database
```

## Processing Logic
- **`processProduct()`** - Core function for single product processing
- **`processBatch()`** - Wrapper for batch processing
- **Stage Processors** - Individual processing functions (scraping, background removal, 3D generation, etc.)
- **Database Helpers** - Mock functions that will be replaced with real API calls in Phase 2