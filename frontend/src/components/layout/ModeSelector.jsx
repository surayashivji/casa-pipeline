import { useState } from 'react';
import { CubeIcon, QueueListIcon } from '@heroicons/react/24/outline';

const ModeSelector = ({ mode, onModeChange }) => {
  const modes = [
    {
      id: 'single',
      name: 'Single Product',
      description: 'Process one product at a time with full control',
      icon: CubeIcon,
      features: [
        'Manual image selection',
        'Step-by-step approval',
        'High-quality processing',
        'Real-time 3D preview'
      ]
    },
    {
      id: 'batch',
      name: 'Batch Processing',
      description: 'Process multiple products automatically',
      icon: QueueListIcon,
      features: [
        'Bulk product processing',
        'Smart defaults',
        'Parallel processing',
        'Results dashboard'
      ]
    }
  ];

  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">
          Choose Processing Mode
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Select how you'd like to process furniture products into 3D models
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
        {modes.map((modeOption) => {
          const Icon = modeOption.icon;
          const isSelected = mode === modeOption.id;
          
          return (
            <div
              key={modeOption.id}
              onClick={() => onModeChange(modeOption.id)}
              className={`
                relative cursor-pointer rounded-xl border-2 p-6 transition-colors duration-200
                ${isSelected 
                  ? 'border-primary-500 bg-primary-50 shadow-md' 
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
                }
              `}
            >
              <div className="flex items-start space-x-3">
                <div className={`
                  flex-shrink-0 p-3 rounded-lg transition-colors duration-200
                  ${isSelected 
                    ? 'bg-primary-100' 
                    : 'bg-gray-100'
                  }
                `}>
                  <Icon className={`h-6 w-6 ${
                    isSelected ? 'text-primary-600' : 'text-gray-600'
                  }`} />
                </div>
                
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {modeOption.name}
                  </h3>
                  <p className={`mt-0.5 text-sm ${
                    isSelected ? 'text-gray-700' : 'text-gray-600'
                  }`}>
                    {modeOption.description}
                  </p>
                  
                  <ul className="mt-3 space-y-1">
                    {modeOption.features.slice(0, 2).map((feature, featureIndex) => (
                      <li 
                        key={featureIndex} 
                        className={`flex items-center text-xs ${
                          isSelected ? 'text-gray-700' : 'text-gray-500'
                        }`}
                      >
                        <div className={`w-1 h-1 rounded-full mr-2 ${
                          isSelected ? 'bg-primary-500' : 'bg-gray-400'
                        }`} />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {isSelected && (
                <div className="absolute top-4 right-4">
                  <div className="w-6 h-6 rounded-full bg-primary-500 flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

    </div>
  );
};

export default ModeSelector;
