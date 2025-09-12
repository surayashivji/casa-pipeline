/**
 * API Service for Room Decorator 3D Pipeline
 * Replaces mock functions with real backend API calls
 */

const API_BASE_URL = 'http://localhost:8000/api';

// API client with error handling
class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async patch(endpoint, data) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }
}

const apiClient = new ApiClient();

// URL Detection
export const detectUrl = async (url) => {
  return apiClient.post('/detect-url', { url });
};

// Single Product Pipeline
export const scrapeProduct = async (url, mode = 'single') => {
  return apiClient.post('/scrape', { url, mode });
};

export const selectImages = async (productId, selectedImages) => {
  return apiClient.post('/select-images', {
    product_id: productId,
    selected_images: selectedImages,
  });
};

export const removeBackgrounds = async (productId, imageUrls) => {
  return apiClient.post('/remove-backgrounds', {
    product_id: productId,
    image_urls: imageUrls,
  });
};

export const approveImages = async (productId, approvedImages) => {
  return apiClient.post('/approve-images', {
    product_id: productId,
    approved_images: approvedImages,
  });
};

export const generate3DModel = async (productId, approvedImages, quality = 'high') => {
  return apiClient.post('/generate-3d', {
    product_id: productId,
    approved_images: approvedImages,
    quality,
  });
};

export const checkModelStatus = async (taskId) => {
  return apiClient.get(`/model-status/${taskId}`);
};

export const optimizeModel = async (productId, modelUrl) => {
  return apiClient.post('/optimize-model', {
    product_id: productId,
    model_url: modelUrl,
  });
};

export const saveProduct = async (productId, finalModelUrl, metadata = {}) => {
  return apiClient.post('/save-product', {
    product_id: productId,
    final_model_url: finalModelUrl,
    metadata,
  });
};

// Batch Processing
export const scrapeCategory = async (categoryUrl, maxProducts = 10, filters = {}) => {
  return apiClient.post('/scrape-category', {
    category_url: categoryUrl,
    max_products: maxProducts,
    filters,
  });
};

export const startBatchProcess = async (productIds, settings = {}) => {
  return apiClient.post('/batch-process', {
    product_ids: productIds,
    settings,
  });
};

export const getBatchStatus = async (batchId) => {
  return apiClient.get(`/batch-status/${batchId}`);
};

export const cancelBatch = async (batchId) => {
  return apiClient.post(`/batch-cancel/${batchId}`);
};

export const getBatchHistory = async () => {
  return apiClient.get('/batch-history');
};

// Monitoring and Health
export const getHealthStatus = async () => {
  return apiClient.get('/health');
};

export const getMetrics = async () => {
  return apiClient.get('/metrics');
};

export const resetMetrics = async () => {
  return apiClient.get('/metrics/reset');
};

export const getLogs = async () => {
  return apiClient.get('/logs');
};

// WebSocket connection for real-time updates
export class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket('ws://localhost:8000/ws');
        
        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('WebSocket message parse error:', error);
          }
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  handleMessage(data) {
    // Emit custom events for different message types
    const event = new CustomEvent('websocket-message', { detail: data });
    window.dispatchEvent(event);
  }

  subscribeToProduct(productId) {
    this.send({
      type: 'subscribe_product',
      product_id: productId,
    });
  }

  subscribeToBatch(batchId) {
    this.send({
      type: 'subscribe_batch',
      batch_id: batchId,
    });
  }

  ping() {
    this.send({ type: 'ping' });
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect().catch(() => {
          // Reconnection failed, will try again
        });
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Create singleton WebSocket service
export const webSocketService = new WebSocketService();

// Export all functions for easy importing
export default {
  // URL Detection
  detectUrl,
  
  // Single Product Pipeline
  scrapeProduct,
  selectImages,
  removeBackgrounds,
  approveImages,
  generate3DModel,
  checkModelStatus,
  optimizeModel,
  saveProduct,
  
  // Batch Processing
  scrapeCategory,
  startBatchProcess,
  getBatchStatus,
  cancelBatch,
  getBatchHistory,
  
  // Monitoring
  getHealthStatus,
  getMetrics,
  resetMetrics,
  getLogs,
  
  // WebSocket
  webSocketService,
};
