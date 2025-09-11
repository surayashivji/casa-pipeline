import { XCircleIcon, XMarkIcon } from '@heroicons/react/24/solid';

const ErrorMessage = ({ title, message, onDismiss }) => {
  return (
    <div className="bg-red-50 border border-red-200 rounded-md p-4">
      <div className="flex">
        <div className="flex-shrink-0">
          <XCircleIcon className="h-5 w-5 text-red-400" />
        </div>
        <div className="ml-3 flex-1">
          {title && <h3 className="text-sm font-medium text-red-800">{title}</h3>}
          <p className="text-sm text-red-700">{message}</p>
        </div>
        {onDismiss && (
          <button onClick={onDismiss} className="ml-3 text-red-400 hover:text-red-500">
            <XMarkIcon className="h-5 w-5" />
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;
