import { useState, useEffect } from 'react';
import { CheckCircleIcon, XCircleIcon, ClockIcon } from '@heroicons/react/24/solid';
import { ArrowPathIcon, EyeIcon } from '@heroicons/react/24/outline';
// Note: startBatchProcess and getBatchStatus available for future batch API integration
import { processBatch } from '../../shared/utils/productProcessing';

// Individual stage cell components - moved outside main component
const DatabaseSaveCell = ({ stageData, isCurrentStage = false }) => {
  const getStatusIcon = () => {
    if (!stageData) return <div className="w-8 h-8 bg-gray-100 rounded border border-gray-200 flex items-center justify-center">
      <span className="text-gray-400 text-xs">—</span>
    </div>;
    
    switch (stageData.status) {
      case 'completed':
      case 'complete': // Handle both 'completed' and 'complete'
        return <div className="w-8 h-8 bg-green-100 rounded border border-green-200 flex items-center justify-center">
          <span className="text-green-600 text-xs">💾</span>
        </div>;
      case 'processing':
        return <div className="w-8 h-8 bg-blue-100 rounded border border-blue-200 flex items-center justify-center ring-2 ring-blue-300">
          <div className="animate-spin h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
        </div>;
      case 'failed':
        return <div className="w-8 h-8 bg-red-100 rounded border border-red-200 flex items-center justify-center">
          <span className="text-red-600 text-xs">❌</span>
        </div>;
      default:
        return <div className={`w-8 h-8 bg-gray-100 rounded border border-gray-200 flex items-center justify-center ${isCurrentStage ? 'ring-2 ring-gray-300' : ''}`}>
          <span className="text-gray-400 text-xs">—</span>
        </div>;
    }
  };

  return (
    <div className="flex flex-col items-center space-y-1">
      {getStatusIcon()}
      <div className="flex items-center space-x-1">
        <span className={`text-xs ${isCurrentStage ? 'text-blue-600 font-medium' : 'text-gray-600'}`}>Save Details</span>
        {(stageData?.status === 'completed' || stageData?.status === 'complete') && (
          <span className="text-green-600 text-xs">✅</span>
        )}
      </div>
    </div>
  );
};

const BackgroundRemovalCell = ({ stageData, result, isCurrentStage = false }) => {
  const getStatusIcon = () => {
    if (!stageData) return <div className="w-16 h-16 bg-gray-100 rounded border border-gray-200 flex items-center justify-center">
      <span className="text-gray-400 text-xs">—</span>
    </div>;
    
    switch (stageData.status) {
      case 'completed':
      case 'complete': // Handle both 'completed' and 'complete'
        return <div className="w-16 h-16 bg-green-100 rounded border border-green-200 flex items-center justify-center overflow-hidden">
          {result?.stages?.backgroundRemoval?.data?.processedImages?.[0]?.processed ? (
            <img
              src={result.stages.backgroundRemoval.data.processedImages[0].processed}
              alt="Processed"
              className="max-w-full max-h-full object-contain"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
          ) : null}
          <div className="hidden w-full h-full items-center justify-center">
            <span className="text-green-600 text-xs">✅</span>
          </div>
        </div>;
      case 'processing':
        return <div className="w-16 h-16 bg-blue-100 rounded border border-blue-200 flex items-center justify-center ring-2 ring-blue-300">
          <div className="animate-spin h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full"></div>
        </div>;
      case 'failed':
        return <div className="w-16 h-16 bg-red-100 rounded border border-red-200 flex items-center justify-center">
          <span className="text-red-600 text-xs">❌</span>
        </div>;
      default:
        return <div className={`w-16 h-16 bg-gray-100 rounded border border-gray-200 flex items-center justify-center ${isCurrentStage ? 'ring-2 ring-gray-300' : ''}`}>
          <span className="text-gray-400 text-xs">—</span>
        </div>;
    }
  };

  return (
    <div className="flex flex-col items-center space-y-1">
      {getStatusIcon()}
      <div className="flex items-center space-x-1">
        <span className={`text-xs ${isCurrentStage ? 'text-blue-600 font-medium' : 'text-gray-600'}`}>Background</span>
        {(stageData?.status === 'completed' || stageData?.status === 'complete') && (
          <span className="text-green-600 text-xs">✅</span>
        )}
      </div>
    </div>
  );
};

const Model3DCell = ({ stageData, result, isCurrentStage = false }) => {
  const getStatusIcon = () => {
    if (!stageData) return <div className="w-16 h-16 bg-gray-100 rounded border border-gray-200 flex items-center justify-center">
      <span className="text-gray-400 text-xs">—</span>
    </div>;
    
    switch (stageData.status) {
      case 'completed':
      case 'complete': // Handle both 'completed' and 'complete'
        return <div className="w-16 h-16 bg-green-100 rounded border border-green-200 flex items-center justify-center overflow-hidden">
          {result?.stages?.modelGeneration?.data?.thumbnailUrl ? (
            <img
              src={result.stages.modelGeneration.data.thumbnailUrl}
              alt="3D Model"
              className="max-w-full max-h-full object-contain"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
          ) : null}
          <div className="hidden w-full h-full items-center justify-center">
            <span className="text-green-600 text-xs">✅</span>
          </div>
        </div>;
      case 'processing':
        return <div className="w-16 h-16 bg-blue-100 rounded border border-blue-200 flex items-center justify-center ring-2 ring-blue-300">
          <div className="animate-spin h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full"></div>
        </div>;
      case 'failed':
        return <div className="w-16 h-16 bg-red-100 rounded border border-red-200 flex items-center justify-center">
          <span className="text-red-600 text-xs">❌</span>
        </div>;
      default:
        return <div className={`w-16 h-16 bg-gray-100 rounded border border-gray-200 flex items-center justify-center ${isCurrentStage ? 'ring-2 ring-gray-300' : ''}`}>
          <span className="text-gray-400 text-xs">—</span>
        </div>;
    }
  };

  return (
    <div className="flex flex-col items-center space-y-1">
      {getStatusIcon()}
      <div className="flex items-center space-x-1">
        <span className={`text-xs ${isCurrentStage ? 'text-blue-600 font-medium' : 'text-gray-600'}`}>3D Model</span>
        {(stageData?.status === 'completed' || stageData?.status === 'complete') && (
          <span className="text-green-600 text-xs">✅</span>
        )}
      </div>
    </div>
  );
};

const OptimizationCell = ({ stageData, result, isCurrentStage = false }) => {
  const getStatusIcon = () => {
    if (!stageData) return <div className="w-8 h-8 bg-gray-100 rounded border border-gray-200 flex items-center justify-center">
      <span className="text-gray-400 text-xs">—</span>
    </div>;
    
    switch (stageData.status) {
      case 'completed':
      case 'complete': // Handle both 'completed' and 'complete'
        return <div className="w-8 h-8 bg-green-100 rounded border border-green-200 flex items-center justify-center">
          <span className="text-green-600 text-xs">⚡</span>
        </div>;
      case 'processing':
        return <div className="w-8 h-8 bg-blue-100 rounded border border-blue-200 flex items-center justify-center ring-2 ring-blue-300">
          <div className="animate-spin h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
        </div>;
      case 'failed':
        return <div className="w-8 h-8 bg-red-100 rounded border border-red-200 flex items-center justify-center">
          <span className="text-red-600 text-xs">❌</span>
        </div>;
      default:
        return <div className={`w-8 h-8 bg-gray-100 rounded border border-gray-200 flex items-center justify-center ${isCurrentStage ? 'ring-2 ring-gray-300' : ''}`}>
          <span className="text-gray-400 text-xs">—</span>
        </div>;
    }
  };

  const getOptimizationInfo = () => {
    if (!result?.stages?.optimization?.data) return null;
    
    const data = result.stages.optimization.data;
    return (
      <div className="text-xs text-gray-600 mt-1">
        <div>{data.compressionRatio ? `${(data.compressionRatio * 100).toFixed(0)}%` : 'N/A'}</div>
        <div>{data.optimizedSize ? `${data.optimizedSize}MB` : 'N/A'}</div>
      </div>
    );
  };

  return (
    <div className="flex flex-col items-center space-y-1">
      {getStatusIcon()}
      <div className="flex items-center space-x-1">
        <span className={`text-xs ${isCurrentStage ? 'text-blue-600 font-medium' : 'text-gray-600'}`}>Optimize</span>
        {(stageData?.status === 'completed' || stageData?.status === 'complete') && (
          <span className="text-green-600 text-xs">✅</span>
        )}
      </div>
      {getOptimizationInfo()}
    </div>
  );
};

