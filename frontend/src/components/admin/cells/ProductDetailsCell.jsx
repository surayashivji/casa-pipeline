const ProductDetailsCell = ({ product }) => {
  const handleUrlClick = () => {
    if (product.url) {
      window.open(product.url, '_blank', 'noopener,noreferrer');
    }
  };

  // Get processing status
  const getProcessingStatus = () => {
    const stages = Array.isArray(product?.stages) ? product.stages : [];
    const completedStages = stages.filter(s => s?.status === 'completed');
    const failedStages = stages.filter(s => s?.status === 'failed');
    const processingStages = stages.filter(s => s?.status === 'processing');
    
    if (failedStages.length > 0) {
      return { 
        status: 'Failed', 
        color: 'text-red-600',
        icon: '❌'
      };
    }
    if (processingStages.length > 0) {
      return { 
        status: 'Processing', 
        color: 'text-blue-600',
        icon: '🔄'
      };
    }
    
    // Complete if all 5 database stages are completed
    if (completedStages.length >= 5) {
      return { 
        status: 'Complete', 
        color: 'text-green-600',
        icon: '✅'
      };
    }
    
    // Incomplete if some stages are completed but not all 5
    if (completedStages.length > 0) {
      return { 
        status: 'Incomplete', 
        color: 'text-yellow-600',
        icon: '⚠️'
      };
    }
    
    return { 
      status: 'Pending', 
      color: 'text-yellow-600',
      icon: '⏸️'
    };
  };

  const statusInfo = getProcessingStatus();

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
              className="text-blue-600 hover:text-blue-800 hover:underline break-all text-left block leading-tight"
              title={`Click to open: ${product.url}`}
            >
              {product.url}
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
        
        {/* Processing Status */}
        <div className="mt-2 pt-2 border-t border-gray-200">
          <span className="text-gray-500">Status: </span>
          <span className={`${statusInfo.color} font-medium flex items-center gap-1`}>
            <span>{statusInfo.icon}</span>
            {statusInfo.status}
          </span>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailsCell;
