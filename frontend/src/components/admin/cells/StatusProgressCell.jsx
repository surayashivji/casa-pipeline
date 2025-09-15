const StatusProgressCell = ({ product }) => {
  // Ensure stages is always an array
  const stages = Array.isArray(product?.stages) ? product.stages : [];
  const completedStages = stages.filter(s => s?.status === 'completed');
  const failedStages = stages.filter(s => s?.status === 'failed');
  const processingStages = stages.filter(s => s?.status === 'processing');
  
  const getOverallStatus = () => {
    if (failedStages.length > 0) {
      return { 
        status: 'failed', 
        text: 'Failed', 
        color: 'red', 
        icon: '❌',
        failedStage: failedStages[0].stage_name
      };
    }
    if (processingStages.length > 0) {
      return { 
        status: 'processing', 
        text: 'Processing', 
        color: 'blue', 
        icon: '🔄',
        currentStage: processingStages[0].stage_name
      };
    }
    if (completedStages.length === stages.length && stages.length > 0) {
      return { 
        status: 'completed', 
        text: 'Completed', 
        color: 'green', 
        icon: '✅'
      };
    }
    return { 
      status: 'pending', 
      text: 'Pending', 
      color: 'yellow', 
      icon: '⏸️'
    };
  };

  const statusInfo = getOverallStatus();

  return (
    <div className="w-40 p-4">
      <div className="space-y-2">
        {/* Overall Status */}
        <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-${statusInfo.color}-100 text-${statusInfo.color}-800`}>
          <span className="mr-1">{statusInfo.icon}</span>
          {statusInfo.text}
        </div>
        
        {/* Failed Stage */}
        {statusInfo.failedStage && (
          <div className="text-xs text-red-600">
            Failed: {statusInfo.failedStage}
          </div>
        )}
        
        {/* Current Stage */}
        {statusInfo.currentStage && (
          <div className="text-xs text-blue-600">
            Processing: {statusInfo.currentStage}
          </div>
        )}
        
        {/* Progress Bar */}
        {stages.length > 0 && (
          <div className="space-y-1">
            <div className="flex justify-between text-xs text-gray-600">
              <span>Progress</span>
              <span>{completedStages.length}/{stages.length}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div 
                className={`h-1.5 rounded-full bg-${statusInfo.color}-500`}
                style={{ width: `${(completedStages.length / stages.length) * 100}%` }}
              ></div>
            </div>
          </div>
        )}
        
        {/* Cost */}
        <div className="text-xs text-gray-500">
          ${product.total_cost_usd?.toFixed(2) || '0.00'}
        </div>
      </div>
    </div>
  );
};

export default StatusProgressCell;
