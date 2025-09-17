const TextureURLCell = ({ product }) => {
  const models = Array.isArray(product?.models_3d) ? product.models_3d : [];
  // Since is_primary field doesn't exist, just use the first model with a texture URL
  const primaryModel = models.find(m => m?.base_texture_url) || models[0];
  
  
  // Helper function to construct full URL
  const getImageUrl = (imageUrl) => {
    if (!imageUrl) return '';
    if (imageUrl.startsWith('/static/')) {
      return `http://localhost:8000${imageUrl}`;
    }
    return imageUrl;
  };

  if (!primaryModel?.base_texture_url) {
    return (
      <div className="w-32 p-4">
        <div className="text-sm text-gray-500">No Texture</div>
      </div>
    );
  }

  return (
    <div className="w-32 p-4">
      <a 
        href={primaryModel.base_texture_url} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-xs font-medium text-blue-600 hover:text-blue-800 hover:underline mb-2 block"
        title={`Download texture: ${primaryModel.base_texture_url}`}
      >
        Texture
      </a>
      
      {/* Texture Preview */}
      <div className="w-24 h-24 bg-gray-100 rounded border border-gray-200 flex items-center justify-center overflow-hidden">
        <img 
          src={getImageUrl(primaryModel.base_texture_url)} 
          alt="Texture Preview"
          className="max-w-full max-h-full object-contain"
          onError={(e) => {
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'flex';
          }}
        />
        <div className="hidden w-full h-full items-center justify-center text-gray-400 text-xs">
          Texture
        </div>
      </div>
    </div>
  );
};

export default TextureURLCell;
