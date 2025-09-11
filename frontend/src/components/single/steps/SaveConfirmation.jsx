import { useState } from 'react';
import { CheckCircleIcon } from '@heroicons/react/24/solid';

const SaveConfirmation = ({ data, onNext, onBack, isLastStep }) => {
  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    
    // Simulate saving to database
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsSaving(false);
    setIsSaved(true);
  };

  const handleNewProduct = () => {
    // Reset the pipeline
    window.location.reload();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Save to Database</h2>
        <p className="mt-2 text-gray-600">
          Review the final details and save your 3D model to the database
        </p>
      </div>

      {!isSaved ? (
        <>
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Summary</h3>
            
            <dl className="space-y-3">
              <div className="flex justify-between">
                <dt className="text-gray-600">Product:</dt>
                <dd className="text-gray-900 font-medium">{data.product.name}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">URL:</dt>
                <dd className="text-gray-900 text-sm truncate max-w-xs">{data.url}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Images Processed:</dt>
                <dd className="text-gray-900">{data.approvedImages.length}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">3D Model Quality:</dt>
                <dd className="text-gray-900 capitalize">{data.selectedLOD}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Total Processing Time:</dt>
                <dd className="text-gray-900">~2 minutes</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Estimated Cost:</dt>
                <dd className="text-gray-900">$0.50</dd>
              </div>
            </dl>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <p className="text-sm text-yellow-800">
              <strong>Note:</strong> Once saved, the model will be available in your iOS app. 
              You can process additional LOD versions later if needed.
            </p>
          </div>

          <div className="flex justify-between">
            <button
              onClick={onBack}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Back
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSaving ? (
                <>
                  <span className="animate-spin inline-block mr-2">⏳</span>
                  Saving to Database...
                </>
              ) : (
                'Save to Database'
              )}
            </button>
          </div>
        </>
      ) : (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-8">
            <div className="flex flex-col items-center text-center">
              <CheckCircleIcon className="h-16 w-16 text-green-600 mb-4" />
              <h3 className="text-2xl font-bold text-green-900 mb-2">Successfully Saved!</h3>
              <p className="text-green-700">
                The 3D model for {data.product.name} has been saved to the database 
                and is now available in your iOS app.
              </p>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-6">
            <h4 className="font-medium text-gray-900 mb-3">Database Record Created:</h4>
            <code className="block bg-gray-800 text-green-400 p-4 rounded-md text-sm">
              {JSON.stringify({
                id: 'prod_' + Math.random().toString(36).substr(2, 9),
                product_name: data.product.name,
                model_url: 'https://storage.app.com/models/' + data.product.id + '.glb',
                lod_level: data.selectedLOD,
                created_at: new Date().toISOString()
              }, null, 2)}
            </code>
          </div>

          <div className="flex justify-center space-x-4">
            <button
              onClick={handleNewProduct}
              className="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Process Another Product
            </button>
            <button
              onClick={() => window.location.href = '/batch'}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Switch to Batch Mode
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SaveConfirmation;
