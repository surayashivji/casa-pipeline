# Room Decorator Pipeline - Shared Architecture

## Core Processing Architecture

Both **Single Product** and **Batch Processing** modes use the EXACT SAME core processing logic:

```
┌─────────────────────────────────────────────────────────────┐
│                    productProcessing.js                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  processProduct(product, options)                           │
│    ├── Stage 1: Scraping                                   │
│    ├── Stage 2: Image Selection                            │
│    ├── Stage 3: Background Removal                         │
│    ├── Stage 4: 3D Model Generation                        │
│    ├── Stage 5: Optimization                               │
│    └── Stage 6: Saving                                     │
│                                                             │
│  processBatch(products, options)                           │
│    └── Loop: calls processProduct() for each               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
                ┌─────────────┴─────────────┐
                │                           │
    ┌───────────▼────────┐      ┌──────────▼──────────┐
    │  SINGLE PRODUCT    │      │  BATCH PROCESSING   │
    ├────────────────────┤      ├─────────────────────┤
    │                    │      │                     │
    │ Manual Steps:      │      │ Automated:          │
    │ - URL Input       │      │ - Category Input    │
    │ - Review          │      │ - Select Products   │
    │ - Image Select    │      │ - Process All       │
    │ - BG Approval     │      │                     │
    │ - 3D Preview      │      │ Uses:               │
    │                    │      │ processBatch() →    │
    │ Uses:              │      │   processProduct()  │
    │ processProduct()   │      │   (autoApprove)     │
    │ (manual approval)  │      │                     │
    └────────────────────┘      └─────────────────────┘
```

## Key Architecture Points:

### 1. **Shared Core Function**
- `processProduct()` is the SINGLE source of truth for processing
- Contains all business logic for the 6-stage pipeline
- Returns standardized result format with stage data

### 2. **Mode Differences**
- **Single Product**: Manual approval at each stage
- **Batch Processing**: `autoApprove: true` flag skips manual steps

### 3. **Shared UI Components**
- `ProductPipelineView` - Displays processing results
- `PipelineStageDisplay` - Shows individual stage data
- Both modes use these for consistent visualization

### 4. **Implementation Ready**
When moving to Phase 2 (Backend API), you only need to update `processProduct()`:

```javascript
// Current (Phase 1 - Mock):
result.stages.scraping = {
  status: 'complete',
  data: { /* mock data */ }
};

// Future (Phase 2 - Real API):
const scrapingResult = await api.scrapeProduct(product.url);
result.stages.scraping = {
  status: 'complete',
  data: scrapingResult
};
```

### 5. **Batch Processing Flow**
```javascript
processBatch(products) {
  for each product:
    result = await processProduct(product, { autoApprove: true })
    onProductComplete(result)  // UI updates in real-time
}
```

## Benefits of This Architecture:

1. **DRY (Don't Repeat Yourself)**: Zero code duplication
2. **Consistency**: Both modes behave identically
3. **Maintainability**: Update logic in one place
4. **Testability**: Test core function, both modes work
5. **Scalability**: Easy to add new modes (e.g., priority processing)
6. **Real Backend Ready**: Just replace mock delays with API calls

## Current Usage:

### Single Product Mode:
- Currently not using `processProduct()` directly (uses individual step components)
- TODO: Could be refactored to use `processProduct()` with manual checkpoints

### Batch Processing Mode:
- `BatchProcessingDashboard` → `processBatch()` → `processProduct()` (multiple times)
- Real-time UI updates via callbacks
- Unified view of processing + results

This architecture ensures that when you implement the real backend in Phase 2, both modes will automatically get the real functionality with minimal code changes!
