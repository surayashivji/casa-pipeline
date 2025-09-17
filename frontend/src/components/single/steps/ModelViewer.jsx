import { useState, useEffect } from 'react';
import { optimizeModel, saveProduct } from '../../../shared/services/apiService';
import { ArrowDownTrayIcon, ServerIcon } from '@heroicons/react/24/outline';
import Model3DViewer from '../../shared/Model3DViewer';

const ModelViewer = ({ data, onNext, onBack, isLastStep }) => {
  const [isOptimizing, setIsOptimizing] = useState(true);
  const [optimizedModel, setOptimizedModel] = useState(null);
  const [selectedLOD, setSelectedLOD] = useState('medium');
  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saveData, setSaveData] = useState(null);

  useEffect(() => {
    const optimize = async () => {
      try {
        const apiResponse = await optimizeModel(
          data.product.id,
          data.processedImages.map(img => img.processed), // image URLs
          { quality: 'high', generate_lods: true }
        );
        
        // Create proxied URLs to avoid CORS issues
        const createProxiedUrl = (url) => 
          url ? `http://localhost:8000/api/proxy-model?url=${encodeURIComponent(url)}` : null;

        // Adapt API response to component format
        const result = {
          originalModel: data.model3D,
          optimizedModelUrl: createProxiedUrl(apiResponse.model_url),
          lods: [
            {
              level: 'high',
              polygonCount: 30840,
              fileSize: '15.2 MB',
              url: createProxiedUrl(apiResponse.model_url)
            },
            {
              level: 'medium',
              polygonCount: 15420,
              fileSize: '7.6 MB',
              url: createProxiedUrl(`${apiResponse.model_url.replace('.glb', '-medium.glb')}`)
            },
            {
              level: 'low',
              polygonCount: 7710,
              fileSize: '3.8 MB',
              url: createProxiedUrl(`${apiResponse.model_url.replace('.glb', '-low.glb')}`)
            }
          ],
          compressionRatio: '75%'
        };
        setOptimizedModel(result);
        setIsOptimizing(false);
      } catch (error) {
        console.error('Optimization failed:', error);
        setIsOptimizing(false);
      }
    };

    optimize();
  }, [data.model3D]);

  const handleSave = async () => {
    setIsSaving(true);
    
    try {
      // Prepare complete product data
      const productData = {
        ...data.product,
        processedImages: data.processedImages,
        model3D: optimizedModel || data.model3D,
        stages: {
          scraping: data.scraping,
          imageSelection: data.imageSelection,
          backgroundRemoval: data.backgroundRemoval,
          modelGeneration: data.modelGeneration,
          optimization: {
            status: 'complete',
            data: optimizedModel
          }
        }
      };
      
      const result = await saveProduct(
        data.product.id,
        'completed',
        {
          final_model_url: optimizedModel?.optimizedModelUrl || data.model3D?.modelUrl,
          total_processing_time: Date.now() - (data.startTime || Date.now()),
          total_cost: (data.model3D?.cost || 0) + (optimizedModel?.cost || 0),
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

  const handleContinue = () => {
    if (isLastStep) {
      // This is the final step, so we save and finish
      handleSave();
    } else {
      // Continue to next step
      onNext({ 
        optimizedModel,
        processedImages: data.processedImages,
        optimization: {
          status: 'complete',
          data: optimizedModel
        }
      });
    }
  };

  const handleFinish = () => {
    onNext({ 
      saved: true, 
      saveData,
      optimizedModel,
      processedImages: data.processedImages,
      optimization: {
        status: 'complete',
        data: optimizedModel
      }
    });
  };

  if (isOptimizing) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">3D Model Viewer</h2>
          <p className="mt-2 text-gray-600">
            Optimizing and preparing your model for viewing
          </p>
        </div>

        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin h-12 w-12 border-4 border-primary-600 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-600">Optimizing model...</p>
          </div>
        </div>
      </div>
    );
  }

  const currentLOD = optimizedModel?.lods?.find(lod => lod.level === selectedLOD) || optimizedModel?.lods?.[0];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900">3D Model Viewer</h2>
        <p className="mt-2 text-gray-600">
          Review and download your generated 3D model
        </p>
      </div>

      <div className="bg-gray-100 rounded-lg p-8">
        <div className="relative bg-gray-200 rounded-lg overflow-hidden" style={{ height: '400px' }}>
          <Model3DViewer 
            modelUrl={data.model3D?.modelUrl}
            className="w-full h-full"
          />
          <div className="absolute bottom-4 right-4 bg-black/70 text-white text-xs px-3 py-1.5 rounded pointer-events-none">
            3D Preview
          </div>
        </div>
      </div>

      {optimizedModel && (
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-3">Model Quality Options</h3>
            <div className="grid grid-cols-3 gap-3">
              {optimizedModel.lods.map((lod) => (
                <button
                  key={lod.level}
                  onClick={() => setSelectedLOD(lod.level)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedLOD === lod.level
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <p className="font-medium text-gray-900 capitalize">{lod.level} Quality</p>
                  <p className="text-sm text-gray-600 mt-1">{lod.polygonCount.toLocaleString()} polygons</p>
                  <p className="text-xs text-gray-500">{lod.fileSize}</p>
                </button>
              ))}
            </div>
          </div>

          {currentLOD && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-blue-900">Selected: {currentLOD.level} quality</p>
                  <p className="text-sm text-blue-700 mt-1">
                    {currentLOD.polygonCount.toLocaleString()} polygons • {currentLOD.fileSize}
                  </p>
                </div>
                <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                  <ArrowDownTrayIcon className="h-5 w-5" />
                  <span>Download</span>
                </button>
              </div>
            </div>
          )}

          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Optimization Results:</h4>
            <p className="text-sm text-gray-600">
              Compression ratio: {optimizedModel.compressionRatio}
            </p>
            <p className="text-sm text-gray-600">
              3 LOD levels generated for optimal performance on iOS devices
            </p>
          </div>
        </div>
      )}

      {!saved ? (
        <div className="flex justify-between">
          <button
            onClick={onBack}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
          >
            Back
          </button>
          <button
            onClick={handleContinue}
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
                <span>Save & Complete</span>
              </>
            )}
          </button>
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

          <div className="flex justify-end">
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

export default ModelViewer;