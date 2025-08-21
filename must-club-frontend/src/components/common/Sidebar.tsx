import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Calendar, 
  Users, 
  BookOpen, 
  User, 
  Settings,
  Shield,
  MessageSquare,
  Star,
  Handshake,
  UserCheck
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  type: 'user' | 'admin';
}

const Sidebar: React.FC<SidebarProps> = ({ type }) => {
  const location = useLocation();
  const { user } = useAuth();

  const userNavItems = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Events', href: '/events', icon: Calendar },
    { name: 'Communities', href: '/communities', icon: Users },
    { name: 'Blog', href: '/blog', icon: BookOpen },
    { name: 'Profile', href: '/profile', icon: User },
  ];

  const adminNavItems = [
    { name: 'Admin Dashboard', href: '/admin', icon: Shield },
    { name: 'Users', href: '/admin/users', icon: Users },
    { name: 'Events', href: '/admin/events', icon: Calendar },
    { name: 'Communities', href: '/admin/communities', icon: Users },
    { name: 'Blog Posts', href: '/admin/blog', icon: BookOpen },
    { name: 'Feedback', href: '/admin/feedback', icon: MessageSquare },
    { name: 'Partners', href: '/admin/partners', icon: Handshake },
    { name: 'Testimonials', href: '/admin/testimonials', icon: Star },
    { name: 'Executives', href: '/admin/executives', icon: UserCheck },
    { name: 'Settings', href: '/admin/settings', icon: Settings },
  ];

  const navItems = type === 'admin' ? adminNavItems : userNavItems;

  return (
    <div className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 bg-white shadow-lg border-r border-gray-200 overflow-y-auto">
      <div className="p-4">
        {/* User Info */}
        <div className="mb-6 p-4 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg border border-primary-100">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
              <span className="text-white font-medium">
                {user?.first_name?.[0] || user?.username?.[0] || 'U'}
              </span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">
                {user?.first_name && user?.last_name 
                  ? `${user.first_name} ${user.last_name}` 
                  : user?.username
                }
              </p>
              <p className="text-xs text-gray-600">
                {type === 'admin' ? 'Administrator' : 'Member'}
              </p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="space-y-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200
                  ${isActive 
                    ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-md' 
                    : 'text-gray-700 hover:bg-gray-100 hover:text-primary-600'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Quick Actions */}
        <div className="mt-8 p-4 bg-gradient-to-r from-secondary-50 to-primary-50 rounded-lg border border-secondary-100">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Actions</h3>
          <div className="space-y-2">
            {type === 'admin' ? (
              <>
                <Link
                  to="/admin/events/create"
                  className="block text-xs text-secondary-600 hover:text-secondary-700 font-medium"
                >
                  Create New Event
                </Link>
                <Link
                  to="/admin/communities/create"
                  className="block text-xs text-secondary-600 hover:text-secondary-700 font-medium"
                >
                  Add Community
                </Link>
                <Link
                  to="/admin/blog/create"
                  className="block text-xs text-secondary-600 hover:text-secondary-700 font-medium"
                >
                  Write Blog Post
                </Link>
              </>
            ) : (
              <>
                <Link
                  to="/events"
                  className="block text-xs text-secondary-600 hover:text-secondary-700 font-medium"
                >
                  Browse Events
                </Link>
                <Link
                  to="/communities"
                  className="block text-xs text-secondary-600 hover:text-secondary-700 font-medium"
                >
                  Join Communities
                </Link>
                <Link
                  to="/feedback"
                  className="block text-xs text-secondary-600 hover:text-secondary-700 font-medium"
                >
                  Send Feedback
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;