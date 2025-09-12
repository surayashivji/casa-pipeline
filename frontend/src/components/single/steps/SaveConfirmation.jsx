import { useState } from 'react';
import { saveProduct } from '../../../shared/services/apiService';
import { ServerIcon } from '@heroicons/react/24/outline';
import ProductPipelineView from '../../../shared/components/ProductPipelineView';

const SaveConfirmation = ({ data, onNext, onBack }) => {
  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saveData, setSaveData] = useState(null);

  const handleSave = async () => {
    setIsSaving(true);
    
    try {
      // Prepare complete product data
      const productData = {
        ...data.product,
        processedImages: data.processedImages,
        model3D: data.optimizedModel || data.model3D,
        stages: {
          scraping: data.scraping,
          imageSelection: data.imageSelection,
          backgroundRemoval: data.backgroundRemoval,
          modelGeneration: data.modelGeneration,
          optimization: data.optimization
        }
      };
      
      const result = await saveProduct(
        data.product.id,
        'completed',
        {
          final_model_url: data.optimizedModel?.optimizedModelUrl || data.model3D?.modelUrl,
          total_processing_time: Date.now() - (data.startTime || Date.now()),
          total_cost: (data.model3D?.cost || 0) + (data.optimizedModel?.cost || 0),
          stages_completed: ['scraping', 'image_selection', 'background_removal', 'model_generation', 'optimization']
        }
      );
      
      setSaveData(result);
      setSaved(true);
      setIsSaving(false);
    } catch (error) {
      console.error('Save failed:', error);
      setIsSaving(false);
    }
  };

  const handleFinish = () => {
    onNext({ saved: true, saveData });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Save to Database</h2>
        <p className="mt-2 text-gray-600">
          Save your 3D model and product data to the pipeline database
        </p>
      </div>

      {!saved ? (
        <div className="space-y-6">
          {/* Product Pipeline Results */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Pipeline Results</h3>
            <ProductPipelineView 
              productResult={{
                product: data.product,
                processedImages: data.processedImages,
                model3D: data.optimizedModel || data.model3D,
                stages: {
                  scraping: data.scraping,
                  imageSelection: data.imageSelection,
                  backgroundRemoval: data.backgroundRemoval,
                  modelGeneration: data.modelGeneration,
                  optimization: data.optimization
                }
              }}
              layout="grid"
              showStages={['imageSelection', 'backgroundRemoval', 'modelGeneration', 'optimization']}
            />
          </div>

          <div className="flex justify-between">
            <button
              onClick={onBack}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Back
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isSaving ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <ServerIcon className="h-5 w-5" />
                  <span>Save to Database</span>
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-medium text-green-900">Successfully Saved!</h3>
                <p className="mt-1 text-sm text-green-700">
                  Your 3D model and product data have been saved to the database.
                </p>
                {saveData && (
                  <div className="mt-3 space-y-1 text-sm">
                    <p><span className="font-medium">Product ID:</span> {saveData.productId}</p>
                    <p><span className="font-medium">Saved at:</span> {new Date(saveData.savedAt).toLocaleString()}</p>
                    <p><span className="font-medium">Database ID:</span> <code className="text-xs bg-green-100 px-1 py-0.5 rounded">{saveData.productId}</code></p>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-2">Next Steps:</h4>
            <ul className="space-y-1 text-sm text-blue-800">
              <li>• View your model in the 3D library</li>
              <li>• Download for use in iOS app</li>
              <li>• Process another product</li>
              <li>• Access from batch processing dashboard</li>
            </ul>
          </div>

          <div className="flex justify-end space-x-3">
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Process Another
            </button>
            <button
              onClick={handleFinish}
              className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              View in Library
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SaveConfirmation;