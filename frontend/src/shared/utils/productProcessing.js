// Shared product processing utilities used by both single and batch pipelines
import { 
  scrapeProduct,
  selectImages,
  removeBackgrounds,
  generate3DModel,
  optimizeModel,
  saveResults
} from './stageProcessors';

/**
 * Process a product through the pipeline stages
 * In Phase 1, this uses mock processors. In Phase 2, the stage processors will call real APIs
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
      const scrapedData = await scrapeProduct(product.url);
      result.stages.scraping = {
        status: 'complete',
        data: scrapedData
      };
      // Update product info with scraped data
      Object.assign(result, scrapedData);
    } else {
      result.stages.scraping = existingData.scraping;
      Object.assign(result, existingData.productData);
    }

    // Stage 2: Image Selection
    if (!existingData.selectedImages) {
      onProgress({ stage: 'imageSelection', progress: 25 });
      const selectedImages = await selectImages(
        result.images || product.images || [], 
        { autoSelect: autoApprove }
      );
      result.stages.imageSelection = {
        status: 'complete',
        data: {
          selectedImages,
          allImages: result.images || product.images || []
        }
      };
    } else {
      result.stages.imageSelection = existingData.imageSelection;
    }

    // Stage 3: Background Removal
    if (!existingData.processedImages) {
      onProgress({ stage: 'backgroundRemoval', progress: 45 });
      const processedImages = await removeBackgrounds(
        result.stages.imageSelection.data.selectedImages,
        (progress) => onProgress({ 
          stage: 'backgroundRemoval', 
          progress: 45 + (progress.percent * 0.2) // 45-65%
        })
      );
      result.stages.backgroundRemoval = {
        status: 'complete',
        data: {
          processedImages,
          processedImage: processedImages[0]?.processed, // Primary image
          maskImage: processedImages[0]?.mask
        }
      };
    } else {
      result.stages.backgroundRemoval = existingData.backgroundRemoval;
    }

    // Stage 4: 3D Model Generation
    if (!existingData.model3D) {
      onProgress({ stage: 'modelGeneration', progress: 70 });
      const model3D = await generate3DModel(
        result.stages.backgroundRemoval.data.processedImages,
        result,
        (progress) => onProgress({ 
          stage: 'modelGeneration', 
          progress: 70 + (progress.progress * 0.15) // 70-85%
        })
      );
      result.stages.modelGeneration = {
        status: 'complete',
        data: model3D
      };
    } else {
      result.stages.modelGeneration = existingData.modelGeneration;
    }

    // Stage 5: Optimization
    if (!existingData.optimizedModel) {
      onProgress({ stage: 'optimization', progress: 90 });
      const optimized = await optimizeModel(result.stages.modelGeneration.data);
      result.stages.optimization = {
        status: 'complete',
        data: optimized
      };
    } else {
      result.stages.optimization = existingData.optimization;
    }

    // Stage 6: Saving
    onProgress({ stage: 'saving', progress: 95 });
    const saveResult = await saveResults({
      ...result,
      model3D: result.stages.optimization.data
    });
    result.stages.saving = {
      status: 'complete',
      data: saveResult
    };

    result.status = 'success';
    result.endTime = Date.now();
    result.processingTime = ((result.endTime - result.startTime) / 1000).toFixed(1) + 's';
    result.cost = 0.50; // Mock cost

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