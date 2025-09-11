import { useState, useRef, useEffect } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Box } from '@react-three/drei';

// 3D Model Component
function FurnitureModel() {
  const meshRef = useRef();
  
  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.2;
    }
  });

  return (
    <Box ref={meshRef} args={[2, 2, 2]}>
      <meshStandardMaterial color="#8b7355" />
    </Box>
  );
}

const ModelViewer = ({ data, onNext, onBack }) => {
  const [selectedLOD, setSelectedLOD] = useState('medium');
  const model = data.model3D;

  const lodOptions = [
    { level: 'high', polygons: 30000, size: '15MB', device: 'iPad Pro, iPhone 14 Pro' },
    { level: 'medium', polygons: 10000, size: '5MB', device: 'iPhone 12, iPhone 13' },
    { level: 'low', polygons: 3000, size: '1.5MB', device: 'iPhone SE, older devices' }
  ];

  const handleContinue = () => {
    onNext({ selectedLOD });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Review 3D Model</h2>
        <p className="mt-2 text-gray-600">
          Inspect the generated model and select the appropriate quality level for your target devices
        </p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2">
          <div className="bg-gray-900 rounded-lg overflow-hidden" style={{ height: '500px' }}>
            <Canvas camera={{ position: [5, 5, 5], fov: 50 }}>
              <ambientLight intensity={0.5} />
              <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} />
              <pointLight position={[-10, -10, -10]} />
              <FurnitureModel />
              <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
              <gridHelper args={[10, 10]} />
            </Canvas>
          </div>
          
          <div className="mt-4 flex justify-center space-x-4">
            <button className="px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-600 text-sm">
              Reset Camera
            </button>
            <button className="px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-600 text-sm">
              Toggle Wireframe
            </button>
            <button className="px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-600 text-sm">
              Toggle Texture
            </button>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-3">LOD Selection</h3>
            <div className="space-y-2">
              {lodOptions.map((lod) => (
                <div
                  key={lod.level}
                  onClick={() => setSelectedLOD(lod.level)}
                  className={`
                    p-3 rounded-lg border-2 cursor-pointer transition-all
                    ${selectedLOD === lod.level 
                      ? 'border-indigo-500 bg-indigo-50' 
                      : 'border-gray-200 hover:border-gray-300'
                    }
                  `}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium capitalize">{lod.level} Quality</p>
                      <p className="text-sm text-gray-600">{lod.polygons.toLocaleString()} polygons</p>
                      <p className="text-xs text-gray-500 mt-1">{lod.device}</p>
                    </div>
                    <span className="text-sm text-gray-500">{lod.size}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
            <p className="text-sm text-blue-800">
              <strong>Recommendation:</strong> Use Medium quality for most iOS devices. 
              It provides a good balance between visual quality and performance.
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Model Stats</h4>
            <dl className="space-y-1 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">Format:</dt>
                <dd className="text-gray-900">GLB / USDZ</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Textures:</dt>
                <dd className="text-gray-900">2K PBR</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Materials:</dt>
                <dd className="text-gray-900">3</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      <div className="flex justify-between">
        <button
          onClick={onBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
        >
          Back
        </button>
        <button
          onClick={handleContinue}
          className="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Save Model ({selectedLOD} quality)
        </button>
      </div>
    </div>
  );
};

export default ModelViewer;
