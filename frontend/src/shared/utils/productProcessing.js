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
                       'databaseSave';
    
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
 * Process remaining stages for a single product (simplified)
 */
const processRemainingStages = async (product, onProgress, onProductComplete) => {
  const result = {
    id: product.id,
    name: product.name,
    overallStatus: 'processing',
    stages: {
      databaseSave: {
        status: 'complete',
        data: {
          productId: product.id,
          savedAt: new Date().toISOString(),
          status: 'saved',
          databaseId: product.id
        }
      }
    },
    startTime: Date.now()
  };

  try {
    // Background removal is already handled in batch processing, skip it here
    console.log('Skipping background removal for:', product.name, '(already processed in batch)');

    // Stage 1: 3D Model Generation
    console.log('Generating 3D model for:', product.name);
    await new Promise(resolve => setTimeout(resolve, 3000)); // 3 second delay
    
    result.stages.modelGeneration = {
      status: 'complete',
      data: {
        modelUrl: `https://example.com/model-${product.id}.glb`,
        modelFormat: 'glb',
        vertices: 12543,
        faces: 8421,
        textures: 3
      }
    };
    
    onProductComplete(result); // Update UI immediately

    // Stage 2: Optimization
    console.log('Optimizing model for:', product.name);
    await new Promise(resolve => setTimeout(resolve, 2000)); // 2 second delay
    
    result.stages.optimization = {
      status: 'complete',
      data: {
        optimizedModelUrl: `https://example.com/optimized-${product.id}.glb`,
        originalSize: '2.3MB',
        optimizedSize: '1.1MB',
        compressionRatio: '52%'
      }
    };

    result.overallStatus = 'completed';
    result.endTime = Date.now();
    onProductComplete(result); // Final update
    return result;
    
  } catch (error) {
    console.error(`Processing failed for ${product.name}:`, error);
    result.overallStatus = 'failed';
    result.error = error.message;
    result.endTime = Date.now();
    onProductComplete(result); // Update UI even on failure
    return result;
  }
};

/**
 * Process multiple products in batch
 */
export const processBatch = async (products, options = {}) => {
  const {
    onProgress = () => {},
    onProductComplete = () => {}
  } = options;

  try {
    // Step 1: Batch save all products to database (all at once)
    console.log('Starting batch save of all products to database...');
    onProgress({ 
      batchProgress: 5,
      currentProduct: 'Saving all products to database...',
      currentIndex: -1,
      total: products.length
    });
    
    const saveResponse = await fetch('/api/batch/save-products', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        products: products
      })
    });
    
    if (!saveResponse.ok) {
      throw new Error(`Failed to save products: ${saveResponse.statusText}`);
    }
    
    const saveResult = await saveResponse.json();
    console.log(`Successfully saved ${saveResult.total_saved} products to database`);
    
    // Step 2: Create product ID mapping
    const savedProductsMap = {};
    saveResult.products.forEach(savedProduct => {
      const originalProduct = products.find(p => p.name === savedProduct.name);
      if (originalProduct) {
        savedProductsMap[originalProduct.name] = savedProduct.id;
      }
    });
    
    // Step 3: Immediately update UI for ALL products with database save complete
    console.log('Updating UI for batch save completion...');
    for (let i = 0; i < products.length; i++) {
      const product = products[i];
      const updatedProduct = {
        ...product,
        id: savedProductsMap[product.name] || product.id
      };
      
      const result = {
        id: updatedProduct.id,
        name: updatedProduct.name,
        overallStatus: 'processing',
        stages: {
          databaseSave: {
            status: 'complete',
            data: {
              productId: updatedProduct.id,
              savedAt: new Date().toISOString(),
              status: 'saved',
              databaseId: updatedProduct.id
            }
          }
        },
        startTime: Date.now()
      };
      
      // Immediately update UI for this product
      onProductComplete(result);
    }
    
    // Step 4: Batch Background Removal (all products at once)
    console.log('Starting batch background removal...');
    onProgress({ 
      batchProgress: 20,
      currentProduct: 'Processing background removal for all products...',
      currentIndex: -1,
      total: products.length
    });
    
    try {
      const bgRemovalResponse = await fetch('/api/batch/background-removal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          products: products.map(product => ({
            ...product,
            id: savedProductsMap[product.name] || product.id
          }))
        })
      });
      
      if (!bgRemovalResponse.ok) {
        throw new Error(`Failed to process background removal: ${bgRemovalResponse.statusText}`);
      }
      
      const bgRemovalResult = await bgRemovalResponse.json();
      console.log(`Successfully processed background removal: ${bgRemovalResult.successful_images}/${bgRemovalResult.total_images} images`);
      
      // Update UI for all products with background removal complete
      for (let i = 0; i < products.length; i++) {
        const product = products[i];
        const updatedProduct = {
          ...product,
          id: savedProductsMap[product.name] || product.id
        };
        
        // Find the corresponding result from the API response
        const productResult = bgRemovalResult.products.find(p => p.id === updatedProduct.id);
        const successCount = productResult ? productResult.success_count : 0;
        const totalCount = productResult ? productResult.total_count : (product.images?.length || 1);
        
        const result = {
          id: updatedProduct.id,
          name: updatedProduct.name,
          overallStatus: 'processing',
          stages: {
            databaseSave: {
              status: 'complete',
              data: {
                productId: updatedProduct.id,
                savedAt: new Date().toISOString(),
                status: 'saved',
                databaseId: updatedProduct.id
              }
            },
            backgroundRemoval: {
              status: 'complete',
              data: {
                processedImageUrl: `http://localhost:8000/static/processed/${updatedProduct.id}_0_processed.png`,
                originalImageCount: product.images?.length || 1,
                processedImageCount: successCount
              }
            }
          },
          startTime: Date.now()
        };
        
        onProductComplete(result);
      }
      
    } catch (error) {
      console.error('Batch background removal failed:', error);
      // Continue with mock processing if real API fails
    }
    
    // Step 5: Process remaining stages for each product (3D Model, Optimization)
    for (let i = 0; i < products.length; i++) {
      const product = products[i];
      const updatedProduct = {
        ...product,
        id: savedProductsMap[product.name] || product.id
      };
      
      onProgress({ 
        batchProgress: 30 + ((i / products.length) * 70),
        currentProduct: product.name,
        currentIndex: i,
        total: products.length
      });

      // Process remaining stages with immediate UI updates
      await processRemainingStages(updatedProduct, onProgress, onProductComplete);
    }

    return [];
    
  } catch (error) {
    console.error('Batch processing failed:', error);
    throw error;
  }
};