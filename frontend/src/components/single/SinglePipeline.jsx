import { useState } from 'react';
import { CheckIcon } from '@heroicons/react/24/solid';
import URLInput from './steps/URLInput';
import ProductReview from './steps/ProductReview';
import ImageSelector from './steps/ImageSelector';
import BackgroundRemoval from './steps/BackgroundRemoval';
import ApprovalInterface from './steps/ApprovalInterface';
import ModelGeneration from './steps/ModelGeneration';
import ModelViewer from './steps/ModelViewer';
import SaveConfirmation from './steps/SaveConfirmation';

const SinglePipeline = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [pipelineData, setPipelineData] = useState({});

  const steps = [
    { name: 'URL Input', component: URLInput },
    { name: 'Product Review', component: ProductReview },
    { name: 'Image Selection', component: ImageSelector },
    { name: 'Background Removal', component: BackgroundRemoval },
    { name: 'Image Approval', component: ApprovalInterface },
    { name: '3D Generation', component: ModelGeneration },
    { name: 'Model Viewer', component: ModelViewer },
    { name: 'Save Confirmation', component: SaveConfirmation }
  ];

  const handleNext = (data) => {
    setPipelineData(prev => ({ ...prev, ...data }));
    setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
  };

  const handleBack = () => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  };

  const CurrentComponent = steps[currentStep].component;

  return (
    <div className="max-w-6xl mx-auto animate-fade-in">
      {/* Progress Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            Single Product Pipeline
          </h1>
          <div className="px-4 py-2 bg-gray-100 rounded-full text-sm font-medium text-gray-700">
            Step {currentStep + 1} of {steps.length}
          </div>
        </div>
        
        {/* Enhanced Step Indicators */}
        <div className="relative">
          {/* Progress Line */}
          <div className="absolute top-5 left-0 w-full h-0.5 bg-gray-200">
            <div 
              className="h-full bg-gradient-to-r from-primary-500 to-primary-600 transition-all duration-700 ease-out"
              style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
            />
          </div>
          
          {/* Step Indicators */}
          <div className="relative flex justify-between">
            {steps.map((step, index) => (
              <div key={index} className="flex flex-col items-center">
                <div
                  className={`
                    step-indicator z-10 transition-all duration-300
                    ${index === currentStep ? 'step-indicator active scale-110' : 
                      index < currentStep ? 'step-indicator completed' : 
                      'step-indicator inactive'}
                  `}
                >
                  {index < currentStep ? (
                    <CheckIcon className="w-5 h-5" />
                  ) : (
                    <span className="text-sm">{index + 1}</span>
                  )}
                </div>
                <span className={`
                  mt-2 text-xs font-medium transition-colors duration-300
                  ${index === currentStep ? 'text-primary-700' : 
                    index < currentStep ? 'text-green-700' : 
                    'text-gray-400'}
                `}>
                  {step.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Step Content */}
      <div className="card p-8 animate-slide-up">
        <CurrentComponent
          data={pipelineData}
          onNext={handleNext}
          onBack={currentStep > 0 ? handleBack : undefined}
          isLastStep={currentStep === steps.length - 1}
        />
      </div>

      {/* Step Navigation Info */}
      {currentStep > 0 && (
        <div className="mt-6 text-center animate-fade-in">
          <p className="text-sm text-gray-500">
            Use the Back button to return to the previous step
          </p>
        </div>
      )}
    </div>
  );
};

export default SinglePipeline;
