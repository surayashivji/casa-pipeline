import { useState } from 'react';
import { LinkIcon } from '@heroicons/react/24/outline';
import { scrapeProduct } from '../../../shared/services/apiService';
import { validateUrl, createError, ERROR_TYPES, ERROR_SEVERITY, handleApiError } from '../../../shared/utils/errorHandling';
import ErrorMessage from '../../../shared/components/ErrorMessage';
import LoadingState from '../../../shared/components/LoadingState';

const URLInput = ({ onNext }) => {
  const [url, setUrl] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Clear previous errors
    setError(null);
    
    // Validate URL format and domain
    const validationError = validateUrl(url);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsValidating(true);

    try {
      // Use retry logic for API calls
      const result = await handleApiError(
        () => scrapeProduct(url),
        3, // max retries
        1000 // delay between retries
      );
      
      onNext({ 
        product: result.product,
        productData: result.product,
        images: result.images,
        scraping: {
          status: 'complete',
          data: result
        }
      });
    } catch (err) {
      setError(err);
      setRetryCount(prev => prev + 1);
    } finally {
      setIsValidating(false);
    }
  };

  const handleRetry = () => {
    setError(null);
    handleSubmit({ preventDefault: () => {} });
  };

  const handleDismiss = () => {
    setError(null);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">Enter Product URL</h2>
        <p className="mt-2 text-gray-600">
          Paste the URL of a furniture product from a supported retailer
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="url" className="block text-sm font-semibold text-gray-700 mb-2">
            Product URL
          </label>
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <LinkIcon className="h-5 w-5 text-gray-400 group-hover:text-primary-500 transition-colors duration-200" />
            </div>
            <input
              type="url"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.ikea.com/us/en/p/example-product/"
              className="input pl-12"
              disabled={isValidating}
            />
          </div>
          {error && (
            <ErrorMessage 
              error={error} 
              onRetry={handleRetry} 
              onDismiss={handleDismiss}
              className="mt-2"
            />
          )}
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isValidating || !url.trim()}
            className="btn btn-primary px-8 py-3 text-base flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isValidating ? (
              <>
                <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                <span>Scraping data...</span>
              </>
            ) : (
              <span>Scrape Product</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default URLInput;