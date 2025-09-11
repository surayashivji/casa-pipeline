import { useState } from 'react';
import CategoryInput from './CategoryInput';
import ProductGrid from './ProductGrid';
import ProcessingQueue from './ProcessingQueue';
import ResultsDashboard from './ResultsDashboard';

const BatchPipeline = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [pipelineData, setPipelineData] = useState({});

  const steps = [
    { name: 'Category Input', component: CategoryInput },
    { name: 'Product Selection', component: ProductGrid },
    { name: 'Processing Queue', component: ProcessingQueue },
    { name: 'Results Dashboard', component: ResultsDashboard }
  ];

  const handleNext = (data) => {
    setPipelineData(prev => ({ ...prev, ...data }));
    setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
  };

  const handleBack = () => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  };

  const handleNewBatch = () => {
    setCurrentStep(0);
    setPipelineData({});
  };

  const CurrentComponent = steps[currentStep].component;

  return (
    <div className="max-w-6xl mx-auto">
      {/* Progress Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-gray-900">Batch Processing Pipeline</h1>
          <div className="text-sm text-gray-500">
            Step {currentStep + 1} of {steps.length}
          </div>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-purple-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          />
        </div>
        
        <div className="flex justify-between mt-2">
          {steps.map((step, index) => (
            <div
              key={index}
              className={`text-xs font-medium ${
                index <= currentStep ? 'text-purple-600' : 'text-gray-400'
              }`}
            >
              {step.name}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <CurrentComponent
          data={pipelineData}
          onNext={handleNext}
          onBack={currentStep > 0 ? handleBack : undefined}
          onComplete={currentStep === 2 ? () => handleNext({}) : undefined}
          onNewBatch={handleNewBatch}
          products={pipelineData.selectedProducts || []}
          batchJob={pipelineData.batchJob}
        />
      </div>

      {/* Step Navigation Info */}
      {currentStep > 0 && currentStep < 3 && (
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-500">
            Use the Back button to return to the previous step
          </p>
        </div>
      )}
    </div>
  );
};

export default BatchPipeline;
