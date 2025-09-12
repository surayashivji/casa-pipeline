import { useState } from 'react';
import Layout from './components/layout/Layout';
import ModeSelector from './components/layout/ModeSelector';
import SinglePipeline from './components/single/SinglePipeline';
import BatchPipeline from './components/batch/BatchPipeline';
import ErrorBoundary from './shared/components/ErrorBoundary';
import './App.css';

function App() {
  const [mode, setMode] = useState('single'); // 'single' or 'batch'

  return (
    <ErrorBoundary>
      <Layout>
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
    </ErrorBoundary>
  );
}

export default App;
