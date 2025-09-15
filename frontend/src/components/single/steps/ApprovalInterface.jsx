import { useState } from 'react';
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/solid';

const ApprovalInterface = ({ data, onNext, onBack }) => {
  const [approvedImages, setApprovedImages] = useState(
    data.processedImages.map((img, idx) => ({ ...img, id: idx, approved: true }))
  );

  const toggleApproval = (id) => {
    setApprovedImages(prev =>
      prev.map(img =>
        img.id === id ? { ...img, approved: !img.approved } : img
      )
    );
  };

  const handleContinue = () => {
    const approved = approvedImages.filter(img => img.approved);
    if (approved.length === 0) {
      alert('Please approve at least one image');
      return;
    }
    onNext({ 
      approvedImages: approved,
      processedImages: data.processedImages // Preserve processedImages for next steps
    });
  };

  const approvedCount = approvedImages.filter(img => img.approved).length;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Approve Processed Images</h2>
        <p className="mt-2 text-gray-600">
          Review and approve the background-removed images for 3D generation
        </p>
        <p className="mt-1 text-sm text-gray-500">
          These images have had their backgrounds removed using AI. Select which ones to use for 3D model generation.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {approvedImages.map((image) => (
          <div
            key={image.id}
            className={`
              relative rounded-lg border-2 p-4 transition-all
              ${image.approved ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'}
            `}
          >
            <div className="relative">
              <div className="absolute inset-0 bg-gray-100 rounded-md" style={{
                backgroundImage: `linear-gradient(45deg, #e5e7eb 25%, transparent 25%), linear-gradient(-45deg, #e5e7eb 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #e5e7eb 75%), linear-gradient(-45deg, transparent 75%, #e5e7eb 75%)`,
                backgroundSize: '20px 20px',
                backgroundPosition: '0 0, 0 10px, 10px -10px, -10px 0px'
              }}></div>
              <div className="relative w-full h-48 flex items-center justify-center overflow-hidden rounded-md">
                <img
                  src={image.processed}
                  alt={`Processed ${image.id + 1}`}
                  className="max-w-full max-h-full object-contain"
                  style={{ opacity: 0.9 }}
                />
              </div>
            </div>

            <div className="mt-4 flex justify-between items-center">
              <div className="text-sm">
                <p className="font-medium text-gray-700">Processed Image {image.id + 1}</p>
                <p className="text-gray-500">Background removed - Ready for 3D generation</p>
                {image.qualityScore && (
                  <p className="text-xs text-gray-400 mt-1">
                    Quality: {(image.qualityScore * 100).toFixed(0)}%
                    {image.autoApproved && (
                      <span className="ml-2 text-green-600 font-medium">✓ Auto-approved</span>
                    )}
                  </p>
                )}
              </div>
              
              <button
                onClick={() => toggleApproval(image.id)}
                className={`
                  px-4 py-2 rounded-md flex items-center space-x-2 transition-all
                  ${image.approved 
                    ? 'bg-green-600 hover:bg-green-700 text-white' 
                    : 'bg-red-600 hover:bg-red-700 text-white'
                  }
                `}
              >
                {image.approved ? (
                  <>
                    <CheckIcon className="h-4 w-4" />
                    <span>Approved</span>
                  </>
                ) : (
                  <>
                    <XMarkIcon className="h-4 w-4" />
                    <span>Rejected</span>
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
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
          disabled={approvedCount === 0}
          className="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Generate 3D Model with {approvedCount} Image{approvedCount !== 1 ? 's' : ''}
        </button>
      </div>

    </div>
  );
};

export default ApprovalInterface;
