import { ArrowDownTrayIcon, ArrowPathIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import { useState, useEffect } from 'react';
import ProductPipelineView from '../../shared/components/ProductPipelineView';
import { processBatch } from '../../shared/utils/productProcessing';
import { mockProducts } from '../../data/mockProducts';

const ResultsDashboard = ({ batchJob, products = [], onNewBatch }) => {
  const [expandedProducts, setExpandedProducts] = useState([]);
  const [processedResults, setProcessedResults] = useState([]);
  const [isProcessing, setIsProcessing] = useState(true);
  
  // Process products when component mounts
  useEffect(() => {
    const processProducts = async () => {
      // Use passed products or mock products for demo
      const productsToProcess = products.length > 0 ? products : mockProducts.slice(0, 5);
      
      const results = await processBatch(productsToProcess, {
        onProgress: (progress) => {
          console.log('Batch progress:', progress);
        },
        onProductComplete: (result) => {
          console.log('Product complete:', result);
        }
      });
      
      setProcessedResults(results);
      setIsProcessing(false);
    };
    
    // Simulate that processing just finished
    setTimeout(() => {
      processProducts();
    }, 100);
  }, [products]);
  
  const toggleProductExpansion = (productId) => {
    setExpandedProducts(prev => 
      prev.includes(productId) 
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    );
  };

  if (isProcessing) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center py-8">
          <div className="animate-spin h-8 w-8 border-2 border-primary-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Processing results...</p>
        </div>
      </div>
    );
  }

  // Calculate summary stats
  const successCount = processedResults.filter(r => r.status === 'success').length;
  const failedCount = processedResults.filter(r => r.status === 'failed').length;
  const totalCost = processedResults.reduce((sum, r) => sum + (r.cost || 0), 0);
  const totalTime = processedResults.reduce((sum, r) => {
    const time = parseFloat(r.processingTime) || 0;
    return sum + time;
  }, 0);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Batch Processing Results</h2>
          <p className="mt-1 text-gray-600">
            Summary of your batch processing job
          </p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-sm font-medium text-green-600">Successful</p>
            <p className="mt-1 text-2xl font-bold text-green-900">{successCount}</p>
          </div>
          <div className="bg-red-50 rounded-lg p-4">
            <p className="text-sm font-medium text-red-600">Failed</p>
            <p className="mt-1 text-2xl font-bold text-red-900">{failedCount}</p>
          </div>
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-sm font-medium text-blue-600">Total Time</p>
            <p className="mt-1 text-lg font-bold text-blue-900">{totalTime.toFixed(1)}s</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <p className="text-sm font-medium text-purple-600">Total Cost</p>
            <p className="mt-1 text-2xl font-bold text-purple-900">${totalCost.toFixed(2)}</p>
          </div>
        </div>

        {/* Processed Products */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-3">Processed Products</h3>
          <div className="space-y-3">
            {processedResults.map((result) => {
              const isExpanded = expandedProducts.includes(result.id);
              
              return (
                <div key={result.id} className="border border-gray-200 rounded-lg overflow-hidden">
                  {/* Summary Row */}
                  <div 
                    className="px-6 py-4 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => toggleProductExpansion(result.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <button className="text-gray-500 hover:text-gray-700">
                          {isExpanded ? <ChevronUpIcon className="h-5 w-5" /> : <ChevronDownIcon className="h-5 w-5" />}
                        </button>
                        <h4 className="font-medium text-gray-900">{result.name}</h4>
                        {result.status === 'success' ? (
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                            Success
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">
                            Failed
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-6 text-sm text-gray-500">
                        <span>{result.processingTime}</span>
                        <span>${result.cost.toFixed(2)}</span>
                        {result.status === 'success' && (
                          <button className="text-primary-600 hover:text-primary-700 font-medium">
                            Download Model
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Expanded Details */}
                  {isExpanded && (
                    <div className="px-6 py-4 bg-white border-t border-gray-200">
                      <ProductPipelineView 
                        productResult={result}
                        layout="grid"
                        showStages={['imageSelection', 'backgroundRemoval', 'modelGeneration', 'optimization']}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-between">
          <button
            onClick={onNewBatch}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 flex items-center space-x-2"
          >
            <ArrowPathIcon className="h-5 w-5" />
            <span>New Batch</span>
          </button>
          <div className="space-x-3">
            <button className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
              Export Report
            </button>
            <button className="px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 flex items-center space-x-2">
              <ArrowDownTrayIcon className="h-5 w-5" />
              <span>Download All Models</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsDashboard;