const URLCell = ({ product }) => {
  if (!product.url) {
    return (
      <div className="w-64 p-4">
        <div className="text-sm text-gray-500">N/A</div>
      </div>
    );
  }

  return (
    <div className="w-64 p-4">
      <a 
        href={product.url} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-xs text-primary-600 hover:text-primary-700 truncate block"
      >
        {product.url}
      </a>
      <div className="text-xs text-gray-500 mt-1">
        {new URL(product.url).hostname}
      </div>
    </div>
  );
};

export default URLCell;
