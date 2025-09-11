const LoadingSpinner = ({ size = 'medium', color = 'indigo' }) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8',
    large: 'h-12 w-12'
  };

  return (
    <div className="flex justify-center items-center">
      <div className={`animate-spin rounded-full ${sizeClasses[size]} border-b-2 border-${color}-600`}></div>
    </div>
  );
};

export default LoadingSpinner;
