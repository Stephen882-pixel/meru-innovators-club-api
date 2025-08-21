import React from 'react';
import Layout from '../../components/common/Layout';
import { useAuth } from '../../context/AuthContext';

const EventDetailsPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  
  return (
    <Layout showSidebar={isAuthenticated} sidebarType="user">
      <div className="space-y-8">
        <h1 className="text-3xl font-bold text-gray-900">Event Details</h1>
        <p className="text-gray-600">Event details page - to be implemented</p>
      </div>
    </Layout>
  );
};

export default EventDetailsPage;