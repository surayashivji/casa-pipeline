import { useState, useEffect } from 'react';
import { CheckCircleIcon, XCircleIcon, ClockIcon } from '@heroicons/react/24/solid';
import { processBatch } from '../../shared/utils/productProcessing';

const ProcessingQueue = ({ products = [], onComplete }) => {
  const [processingStatus, setProcessingStatus] = useState([]);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [processedResults, setProcessedResults] = useState([]);

  // Processing stages that match our shared logic
  const stages = [
    { key: 'scraping', name: 'Scraping', icon: '📊' },
    { key: 'imageSelection', name: 'Image Selection', icon: '🖼️' },
    { key: 'backgroundRemoval', name: 'Background Removal', icon: '✂️' },
    { key: 'modelGeneration', name: '3D Generation', icon: '🎲' },
    { key: 'optimization', name: 'Optimization', icon: '⚡' },
    { key: 'saving', name: 'Saving', icon: '💾' }
  ];

  useEffect(() => {
    if (!products || products.length === 0) return;

    // Initialize processing status for each product
    const initialStatus = products.map(product => ({
      id: product.id,
      name: product.name,
      stages: stages.reduce((acc, stage) => ({
        ...acc,
        [stage.key]: { status: 'pending', progress: 0 }
      }), {}),
      currentStage: null,
      overallStatus: 'pending'
    }));
    
    setProcessingStatus(initialStatus);

    const runBatchProcessing = async () => {
      const results = await processBatch(products, {
        onProgress: (progress) => {
          setCurrentProgress(progress.batchProgress);
          
          // Update the stage status for the current product
          if (progress.currentIndex !== undefined && progress.stage) {
            setProcessingStatus(prev => {
              const newStatus = [...prev];
              const currentProduct = newStatus[progress.currentIndex];
              
              if (currentProduct) {
                // Update current stage
                currentProduct.currentStage = progress.stage;
                
                // Update stage status
                Object.keys(currentProduct.stages).forEach(stageKey => {
                  const stageIndex = stages.findIndex(s => s.key === stageKey);
                  const currentStageIndex = stages.findIndex(s => s.key === progress.stage);
                  
                  if (stageIndex < currentStageIndex) {
                    // Previous stages are complete
                    currentProduct.stages[stageKey] = { status: 'completed', progress: 100 };
                  } else if (stageKey === progress.stage) {
                    // Current stage is processing
                    currentProduct.stages[stageKey] = { 
                      status: 'processing', 
                      progress: progress.progress || 0 
                    };
                  }
                });
                
                // Update overall status
                currentProduct.overallStatus = 'processing';
              }
              
              return newStatus;
            });
          }
        },
        onProductComplete: (result) => {
          setProcessedResults(prev => [...prev, result]);
          
          // Update final status for completed product
          setProcessingStatus(prev => {
            const newStatus = [...prev];
            const productIndex = products.findIndex(p => p.id === result.id);
            
            if (productIndex !== -1 && newStatus[productIndex]) {
              const product = newStatus[productIndex];
              
              if (result.status === 'success') {
                // All stages completed
                Object.keys(product.stages).forEach(stageKey => {
                  product.stages[stageKey] = { status: 'completed', progress: 100 };
                });
                product.overallStatus = 'completed';
              } else {
                // Mark where it failed
                const failedStage = result.error?.includes('image quality') ? 'modelGeneration' : 'scraping';
                Object.keys(product.stages).forEach(stageKey => {
                  const stageIndex = stages.findIndex(s => s.key === stageKey);
                  const failedIndex = stages.findIndex(s => s.key === failedStage);
                  
                  if (stageIndex < failedIndex) {
                    product.stages[stageKey] = { status: 'completed', progress: 100 };
                  } else if (stageKey === failedStage) {
                    product.stages[stageKey] = { status: 'failed', progress: 0, error: result.error };
                  }
                });
                product.overallStatus = 'failed';
              }
              
              product.currentStage = null;
            }
            
            return newStatus;
          });
        }
      });

      setIsComplete(true);
      setProcessedResults(results);
    };

    // Start processing after a short delay
    setTimeout(() => {
      runBatchProcessing();
    }, 500);
  }, [products]);

  const completedCount = processingStatus.filter(p => p.overallStatus === 'completed').length;
  const failedCount = processingStatus.filter(p => p.overallStatus === 'failed').length;
  const processingCount = processingStatus.filter(p => p.overallStatus === 'processing').length;

  const handleViewResults = () => {
    onComplete({ results: processedResults });
  };

  const getStageIcon = (status, isCurrentStage) => {
    if (status === 'completed') {
      return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
    } else if (status === 'failed') {
      return <XCircleIcon className="h-5 w-5 text-red-600" />;
    } else if (status === 'processing' || isCurrentStage) {
      return <div className="animate-spin h-5 w-5 border-2 border-primary-600 border-t-transparent rounded-full" />;
    } else {
      return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Batch Processing Queue</h2>
          <p className="mt-1 text-gray-600">
            Processing {products.length} products through the pipeline
          </p>
        </div>

        {/* Overall Progress */}
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-purple-900 font-medium">Overall Progress</span>
            <span className="text-purple-700">{Math.round(currentProgress)}%</span>
          </div>
          <div className="w-full bg-purple-200 rounded-full h-3">
            <div 
              className="bg-gradient-to-r from-purple-500 to-purple-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${currentProgress}%` }}
            />
          </div>
          <div className="mt-2 flex justify-between text-sm text-purple-700">
            <span>✓ {completedCount} completed</span>
            <span>⚡ {processingCount} processing</span>
            <span>✗ {failedCount} failed</span>
          </div>
        </div>

        {/* Processing Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                {stages.map(stage => (
                  <th key={stage.key} className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <div className="flex flex-col items-center space-y-1">
                      <span className="text-lg">{stage.icon}</span>
                      <span className="text-[10px]">{stage.name}</span>
                    </div>
                  </th>
                ))}
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {processingStatus.map((product) => (
                <tr key={product.id} className={
                  product.overallStatus === 'processing' ? 'bg-purple-50' :
                  product.overallStatus === 'completed' ? 'bg-green-50' :
                  product.overallStatus === 'failed' ? 'bg-red-50' :
                  ''
                }>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {product.name}
                  </td>
                  {stages.map(stage => {
                    const stageData = product.stages[stage.key];
                    const isCurrentStage = product.currentStage === stage.key;
                    
                    return (
                      <td key={stage.key} className="px-3 py-4 whitespace-nowrap text-center">
                        <div className="flex justify-center">
                          {getStageIcon(stageData.status, isCurrentStage)}
                        </div>
                        {stageData.error && (
                          <div className="mt-1">
                            <span className="text-xs text-red-600" title={stageData.error}>
                              Error
                            </span>
                          </div>
                        )}
                      </td>
                    );
                  })}
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    {product.overallStatus === 'completed' && (
                      <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                        Complete
                      </span>
                    )}
                    {product.overallStatus === 'processing' && (
                      <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded-full">
                        Processing
                      </span>
                    )}
                    {product.overallStatus === 'failed' && (
                      <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">
                        Failed
                      </span>
                    )}
                    {product.overallStatus === 'pending' && (
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                        Pending
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Completion Message */}
        {isComplete && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
              <div>
                <p className="font-medium text-green-900">Batch Processing Complete!</p>
                <p className="text-sm text-green-700 mt-1">
                  Successfully processed {completedCount} of {products.length} products
                  {failedCount > 0 && ` (${failedCount} failed)`}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="flex justify-end">
          <button
            onClick={handleViewResults}
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