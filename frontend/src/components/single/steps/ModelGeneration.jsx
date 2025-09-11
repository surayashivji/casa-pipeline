import { useState, useEffect } from 'react';
import { generateMock3DModel } from '../../../data/mockProcessingStates';
import { CheckIcon, CubeIcon } from '@heroicons/react/24/solid';

const ModelGeneration = ({ data, onNext, onBack }) => {
  const [isGenerating, setIsGenerating] = useState(true);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Initializing Meshy API...');
  const [model3D, setModel3D] = useState(null);

  useEffect(() => {
    // Simulate 3D generation process
    const steps = [
      { progress: 10, status: 'Uploading images to Meshy...', delay: 1000 },
      { progress: 30, status: 'Analyzing product structure...', delay: 2000 },
      { progress: 50, status: 'Generating 3D geometry...', delay: 3000 },
      { progress: 70, status: 'Creating textures and materials...', delay: 2000 },
      { progress: 90, status: 'Optimizing model...', delay: 1500 },
      { progress: 100, status: 'Generation complete!', delay: 500 }
    ];

    let currentStep = 0;
    
    const runStep = () => {
      if (currentStep < steps.length) {
        const step = steps[currentStep];
        setProgress(step.progress);
        setStatus(step.status);
        
        setTimeout(() => {
          currentStep++;
          runStep();
        }, step.delay);
      } else {
        setModel3D(generateMock3DModel(data.product.id));
        setIsGenerating(false);
      }
    };

    runStep();
  }, [data.product.id]);

  const handleContinue = () => {
    onNext({ model3D });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">3D Model Generation</h2>
        <p className="mt-2 text-gray-600">
          Using Meshy AI to create a 3D model from your approved images
        </p>
      </div>

      {isGenerating ? (
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-8">
            <div className="flex flex-col items-center space-y-4">
              <div className="relative">
                <div className="w-24 h-24 rounded-full border-4 border-indigo-200 flex items-center justify-center">
                  <div className="absolute inset-0 rounded-full border-4 border-indigo-600 border-t-transparent animate-spin"></div>
                  <span className="text-2xl font-bold text-indigo-600">{progress}%</span>
                </div>
              </div>
              
              <p className="text-lg font-medium text-gray-700">{status}</p>
              
              <div className="w-full max-w-md">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-indigo-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <p className="text-sm text-blue-800">
              <strong>Tip:</strong> Meshy AI typically takes 30-60 seconds to generate a high-quality 3D model.
              The more images provided, the better the result.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-start space-x-3">
              <CheckIcon className="h-6 w-6 text-green-600 mt-1" />
              <div>
                <h3 className="text-lg font-medium text-green-900">3D Model Generated Successfully!</h3>
                <p className="mt-1 text-green-700">
                  Your model is ready for review and optimization.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Generation Details</h3>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Task ID</dt>
                <dd className="mt-1 text-sm text-gray-900">{model3D?.meshyTaskId}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Generation Time</dt>
                <dd className="mt-1 text-sm text-gray-900">{model3D?.generationTime} seconds</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Polygon Count</dt>
                <dd className="mt-1 text-sm text-gray-900">~15,000 (original)</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">API Cost</dt>
                <dd className="mt-1 text-sm text-gray-900">${model3D?.cost.toFixed(2)}</dd>
              </div>
            </dl>
          </div>

          <div className="bg-gray-100 rounded-lg p-4 flex items-center justify-center h-64">
            <div className="text-center">
              <CubeIcon className="h-16 w-16 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">3D Model Preview</p>
              <p className="text-sm text-gray-500 mt-1">Model viewer will be shown in next step</p>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-between">
        <button
          onClick={onBack}
          disabled={isGenerating}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Back
        </button>
        <button
          onClick={handleContinue}
          disabled={isGenerating}
          className="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? 'Generating Model...' : 'View 3D Model'}
        </button>
      </div>
    </div>
  );
};

export default ModelGeneration;