const StatusCell = ({ product }) => {
  const getStatusInfo = () => {
    switch (product.overallStatus) {
      case 'completed':
        return {
          text: 'Completed',
          color: 'text-green-600',
          bgColor: 'bg-green-100',
          borderColor: 'border-green-200',
          icon: '✅'
        };
      case 'processing':
        return {
          text: 'Processing',
          color: 'text-blue-600',
          bgColor: 'bg-blue-100',
          borderColor: 'border-blue-200',
          icon: '🔄'
        };
      case 'failed':
        return {
          text: 'Failed',
          color: 'text-red-600',
          bgColor: 'bg-red-100',
          borderColor: 'border-red-200',
          icon: '❌'
        };
      default:
        return {
          text: 'Pending',
          color: 'text-gray-600',
          bgColor: 'bg-gray-100',
          borderColor: 'border-gray-200',
          icon: '—'
        };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <div className="flex flex-col items-center space-y-1">
      <div className={`px-3 py-1 rounded-full text-xs font-medium ${statusInfo.color} ${statusInfo.bgColor} ${statusInfo.borderColor} border`}>
        <span className="mr-1">{statusInfo.icon}</span>
        {statusInfo.text}
      </div>
      {product.overallStatus === 'completed' && product.endTime && product.startTime && (
        <div className="text-xs text-gray-500">
          {((product.endTime - product.startTime) / 1000).toFixed(1)}s
        </div>
      )}
    </div>
  );
};

const BatchProcessingDashboard = ({ products = [], onNewBatch }) => {
  const [processingStatus, setProcessingStatus] = useState([]);
  const [processedResults, setProcessedResults] = useState({});
  const [currentProgress, setCurrentProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(true);
  const [startTime, setStartTime] = useState(Date.now());

  // Processing stages for batch processing (CSV data already uploaded)
  const stages = [
    { key: 'databaseSave', name: 'Save Details', icon: '💾', description: 'Saving product details to database' },
    { key: 'backgroundRemoval', name: 'BG Removal', icon: '✂️', description: 'Background Removed' },
    { key: 'modelGeneration', name: '3D Gen', icon: '🎲', description: '3D Model' },
    { key: 'optimization', name: 'Optimize', icon: '⚡', description: 'Optimization' }
  ];

  useEffect(() => {
    if (!products || products.length === 0) return;

    // Initialize processing status for each product
    const initialStatus = products.map((product, index) => ({
      id: product.id || `batch-product-${index}`,
      name: product.name,
      brand: product.brand,
      images: product.images || product.image_urls, // Handle both formats
      price: product.price,
      dimensions: product.dimensions,
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
          
          console.log('onProductComplete called for:', result.name, 'with stages:', Object.keys(result.stages || {}));
          
          setProcessedResults(prev => ({
            ...prev,
            [resultId]: result
          }));
          
          // Update status - handle both intermediate and final results
          setProcessingStatus(prev => {
            const newStatus = [...prev];
            // Try to match by ID first, then by name as fallback
            const productIndex = products.findIndex(p => p.id === result.id || p.name === result.name);
            
            console.log('Product matching - result.id:', result.id, 'result.name:', result.name, 'found index:', productIndex);
            
            if (productIndex !== -1 && newStatus[productIndex]) {
              const product = newStatus[productIndex];
              
              // Update individual stage statuses from the result
              if (result.stages) {
                Object.keys(result.stages).forEach(stageKey => {
                  const stageResult = result.stages[stageKey];
                  if (stageResult && stageResult.status) {
                    product.stages[stageKey] = {
                      status: stageResult.status,
                      progress: stageResult.status === 'complete' ? 100 : 0,
                      data: stageResult.data
                    };
                  }
                });
              }
              
              // Update overall status
              if (result.overallStatus === 'completed') {
                product.overallStatus = 'completed';
                product.endTime = Date.now();
                product.currentStage = null;
              } else if (result.overallStatus === 'failed') {
                product.overallStatus = 'failed';
                product.endTime = Date.now();
                product.currentStage = null;
              } else if (result.overallStatus === 'processing') {
                product.overallStatus = 'processing';
                // Keep current stage active
              }
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

  const completedCount = processingStatus.filter(p => p.stages.databaseSave?.status === 'completed').length;
  const failedCount = processingStatus.filter(p => p.overallStatus === 'failed').length;
  const processingCount = processingStatus.filter(p => p.overallStatus === 'processing').length;
  const totalCost = Object.values(processedResults).reduce((sum, r) => sum + (r.cost || 0), 0);
  const elapsedTime = Math.floor((Date.now() - startTime) / 1000);


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
            {/* <p className="text-sm text-gray-500">
              Est. Cost: ${totalCost.toFixed(2)}
            </p> */}
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

        {/* Processing Table - Admin Dashboard Style */}
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Save Details
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Background Removal
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    3D Model
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Optimization
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {processingStatus.map((product) => {
                  const result = processedResults[product.id];
                  
                  return (
                    <tr key={product.id} className="hover:bg-gray-50">
                      {/* Product Info */}
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-gray-100 rounded border border-gray-200 flex items-center justify-center overflow-hidden">
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
                              <span className="text-gray-400 text-xs">No Image</span>
                            )}
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900 truncate max-w-48">
                              {product.name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {product.brand || 'Unknown Brand'}
                            </div>
                          </div>
                        </div>
                      </td>
                      
                      {/* Database Save Stage */}
                      <td className="px-6 py-4">
                        <DatabaseSaveCell 
                          stageData={product.stages.databaseSave} 
                          isCurrentStage={product.currentStage === 'databaseSave'}
                        />
                      </td>
                      
                      {/* Background Removal Stage */}
                      <td className="px-6 py-4">
                        <BackgroundRemovalCell 
                          stageData={product.stages.backgroundRemoval} 
                          result={result}
                          isCurrentStage={product.currentStage === 'backgroundRemoval'}
                        />
                      </td>
                      
                      {/* 3D Model Stage */}
                      <td className="px-6 py-4">
                        <Model3DCell 
                          stageData={product.stages.modelGeneration} 
                          result={result}
                          isCurrentStage={product.currentStage === 'modelGeneration'}
                        />
                      </td>
                      
                      {/* Optimization Stage */}
                      <td className="px-6 py-4">
                        <OptimizationCell 
                          stageData={product.stages.optimization} 
                          result={result}
                          isCurrentStage={product.currentStage === 'optimization'}
                        />
                      </td>
                      
                      {/* Overall Status */}
                      <td className="px-6 py-4">
                        <StatusCell product={product} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
};

export default BatchProcessingDashboard;
