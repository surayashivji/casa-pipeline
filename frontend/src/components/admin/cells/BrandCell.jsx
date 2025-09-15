const BrandCell = ({ product }) => {
  return (
    <div className="w-24 p-4">
      <div className="text-sm text-gray-900">
        {product.brand || 'N/A'}
      </div>
    </div>
  );
};

export default BrandCell;
