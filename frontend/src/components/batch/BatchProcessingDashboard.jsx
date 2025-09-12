import { useState, useEffect } from 'react';
import { CheckCircleIcon, XCircleIcon, ClockIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/solid';
import { ArrowDownTrayIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
// Note: startBatchProcess and getBatchStatus available for future batch API integration
import { processBatch } from '../../shared/utils/productProcessing';
import ProductPipelineView from '../../shared/components/ProductPipelineView';

const BatchProcessingDashboard = ({ products = [], onNewBatch }) => {
  const [processingStatus, setProcessingStatus] = useState([]);
  const [processedResults, setProcessedResults] = useState({});
  const [expandedProducts, setExpandedProducts] = useState([]);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(true);
  const [startTime, setStartTime] = useState(Date.now());

  // Processing stages that match our shared logic
  const stages = [
    { key: 'scraping', name: 'Scraping', icon: '📊', description: 'Scraped Image' },
    { key: 'imageSelection', name: 'Images', icon: '🖼️', description: 'Selected Images' },
    { key: 'backgroundRemoval', name: 'BG Removal', icon: '✂️', description: 'Background Removed' },
    { key: 'modelGeneration', name: '3D Gen', icon: '🎲', description: '3D Model' },
    { key: 'optimization', name: 'Optimize', icon: '⚡', description: 'Optimization' },
    { key: 'saving', name: 'Save', icon: '💾', description: 'Saved to Database' }
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
      overallStatus: 'pending',
      startTime: null,
      endTime: null
    }));
    
    setProcessingStatus(initialStatus);
    setStartTime(Date.now());

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
                // Set start time if not set
                if (!currentProduct.startTime) {
                  currentProduct.startTime = Date.now();
                }
                
                // Update current stage
                currentProduct.currentStage = progress.stage;
                
                // Update stage status
                Object.keys(currentProduct.stages).forEach(stageKey => {
                  const stageIndex = stages.findIndex(s => s.key === stageKey);
                  const currentStageIndex = stages.findIndex(s => s.key === progress.stage);
                  
                  if (stageIndex < currentStageIndex) {
                    currentProduct.stages[stageKey] = { status: 'completed', progress: 100 };
                  } else if (stageKey === progress.stage) {
                    const progressValue = progress.progress || 0;
                    currentProduct.stages[stageKey] = { 
                      status: progressValue >= 100 ? 'completed' : 'processing', 
                      progress: progressValue 
                    };
                  }
                });
                
                currentProduct.overallStatus = 'processing';
              }
              
              return newStatus;
            });
          }
        },
        onProductComplete: (result) => {
          // Store the full result for expanded view using the original product ID
          const originalProductId = products.find(p => p.name === result.name)?.id;
          const resultId = originalProductId || result.id;
          
          setProcessedResults(prev => ({
            ...prev,
            [resultId]: result
          }));
          
          // Update status
          setProcessingStatus(prev => {
            const newStatus = [...prev];
            const productIndex = products.findIndex(p => p.id === result.id);
            
            if (productIndex !== -1 && newStatus[productIndex]) {
              const product = newStatus[productIndex];
              product.endTime = Date.now();
              
              if (result.status === 'success') {
                Object.keys(product.stages).forEach(stageKey => {
                  product.stages[stageKey] = { status: 'completed', progress: 100 };
                });
                product.overallStatus = 'completed';
              } else {
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

      setIsProcessing(false);
    };

    // Start processing after a short delay
    setTimeout(() => {
      runBatchProcessing();
    }, 500);
  }, [products]);

  const completedCount = processingStatus.filter(p => p.overallStatus === 'completed').length;
  const failedCount = processingStatus.filter(p => p.overallStatus === 'failed').length;
  const processingCount = processingStatus.filter(p => p.overallStatus === 'processing').length;
  const totalCost = Object.values(processedResults).reduce((sum, r) => sum + (r.cost || 0), 0);
  const elapsedTime = Math.floor((Date.now() - startTime) / 1000);

  const toggleProductExpansion = (productId) => {
    setExpandedProducts(prev => 
      prev.includes(productId) 
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    );
  };

  const getStageIcon = (status, isCurrentStage) => {
    if (status === 'completed') {
      return <CheckCircleIcon className="h-4 w-4 text-green-600" />;
    } else if (status === 'failed') {
      return <XCircleIcon className="h-4 w-4 text-red-600" />;
    } else if (status === 'processing' || isCurrentStage) {
      return <div className="animate-spin h-4 w-4 border-2 border-primary-600 border-t-transparent rounded-full" />;
    } else {
      return <ClockIcon className="h-4 w-4 text-gray-400" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Batch Processing Dashboard</h2>
            <p className="mt-1 text-gray-600">
              Processing {products.length} products through the pipeline
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">
              Elapsed Time: {Math.floor(elapsedTime / 60)}:{(elapsedTime % 60).toString().padStart(2, '0')}
            </p>
            <p className="text-sm text-gray-500">
              Est. Cost: ${totalCost.toFixed(2)}
            </p>
          </div>
        </div>

        {/* Summary Stats - Compact Text Format */}
        <div className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-700">Processing: {processingCount}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-700">Completed: {completedCount}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-700">Failed: {failedCount}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-700">Progress: {Math.round(currentProgress)}%</span>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="bg-gray-100 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-primary-500 to-primary-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${currentProgress}%` }}
          />
        </div>

        {/* Processing Table with Expandable Rows */}
        <div className="space-y-2">
          {processingStatus.map((product) => {
            const isExpanded = expandedProducts.includes(product.id);
            const result = processedResults[product.id];
            
            return (
              <div key={product.id} className="border border-gray-200 rounded-lg overflow-hidden">
                {/* Main Row */}
                <div 
                  className={`px-4 py-3 cursor-pointer transition-colors ${
                    product.overallStatus === 'processing' ? 'bg-primary-50 hover:bg-primary-100' :
                    product.overallStatus === 'completed' ? 'bg-green-50 hover:bg-green-100' :
                    product.overallStatus === 'failed' ? 'bg-red-50 hover:bg-red-100' :
                    'bg-gray-50 hover:bg-gray-100'
                  }`}
                  onClick={() => toggleProductExpansion(product.id)}
                >
                  <div className="flex items-center justify-between">
                    {/* Product Info */}
                    <div className="flex items-center space-x-3 flex-1">
                      <button className="text-gray-500 hover:text-gray-700">
                        {isExpanded ? <ChevronUpIcon className="h-5 w-5" /> : <ChevronDownIcon className="h-5 w-5" />}
                      </button>
                      
                      <div>
                        <h4 className="font-medium text-gray-900">{product.name}</h4>
                        <p className="text-sm text-gray-500">
                          {product.overallStatus === 'processing' && product.currentStage && 
                            `Currently: ${stages.find(s => s.key === product.currentStage)?.name || product.currentStage}`
                          }
                          {product.overallStatus === 'completed' && 
                            `Completed in ${((product.endTime - product.startTime) / 1000).toFixed(1)}s`
                          }
                          {product.overallStatus === 'failed' && 
                            'Processing failed'
                          }
                          {product.overallStatus === 'pending' && 
                            'Waiting to start'
                          }
                        </p>
                      </div>
                    </div>
                    
                    {/* Stage Status with Descriptive Text */}
                    <div className="flex items-center space-x-8">
                      {stages.map(stage => {
                        const stageData = product.stages[stage.key];
                        const isCurrentStage = product.currentStage === stage.key;
                        
                        return (
                          <div key={stage.key} className="flex flex-col items-center min-w-0">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className="text-sm">{stage.icon}</span>
                              {getStageIcon(stageData.status, isCurrentStage)}
                            </div>
                            <span className="text-xs text-gray-600 text-center leading-tight max-w-16">
                              {stage.description}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                    
                    {/* Actions - Only for completed items */}
                    <div className="flex items-center space-x-4 ml-6">
                      {product.overallStatus === 'failed' && (
                        <button className="text-gray-600 hover:text-gray-700 font-medium text-sm">
                          Retry
                        </button>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Expanded Details */}
                {isExpanded && result && (
                  <div className="px-6 py-4 bg-white border-t border-gray-200">
                    <div className="space-y-4">
                      {/* Pipeline View */}
                      <ProductPipelineView 
                        productResult={result}
                        layout="grid"
                        showStages={['imageSelection', 'backgroundRemoval', 'modelGeneration', 'optimization']}
                      />
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Actions */}
        <div className="flex justify-between pt-4 border-t border-gray-200">
          <button
            onClick={onNewBatch}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 flex items-center space-x-2"
          >
            <ArrowPathIcon className="h-5 w-5" />
            <span>New Batch</span>
          </button>
          <button 
            className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 flex items-center space-x-2 disabled:opacity-50"
            disabled={completedCount === 0}
          >
            <ArrowDownTrayIcon className="h-5 w-5" />
            <span>Download All ({completedCount})</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default BatchProcessingDashboard;
