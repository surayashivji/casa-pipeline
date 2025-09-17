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

  // Get available model formats
  const getAvailableFormats = () => {
    if (!primaryModel?.model_urls) return [];
    
    const formats = [];
    const modelUrls = primaryModel.model_urls;
    
    if (modelUrls.glb) formats.push({ type: 'GLB', url: modelUrls.glb, description: 'Binary glTF' });
    if (modelUrls.fbx) formats.push({ type: 'FBX', url: modelUrls.fbx, description: 'Autodesk FBX' });
    if (modelUrls.usdz) formats.push({ type: 'USDZ', url: modelUrls.usdz, description: 'Universal Scene' });
    if (modelUrls.obj) formats.push({ type: 'OBJ', url: modelUrls.obj, description: 'Wavefront OBJ' });
    if (modelUrls.mtl) formats.push({ type: 'MTL', url: modelUrls.mtl, description: 'Material file' });
    
    return formats;
  };

  const availableFormats = getAvailableFormats();

  return (
    <div className="w-48 p-4">
      <div className="text-xs font-medium text-gray-700 mb-2">
        3D Model
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
              </>
            ) : modelStatus.status === 'processing' ? (
              <div className="text-yellow-600">Generating 3D model...</div>
            ) : modelStatus.status === 'failed' ? (
              <div className="text-red-600">Generation failed</div>
            ) : (
              <div className="text-gray-500">Status unknown</div>
            )}
          </div>
          
          {/* Download Links */}
          {modelStatus.status === 'completed' && availableFormats.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {availableFormats.map((format, index) => (
                <a
                  key={index}
                  href={format.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:text-blue-800 hover:underline"
                  title={`Download ${format.type} - ${format.description}`}
                >
                  {format.type}
                </a>
              ))}
            </div>
          )}
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
