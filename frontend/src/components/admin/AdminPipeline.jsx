import { useState, useEffect } from 'react';
import AdminProductsTable from './AdminProductsTable';

const AdminPipeline = () => {
  return (
    <div className="w-full animate-fade-in">

      {/* Admin Content - Full Width */}
      <div className="w-full">
        <AdminProductsTable />
      </div>
    </div>
  );
};

export default AdminPipeline;
