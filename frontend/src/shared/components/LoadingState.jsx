import React from 'react';
import ErrorMessage from './ErrorMessage';

const LoadingState = ({ 
  isLoading, 
  error, 
  onRetry, 
  onDismiss,
  message = 'Loading...',
  children 
}) => {
  if (error) {
    return (
      <ErrorMessage 
        error={error} 
        onRetry={onRetry} 
        onDismiss={onDismiss}
      />
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-primary-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">{message}</p>
        </div>
      </div>
    );
  }

  return children;
};

export default LoadingState;
