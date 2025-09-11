import { ArrowDownTrayIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

const ResultsDashboard = ({ batchJob, onNewBatch }) => {
  // Mock results data
  const results = {
    totalProcessed: 5,
    successful: 4,
    failed: 1,
    totalTime: '2 minutes 34 seconds',
    totalCost: 2.50,
    models: [
      { name: 'EKTORP Sofa', status: 'success', time: '32s', cost: 0.50 },
      { name: 'POÄNG Chair', status: 'success', time: '28s', cost: 0.50 },
      { name: 'LACK Table', status: 'success', time: '25s', cost: 0.50 },
      { name: 'BILLY Bookcase', status: 'success', time: '30s', cost: 0.50 },
      { name: 'FLINTAN Chair', status: 'failed', time: '15s', cost: 0.00, error: 'Insufficient image quality' }
    ]
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Batch Processing Results</h2>
          <p className="mt-1 text-gray-600">
            Summary of your batch processing job
          </p>
        </div>

        <div className="grid grid-cols-4 gap-4">
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-sm font-medium text-green-600">Successful</p>
            <p className="mt-1 text-2xl font-bold text-green-900">{results.successful}</p>
          </div>
          <div className="bg-red-50 rounded-lg p-4">
            <p className="text-sm font-medium text-red-600">Failed</p>
            <p className="mt-1 text-2xl font-bold text-red-900">{results.failed}</p>
          </div>
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-sm font-medium text-blue-600">Total Time</p>
            <p className="mt-1 text-lg font-bold text-blue-900">{results.totalTime}</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <p className="text-sm font-medium text-purple-600">Total Cost</p>
            <p className="mt-1 text-2xl font-bold text-purple-900">${results.totalCost.toFixed(2)}</p>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-3">Processed Products</h3>
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {results.models.map((model, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {model.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {model.status === 'success' ? (
                        <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                          Success
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">
                          Failed
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {model.time}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      ${model.cost.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {model.status === 'success' ? (
                        <button className="text-indigo-600 hover:text-indigo-900">
                          Download
                        </button>
                      ) : (
                        <button className="text-gray-600 hover:text-gray-900">
                          Retry
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="flex justify-between">
          <button
            onClick={onNewBatch}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 flex items-center space-x-2"
          >
            <ArrowPathIcon className="h-5 w-5" />
            <span>New Batch</span>
          </button>
          <div className="space-x-3">
            <button className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
              Export Report
            </button>
            <button className="px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 flex items-center space-x-2">
              <ArrowDownTrayIcon className="h-5 w-5" />
              <span>Download All Models</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsDashboard;
