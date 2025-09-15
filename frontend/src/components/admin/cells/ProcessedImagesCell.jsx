const ProcessedImagesCell = ({ product }) => {
  const processedImages = Array.isArray(product?.images) ? product.images.filter(img => img?.image_type === 'processed') : [];
  
  return (
    <div className="w-64 p-4">
      <div className="text-xs font-medium text-gray-700 mb-2">
        Processed Images ({processedImages.length})
      </div>
      
      {processedImages.length > 0 ? (
        <div className="grid grid-cols-2 gap-2">
          {processedImages.slice(0, 4).map((image, index) => (
            <div key={index} className="w-24 h-24 bg-checkered rounded border border-gray-200 flex items-center justify-center overflow-hidden">
              <img 
                src={image.s3_url} 
                alt={`Processed ${index + 1}`}
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
          {processedImages.length > 4 && (
            <div className="w-24 h-24 bg-gray-100 rounded border border-gray-200 flex items-center justify-center">
              <div className="text-gray-400 text-xs text-center">
                +{processedImages.length - 4}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="w-24 h-24 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center">
          <div className="text-gray-400 text-xs text-center">
            No<br/>Processed
          </div>
        </div>
      )}
    </div>
  );
};

export default ProcessedImagesCell;
