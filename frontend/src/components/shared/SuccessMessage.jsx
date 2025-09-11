import { CheckCircleIcon } from '@heroicons/react/24/solid';

const SuccessMessage = ({ title, message }) => {
  return (
    <div className="bg-green-50 border border-green-200 rounded-md p-4">
      <div className="flex">
        <div className="flex-shrink-0">
          <CheckCircleIcon className="h-5 w-5 text-green-400" />
        </div>
        <div className="ml-3">
          {title && <h3 className="text-sm font-medium text-green-800">{title}</h3>}
          <p className="text-sm text-green-700">{message}</p>
        </div>
      </div>
    </div>
  );
};

export default SuccessMessage;
