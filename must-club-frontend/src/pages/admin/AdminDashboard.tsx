import React from 'react';
import Layout from '../../components/common/Layout';

const AdminDashboard: React.FC = () => {
  return (
    <Layout showSidebar sidebarType="admin">
      <div className="space-y-8">
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600">Welcome to the admin panel. Manage your club from here.</p>
        {/* Admin dashboard content will be implemented */}
      </div>
    </Layout>
  );
};

export default AdminDashboard;