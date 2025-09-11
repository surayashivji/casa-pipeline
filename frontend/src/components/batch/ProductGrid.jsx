import { useState } from 'react';
import { mockProducts } from '../../data/mockProducts';
import { CheckIcon } from '@heroicons/react/24/solid';

const ProductGrid = ({ products, onNext, onBack }) => {
  const [selectedProducts, setSelectedProducts] = useState([]);
  
  // Use mock products for now
  const displayProducts = mockProducts;

  const toggleProduct = (productId) => {
    setSelectedProducts(prev => {
      if (prev.includes(productId)) {
        return prev.filter(id => id !== productId);
      }
      return [...prev, productId];
    });
  };

  const selectAll = () => {
    setSelectedProducts(displayProducts.map(p => p.id));
  };

  const clearSelection = () => {
    setSelectedProducts([]);
  };

  const handleProcess = () => {
    if (selectedProducts.length === 0) {
      alert('Please select at least one product');
      return;
    }
    const selected = displayProducts.filter(p => selectedProducts.includes(p.id));
    onNext({ selectedProducts: selected });
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Select Products to Process</h2>
            <p className="mt-1 text-gray-600">
              Found {displayProducts.length} products. Select which ones to generate 3D models for.
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">
              {selectedProducts.length} of {displayProducts.length} selected
            </p>
            <div className="mt-2 space-x-2">
              <button
                onClick={selectAll}
                className="text-sm text-purple-600 hover:text-purple-500"
              >
                Select All
              </button>
              <button
                onClick={clearSelection}
                className="text-sm text-gray-600 hover:text-gray-500"
              >
                Clear
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {displayProducts.map(product => {
            const isSelected = selectedProducts.includes(product.id);
            return (
              <div
                key={product.id}
                onClick={() => toggleProduct(product.id)}
                className={`
                  relative cursor-pointer rounded-lg border-2 transition-all
                  ${isSelected ? 'border-purple-500 shadow-lg' : 'border-gray-200 hover:border-gray-300'}
                `}
              >
                <div className="aspect-w-1 aspect-h-1">
                  <img
                    src={product.images[0]}
                    alt={product.name}
                    className="w-full h-48 object-cover rounded-t-lg"
                  />
                </div>
                
                <div className="p-4">
                  <h3 className="font-medium text-gray-900">{product.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">{product.description}</p>
                  <div className="mt-2 flex justify-between items-center">
                    <span className="text-lg font-semibold text-gray-900">${product.price}</span>
                    <span className={`
                      px-2 py-1 rounded-full text-xs font-medium
                      ${product.in_stock 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                      }
                    `}>
                      {product.in_stock ? 'In Stock' : 'Out of Stock'}
                    </span>
                  </div>
                </div>

                {isSelected && (
                  <div className="absolute top-2 right-2 bg-purple-500 rounded-full p-2">
                    <CheckIcon className="h-5 w-5 text-white" />
                  </div>
                )}
              </div>
            );
          })}
        </div>

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
            className="px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Process {selectedProducts.length} Product{selectedProducts.length !== 1 ? 's' : ''}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductGrid;
