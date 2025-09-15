import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/solid';

/**
 * Shared component to display a single pipeline stage result
 * Used by both single product and batch processing views
 */
const PipelineStageDisplay = ({ stage, stageData, compact = false }) => {
  if (!stageData) return null;

  const stageConfig = {
    scraping: {
      title: 'Product Data',
      icon: '📊',
      displayFields: ['name', 'price', 'brand', 'category']
    },
    imageSelection: {
      title: 'Selected Image',
      icon: '🖼️',
      displayType: 'image'
    },
    backgroundRemoval: {
      title: 'Background Removed',
      icon: '✂️',
      displayType: 'processedImage'
    },
    modelGeneration: {
      title: '3D Model',
      icon: '🎲',
      displayType: 'modelPreview',
      displayFields: ['vertices', 'triangles']
    },
    optimization: {
      title: 'Optimization',
      icon: '⚡',
      displayFields: ['originalSize', 'optimizedSize', 'compressionRatio']
    },
    saving: {
      title: 'Saved',
      icon: '💾',
      displayFields: ['savedAt']
    }
  };

  const config = stageConfig[stage];
  if (!config) return null;

  const isComplete = stageData.status === 'complete';
  const isFailed = stageData.status === 'failed';

  if (compact) {
    return (
      <div className="flex items-center space-x-2">
        <span className="text-lg">{config.icon}</span>
        <span className="text-sm font-medium">{config.title}</span>
        {isComplete && <CheckCircleIcon className="h-4 w-4 text-green-500" />}
        {isFailed && <XCircleIcon className="h-4 w-4 text-red-500" />}
      </div>
    );
  }

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-xl">{config.icon}</span>
          <h4 className="font-medium text-gray-900">{config.title}</h4>
        </div>
        {isComplete && <CheckCircleIcon className="h-5 w-5 text-green-500" />}
        {isFailed && <XCircleIcon className="h-5 w-5 text-red-500" />}
      </div>

      {stageData.data && (
        <div className="space-y-2">
          {/* Image Display */}
          {config.displayType === 'image' && stageData.data.selectedImage && (
            <div className="w-full h-48 bg-gray-50 rounded border border-gray-200 flex items-center justify-center overflow-hidden">
              <img 
                src={stageData.data.selectedImage} 
                alt={config.title}
                className="max-w-full max-h-full object-contain"
              />
            </div>
          )}

          {/* Processed Image Display (with checkered background) */}
          {config.displayType === 'processedImage' && stageData.data.processedImage && (
            <div className="w-full h-48 bg-checkered rounded border border-gray-200 flex items-center justify-center">
              <img 
                src={stageData.data.processedImage} 
                alt={config.title}
                className="max-w-full max-h-full object-contain"
              />
            </div>
          )}

          {/* Model Preview Display */}
          {config.displayType === 'modelPreview' && stageData.data.modelPreview && (
            <div className="relative w-full h-48 bg-gray-100 rounded border border-gray-200 flex items-center justify-center overflow-hidden">
              <img 
                src={stageData.data.modelPreview} 
                alt={config.title}
                className="max-w-full max-h-full object-contain"
              />
              <div className="absolute top-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                3D Preview
              </div>
            </div>
          )}

          {/* Field Display */}
          {config.displayFields && (
            <div className="text-sm space-y-1">
              {config.displayFields.map(field => {
                const value = stageData.data[field];
                if (!value) return null;
                
                return (
                  <div key={field} className="flex justify-between">
                    <span className="text-gray-500 capitalize">
                      {field.replace(/([A-Z])/g, ' $1').trim()}:
                    </span>
                    <span className="text-gray-900 font-medium">
                      {typeof value === 'object' ? JSON.stringify(value) : value}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {stageData.error && (
        <div className="mt-2 text-sm text-red-600">
          Error: {stageData.error}
        </div>
      )}
    </div>
  );
};

export default PipelineStageDisplay;
