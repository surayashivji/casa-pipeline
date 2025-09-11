import { useState } from 'react';
import { LinkIcon } from '@heroicons/react/24/outline';

const URLInput = ({ onNext }) => {
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
      setError('Please enter a product URL');
      return;
    }

    if (!validateUrl(url)) {
      setError('Please enter a valid URL from a supported retailer (IKEA, Target, West Elm, Urban Outfitters)');
      return;
    }

    setIsValidating(true);
    setError('');

    // Simulate URL validation and product detection
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Mock product data based on URL
    const mockProduct = {
      id: 'prod_' + Math.random().toString(36).substr(2, 9),
      url: url,
      name: 'Sample Product',
      description: 'This is a sample product for demonstration',
      brand: 'IKEA',
      price: 99.99,
      images: [
        'https://via.placeholder.com/400x300/8b7355/ffffff?text=Product+View+1',
        'https://via.placeholder.com/400x300/8b7355/ffffff?text=Product+View+2',
        'https://via.placeholder.com/400x300/8b7355/ffffff?text=Product+View+3'
      ],
      dimensions: {
        width: 20,
        height: 30,
        depth: 20,
        unit: 'inches'
      },
      category: 'furniture',
      room_type: 'living_room',
      style_tags: ['modern', 'scandinavian'],
      placement_type: 'floor',
      assembly_required: true,
      in_stock: true
    };

    setIsValidating(false);
    onNext({ product: mockProduct, url });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">Enter Product URL</h2>
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
            <p className="mt-2 text-sm text-red-600">{error}</p>
          )}
        </div>

        <div className="bg-gradient-to-br from-primary-50 to-primary-100 border border-primary-200 rounded-xl p-5 shadow-soft">
          <h3 className="text-sm font-semibold text-primary-900 mb-3">Supported Retailers:</h3>
          <ul className="text-sm text-primary-800 space-y-2">
            <li className="flex items-center">
              <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mr-2"></div>
              IKEA (ikea.com)
            </li>
            <li className="flex items-center">
              <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mr-2"></div>
              Target (target.com)
            </li>
            <li className="flex items-center">
              <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mr-2"></div>
              West Elm (westelm.com)
            </li>
            <li className="flex items-center">
              <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mr-2"></div>
              Urban Outfitters (urbanoutfitters.com)
            </li>
          </ul>
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
                <span>Validating URL...</span>
              </>
            ) : (
              <span>Continue to Product Review</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default URLInput;
