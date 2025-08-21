import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AdminRoute from './components/auth/AdminRoute';

// Pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';

// User Pages
import UserDashboard from './pages/user/UserDashboard';
import EventsPage from './pages/user/EventsPage';
import EventDetailsPage from './pages/user/EventDetailsPage';
import CommunitiesPage from './pages/user/CommunitiesPage';
import CommunityDetailsPage from './pages/user/CommunityDetailsPage';
import BlogPage from './pages/user/BlogPage';
import ProfilePage from './pages/user/ProfilePage';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUsersPage from './pages/admin/AdminUsersPage';
import AdminEventsPage from './pages/admin/AdminEventsPage';
import AdminCommunitiesPage from './pages/admin/AdminCommunitiesPage';
import AdminBlogPage from './pages/admin/AdminBlogPage';
import AdminFeedbackPage from './pages/admin/AdminFeedbackPage';
import AdminPartnersPage from './pages/admin/AdminPartnersPage';
import AdminTestimonialsPage from './pages/admin/AdminTestimonialsPage';
import AdminExecutivesPage from './pages/admin/AdminExecutivesPage';

// Public Pages
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';
import NotFoundPage from './pages/NotFoundPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />

            {/* Protected User Routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <UserDashboard />
              </ProtectedRoute>
            } />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/events/:id" element={<EventDetailsPage />} />
            <Route path="/communities" element={<CommunitiesPage />} />
            <Route path="/communities/:id" element={<CommunityDetailsPage />} />
            <Route path="/blog" element={<BlogPage />} />
            <Route path="/profile" element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            } />

            {/* Admin Routes */}
            <Route path="/admin" element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            } />
            <Route path="/admin/users" element={
              <AdminRoute>
                <AdminUsersPage />
              </AdminRoute>
            } />
            <Route path="/admin/events" element={
              <AdminRoute>
                <AdminEventsPage />
              </AdminRoute>
            } />
            <Route path="/admin/communities" element={
              <AdminRoute>
                <AdminCommunitiesPage />
              </AdminRoute>
            } />
            <Route path="/admin/blog" element={
              <AdminRoute>
                <AdminBlogPage />
              </AdminRoute>
            } />
            <Route path="/admin/feedback" element={
              <AdminRoute>
                <AdminFeedbackPage />
              </AdminRoute>
            } />
            <Route path="/admin/partners" element={
              <AdminRoute>
                <AdminPartnersPage />
              </AdminRoute>
            } />
            <Route path="/admin/testimonials" element={
              <AdminRoute>
                <AdminTestimonialsPage />
              </AdminRoute>
            } />
            <Route path="/admin/executives" element={
              <AdminRoute>
                <AdminExecutivesPage />
              </AdminRoute>
            } />

            {/* Catch all route */}
            <Route path="/404" element={<NotFoundPage />} />
            <Route path="*" element={<Navigate to="/404" replace />} />
          </Routes>

          {/* Toast Notifications */}
          <ToastContainer
            position="top-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="light"
            toastClassName="bg-white shadow-lg border border-gray-200"
          />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;