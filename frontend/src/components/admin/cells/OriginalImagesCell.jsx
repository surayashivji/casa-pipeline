const OriginalImagesCell = ({ product }) => {
  const originalImages = Array.isArray(product?.images) ? product.images.filter(img => img?.image_type === 'original') : [];
  
  return (
    <div className="w-64 p-4">
      <div className="text-xs font-medium text-gray-700 mb-2">
        Original Images ({originalImages.length})
      </div>
      
      {originalImages.length > 0 ? (
        <div className="grid grid-cols-2 gap-2">
          {originalImages.slice(0, 4).map((image, index) => (
            <div key={index} className="w-24 h-24 bg-gray-50 rounded border border-gray-200 flex items-center justify-center overflow-hidden">
              <img 
                src={image.s3_url} 
                alt={`Original ${index + 1}`}
                className="max-w-full max-h-full object-contain"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
              <div className="hidden w-full h-full items-center justify-center text-gray-400 text-xs">
                Error
              </div>
            </div>
          ))}
          {originalImages.length > 4 && (
            <div className="w-24 h-24 bg-gray-100 rounded border border-gray-200 flex items-center justify-center">
              <div className="text-gray-400 text-xs text-center">
                +{originalImages.length - 4}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="w-24 h-24 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center">
          <div className="text-gray-400 text-xs text-center">
            No<br/>Images
          </div>
        </div>
      )}
    </div>
  );
};

export default OriginalImagesCell;
