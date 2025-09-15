const PriceCell = ({ product }) => {
  return (
    <div className="w-24 p-4">
      <div className="text-sm font-medium text-gray-900">
        {product.price ? `$${product.price}` : 'N/A'}
      </div>
    </div>
  );
};

export default PriceCell;
