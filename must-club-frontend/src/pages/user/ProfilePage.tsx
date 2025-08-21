import React from 'react';
import Layout from '../../components/common/Layout';

const ProfilePage: React.FC = () => {
  return (
    <Layout showSidebar sidebarType="user">
      <div className="space-y-8">
        <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>
        <p className="text-gray-600">Profile page - to be implemented</p>
      </div>
    </Layout>
  );
};

export default ProfilePage;