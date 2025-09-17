import { useState, useEffect } from 'react';
import { mockProducts } from '../../data/mockProducts';
import { CheckIcon } from '@heroicons/react/24/solid';

const ProductGrid = ({ products, onNext, onBack }) => {
  // Use provided products or fallback to mock products
  const displayProducts = products && products.length > 0 ? products : mockProducts;
  
  // Convert CSV data to display format if needed
  const formattedProducts = displayProducts.map((product, index) => {
    // If it's CSV data, convert to display format
    if (product.name && product.brand && product.price && product.image_urls) {
      return {
        id: `csv-${index}`,
        name: product.name,
        brand: product.brand,
        price: product.price,
        images: product.image_urls,
        dimensions: {
          width: product.width_inches,
          height: product.height_inches,
          depth: product.depth_inches
        }
      };
    }
    // If it's already in display format, return as is
    return product;
  });
  
  // Initialize with all products selected by default
  const [selectedProducts, setSelectedProducts] = useState(
    formattedProducts.map(p => p.id)
  );

  const toggleProduct = (productId) => {
    setSelectedProducts(prev => {
      if (prev.includes(productId)) {
        return prev.filter(id => id !== productId);
      }
      return [...prev, productId];
    });
  };

  const selectAll = () => {
    setSelectedProducts(formattedProducts.map(p => p.id));
  };

  const clearSelection = () => {
    setSelectedProducts([]);
  };

  const handleProcess = () => {
    if (selectedProducts.length === 0) {
      alert('Please select at least one product');
      return;
    }
    const selected = formattedProducts.filter(p => selectedProducts.includes(p.id));
    onNext({ selectedProducts: selected });
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Select Products to Process</h2>
            <p className="mt-1 text-gray-600">
              {selectedProducts.length} of {formattedProducts.length} products selected
            </p>
            <div className="mt-2 space-x-2">
              <button
                onClick={selectAll}
                className="text-sm text-primary-600 hover:text-primary-500"
              >
                Select All
              </button>
              <button
                onClick={clearSelection}
                className="text-sm text-gray-600 hover:text-gray-500"
              >
                Clear Selection
              </button>
            </div>
          </div>
        </div>

        {/* Product List - Vertical Layout */}
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <div className="max-h-96 overflow-y-auto">
            {formattedProducts.map((product, index) => {
              const isSelected = selectedProducts.includes(product.id);
              return (
                <div
                  key={product.id}
                  onClick={() => toggleProduct(product.id)}
                  className={`
                    cursor-pointer border-b border-gray-100 last:border-b-0 transition-all
                    ${isSelected 
                      ? 'bg-primary-50 hover:bg-primary-100' 
                      : 'bg-white hover:bg-gray-50'
                    }
                  `}
                >
                  <div className="flex items-center p-4">
                    {/* Checkbox */}
                    <div className="flex-shrink-0 mr-4">
                      <div className={`
                        w-5 h-5 rounded border-2 flex items-center justify-center transition-all
                        ${isSelected 
                          ? 'bg-primary-600 border-primary-600' 
                          : 'bg-white border-gray-300'
                        }
                      `}>
                        {isSelected && (
                          <CheckIcon className="h-3 w-3 text-white" />
                        )}
                      </div>
                    </div>

                    {/* Product Image */}
                    <div className="flex-shrink-0 w-16 h-16 mr-4 bg-gray-50 rounded flex items-center justify-center overflow-hidden">
                      {product.images && product.images.length > 0 ? (
                        <img
                          src={product.images[0]}
                          alt={product.name}
                          className="max-w-full max-h-full object-contain"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                        />
                      ) : (
                        <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                          <span className="text-gray-400 text-xs">No Image</span>
                        </div>
                      )}
                    </div>

                    {/* Product Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="text-sm font-medium text-gray-900 truncate">
                            {product.name}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {product.brand} • ${product.price}
                          </p>
                        </div>
                      </div>
                      {product.dimensions && (
                        <p className="mt-1 text-xs text-gray-500">
                          {product.dimensions.width}" × {product.dimensions.height}" × {product.dimensions.depth}"
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Summary Stats */}
        {/* <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex justify-between items-center text-sm">
            <div>
              <span className="font-medium text-gray-900">Estimated Processing Time:</span>
              <span className="ml-2 text-gray-600">~{selectedProducts.length * 30} seconds</span>
            </div>
            <div>
              <span className="font-medium text-gray-900">Estimated Cost:</span>
              <span className="ml-2 text-gray-600">${(selectedProducts.length * 0.50).toFixed(2)}</span>
            </div>
          </div>
        </div> */}

        {/* Action Buttons */}
        <div className="flex justify-between">
          <button
            onClick={onBack}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
          >
            Back
          </button>
          <button
            onClick={handleProcess}
            disabled={selectedProducts.length === 0}
            className="btn btn-primary px-8 py-3 text-base flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>Process {selectedProducts.length} Product{selectedProducts.length !== 1 ? 's' : ''}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductGrid;