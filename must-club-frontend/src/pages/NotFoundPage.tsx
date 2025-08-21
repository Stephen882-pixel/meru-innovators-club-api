import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';
import Layout from '../components/common/Layout';
import Button from '../components/common/Button';
import Card from '../components/common/Card';

const NotFoundPage: React.FC = () => {
  return (
    <Layout>
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="text-center max-w-md mx-auto">
          <div className="mb-6">
            <div className="w-24 h-24 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-white font-bold text-4xl">404</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Page Not Found</h1>
            <p className="text-gray-600">
              The page you're looking for doesn't exist or has been moved.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button 
              variant="primary" 
              leftIcon={<Home className="w-4 h-4" />}
              onClick={() => window.location.href = '/'}
            >
              Go Home
            </Button>
            <Button 
              variant="outline" 
              leftIcon={<ArrowLeft className="w-4 h-4" />}
              onClick={() => window.history.back()}
            >
              Go Back
            </Button>
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default NotFoundPage;