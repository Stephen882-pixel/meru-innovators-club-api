import React from 'react';
import { useAuth } from '../../context/AuthContext';
import Header from './Header';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
  showSidebar?: boolean;
  sidebarType?: 'user' | 'admin';
}

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  showSidebar = false, 
  sidebarType = 'user' 
}) => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      <Header />
      
      <div className="flex">
        {showSidebar && isAuthenticated && (
          <Sidebar type={sidebarType} />
        )}
        
        <main className={`flex-1 ${showSidebar && isAuthenticated ? 'ml-64' : ''}`}>
          <div className="px-4 py-6 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;