import { useState, useEffect, useRef } from 'react';
import { removeBackgrounds } from '../../../shared/services/apiService';

const BackgroundRemoval = ({ data, onNext, onBack }) => {
  const [isProcessing, setIsProcessing] = useState(true);
  const [processedImages, setProcessedImages] = useState([]);
  const hasProcessed = useRef(false);

  useEffect(() => {
    // Check if we have valid data
    if (!data.product?.id || !data.selectedImages || data.selectedImages.length === 0) {
      return;
    }
    
    // Prevent duplicate processing
    if (hasProcessed.current) {
      return;
    }
    
    const processImages = async () => {
      try {
        hasProcessed.current = true;
        
        const apiResponse = await removeBackgrounds(
          data.product.id,
          data.selectedImages // image URLs
        );
        
        // Adapt API response to component format
        const results = apiResponse.processed_images.map((img, index) => {
          // Construct full URL for processed image
          let processedUrl = img.processed_url;
          if (processedUrl && processedUrl.startsWith('/static/')) {
            processedUrl = `http://localhost:8000${processedUrl}`;
          }
          
          return {
            original: data.selectedImages[index],
            processed: processedUrl || `https://example.com/processed-${index}.jpg`,
            mask: img.mask_url || `https://example.com/mask-${index}.png`,
            qualityScore: img.quality_score,
            autoApproved: img.auto_approved
          };
        });
        
        setProcessedImages(results);
        setIsProcessing(false);
      } catch (error) {
        console.error('Background removal failed:', error);
        setIsProcessing(false);
      }
    };

    processImages();
  }, [data.product?.id]); // Only depend on product ID, not selectedImages

  const handleContinue = () => {
    onNext({ 
      processedImages,
      backgroundRemoval: {
        status: 'complete',
        data: {
          processedImages,
          processedImage: processedImages[0]?.processed,
          maskImage: processedImages[0]?.mask
        }
      }
    });
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
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin h-12 w-12 border-4 border-primary-600 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-600 mb-2">Processing images...</p>
            <p className="text-sm text-gray-500">
              This may take a few moments
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            {processedImages.map((result, index) => (
              <div key={index} className="space-y-2">
                <h3 className="text-sm font-medium text-gray-700">
                  Image {index + 1}
                </h3>
                
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Original</p>
                    <div className="w-full h-32 bg-gray-50 rounded border border-gray-200 flex items-center justify-center overflow-hidden">
                      <img 
                        src={result.original}
                        alt={`Original ${index + 1}`}
                        className="max-w-full max-h-full object-contain"
                      />
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Background Removed</p>
                    <div className="w-full h-32 bg-checkered rounded border border-gray-200 flex items-center justify-center">
                      <img 
                        src={result.processed}
                        alt={`Processed ${index + 1}`}
                        className="max-w-full max-h-full object-contain"
                      />
                    </div>
                    {result.qualityScore && (
                      <div className="mt-1 text-xs text-gray-600">
                        Quality: {(result.qualityScore * 100).toFixed(0)}%
                        {result.autoApproved && (
                          <span className="ml-2 text-green-600 font-medium">✓ Auto-approved</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <svg className="h-5 w-5 text-green-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="font-medium text-green-900">Background removal complete!</p>
                <p className="text-sm text-green-700 mt-1">
                  {processedImages.length} image{processedImages.length !== 1 ? 's' : ''} processed successfully
                </p>
              </div>
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
              Continue to Approval
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default BackgroundRemoval;