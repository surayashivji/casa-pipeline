import React from 'react';
import { ExclamationTriangleIcon, XMarkIcon, ArrowPathIcon } from '@heroicons/react/24/solid';
import { getErrorMessage, getErrorSeverityStyles, isRetryableError } from '../utils/errorHandling';

const ErrorMessage = ({ 
  error, 
  onRetry, 
  onDismiss, 
  showRetry = true, 
  showDismiss = true,
  className = '' 
}) => {
  if (!error) return null;

  const message = getErrorMessage(error);
  const severity = error.severity || 'medium';
  const styles = getErrorSeverityStyles(severity);
  const canRetry = showRetry && isRetryableError(error);

  return (
    <div className={`rounded-md border p-4 ${styles} ${className}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <ExclamationTriangleIcon className="h-5 w-5" />
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium">
            {severity === 'critical' ? 'Critical Error' : 
             severity === 'high' ? 'Error' : 
             severity === 'medium' ? 'Warning' : 'Notice'}
          </h3>
          <div className="mt-2 text-sm">
            <p>{message}</p>
            {error.details && Object.keys(error.details).length > 0 && (
              <details className="mt-2">
                <summary className="cursor-pointer font-medium">More details</summary>
                <pre className="mt-1 text-xs whitespace-pre-wrap">
                  {JSON.stringify(error.details, null, 2)}
                </pre>
              </details>
            )}
          </div>
          <div className="mt-3 flex space-x-3">
            {canRetry && onRetry && (
              <button
                onClick={onRetry}
                className="inline-flex items-center space-x-1 text-sm font-medium hover:underline"
              >
                <ArrowPathIcon className="h-4 w-4" />
                <span>Retry</span>
              </button>
            )}
            {showDismiss && onDismiss && (
              <button
                onClick={onDismiss}
                className="inline-flex items-center space-x-1 text-sm font-medium hover:underline"
              >
                <XMarkIcon className="h-4 w-4" />
                <span>Dismiss</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;
