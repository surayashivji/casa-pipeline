import { useState } from 'react';
import { saveResults } from '../../../shared/utils/stageProcessors';
import { CloudArrowUpIcon } from '@heroicons/react/24/outline';

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
      
      const result = await saveResults(productData);
      
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
        <h2 className="text-2xl font-bold text-gray-900">Save & Export</h2>
        <p className="mt-2 text-gray-600">
          Save your 3D model and product data
        </p>
      </div>

      {!saved ? (
        <div className="space-y-6">
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Ready to Save</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Product data scraped</p>
                  <p className="text-sm text-gray-600">{data.product.name}</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Images processed</p>
                  <p className="text-sm text-gray-600">{data.processedImages?.length || 0} images with backgrounds removed</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">3D model generated</p>
                  <p className="text-sm text-gray-600">
                    {data.model3D?.vertices?.toLocaleString() || 0} vertices, {data.model3D?.fileSize || 'N/A'}
                  </p>
                </div>
              </div>

              {data.optimizedModel && (
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Model optimized</p>
                    <p className="text-sm text-gray-600">3 LOD levels created</p>
                  </div>
                </div>
              )}
            </div>
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
                  <CloudArrowUpIcon className="h-5 w-5" />
                  <span>Save to Cloud</span>
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
                  Your 3D model and product data have been saved to the cloud.
                </p>
                {saveData && (
                  <div className="mt-3 space-y-1 text-sm">
                    <p><span className="font-medium">Product ID:</span> {saveData.productId}</p>
                    <p><span className="font-medium">Saved at:</span> {new Date(saveData.savedAt).toLocaleString()}</p>
                    <p><span className="font-medium">S3 Location:</span> <code className="text-xs bg-green-100 px-1 py-0.5 rounded">{saveData.s3Location}</code></p>
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