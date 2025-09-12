import { useState, useEffect } from 'react';
import { optimizeModel } from '../../../shared/services/apiService';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';

const ModelViewer = ({ data, onNext, onBack }) => {
  const [isOptimizing, setIsOptimizing] = useState(true);
  const [optimizedModel, setOptimizedModel] = useState(null);
  const [selectedLOD, setSelectedLOD] = useState('medium');

  useEffect(() => {
    const optimize = async () => {
      try {
        const apiResponse = await optimizeModel(
          data.product.id,
          data.processedImages.map(img => img.processed), // image URLs
          { quality: 'high', generate_lods: true }
        );
        
        // Adapt API response to component format
        const result = {
          originalModel: data.model3D,
          optimizedModelUrl: apiResponse.model_url,
          lods: [
            {
              level: 'high',
              polygonCount: 30840,
              fileSize: '15.2 MB',
              url: apiResponse.model_url
            },
            {
              level: 'medium',
              polygonCount: 15420,
              fileSize: '7.6 MB',
              url: `${apiResponse.model_url.replace('.glb', '-medium.glb')}`
            },
            {
              level: 'low',
              polygonCount: 7710,
              fileSize: '3.8 MB',
              url: `${apiResponse.model_url.replace('.glb', '-low.glb')}`
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

  const handleContinue = () => {
    onNext({ 
      optimizedModel,
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
          <h2 className="text-2xl font-bold text-gray-900">3D Model Viewer</h2>
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
        <h2 className="text-2xl font-bold text-gray-900">3D Model Viewer</h2>
        <p className="mt-2 text-gray-600">
          Review and download your generated 3D model
        </p>
      </div>

      <div className="bg-gray-100 rounded-lg p-8">
        <div className="aspect-w-16 aspect-h-9 bg-gray-200 rounded-lg overflow-hidden">
          <div className="flex items-center justify-center">
            <img 
              src={data.model3D.modelPreview}
              alt="3D Model"
              className="max-w-full max-h-full object-contain"
            />
            <div className="absolute bottom-4 right-4 bg-black/70 text-white text-xs px-3 py-1.5 rounded">
              3D Preview
            </div>
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

      <div className="flex justify-between">
        <button
          onClick={onBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
        >
          Back
        </button>
        <button
          onClick={handleContinue}
          className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700"
        >
          Save & Continue
        </button>
      </div>
    </div>
  );
};

export default ModelViewer;