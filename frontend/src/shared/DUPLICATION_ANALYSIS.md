# Code Duplication Analysis: Single Product vs Shared Processing

## Current Situation

### Single Product Mode Components:
1. **URLInput.jsx**
   - Has its own mock product generation
   - Uses `setTimeout(1500)` for delay

2. **BackgroundRemoval.jsx**
   - Uses `generateProcessedImage()` from mockProcessingStates.js
   - Uses `setTimeout(1500)` for delay

3. **ModelGeneration.jsx**
   - Uses `generateMock3DModel()` from mockProcessingStates.js
   - Has its own step progression logic

4. **SaveConfirmation.jsx**
   - Uses `setTimeout(2000)` for saving simulation

### Shared Processing (`processProduct()`):
- Has ALL logic in one place
- Uses `simulateDelay()` helper
- Generates all mock data inline
- Returns standardized result format

## DUPLICATION FOUND ❌

Yes, there IS duplication! The single product components are NOT using the shared `processProduct()` function. They have their own:
- Mock data generation logic
- Delay simulations
- Processing logic

## Issues with Current Duplication:

1. **Different Mock Data Sources**
   - Single: Uses `mockProcessingStates.js` functions
   - Batch: Uses inline generation in `processProduct()`

2. **Different Delay Times**
   - Single: Various hardcoded delays (1500ms, 2000ms)
   - Batch: Configurable delays in stages object

3. **Different Data Formats**
   - Single: Each component has its own format
   - Batch: Standardized format from `processProduct()`

## Recommended Refactoring:

### Option 1: Refactor Single Product to Use Shared Logic
```javascript
// In BackgroundRemoval.jsx
import { processProduct } from '../../../shared/utils/productProcessing';

useEffect(() => {
  const process = async () => {
    // Process just the background removal stage
    const result = await processProduct(data.product, {
      stages: ['backgroundRemoval'], // Only run this stage
      previousStages: data.previousStages // Pass previous results
    });
    setProcessedImages(result.stages.backgroundRemoval.data.processedImage);
  };
  process();
}, []);
```

### Option 2: Extract Shared Stage Functions
```javascript
// shared/utils/stageProcessors.js
export const processBackgroundRemoval = async (images) => {
  // Shared logic used by both modes
};

export const process3DGeneration = async (processedImage) => {
  // Shared logic used by both modes
};
```

### Option 3: Keep As-Is But Document
- Single product needs manual UI between stages
- Different UX requirements might justify separate implementations
- But should at least share mock data generation

## Impact on Phase 2:

⚠️ **This duplication means you'll need to update code in MULTIPLE places when implementing real APIs!**

Instead of updating just `processProduct()`, you'll need to update:
- URLInput.jsx (for real scraping)
- BackgroundRemoval.jsx (for real RMBG API)
- ModelGeneration.jsx (for real Meshy API)
- SaveConfirmation.jsx (for real S3/database)
- AND processProduct() for batch mode

This violates DRY principles and increases maintenance burden.
