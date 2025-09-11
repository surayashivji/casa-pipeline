// Simulated processing states and batch jobs
export const processingStates = {
  IDLE: 'idle',
  SCRAPING: 'scraping',
  PROCESSING_IMAGES: 'processing_images',
  GENERATING_3D: 'generating_3d',
  OPTIMIZING: 'optimizing',
  COMPLETED: 'completed',
  ERROR: 'error'
};

export const mockBatchJobs = [
  {
    id: 'batch_1',
    sourceUrl: 'https://www.ikea.com/us/en/cat/chairs-20202/',
    sourceType: 'category',
    totalProducts: 25,
    processedCount: 18,
    successfulCount: 16,
    failedCount: 2,
    status: 'processing',
    startedAt: new Date(Date.now() - 1000 * 60 * 15),
    estimatedCompletion: new Date(Date.now() + 1000 * 60 * 5),
    products: []
  }
];

// Generate mock processed images
export const generateProcessedImage = (originalUrl) => {
  return {
    original: originalUrl,
    processed: originalUrl.replace('.jpg', '_transparent.jpg'), // In reality, this would be a different URL
    processingTime: (Math.random() * 3 + 1).toFixed(1),
    fileSize: `${(Math.random() * 2 + 1).toFixed(1)}MB`
  };
};

// Generate mock 3D model
export const generateMock3DModel = (productId) => {
  return {
    id: `model_${productId}`,
    productId: productId,
    meshyTaskId: `task_${Math.random().toString(36).substr(2, 9)}`,
    status: 'completed',
    modelUrl: 'https://example.com/models/furniture.glb',
    thumbnailUrl: 'https://via.placeholder.com/400x300/333333/ffffff?text=3D+Model',
    lods: [
      {
        level: 'high',
        polygonCount: 30000,
        fileSize: '15MB',
        format: 'glb'
      },
      {
        level: 'medium',
        polygonCount: 10000,
        fileSize: '5MB',
        format: 'glb'
      },
      {
        level: 'low',
        polygonCount: 3000,
        fileSize: '1.5MB',
        format: 'glb'
      }
    ],
    generationTime: 45,
    cost: 0.50
  };
};
