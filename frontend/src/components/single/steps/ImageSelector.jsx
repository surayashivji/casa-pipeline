import { useState } from 'react';
import { CheckIcon } from '@heroicons/react/24/solid';

const ImageSelector = ({ data, onNext, onBack }) => {
  const [selectedImages, setSelectedImages] = useState(data.selectedImages || (data.images && data.images.length > 0 ? [data.images[0]] : []));
  const product = data.product;
  const images = data.images || [];

  const toggleImage = (image) => {
    setSelectedImages(prev => {
      if (prev.includes(image)) {
        return prev.filter(img => img !== image);
      }
      return [...prev, image];
    });
  };

  const selectAll = () => {
    setSelectedImages(images);
  };

  const deselectAll = () => {
    setSelectedImages([]);
  };

  const handleContinue = () => {
    if (selectedImages.length === 0) {
      alert('Please select at least one image');
      return;
    }
    onNext({ selectedImages });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900">Select Images for Processing</h2>
        <p className="mt-2 text-gray-600">
          Choose which product images to use for background removal (maximum 4 recommended)
        </p>
      </div>

      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-600">
          {selectedImages.length} of {images.length} images selected
        </div>
        <div className="space-x-2">
          <button
            onClick={selectAll}
            className="text-sm text-primary-600 hover:text-primary-500"
          >
            Select All
          </button>
          <button
            onClick={deselectAll}
            className="text-sm text-gray-600 hover:text-gray-500"
          >
            Clear Selection
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {images.map((image, index) => {
          const isSelected = selectedImages.includes(image);
          return (
            <div
              key={index}
              onClick={() => toggleImage(image)}
              className={`
                relative cursor-pointer rounded-lg overflow-hidden border-2 transition-all
                ${isSelected ? 'border-primary-500 shadow-lg' : 'border-gray-200 hover:border-gray-300'}
              `}
            >
              <div className="w-full h-48 bg-gray-50 flex items-center justify-center overflow-hidden">
                <img
                  src={image}
                  alt={`Product view ${index + 1}`}
                  className="max-w-full max-h-full object-contain"
                />
              </div>
              {isSelected && (
                <div className="absolute top-2 right-2 bg-primary-500 rounded-full p-1">
                  <CheckIcon className="h-5 w-5 text-white" />
                </div>
              )}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent p-2">
                <p className="text-white text-sm">View {index + 1}</p>
              </div>
            </div>
          );
        })}
      </div>

      {selectedImages.length > 4 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <p className="text-sm text-yellow-800">
            <strong>Note:</strong> You've selected {selectedImages.length} images. 
            Using more than 4 images may increase processing time without improving model quality.
          </p>
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
          disabled={selectedImages.length === 0}
          className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continue with {selectedImages.length} Image{selectedImages.length !== 1 ? 's' : ''}
        </button>
      </div>
    </div>
  );
};

export default ImageSelector;
