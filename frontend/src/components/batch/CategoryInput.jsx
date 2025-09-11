import { useState } from 'react';
import { LinkIcon } from '@heroicons/react/24/outline';

const CategoryInput = ({ onNext, onBack }) => {
  const [url, setUrl] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState('');

  const validateUrl = (url) => {
    const supportedRetailers = [
      'ikea.com',
      'target.com',
      'westelm.com',
      'urbanoutfitters.com'
    ];
    
    try {
      const urlObj = new URL(url);
      return supportedRetailers.some(retailer => urlObj.hostname.includes(retailer));
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!url.trim()) {
      setError('Please enter a category or search URL');
      return;
    }

    if (!validateUrl(url)) {
      setError('Please enter a valid URL from a supported retailer');
      return;
    }

    setIsValidating(true);
    setError('');

    // Simulate category scraping
    await new Promise(resolve => setTimeout(resolve, 2000));

    setIsValidating(false);
    onNext({ categoryUrl: url });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Enter Category or Search URL</h2>
        <p className="mt-2 text-gray-600">
          Paste a URL for a furniture category, search results, or collection page
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
            Category/Search URL
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <LinkIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="url"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.ikea.com/us/en/cat/chairs-20202/"
              className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
              disabled={isValidating}
            />
          </div>
          {error && (
            <p className="mt-2 text-sm text-red-600">{error}</p>
          )}
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-md p-4">
          <h3 className="text-sm font-medium text-purple-900 mb-2">Supported URL Types:</h3>
          <ul className="text-sm text-purple-800 space-y-1">
            <li>• Category pages (e.g., /cat/chairs-20202/)</li>
            <li>• Search results (e.g., /search/?q=dining+table)</li>
            <li>• Collection pages (e.g., /rooms/living-room/)</li>
            <li>• Brand pages (e.g., /brands/designer-name/)</li>
          </ul>
        </div>


        <div className="flex justify-between">
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Back
            </button>
          )}
          <button
            type="submit"
            disabled={isValidating || !url.trim()}
            className="px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isValidating ? (
              <>
                <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                <span>Scraping Category...</span>
              </>
            ) : (
              <span>Find Products</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CategoryInput;
