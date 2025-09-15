const IDCell = ({ product, index, pagination }) => {
  const rowNumber = ((pagination.page - 1) * pagination.limit) + index + 1;
  
  return (
    <div className="w-16 p-4">
      <div className="text-sm font-mono text-gray-600 text-center">
        {rowNumber}
      </div>
    </div>
  );
};

export default IDCell;
