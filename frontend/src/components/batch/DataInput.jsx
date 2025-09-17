import { useState, useRef } from 'react';
import { DocumentArrowUpIcon, DocumentArrowDownIcon } from '@heroicons/react/24/outline';

const DataInput = ({ onNext, onBack }) => {
  const [file, setFile] = useState(null);
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState('');
  const [csvData, setCsvData] = useState(null);
  const [validationResults, setValidationResults] = useState(null);
  const fileInputRef = useRef(null);


  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError('');
      validateCsvFile(selectedFile);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const droppedFile = files[0];
      if (droppedFile.type === 'text/csv' || droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
        setError('');
        validateCsvFile(droppedFile);
      } else {
        setError('Please upload a CSV file');
      }
    }
  };

  const validateCsvFile = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setIsValidating(true);
      setError('');

      const response = await fetch('/api/batch/validate-csv-data', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setCsvData(result.data);
        setValidationResults({
          isValid: result.isValid,
          validRows: result.validRows,
          errorCount: result.errorCount,
          errors: result.errors
        });
      } else {
        console.error('Validation failed:', result);
        setError(result.detail || 'Failed to validate CSV file');
        setCsvData(null);
        setValidationResults(null);
      }
    } catch (err) {
      console.error('Validation error:', err);
      setError('Failed to validate CSV file. Please check your connection.');
      setCsvData(null);
      setValidationResults(null);
    } finally {
      setIsValidating(false);
    }
  };


  const handleFileSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a CSV file');
      return;
    }

    if (!csvData || !validationResults?.isValid) {
      setError('Please fix validation errors before proceeding');
      return;
    }

    setIsValidating(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/batch/upload-csv', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        onNext({ 
          csvData: result.data,
          batchId: result.batch_id,
          inputType: 'csv'
        });
      } else {
        setError(result.detail || 'Failed to upload CSV file');
      }
    } catch (err) {
      setError('Failed to upload CSV file. Please check your connection.');
    } finally {
      setIsValidating(false);
    }
  };

  const downloadTemplate = async () => {
    try {
      const response = await fetch('/api/batch/download-template');
      const blob = await response.blob();
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'batch_products_template.csv';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Failed to download template');
    }
  };

  const getValidationStatus = () => {
    if (!validationResults) return null;
    
    if (validationResults.isValid) {
      return (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex items-center">
            <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center mr-3">
              <span className="text-white text-xs">✓</span>
            </div>
            <div>
              <h3 className="text-sm font-medium text-green-900">CSV Valid</h3>
              <p className="text-sm text-green-800">
                {validationResults.validRows} products ready for processing
              </p>
            </div>
          </div>
        </div>
      );
    } else {
      return (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex items-center">
            <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center mr-3">
              <span className="text-white text-xs">✗</span>
            </div>
            <div>
              <h3 className="text-sm font-medium text-red-900">Validation Errors</h3>
              <p className="text-sm text-red-800">
                {validationResults.errorCount} errors found. Please fix them before proceeding.
              </p>
              {validationResults.errors && validationResults.errors.length > 0 && (
                <ul className="mt-2 text-xs text-red-700 space-y-1">
                  {validationResults.errors.slice(0, 3).map((error, index) => (
                    <li key={index}>• {error}</li>
                  ))}
                  {validationResults.errors.length > 3 && (
                    <li>• ... and {validationResults.errors.length - 3} more errors</li>
                  )}
                </ul>
              )}
            </div>
          </div>
        </div>
      );
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Upload Data</h2>
        <p className="mt-2 text-gray-600">
          Upload a CSV file with product data for batch processing.
        </p>
      </div>
      <form onSubmit={handleFileSubmit} className="space-y-4">
          {/* File Upload */}
          <div>
            <label htmlFor="file" className="block text-sm font-medium text-gray-700 mb-2">
              CSV File
            </label>
            <div 
              className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors cursor-pointer"
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="space-y-1 text-center">
                <DocumentArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                <div className="flex text-sm text-gray-600">
                  <label
                    htmlFor="file"
                    className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
                  >
                    <span>Upload a file</span>
                    <input
                      ref={fileInputRef}
                      id="file"
                      name="file"
                      type="file"
                      accept=".csv"
                      className="sr-only"
                      onChange={handleFileChange}
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-gray-500">CSV files only</p>
              </div>
            </div>
            {file && (
              <div className="mt-2">
                <p className="text-sm text-gray-600">
                  Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
                </p>
                {isValidating && (
                  <p className="text-sm text-blue-600 mt-1">
                    Validating CSV file...
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Template Download */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-blue-900">CSV Template</h3>
                <p className="text-sm text-blue-800">
                  Download our CSV template with the correct format and sample data
                </p>
              </div>
              <button
                type="button"
                onClick={downloadTemplate}
                className="ml-4 px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 flex items-center space-x-2"
              >
                <DocumentArrowDownIcon className="h-4 w-4" />
                <span>Download</span>
              </button>
            </div>
          </div>

          {/* Validation Results */}
          {validationResults && getValidationStatus()}


          {error && (
            <p className="text-sm text-red-600">{error}</p>
          )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isValidating || !file || !validationResults?.isValid}
            className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            onClick={() => {
            }}
          >
            {isValidating ? (
              <>
                <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                <span>Processing CSV...</span>
              </>
            ) : (
              <span>Process {csvData?.length || 0} Products</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default DataInput;
