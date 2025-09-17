const StatusProgressCell = ({ product }) => {
  // Define the expected pipeline stages in order
  const EXPECTED_STAGES = [
    'scraping',
    'image_selection', 
    'background_removal',
    'image_approval',
    '3d_generation',
    'optimization',
    'saving'
  ];
  
  // Ensure stages is always an array
  const stages = Array.isArray(product?.stages) ? product.stages : [];
  const completedStages = stages.filter(s => s?.status === 'completed');
  const failedStages = stages.filter(s => s?.status === 'failed');
  const processingStages = stages.filter(s => s?.status === 'processing');
  
  // Calculate progress against expected total stages
  const totalExpectedStages = EXPECTED_STAGES.length;
  const completedExpectedStages = EXPECTED_STAGES.filter(stageName => 
    stages.some(stage => stage.stage_name === stageName && stage.status === 'completed')
  ).length;
  
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

  const getStageIcon = (stage) => {
    switch (stage.status) {
      case 'completed': return '✅';
      case 'processing': return '🔄';
      case 'failed': return '❌';
      default: return '⏸️';
    }
  };

  const getStageColor = (stage) => {
    switch (stage.status) {
      case 'completed': return 'text-gray-900';
      case 'processing': return 'text-blue-600';
      case 'failed': return 'text-red-600';
      default: return 'text-gray-500';
    }
  };

  const formatStageName = (stageName) => {
    return stageName
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="w-48 p-4">
      <div className="space-y-2">
        {/* Individual Steps - Show only stages that exist in database */}
        {stages.length > 0 && (
          <div className="space-y-1">
            {stages
              .sort((a, b) => a.stage_order - b.stage_order)
              .map((stage, index) => (
                <div key={stage.id || index} className="flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-1">
                    <span className="text-xs">{getStageIcon(stage)}</span>
                    <span className={`${getStageColor(stage)} truncate`} title={formatStageName(stage.stage_name)}>
                      {formatStageName(stage.stage_name)}
                    </span>
                  </div>
                  {stage.status === 'processing' && (
                    <div className="animate-pulse text-blue-500 text-xs">●</div>
                  )}
                </div>
              ))}
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
