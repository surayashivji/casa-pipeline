import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CubeIcon, CogIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

const Layout = ({ children, showAdminButton = false, onAdminClick, isAdminMode = false }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogoClick = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-gray-50 to-primary-50/20">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleLogoClick}
                className="p-2 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl hover:from-primary-600 hover:to-primary-700 transition-all duration-200 cursor-pointer"
                title="Go to main page"
              >
                <CubeIcon className="h-7 w-7 text-white" />
              </button>
              <div>
                <h1 className="text-xl font-bold text-gray-900 tracking-tight">Casa Pipeline</h1>
                <p className="text-sm text-gray-500">3D Model Generation System</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {showAdminButton && (
                <button
                  onClick={onAdminClick}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors duration-200 ${
                    isAdminMode 
                      ? 'bg-gray-100 hover:bg-gray-200 text-gray-700' 
                      : 'bg-primary-600 hover:bg-primary-700 text-white'
                  }`}
                >
                  {isAdminMode ? (
                    <ArrowLeftIcon className="h-5 w-5" />
                  ) : (
                    <CogIcon className="h-5 w-5" />
                  )}
                  <span className="text-sm font-medium">
                    {isAdminMode ? 'Back to Processing' : 'Admin Dashboard'}
                  </span>
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className={`${isAdminMode ? 'w-full' : 'max-w-7xl mx-auto'} py-8 ${isAdminMode ? '' : 'px-4 sm:px-6 lg:px-8'} animate-fade-in`}>
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white/50 backdrop-blur-sm border-t border-gray-100 mt-16">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              © Casa
            </div>
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                <span className="text-gray-600">Development</span>
              </div>
              <div className="text-gray-400">•</div>
              <span className="text-gray-600 font-medium">v1.0.0</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
