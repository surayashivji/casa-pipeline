const Model3DCell = ({ product }) => {
  const models = Array.isArray(product?.models_3d) ? product.models_3d : [];
  const primaryModel = models.find(m => m?.is_primary) || models[0];
  
  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };
  
  return (
    <div className="w-48 p-4">
      <div className="text-xs font-medium text-gray-700 mb-2">
        3D Model
      </div>
      
      {primaryModel ? (
        <div className="space-y-2">
          {/* 3D Model Preview */}
          <div className="w-32 h-32 bg-gray-100 rounded border border-gray-200 flex items-center justify-center overflow-hidden">
            {primaryModel.preview_url ? (
              <img 
                src={primaryModel.preview_url} 
                alt="3D Model Preview"
                className="max-w-full max-h-full object-contain"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
            ) : null}
            <div className="hidden w-full h-full items-center justify-center text-gray-400 text-xs">
              3D<br/>Preview
            </div>
          </div>
          
          {/* Model Info */}
          <div className="text-xs text-gray-600">
            <div>Vertices: {primaryModel.vertices_count?.toLocaleString() || 'N/A'}</div>
            <div>Triangles: {primaryModel.triangles_count?.toLocaleString() || 'N/A'}</div>
            <div>Size: {formatFileSize(primaryModel.file_size_bytes)}</div>
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
