import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import Layout from './components/layout/Layout';
import ModeSelector from './components/layout/ModeSelector';
import SinglePipeline from './components/single/SinglePipeline';
import BatchPipeline from './components/batch/BatchPipeline';
import AdminPipeline from './components/admin/AdminPipeline';
import ErrorBoundary from './shared/components/ErrorBoundary';
import './App.css';

function AppContent() {
  const [mode, setMode] = useState('single'); // 'single' or 'batch'
  const navigate = useNavigate();
  const location = useLocation();

  const isAdminMode = location.pathname === '/admin';

  const handleAdminClick = () => {
    window.open('/admin', '_blank');
  };

  const handleBackToProcessing = () => {
    navigate('/');
  };

  if (isAdminMode) {
    return (
      <Layout showAdminButton={true} onAdminClick={handleBackToProcessing} isAdminMode={true}>
        <AdminPipeline />
      </Layout>
    );
  }

  return (
    <Layout showAdminButton={true} onAdminClick={handleAdminClick}>
      <div className="max-w-7xl mx-auto px-4 py-6">
        <ModeSelector mode={mode} onModeChange={setMode} />
        
        <div className="mt-6">
          {mode === 'single' ? (
            <SinglePipeline />
          ) : (
            <BatchPipeline />
          )}
        </div>
      </div>
    </Layout>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/" element={<AppContent />} />
          <Route path="/admin" element={<AppContent />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
