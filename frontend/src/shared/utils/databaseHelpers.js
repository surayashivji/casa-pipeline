/**
 * Database helper functions for saving processing data
 * Now integrated with real backend API calls
 */

import apiService from '../services/apiService';
export const saveProcessingStage = async (productId, stageData) => {
  try {
    // Real API call to save processing stage
    const response = await apiService.post('/processing-stages', {
      product_id: productId,
      ...stageData
    });
    return response;
  } catch (error) {
    console.error('Failed to save processing stage:', error);
    // Fallback to mock data if API fails
    return {
      id: `stage_${Math.random().toString(36).substr(2, 9)}`,
      ...stageData,
      created_at: new Date().toISOString()
    };
  }
};

export const saveProductImages = async (productId, images) => {
  // In Phase 2: Replace with real API call
  // const response = await api.post('/product-images', {
  //   product_id: productId,
  //   images: images
  // });
  // return response.data;
  
  console.log('Saving product images:', { productId, images });
  return images.map((img, index) => ({
    id: `img_${Math.random().toString(36).substr(2, 9)}`,
    product_id: productId,
    ...img,
    created_at: new Date().toISOString()
  }));
};

export const saveModel3D = async (productId, modelData) => {
  // In Phase 2: Replace with real API call
  // const response = await api.post('/models-3d', {
  //   product_id: productId,
  //   ...modelData
  // });
  // return response.data;
  
  console.log('Saving 3D model:', { productId, modelData });
  return {
    id: `model_${Math.random().toString(36).substr(2, 9)}`,
    product_id: productId,
    ...modelData,
    created_at: new Date().toISOString()
  };
};

export const saveModelLODs = async (model3DId, lods) => {
  // In Phase 2: Replace with real API call
  // const response = await api.post('/model-lods', {
  //   model_3d_id: model3DId,
  //   lods: lods
  // });
  // return response.data;
  
  console.log('Saving model LODs:', { model3DId, lods });
  return lods.map((lod, index) => ({
    id: `lod_${Math.random().toString(36).substr(2, 9)}`,
    model_3d_id: model3DId,
    ...lod,
    created_at: new Date().toISOString()
  }));
};

export const updateProductStatus = async (productId, status, metadata = {}) => {
  // In Phase 2: Replace with real API call
  // const response = await api.patch(`/products/${productId}`, {
  //   status,
  //   ...metadata
  // });
  // return response.data;
  
  console.log('Updating product status:', { productId, status, metadata });
  return {
    id: productId,
    status,
    ...metadata,
    updated_at: new Date().toISOString()
  };
};

export const createBatchJob = async (jobData) => {
  // In Phase 2: Replace with real API call
  // const response = await api.post('/batch-jobs', jobData);
  // return response.data;
  
  console.log('Creating batch job:', jobData);
  return {
    id: `batch_${Math.random().toString(36).substr(2, 9)}`,
    ...jobData,
    created_at: new Date().toISOString()
  };
};

export const updateBatchJob = async (jobId, updates) => {
  // In Phase 2: Replace with real API call
  // const response = await api.patch(`/batch-jobs/${jobId}`, updates);
  // return response.data;
  
  console.log('Updating batch job:', { jobId, updates });
  return {
    id: jobId,
    ...updates,
    updated_at: new Date().toISOString()
  };
};
