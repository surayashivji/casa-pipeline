import { useState, useEffect, useCallback } from 'react';
import { getProducts } from '../../shared/services/apiService';
import IDCell from './cells/IDCell';
import NameCell from './cells/NameCell';
import BrandCell from './cells/BrandCell';
import URLCell from './cells/URLCell';
import ProductDetailsCell from './cells/ProductDetailsCell';
import OriginalImagesCell from './cells/OriginalImagesCell';
import ProcessedImagesCell from './cells/ProcessedImagesCell';
import Model3DCell from './cells/Model3DCell';
import StatusProgressCell from './cells/StatusProgressCell';
import PriceCell from './cells/PriceCell';

const AdminProductsTable = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    brand: '',
    category: '',
    status: ''
  });
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0
  });

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(filters.search);
    }, 300); // 300ms delay

    return () => clearTimeout(timer);
  }, [filters.search]);

  // Fetch products from admin API
  useEffect(() => {
    fetchProducts();
  }, [debouncedSearch, filters.brand, filters.category, filters.status, pagination.page]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const params = {
        offset: (pagination.page - 1) * pagination.limit,
        limit: pagination.limit,
        include_images: true,
        include_stages: true,
        ...(debouncedSearch && { search: debouncedSearch }),
        ...(filters.brand && { retailer: filters.brand }),
        ...(filters.category && { category: filters.category }),
        ...(filters.status && { status: filters.status })
      };

      const data = await getProducts(params);
      console.log('API Response:', data);
      console.log('Products with images:', data.products?.map(p => ({ id: p.id, name: p.name, imageCount: p.images?.length || 0 })));
      setProducts(data.products || []);
      setPagination(prev => ({
        ...prev,
        total: data.total || 0
      }));
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch products:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPagination(prev => ({ ...prev, page: 1 })); // Reset to first page
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading products...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-600 text-lg font-medium">Error loading products</div>
          <p className="mt-2 text-gray-600">{error}</p>
          <button 
            onClick={fetchProducts}
            className="mt-4 btn btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 px-6 pt-2 pb-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-50 to-primary-100 border-b border-primary-200 px-6 py-8 rounded-t-lg">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-primary-900">Products Database</h1>
            <p className="text-primary-700 mt-1 mb-2">{pagination.total} products</p>
          </div>
        </div>
        
        {/* Filters */}
        <div className="flex flex-wrap gap-4">
          <input
            type="text"
            placeholder="Search products..."
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          <select 
            value={filters.brand}
            onChange={(e) => handleFilterChange('brand', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Brands</option>
            <option value="IKEA">IKEA</option>
            <option value="Target">Target</option>
            <option value="West Elm">West Elm</option>
            <option value="Urban Outfitters">Urban Outfitters</option>
          </select>
          <select 
            value={filters.category}
            onChange={(e) => handleFilterChange('category', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Categories</option>
            <option value="furniture">Furniture</option>
            <option value="decor">Decor</option>
            <option value="lighting">Lighting</option>
            <option value="storage">Storage</option>
          </select>
          <select 
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Status</option>
            <option value="completed">Completed</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
            <option value="scraped">Scraped</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white w-full rounded-b-lg shadow-sm border border-gray-200">
        <div className="overflow-x-auto w-full">
          <table className="min-w-full">
            <thead className="bg-primary-50 border-b border-primary-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-primary-700 uppercase tracking-wider w-16">
                  #
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-primary-700 uppercase tracking-wider w-64">
                  Name
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-primary-700 uppercase tracking-wider w-24">
                  Brand
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-primary-700 uppercase tracking-wider w-64">
                  Original Images
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-primary-700 uppercase tracking-wider w-64">
                  Processed Images
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-primary-700 uppercase tracking-wider w-48">
                  3D Model
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-primary-700 uppercase tracking-wider w-40">
                  Status/Progress
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-primary-700 uppercase tracking-wider w-48">
                  Details
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {products.map((product, index) => {
                // Ensure product has required fields
                if (!product || !product.id) {
                  return null;
                }
                
                return (
                <tr key={product.id} className="hover:bg-gray-50">
                  <td className="px-0 py-0">
                    <IDCell product={product} index={index} pagination={pagination} />
                  </td>
                  <td className="px-0 py-0">
                    <NameCell product={product} />
                  </td>
                  <td className="px-0 py-0">
                    <BrandCell product={product} />
                  </td>
                  <td className="px-0 py-0">
                    <OriginalImagesCell product={product} />
                  </td>
                  <td className="px-0 py-0">
                    <ProcessedImagesCell product={product} />
                  </td>
                  <td className="px-0 py-0">
                    <Model3DCell product={product} />
                  </td>
                  <td className="px-0 py-0">
                    <StatusProgressCell product={product} />
                  </td>
                  <td className="px-0 py-0">
                    <ProductDetailsCell product={product} />
                  </td>
                </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {pagination.total > pagination.limit && (
        <div className="bg-white border-t border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {((pagination.page - 1) * pagination.limit) + 1} to {Math.min(pagination.page * pagination.limit, pagination.total)} of {pagination.total} products
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => handlePageChange(pagination.page - 1)}
                disabled={pagination.page === 1}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Previous
              </button>
              <button
                onClick={() => handlePageChange(pagination.page + 1)}
                disabled={pagination.page * pagination.limit >= pagination.total}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminProductsTable;
