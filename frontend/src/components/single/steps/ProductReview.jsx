import { useState } from 'react';
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/solid';

const ProductReview = ({ data, onNext, onBack }) => {
  const [isApproved, setIsApproved] = useState(false);
  const product = data.product;
  const images = data.images || [];

  const handleContinue = () => {
    if (!isApproved) {
      alert('Please review and approve the product data before continuing');
      return;
    }
    onNext({ product });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900">Review Product Data</h2>
        <p className="mt-2 text-gray-600">
          Verify the scraped product information before proceeding with image selection
        </p>
        <a 
          href={product.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="mt-2 inline-flex items-center text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          View original product →
        </a>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <div className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-gray-900">{product.name}</h3>
              <p className="mt-1 text-gray-600">{product.description}</p>
              <div className="mt-2 flex items-center space-x-4">
                <span className="text-2xl font-bold text-gray-900">${product.price}</span>
              </div>
            </div>
            <div className="ml-6">
              <img
                src={images[0]}
                alt={product.name}
                className="w-32 h-32 object-contain rounded-lg border border-gray-200 bg-gray-50"
              />
            </div>
          </div>
        </div>

        <div className="border-t border-gray-200 bg-gray-50 px-6 py-4">
          <dl className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="font-medium text-gray-500">Brand</dt>
              <dd className="mt-1 text-gray-900">{product.brand}</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-500">Category</dt>
              <dd className="mt-1 text-gray-900 capitalize">{product.category}</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-500">Dimensions</dt>
              <dd className="mt-1 text-gray-900">
                {product.dimensions.width}" × {product.dimensions.height}" × {product.dimensions.depth}"
              </dd>
            </div>
            <div>
              <dt className="font-medium text-gray-500">Room Type</dt>
              <dd className="mt-1 text-gray-900 capitalize">{product.room_type.replace('_', ' ')}</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-500">Style</dt>
              <dd className="mt-1 text-gray-900">{product.style_tags.join(', ')}</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-500">Assembly Required</dt>
              <dd className="mt-1 text-gray-900">{product.assembly_required ? 'Yes' : 'No'}</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Available Images ({images.length})</h4>
        <div className="grid grid-cols-4 gap-2">
          {images.map((image, index) => (
            <div key={index} className="w-full h-20 bg-gray-50 rounded border border-gray-200 flex items-center justify-center overflow-hidden">
              <img
                src={image}
                alt={`Product view ${index + 1}`}
                className="max-w-full max-h-full object-contain"
              />
            </div>
          ))}
        </div>
      </div>


      <div className="flex justify-between items-center">
        <button
          onClick={onBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
        >
          Back
        </button>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setIsApproved(!isApproved)}
            className={`
              flex items-center space-x-2 px-4 py-2 rounded-md border-2 transition-all
              ${isApproved 
                ? 'border-green-500 bg-green-50 text-green-700' 
                : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
              }
            `}
          >
            <CheckIcon className={`h-5 w-5 ${isApproved ? 'text-green-600' : 'text-gray-400'}`} />
            <span>{isApproved ? 'Approved' : 'Approve Info'}</span>
          </button>
          
          <button
            onClick={handleContinue}
            disabled={!isApproved}
            className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue to Image Selection
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductReview;
