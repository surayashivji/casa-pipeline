import { Suspense, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Environment } from '@react-three/drei';

// 3D Model Component
function Model3D({ url, onLoad, onError }) {
  const { scene } = useGLTF(url);
  
  // Call onLoad when model loads successfully
  if (onLoad) onLoad();

  return <primitive object={scene} scale={1} />;
}

// Error Fallback Component
function ErrorFallback({ onRetry }) {
  return (
    <div className="flex items-center justify-center h-full bg-gray-100 rounded-lg">
      <div className="text-center p-4">
        <div className="text-red-500 text-sm mb-2">Failed to load 3D model</div>
        <button 
          onClick={onRetry}
          className="text-xs text-blue-600 hover:text-blue-800 underline"
        >
          Retry
        </button>
      </div>
    </div>
  );
}

// Loading Component
function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center h-full bg-gray-100 rounded-lg">
      <div className="text-center">
        <div className="animate-spin h-8 w-8 border-2 border-blue-600 border-t-transparent rounded-full mx-auto mb-2"></div>
        <div className="text-sm text-gray-600">Loading 3D model...</div>
      </div>
    </div>
  );
}

// Main 3D Viewer Component
const Model3DViewer = ({ 
  modelUrl, 
  className = "w-full h-96", 
  onLoad, 
  onError,
  showControls = true 
}) => {
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  if (!modelUrl) {
    return (
      <div className={`${className} flex items-center justify-center bg-gray-100 rounded-lg`}>
        <div className="text-gray-500 text-sm">No 3D model available</div>
      </div>
    );
  }

  const handleError = (error) => {
    console.error('3D Model loading error:', error);
    setHasError(true);
    setIsLoading(false);
    if (onError) onError(error);
  };

  const handleLoad = () => {
    setIsLoading(false);
    if (onLoad) onLoad();
  };

  const handleRetry = () => {
    setHasError(false);
    setIsLoading(true);
  };

  if (hasError) {
    return (
      <div className={className}>
        <ErrorFallback onRetry={handleRetry} />
      </div>
    );
  }

  return (
    <div className={className} style={{ position: 'relative' }}>
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 rounded-lg z-10">
          <LoadingSpinner />
        </div>
      )}
      <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
        <Suspense fallback={null}>
          {/* Lighting */}
          <ambientLight intensity={0.6} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          
          {/* Environment for better lighting */}
          <Environment preset="studio" />
          
          {/* 3D Model */}
          <Model3D url={modelUrl} onLoad={handleLoad} onError={handleError} />
          
          {/* Camera Controls */}
          {showControls && <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />}
        </Suspense>
      </Canvas>
    </div>
  );
};

export default Model3DViewer;
