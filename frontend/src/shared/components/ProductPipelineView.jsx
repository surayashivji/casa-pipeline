import PipelineStageDisplay from './PipelineStageDisplay';

/**
 * Shared component to display full product pipeline results
 * Used by both single product review and batch results
 */
const ProductPipelineView = ({ 
  productResult, 
  showStages = ['scraping', 'imageSelection', 'backgroundRemoval', 'modelGeneration'],
  layout = 'grid' // 'grid' | 'vertical' | 'horizontal'
}) => {
  if (!productResult || !productResult.stages) {
    return (
      <div className="text-center text-gray-500 py-8">
        No processing data available
      </div>
    );
  }

  const layoutClasses = {
    grid: 'grid grid-cols-2 md:grid-cols-4 gap-4',
    vertical: 'space-y-4',
    horizontal: 'flex space-x-4 overflow-x-auto'
  };

  return (
    <div className="space-y-4">
      {/* Product Header */}
      <div className="border-b border-gray-200 pb-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">{productResult.name}</h3>
            <p className="text-sm text-gray-500">
              {productResult.url && (
                <a 
                  href={productResult.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  View Original Product
                </a>
              )}
            </p>
          </div>
          <div className="text-right">
            {productResult.status === 'success' && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Success
              </span>
            )}
            {productResult.status === 'failed' && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                Failed
              </span>
            )}
            {productResult.processingTime && (
              <p className="text-sm text-gray-500 mt-1">
                Processed in {productResult.processingTime}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Pipeline Stages */}
      <div className={layoutClasses[layout]}>
        {showStages.map(stage => (
          <PipelineStageDisplay
            key={stage}
            stage={stage}
            stageData={productResult.stages[stage]}
          />
        ))}
      </div>

      {/* Error Display */}
      {productResult.error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-sm text-red-800">
            <span className="font-medium">Processing Error:</span> {productResult.error}
          </p>
        </div>
      )}

      {/* Actions */}
      {productResult.status === 'success' && productResult.stages.modelGeneration?.data?.modelUrl && (
        <div className="flex justify-end space-x-3 pt-3 border-t border-gray-200">
          <button className="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50">
            View 3D Model
          </button>
          <button className="px-4 py-2 text-sm bg-primary-600 text-white rounded-md hover:bg-primary-700">
            Download Model
          </button>
        </div>
      )}
    </div>
  );
};

export default ProductPipelineView;
