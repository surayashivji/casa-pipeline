/**
 * Error handling utilities for the pipeline
 */

// Error types for consistent error handling
export const ERROR_TYPES = {
  NETWORK: 'NETWORK_ERROR',
  VALIDATION: 'VALIDATION_ERROR',
  PROCESSING: 'PROCESSING_ERROR',
  TIMEOUT: 'TIMEOUT_ERROR',
  UNKNOWN: 'UNKNOWN_ERROR'
};

// Error severity levels
export const ERROR_SEVERITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
};

/**
 * Create a standardized error object
 */
export const createError = (message, type = ERROR_TYPES.UNKNOWN, severity = ERROR_SEVERITY.MEDIUM, details = {}) => {
  return {
    id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    message,
    type,
    severity,
    details,
    timestamp: new Date().toISOString(),
    retryable: type !== ERROR_TYPES.VALIDATION
  };
};

/**
 * Handle API errors with retry logic
 */
export const handleApiError = async (apiCall, maxRetries = 3, delay = 1000) => {
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await apiCall();
    } catch (error) {
      lastError = error;
      
      // Don't retry validation errors
      if (error.type === ERROR_TYPES.VALIDATION) {
        throw error;
      }
      
      // Don't retry on last attempt
      if (attempt === maxRetries) {
        break;
      }
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay * attempt));
    }
  }
  
  throw createError(
    `Operation failed after ${maxRetries} attempts: ${lastError.message}`,
    ERROR_TYPES.NETWORK,
    ERROR_SEVERITY.HIGH,
    { originalError: lastError, attempts: maxRetries }
  );
};

/**
 * Validate URL format
 */
export const validateUrl = (url) => {
  if (!url || typeof url !== 'string') {
    return createError('URL is required', ERROR_TYPES.VALIDATION, ERROR_SEVERITY.LOW);
  }
  
  try {
    const urlObj = new URL(url);
    
    // Check if it's a supported domain (basic check)
    const supportedDomains = ['ikea.com', 'target.com', 'westelm.com', 'urbanoutfitters.com'];
    const domain = urlObj.hostname.toLowerCase();
    
    if (!supportedDomains.some(supported => domain.includes(supported))) {
      return createError(
        'URL domain not supported. Please use a supported retailer URL.',
        ERROR_TYPES.VALIDATION,
        ERROR_SEVERITY.MEDIUM,
        { supportedDomains, providedDomain: domain }
      );
    }
    
    return null; // No error
  } catch (error) {
    return createError(
      'Invalid URL format. Please enter a valid URL.',
      ERROR_TYPES.VALIDATION,
      ERROR_SEVERITY.LOW,
      { providedUrl: url }
    );
  }
};

/**
 * Get user-friendly error message
 */
export const getErrorMessage = (error) => {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error.message) {
    return error.message;
  }
  
  switch (error.type) {
    case ERROR_TYPES.NETWORK:
      return 'Network error. Please check your connection and try again.';
    case ERROR_TYPES.TIMEOUT:
      return 'Request timed out. Please try again.';
    case ERROR_TYPES.VALIDATION:
      return error.message || 'Invalid input. Please check your data and try again.';
    case ERROR_TYPES.PROCESSING:
      return 'Processing error occurred. Please try again or contact support.';
    default:
      return 'An unexpected error occurred. Please try again.';
  }
};

/**
 * Get error severity styling
 */
export const getErrorSeverityStyles = (severity) => {
  switch (severity) {
    case ERROR_SEVERITY.LOW:
      return 'bg-yellow-50 border-yellow-200 text-yellow-800';
    case ERROR_SEVERITY.MEDIUM:
      return 'bg-orange-50 border-orange-200 text-orange-800';
    case ERROR_SEVERITY.HIGH:
      return 'bg-red-50 border-red-200 text-red-800';
    case ERROR_SEVERITY.CRITICAL:
      return 'bg-red-100 border-red-300 text-red-900';
    default:
      return 'bg-gray-50 border-gray-200 text-gray-800';
  }
};

/**
 * Check if error is retryable
 */
export const isRetryableError = (error) => {
  if (typeof error === 'string') return false;
  return error.retryable !== false && error.type !== ERROR_TYPES.VALIDATION;
};

/**
 * Format error for logging
 */
export const formatErrorForLogging = (error, context = {}) => {
  return {
    error: {
      message: error.message || 'Unknown error',
      type: error.type || ERROR_TYPES.UNKNOWN,
      severity: error.severity || ERROR_SEVERITY.MEDIUM,
      stack: error.stack,
      details: error.details
    },
    context,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    url: window.location.href
  };
};
