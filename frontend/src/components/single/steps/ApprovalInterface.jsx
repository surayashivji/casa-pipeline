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
    onNext({ approvedImages: approved });
  };

  const approvedCount = approvedImages.filter(img => img.approved).length;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Approve Processed Images</h2>
        <p className="mt-2 text-gray-600">
          Review and approve the processed images for 3D generation
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
              <div className="absolute inset-0 bg-checkered rounded-md"></div>
              <img
                src={image.original}
                alt={`Processed ${image.id + 1}`}
                className="relative w-full h-48 object-cover rounded-md"
                style={{ opacity: 0.9 }}
              />
            </div>

            <div className="mt-4 flex justify-between items-center">
              <div className="text-sm">
                <p className="font-medium text-gray-700">Image {image.id + 1}</p>
                <p className="text-gray-500">Ready for 3D generation</p>
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

export default ApprovalInterface;
