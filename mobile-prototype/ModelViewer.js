import React, { useRef, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { GLView } from 'expo-gl';
import { Renderer } from 'expo-three';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

const API_URL = 'https://82401bcb63c6.ngrok-free.app';

export default function ModelViewer({ model, onBack }) {
  const [loading, setLoading] = useState(true);
  const rendererRef = useRef(null);
  const sceneRef = useRef(null);
  const modelRef = useRef(null);
  const frameId = useRef(null);

  const onContextCreate = async (gl) => {
    // Create renderer
    const renderer = new Renderer({ gl });
    rendererRef.current = renderer;
    
    // Create scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#333333');
    sceneRef.current = scene;
    
    // Create camera
    const { drawingBufferWidth: width, drawingBufferHeight: height } = gl;
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 5;
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);
    
    // Load GLB model
    if (model?.model_url) {
      const loader = new GLTFLoader();
      
      loader.load(
        model.model_url,
        (gltf) => {
          console.log('Model loaded!');
          const loadedModel = gltf.scene;
          
          // Center and scale the model
          const box = new THREE.Box3().setFromObject(loadedModel);
          const center = box.getCenter(new THREE.Vector3());
          const size = box.getSize(new THREE.Vector3());
          
          const maxDim = Math.max(size.x, size.y, size.z);
          const scale = 3 / maxDim;
          
          loadedModel.scale.setScalar(scale);
          loadedModel.position.sub(center.multiplyScalar(scale));
          
          scene.add(loadedModel);
          modelRef.current = loadedModel;
          setLoading(false);
        },
        (progress) => {
          console.log('Loading...', (progress.loaded / progress.total * 100) + '%');
        },
        (error) => {
          console.error('Error loading model:', error);
          setLoading(false);
        }
      );
    }
    
    // Animation loop
    const animate = () => {
      frameId.current = requestAnimationFrame(animate);
      
      // Auto-rotate model
      if (modelRef.current) {
        modelRef.current.rotation.y += 0.01;
      }
      
      renderer.render(scene, camera);
      gl.endFrameEXP();
    };
    animate();
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title} numberOfLines={1}>{model.name}</Text>
      </View>
      
      <GLView 
        style={styles.glView} 
        onContextCreate={onContextCreate}
      />
      
      {loading && (
        <View style={styles.loadingOverlay}>
          <Text style={styles.loadingText}>Loading 3D Model...</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 10,
    backgroundColor: '#111',
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButton: {
    marginRight: 15,
  },
  backText: {
    color: 'white',
    fontSize: 16,
  },
  title: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
    flex: 1,
  },
  glView: {
    flex: 1,
  },
  loadingOverlay: {
    position: 'absolute',
    top: '50%',
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  loadingText: {
    color: 'white',
    fontSize: 16,
  },
});