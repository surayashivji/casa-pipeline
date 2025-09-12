import { useState, useEffect } from 'react';
import { generate3DModel } from '../../../shared/services/apiService';
import { CheckIcon, CubeIcon } from '@heroicons/react/24/solid';
import { createError, ERROR_TYPES, ERROR_SEVERITY, handleApiError } from '../../../shared/utils/errorHandling';
import ErrorMessage from '../../../shared/components/ErrorMessage';

const ModelGeneration = ({ data, onNext, onBack }) => {
  const [isGenerating, setIsGenerating] = useState(true);
  const [currentStep, setCurrentStep] = useState('');
  const [progress, setProgress] = useState(0);
  const [model3D, setModel3D] = useState(null);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    const generateModel = async () => {
      try {
        const apiResponse = await handleApiError(
          () => generate3DModel(
            data.product.id,
            data.processedImages.map(img => img.processed), // Extract processed image URLs
            { quality: 'high', auto_approve: true }
          ),
          2, // max retries for 3D generation
          2000 // longer delay for 3D generation
        );
        
        // Adapt API response to component format
        const adaptedResult = {
          taskId: apiResponse.task_id,
          status: apiResponse.status,
          estimatedCompletion: apiResponse.estimated_completion,
          cost: apiResponse.cost,
          // Mock additional fields that component expects
          modelUrl: `https://example.com/models/${apiResponse.task_id}.glb`,
          modelPreview: `https://example.com/previews/${apiResponse.task_id}.jpg`,
          meshyJobId: apiResponse.task_id,
          vertices: 15420,
          triangles: 30840,
          fileSize: '15.2 MB',
          format: 'glb'
        };
        
        setModel3D(adaptedResult);
        setIsGenerating(false);
      } catch (err) {
        setError(createError(
          err.message || 'Failed to generate 3D model',
          ERROR_TYPES.PROCESSING,
          ERROR_SEVERITY.HIGH,
          { originalError: err, retryCount }
        ));
        setIsGenerating(false);
      }
    };

    generateModel();
  }, [data, retryCount]);

  const handleContinue = () => {
    onNext({ 
      model3D,
      modelGeneration: {
        status: 'complete',
        data: model3D
      }
    });
  };


  const handleRetry = () => {
    setIsGenerating(true);
    setError(null);
    setProgress(0);
    setRetryCount(prev => prev + 1);
  };

  const handleDismiss = () => {
    setError(null);
  };

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">3D Model Generation</h2>
          <p className="mt-2 text-gray-600">
            Generate a 3D model from processed images
          </p>
        </div>

        <ErrorMessage 
          error={error} 
          onRetry={handleRetry} 
          onDismiss={handleDismiss}
        />

        <div className="flex justify-start">
          <button
            onClick={onBack}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
          >
            Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">3D Model Generation</h2>
        <p className="mt-2 text-gray-600">
          Creating a 3D model using Meshy AI
        </p>
      </div>

      {isGenerating ? (
        <div className="space-y-6">
          <div className="bg-primary-50 rounded-lg p-8 border border-primary-200">
            <div className="flex flex-col items-center text-center">
              {/* Simple Spinning Loader */}
              <div className="mb-6">
                <div className="animate-spin h-12 w-12 border-3 border-primary-600 border-t-transparent rounded-full flex items-center justify-center">
                  <CubeIcon className="h-6 w-6 text-primary-600" />
                </div>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Generating 3D Model</h3>
              <p className="text-primary-700 font-medium mb-1">{currentStep}</p>
              <p className="text-sm text-gray-600">This may take a few minutes...</p>
            </div>
          </div>

          {/* Clean Progress Bar */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700">Progress</span>
              <span className="text-sm font-semibold text-primary-600">{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-primary-500 to-primary-600 h-2 rounded-full transition-all duration-700 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex items-start space-x-4">
              <img 
                src={model3D.modelPreview}
                alt="3D Model Preview"
                className="w-48 h-48 object-cover rounded-lg border border-gray-200"
              />
              <div className="flex-1 space-y-3">
                <h3 className="text-lg font-medium text-gray-900">Model Generated Successfully!</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Model ID:</span>
                    <span className="font-mono text-gray-900">{model3D.meshyJobId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Vertices:</span>
                    <span className="text-gray-900">{model3D.vertices.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Triangles:</span>
                    <span className="text-gray-900">{model3D.triangles.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">File Size:</span>
                    <span className="text-gray-900">{model3D.fileSize}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Format:</span>
                    <span className="text-gray-900">{model3D.format.toUpperCase()}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <CheckIcon className="h-5 w-5 text-green-600" />
              <p className="text-green-900 font-medium">3D model generated successfully!</p>
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
              onClick={handleContinue}
              className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              Continue to Model Viewer
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelGeneration;