import { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import ModelViewer from './ModelViewer';

const API_URL = 'https://82401bcb63c6.ngrok-free.app';

export default function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/products`, {
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      });
      const data = await response.json();
      setProducts(data.products);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Show model viewer if a product is selected
  if (selectedProduct) {
    const model = selectedProduct.models_3d?.[0];
    return (
      <ModelViewer 
        model={model}
        onBack={() => setSelectedProduct(null)}
      />
    );
  }

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
        <Text>Loading products...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Casa Pipeline Models</Text>
      <Text style={styles.subtitle}>Tap to view 3D model</Text>
      <FlatList
        data={products}
        keyExtractor={item => item.id}
        renderItem={({ item }) => {
          const hasModel = item.models_3d?.length > 0;
          return (
            <TouchableOpacity 
              style={[styles.productCard, !hasModel && styles.disabledCard]}
              onPress={() => hasModel && setSelectedProduct(item)}
              disabled={!hasModel}
            >
              <View style={styles.productInfo}>
                <Text style={styles.productName}>{item.name}</Text>
                <Text style={styles.productBrand}>{item.brand} - ${item.price}</Text>
                {item.dimensions && (
                  <Text style={styles.dimensions}>
                    {item.dimensions.width}"W x {item.dimensions.height}"H x {item.dimensions.depth}"D
                  </Text>
                )}
              </View>
              <View style={styles.modelStatus}>
                <Text style={styles.statusText}>
                  {hasModel ? '✅' : '⏳'}
                </Text>
              </View>
            </TouchableOpacity>
          );
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 50,
    backgroundColor: '#f5f5f5',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    paddingHorizontal: 20,
    paddingBottom: 10,
  },
  productCard: {
    backgroundColor: 'white',
    padding: 15,
    marginHorizontal: 20,
    marginVertical: 5,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  disabledCard: {
    opacity: 0.5,
  },
  productInfo: {
    flex: 1,
  },
  productName: {
    fontSize: 16,
    fontWeight: '600',
  },
  productBrand: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  dimensions: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  modelStatus: {
    marginLeft: 10,
  },
  statusText: {
    fontSize: 24,
  },
});