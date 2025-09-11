import { useState, useEffect } from 'react';
import { generateProcessedImage } from '../../../data/mockProcessingStates';

const BackgroundRemoval = ({ data, onNext, onBack }) => {
  const [isProcessing, setIsProcessing] = useState(true);
  const [processedImages, setProcessedImages] = useState([]);
  const [currentProcessingIndex, setCurrentProcessingIndex] = useState(0);

  useEffect(() => {
    // Simulate processing each image
    const processImages = async () => {
      const processed = [];
      
      for (let i = 0; i < data.selectedImages.length; i++) {
        setCurrentProcessingIndex(i);
        await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate processing time
        processed.push(generateProcessedImage(data.selectedImages[i]));
      }
      
      setProcessedImages(processed);
      setIsProcessing(false);
    };

    processImages();
  }, [data.selectedImages]);

  const handleContinue = () => {
    onNext({ processedImages });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Background Removal</h2>
        <p className="mt-2 text-gray-600">
          Removing backgrounds from selected images using AI
        </p>
      </div>

      {isProcessing ? (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-md p-6">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              <div>
                <p className="text-blue-900 font-medium">
                  Processing image {currentProcessingIndex + 1} of {data.selectedImages.length}
                </p>
                <p className="text-blue-700 text-sm mt-1">
                  Removing background and creating transparency...
                </p>
              </div>
            </div>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-indigo-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${((currentProcessingIndex + 1) / data.selectedImages.length) * 100}%` }}
            />
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-6">
            {processedImages.map((image, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Original</p>
                    <img
                      src={image.original}
                      alt={`Original ${index + 1}`}
                      className="w-full h-64 object-cover rounded-md border border-gray-200"
                    />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Background Removed</p>
                    <div className="relative">
                      <div className="absolute inset-0 bg-checkered rounded-md"></div>
                      <img
                        src={image.original}
                        alt={`Processed ${index + 1}`}
                        className="relative w-full h-64 object-cover rounded-md"
                        style={{ opacity: 0.9 }}
                      />
                    </div>
                  </div>
                </div>
                <div className="mt-3 flex justify-between text-sm text-gray-600">
                  <span>Processing time: {image.processingTime}s</span>
                  <span>File size: {image.fileSize}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <p className="text-green-800">
              ✓ All images processed successfully. Backgrounds removed with high quality.
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
          disabled={isProcessing}
          className="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isProcessing ? 'Processing...' : 'Continue to Approval'}
        </button>
      </div>

      <style jsx>{`
        .bg-checkered {
          background-image: linear-gradient(45deg, #e5e7eb 25%, transparent 25%),
            linear-gradient(-45deg, #e5e7eb 25%, transparent 25%),
            linear-gradient(45deg, transparent 75%, #e5e7eb 75%),
            linear-gradient(-45deg, transparent 75%, #e5e7eb 75%);
          background-size: 20px 20px;
          background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
        }
      `}</style>
    </div>
  );
};

export default BackgroundRemoval;
