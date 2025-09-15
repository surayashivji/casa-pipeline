const ProductDetailsCell = ({ product }) => {
  const handleUrlClick = () => {
    if (product.url) {
      window.open(product.url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className="w-48 p-4">
      <div className="space-y-1 text-xs">
        {/* Product ID */}
        <div className="mb-2">
          <span className="text-gray-500">ID: </span>
          <span className="text-gray-900 font-mono text-xs" title={product.id || 'N/A'}>
            {product.id ? product.id.slice(-12) : 'N/A'}
          </span>
        </div>

        {/* Article Number */}
        <div className="mb-2">
          <span className="text-gray-500">Article: </span>
          <span className="text-gray-900 text-xs">
            {product.ikea_item_number || product.retailer_id || 'N/A'}
          </span>
        </div>

        {/* Price */}
        <div className="mb-2">
          <span className="text-gray-500">Price: </span>
          <span className="text-gray-900 font-semibold">
            {product.price ? `$${product.price.toFixed(2)}` : 'N/A'}
          </span>
        </div>

        {/* URL */}
        <div className="mb-2">
          <span className="text-gray-500">URL: </span>
          {product.url ? (
            <button
              onClick={handleUrlClick}
              className="text-blue-600 hover:text-blue-800 hover:underline truncate max-w-full block"
              title={`Click to open: ${product.url}`}
            >
              {product.url.length > 30 ? `${product.url.slice(0, 30)}...` : product.url}
            </button>
          ) : (
            <span className="text-gray-400">N/A</span>
          )}
        </div>
        
        {/* Dimensions */}
        {product.width_inches && product.height_inches && product.depth_inches ? (
          <div>
            <span className="text-gray-500">Size: </span>
            <span className="text-gray-900">
              {product.width_inches}" × {product.height_inches}" × {product.depth_inches}"
            </span>
          </div>
        ) : (
          <div>
            <span className="text-gray-500">Size: </span>
            <span className="text-gray-400">N/A</span>
          </div>
        )}
        
        {/* Category */}
        <div>
          <span className="text-gray-500">Category: </span>
          <span className="text-gray-900 capitalize">{product.category || 'N/A'}</span>
        </div>
        
        {/* Room Type */}
        <div>
          <span className="text-gray-500">Room: </span>
          <span className="text-gray-900 capitalize">{product.room_type?.replace('_', ' ') || 'N/A'}</span>
        </div>
        
        {/* Style Tags */}
        {product.style_tags && product.style_tags.length > 0 ? (
          <div>
            <span className="text-gray-500">Style: </span>
            <span className="text-gray-900">{product.style_tags.join(', ')}</span>
          </div>
        ) : (
          <div>
            <span className="text-gray-500">Style: </span>
            <span className="text-gray-400">N/A</span>
          </div>
        )}
        
        {/* Assembly Required */}
        <div>
          <span className="text-gray-500">Assembly: </span>
          <span className="text-gray-900">{product.assembly_required ? 'Yes' : 'No'}</span>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailsCell;
