import { useState, useEffect } from 'react';
import { CheckCircleIcon, XCircleIcon, ClockIcon } from '@heroicons/react/24/solid';

const ProcessingQueue = ({ products = [], onComplete }) => {
  const [processingStatus, setProcessingStatus] = useState([]);
  const [isComplete, setIsComplete] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  // Initialize processing status when products change
  useEffect(() => {
    if (products && products.length > 0) {
      setProcessingStatus(
        products.map(p => ({
          ...p,
          status: 'pending',
          progress: 0,
          currentStep: '',
          startTime: null,
          endTime: null
        }))
      );
      setCurrentIndex(0);
      setIsComplete(false);
    }
  }, [products]);

  // Process products one by one
  useEffect(() => {
    if (!processingStatus.length || currentIndex >= processingStatus.length) {
      if (processingStatus.length > 0 && currentIndex >= processingStatus.length) {
        setIsComplete(true);
      }
      return;
    }

    const processCurrentProduct = async () => {
      // Start processing
      setProcessingStatus(prev => prev.map((p, idx) => 
        idx === currentIndex 
          ? { ...p, status: 'processing', startTime: Date.now(), currentStep: 'Scraping' }
          : p
      ));

      // Simulate processing steps
      const steps = [
        { name: 'Scraping', progress: 20, delay: 1000 },
        { name: 'Removing backgrounds', progress: 40, delay: 2000 },
        { name: 'Generating 3D model', progress: 70, delay: 3000 },
        { name: 'Optimizing', progress: 90, delay: 1500 },
        { name: 'Saving', progress: 100, delay: 500 }
      ];

      for (const step of steps) {
        await new Promise(resolve => setTimeout(resolve, step.delay));
        
        setProcessingStatus(prev => prev.map((p, idx) => 
          idx === currentIndex 
            ? { ...p, progress: step.progress, currentStep: step.name }
            : p
        ));
      }

      // Mark as complete (90% success rate)
      const success = Math.random() > 0.1;
      setProcessingStatus(prev => prev.map((p, idx) => 
        idx === currentIndex 
          ? { 
              ...p, 
              status: success ? 'completed' : 'failed',
              progress: 100,
              endTime: Date.now(),
              error: success ? null : 'Failed to generate 3D model'
            }
          : p
      ));

      // Move to next product after a short delay
      setTimeout(() => {
        setCurrentIndex(prev => prev + 1);
      }, 500);
    };

    processCurrentProduct();
  }, [currentIndex, processingStatus.length]);

  const completedCount = processingStatus.filter(p => p.status === 'completed').length;
  const failedCount = processingStatus.filter(p => p.status === 'failed').length;
  const processingCount = processingStatus.filter(p => p.status === 'processing').length;
  const totalProgress = processingStatus.length > 0 
    ? processingStatus.reduce((sum, p) => sum + p.progress, 0) / processingStatus.length 
    : 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Batch Processing Queue</h2>
          <p className="mt-1 text-gray-600">
            Processing {products.length} products automatically
          </p>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-purple-900 font-medium">Overall Progress</span>
            <span className="text-purple-700">{Math.round(totalProgress)}%</span>
          </div>
          <div className="w-full bg-purple-200 rounded-full h-3">
            <div 
              className="bg-gradient-to-r from-purple-500 to-purple-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${totalProgress}%` }}
            />
          </div>
          <div className="mt-2 flex justify-between text-sm text-purple-700">
            <span>✓ {completedCount} completed</span>
            <span>⚡ {processingCount} processing</span>
            <span>✗ {failedCount} failed</span>
          </div>
        </div>

        <div className="space-y-3 max-h-96 overflow-y-auto">
          {processingStatus.map((product, index) => (
            <div 
              key={product.id}
              className={`
                border rounded-lg p-4 transition-all
                ${product.status === 'processing' ? 'border-purple-300 bg-purple-50' :
                  product.status === 'completed' ? 'border-green-300 bg-green-50' :
                  product.status === 'failed' ? 'border-red-300 bg-red-50' :
                  'border-gray-200 bg-gray-50'}
              `}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {product.status === 'pending' && (
                    <ClockIcon className="h-5 w-5 text-gray-400" />
                  )}
                  {product.status === 'processing' && (
                    <div className="animate-spin h-5 w-5 border-2 border-purple-600 border-t-transparent rounded-full"></div>
                  )}
                  {product.status === 'completed' && (
                    <CheckCircleIcon className="h-5 w-5 text-green-600" />
                  )}
                  {product.status === 'failed' && (
                    <XCircleIcon className="h-5 w-5 text-red-600" />
                  )}
                  
                  <div>
                    <p className="font-medium text-gray-900">{product.name}</p>
                    {product.status === 'processing' && (
                      <p className="text-sm text-purple-600">{product.currentStep}</p>
                    )}
                    {product.status === 'failed' && (
                      <p className="text-sm text-red-600">{product.error}</p>
                    )}
                  </div>
                </div>

                {product.status === 'processing' && (
                  <div className="w-32">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${product.progress}%` }}
                      />
                    </div>
                  </div>
                )}
                
                {product.status === 'completed' && (
                  <span className="text-sm text-green-600 font-medium">
                    {((product.endTime - product.startTime) / 1000).toFixed(1)}s
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        {isComplete && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
              <div>
                <p className="font-medium text-green-900">Batch Processing Complete!</p>
                <p className="text-sm text-green-700 mt-1">
                  Successfully processed {completedCount} of {products.length} products
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-end">
          <button
            onClick={onComplete}
            disabled={!isComplete}
            className="px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isComplete ? 'View Results' : 'Processing...'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProcessingQueue;