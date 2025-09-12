// Shared product processing utilities used by both single and batch pipelines
// Updated to use real API service instead of mock stageProcessors
import { scrapeProduct } from '../services/apiService';

/**
 * Helper function to extract product ID consistently
 */
const extractProductId = (response) => {
  return response?.product?.id || response?.id || null;
};

/**
 * Process a product through the pipeline stages
 * Phase 2: Uses mock responses for development. Phase 3+: Will use real API calls
 */
export const processProduct = async (product, options = {}) => {
  const { 
    autoApprove = false, // For batch processing
    onProgress = () => {}, // Progress callback
    existingData = {} // For single mode to pass data between steps
  } = options;

  const result = {
    id: product.id || `prod_${Math.random().toString(36).substr(2, 9)}`,
    name: product.name,
    url: product.url,
    originalData: product,
    stages: {},
    status: 'processing',
    startTime: Date.now()
  };

  try {
    // Stage 1: Scraping (skip if we already have product data)
    if (!existingData.productData) {
      onProgress({ stage: 'scraping', progress: 10 });
      const scrapedData = await scrapeProduct(product.url, 'batch');
      result.stages.scraping = {
        status: 'complete',
        data: scrapedData
      };
      // Update product info with scraped data and use the real product ID
      Object.assign(result, scrapedData);
      result.id = extractProductId(scrapedData); // Use the real UUID from backend
    } else {
      result.stages.scraping = existingData.scraping;
      Object.assign(result, existingData.productData);
      result.id = extractProductId(existingData.productData); // Use the real UUID
    }

    // Stage 2: Image Selection
    if (!existingData.selectedImages) {
      onProgress({ stage: 'imageSelection', progress: 25 });
      // Mock success for Phase 2 development - same as single pipeline
      console.log('Using mock image selection for Phase 2');
      const mockSelectedImages = (result.images || product.images || []).slice(0, 3);
      result.stages.imageSelection = {
        status: 'complete',
        data: {
          selectedImages: mockSelectedImages,
          allImages: result.images || product.images || []
        }
      };
    } else {
      result.stages.imageSelection = existingData.imageSelection;
    }

    // Stage 3: Background Removal
    if (!existingData.processedImages) {
      onProgress({ stage: 'backgroundRemoval', progress: 45 });
      // Mock success for Phase 2 development - same as single pipeline
      console.log('Using mock background removal for Phase 2');
      const mockProcessedImages = result.stages.imageSelection.data.selectedImages.map((img, index) => ({
        original: img,
        processed: img,
        processed_url: img,
        mask_url: `https://example.com/mask-${index}.png`
      }));
      result.stages.backgroundRemoval = {
        status: 'complete',
        data: {
          processedImages: mockProcessedImages,
          processedImage: mockProcessedImages[0]?.processed,
          maskImage: mockProcessedImages[0]?.mask_url
        }
      };
    } else {
      result.stages.backgroundRemoval = existingData.backgroundRemoval;
    }

    // Stage 4: 3D Model Generation
    if (!existingData.model3D) {
      onProgress({ stage: 'modelGeneration', progress: 70 });
      // Mock success for Phase 2 development - same as single pipeline
      console.log('Using mock 3D generation for Phase 2');
      result.stages.modelGeneration = {
        status: 'complete',
        data: {
          taskId: `mock_${Date.now()}`,
          modelUrl: `https://example.com/models/mock-${result.id}.glb`,
          cost: 0.25
        }
      };
    } else {
      result.stages.modelGeneration = existingData.modelGeneration;
    }

    // Stage 5: Optimization
    if (!existingData.optimizedModel) {
      onProgress({ stage: 'optimization', progress: 90 });
      // Mock success for Phase 2 development - same as single pipeline
      console.log('Using mock optimization for Phase 2');
      result.stages.optimization = {
        status: 'complete',
        data: {
          optimizedModelUrl: result.stages.modelGeneration.data.modelUrl,
          lods: [],
          cost: 0.15
        }
      };
    } else {
      result.stages.optimization = existingData.optimization;
    }

    // Stage 6: Saving
    onProgress({ stage: 'saving', progress: 95 });
    // Mock success for Phase 2 development - same as single pipeline
    console.log('Using mock save for Phase 2');
    
    // Add a small delay to simulate real saving
    await new Promise(resolve => setTimeout(resolve, 500));
    
    result.stages.saving = {
      status: 'complete',
      data: { id: result.id, status: 'saved' }
    };

    result.status = 'success';
    result.endTime = Date.now();
    result.processingTime = ((result.endTime - result.startTime) / 1000).toFixed(1) + 's';
    result.cost = 0.50; // Mock cost
    
    // Final progress update to ensure UI knows processing is complete
    onProgress({ stage: 'saving', progress: 100 });

  } catch (error) {
    result.status = 'failed';
    result.error = error.message;
    result.endTime = Date.now();
    result.processingTime = ((result.endTime - result.startTime) / 1000).toFixed(1) + 's';
    result.cost = 0;
    
    // Mark which stage failed
    const failedStage = error.message.includes('image quality') ? 'modelGeneration' : 
                       error.message.includes('background') ? 'backgroundRemoval' : 
                       'scraping';
    
    if (!result.stages[failedStage]) {
      result.stages[failedStage] = {};
    }
    result.stages[failedStage].status = 'failed';
    result.stages[failedStage].error = error.message;
  }

  onProgress({ stage: 'complete', progress: 100 });
  return result;
};

/**
 * Process multiple products in batch
 */
export const processBatch = async (products, options = {}) => {
  const {
    parallel = false, // In Phase 1, we'll process sequentially
    onProgress = () => {},
    onProductComplete = () => {}
  } = options;

  const results = [];
  
  for (let i = 0; i < products.length; i++) {
    const product = products[i];
    onProgress({ 
      batchProgress: (i / products.length) * 100,
      currentProduct: product.name,
      currentIndex: i,
      total: products.length
    });

    const result = await processProduct(product, {
      autoApprove: true,
      onProgress: (productProgress) => {
        onProgress({
          ...productProgress,
          batchProgress: ((i + (productProgress.progress / 100)) / products.length) * 100,
          currentProduct: product.name,
          currentIndex: i,
          total: products.length
        });
      }
    });

    results.push(result);
    onProductComplete(result);
  }

  return results;
};