const NameCell = ({ product }) => {
  const handleNameClick = () => {
    if (product.url) {
      window.open(product.url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className="w-64 p-4">
      <div 
        className={`font-semibold text-sm truncate cursor-pointer transition-colors duration-200 ${
          product.url 
            ? 'text-blue-600 hover:text-blue-800 hover:underline' 
            : 'text-gray-900'
        }`}
        onClick={handleNameClick}
        title={product.url ? `Click to open: ${product.url}` : 'No URL available'}
      >
        {product.name || 'N/A'}
      </div>
      <div className="text-xs text-gray-500 mt-1">
        {product.ikea_item_number || product.retailer_id || 'No ID'}
      </div>
    </div>
  );
};

export default NameCell;
