const Model3DCell = ({ product }) => {
  const models = Array.isArray(product?.models_3d) ? product.models_3d : [];
  const primaryModel = models.find(m => m?.is_primary) || models[0];
  
  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };
  
  // Helper function to construct full URL
  const getImageUrl = (imageUrl) => {
    if (!imageUrl) return '';
    if (imageUrl.startsWith('/static/')) {
      return `http://localhost:8000${imageUrl}`;
    }
    return imageUrl;
  };
  
  // Get model status
  const getModelStatus = () => {
    if (!primaryModel) return { status: 'none', icon: '❌', color: 'red' };
    
    switch (primaryModel.status) {
      case 'completed':
        return { status: 'completed', icon: '✅', color: 'green' };
      case 'processing':
        return { status: 'processing', icon: '⏳', color: 'yellow' };
      case 'failed':
        return { status: 'failed', icon: '❌', color: 'red' };
      default:
        return { status: 'unknown', icon: '❓', color: 'gray' };
    }
  };

  const modelStatus = getModelStatus();

  return (
    <div className="w-48 p-4">
      <div className="text-xs font-medium text-gray-700 mb-2 flex items-center gap-2">
        {primaryModel && primaryModel.model_url ? (
          <a 
            href={primaryModel.model_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer"
            title="Download 3D Model"
          >
            3D Model
          </a>
        ) : (
          <span>3D Model</span>
        )}
        {/* <span className={`text-lg ${
          modelStatus.color === 'green' ? 'text-green-600' :
          modelStatus.color === 'yellow' ? 'text-yellow-600' :
          modelStatus.color === 'red' ? 'text-red-600' :
          'text-gray-600'
        }`}>
          {modelStatus.icon}
        </span> */}
      </div>
      
      {primaryModel ? (
        <div className="space-y-2">
          {/* 3D Model Preview */}
          <div className="w-32 h-32 bg-gray-100 rounded border border-gray-200 flex items-center justify-center overflow-hidden">
            {primaryModel.thumbnail_url ? (
              <img 
                src={getImageUrl(primaryModel.thumbnail_url)} 
                alt="3D Model Preview"
                className="max-w-full max-h-full object-contain"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
            ) : null}
            <div className="hidden w-full h-full items-center justify-center text-gray-400 text-xs">
              {modelStatus.status === 'completed' ? '3D Model' : 'Processing...'}
            </div>
          </div>
          
          {/* Model Info */}
          <div className="text-xs text-gray-600">
            {modelStatus.status === 'completed' ? (
              <>
                <div>Vertices: {primaryModel.vertices_count?.toLocaleString() || 'N/A'}</div>
                <div>Triangles: {primaryModel.triangles_count?.toLocaleString() || 'N/A'}</div>
                <div>Size: {formatFileSize(primaryModel.file_size_bytes)}</div>
                <div>Format: {primaryModel.format?.toUpperCase() || 'GLB'}</div>
              </>
            ) : modelStatus.status === 'processing' ? (
              <div className="text-yellow-600">Generating 3D model...</div>
            ) : modelStatus.status === 'failed' ? (
              <div className="text-red-600">Generation failed</div>
            ) : (
              <div className="text-gray-500">Status unknown</div>
            )}
          </div>
        </div>
      ) : (
        <div className="w-32 h-32 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center">
          <div className="text-gray-400 text-xs text-center">
            No<br/>3D Model
          </div>
        </div>
      )}
    </div>
  );
};

export default Model3DCell;
