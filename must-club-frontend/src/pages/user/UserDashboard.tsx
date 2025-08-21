import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Users, BookOpen, Star, TrendingUp, Clock } from 'lucide-react';
import Layout from '../../components/common/Layout';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { useAuth } from '../../context/AuthContext';
import { eventsAPI, communitiesAPI } from '../../services/api';
import { Event, CommunityProfile, EventRegistration } from '../../types';
import { formatDateTime, getCategoryLabel } from '../../utils/helpers';

const UserDashboard: React.FC = () => {
  const { user, profile } = useAuth();
  const [upcomingEvents, setUpcomingEvents] = useState<Event[]>([]);
  const [userRegistrations, setUserRegistrations] = useState<EventRegistration[]>([]);
  const [joinedCommunities, setJoinedCommunities] = useState<CommunityProfile[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [eventsResponse, registrationsResponse, communitiesResponse] = await Promise.all([
          eventsAPI.getEvents({ limit: 4 }),
          eventsAPI.getUserRegistrations(),
          communitiesAPI.getCommunities(),
        ]);

        setUpcomingEvents(eventsResponse.results);
        setUserRegistrations(registrationsResponse.results);
        // For now, show all communities - in a real app, you'd filter joined communities
        setJoinedCommunities(communitiesResponse.results.slice(0, 3));
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (isLoading) {
    return (
      <Layout showSidebar sidebarType="user">
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout showSidebar sidebarType="user">
      <div className="space-y-8">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-2xl p-8">
          <h1 className="text-3xl font-bold mb-2">
            Welcome back, {user?.first_name || user?.username}! 👋
          </h1>
          <p className="text-primary-100 text-lg">
            Ready to continue your innovation journey? Here's what's happening in your community.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Calendar className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900">{userRegistrations.length}</h3>
            <p className="text-gray-600">Events Registered</p>
          </Card>

          <Card className="text-center">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Users className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900">{joinedCommunities.length}</h3>
            <p className="text-gray-600">Communities Joined</p>
          </Card>

          <Card className="text-center">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <BookOpen className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900">12</h3>
            <p className="text-gray-600">Articles Read</p>
          </Card>

          <Card className="text-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <TrendingUp className="w-6 h-6 text-yellow-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900">85%</h3>
            <p className="text-gray-600">Profile Complete</p>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upcoming Events */}
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Upcoming Events</h2>
              <Link to="/events">
                <Button variant="outline" size="sm">View All</Button>
              </Link>
            </div>

            <div className="space-y-4">
              {upcomingEvents.map((event) => (
                <Card key={event.id} className="p-4 hover:shadow-lg transition-shadow">
                  <div className="flex items-start space-x-4">
                    <img
                      src={event.image_url || '/images/default-event.jpg'}
                      alt={event.title}
                      className="w-16 h-16 object-cover rounded-lg"
                    />
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <Badge variant="primary" size="sm">
                          {getCategoryLabel(event.category)}
                        </Badge>
                        {event.is_virtual && (
                          <Badge variant="info" size="sm">Virtual</Badge>
                        )}
                      </div>
                      <h3 className="font-semibold text-gray-900 mb-1">{event.title}</h3>
                      <div className="flex items-center text-sm text-gray-500 mb-2">
                        <Clock className="w-4 h-4 mr-1" />
                        {formatDateTime(event.date)}
                      </div>
                      <Link to={`/events/${event.id}`}>
                        <Button variant="primary" size="sm">Register</Button>
                      </Link>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>

          {/* My Communities */}
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">My Communities</h2>
              <Link to="/communities">
                <Button variant="outline" size="sm">Explore More</Button>
              </Link>
            </div>

            <div className="space-y-4">
              {joinedCommunities.map((community) => (
                <Card key={community.id} className="p-4 hover:shadow-lg transition-shadow">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">{community.name}</h3>
                      <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                        {community.description}
                      </p>
                      <div className="flex items-center text-sm text-gray-500">
                        <Users className="w-4 h-4 mr-1" />
                        {community.member_count} members
                      </div>
                    </div>
                    <Link to={`/communities/${community.id}`}>
                      <Button variant="secondary" size="sm">View</Button>
                    </Link>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <Card>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link to="/profile">
              <Button variant="outline" fullWidth className="h-16 flex-col">
                <Star className="w-6 h-6 mb-2" />
                Update Profile
              </Button>
            </Link>
            <Link to="/events">
              <Button variant="outline" fullWidth className="h-16 flex-col">
                <Calendar className="w-6 h-6 mb-2" />
                Browse Events
              </Button>
            </Link>
            <Link to="/communities">
              <Button variant="outline" fullWidth className="h-16 flex-col">
                <Users className="w-6 h-6 mb-2" />
                Join Communities
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default UserDashboard;