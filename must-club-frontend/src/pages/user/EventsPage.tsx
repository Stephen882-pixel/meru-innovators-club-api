import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, MapPin, Users, Search, Filter } from 'lucide-react';
import Layout from '../../components/common/Layout';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import Input from '../../components/common/Input';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { useAuth } from '../../context/AuthContext';
import { eventsAPI } from '../../services/api';
import { Event } from '../../types';
import { formatDateTime, getCategoryLabel, getCategoryColor } from '../../utils/helpers';
import { EVENT_CATEGORIES } from '../../utils/constants';

const EventsPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [events, setEvents] = useState<Event[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [showVirtualOnly, setShowVirtualOnly] = useState(false);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await eventsAPI.getEvents();
        setEvents(response.results);
        setFilteredEvents(response.results);
      } catch (error) {
        console.error('Error fetching events:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvents();
  }, []);

  useEffect(() => {
    let filtered = events;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(event =>
        event.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.organizer.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by category
    if (selectedCategory) {
      filtered = filtered.filter(event => event.category === selectedCategory);
    }

    // Filter by virtual events
    if (showVirtualOnly) {
      filtered = filtered.filter(event => event.is_virtual);
    }

    setFilteredEvents(filtered);
  }, [events, searchTerm, selectedCategory, showVirtualOnly]);

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedCategory('');
    setShowVirtualOnly(false);
  };

  if (isLoading) {
    return (
      <Layout showSidebar={isAuthenticated} sidebarType="user">
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout showSidebar={isAuthenticated} sidebarType="user">
      <div className="space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Upcoming Events</h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Discover amazing learning opportunities, workshops, and networking events designed to boost your tech skills.
          </p>
        </div>

        {/* Filters */}
        <Card>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <Filter className="w-5 h-5 text-gray-500" />
              <h3 className="text-lg font-medium text-gray-900">Filter Events</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Input
                type="text"
                placeholder="Search events..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                leftIcon={<Search className="w-4 h-4" />}
              />

              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">All Categories</option>
                {EVENT_CATEGORIES.map((category) => (
                  <option key={category.value} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </select>

              <div className="flex items-center">
                <input
                  id="virtual-only"
                  type="checkbox"
                  checked={showVirtualOnly}
                  onChange={(e) => setShowVirtualOnly(e.target.checked)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="virtual-only" className="ml-2 text-sm text-gray-900">
                  Virtual Events Only
                </label>
              </div>

              <Button variant="outline" onClick={clearFilters}>
                Clear Filters
              </Button>
            </div>
          </div>
        </Card>

        {/* Events Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEvents.map((event) => (
            <Card key={event.id} className="hover:shadow-lg transition-shadow duration-300">
              <div className="aspect-w-16 aspect-h-9 mb-4">
                <img
                  src={event.image_url || '/images/default-event.jpg'}
                  alt={event.title}
                  className="w-full h-48 object-cover rounded-lg"
                />
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Badge 
                    variant="primary" 
                    size="sm"
                    className={getCategoryColor(event.category)}
                  >
                    {getCategoryLabel(event.category)}
                  </Badge>
                  {event.is_virtual && (
                    <Badge variant="info" size="sm">Virtual</Badge>
                  )}
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                  {event.title}
                </h3>
                
                <p className="text-gray-600 text-sm line-clamp-2">
                  {event.description}
                </p>
                
                <div className="space-y-2">
                  <div className="flex items-center text-sm text-gray-500">
                    <Calendar className="w-4 h-4 mr-2" />
                    {formatDateTime(event.date)}
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-500">
                    <MapPin className="w-4 h-4 mr-2" />
                    {event.is_virtual ? 'Virtual Event' : event.location}
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-500">
                    <Users className="w-4 h-4 mr-2" />
                    Organized by {event.organizer}
                  </div>
                </div>
                
                <div className="flex items-center justify-between pt-4">
                  <span className="text-sm font-medium text-primary-600">
                    Free Event
                  </span>
                  <Link to={`/events/${event.id}`}>
                    <Button variant="primary" size="sm">
                      View Details
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* No Events Found */}
        {filteredEvents.length === 0 && (
          <Card className="text-center py-12">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Events Found</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || selectedCategory || showVirtualOnly
                ? "Try adjusting your filters to see more events."
                : "There are no upcoming events at the moment. Check back soon!"}
            </p>
            {(searchTerm || selectedCategory || showVirtualOnly) && (
              <Button variant="outline" onClick={clearFilters}>
                Clear Filters
              </Button>
            )}
          </Card>
        )}

        {/* Call to Action */}
        {!isAuthenticated && (
          <Card className="bg-gradient-to-r from-primary-50 to-secondary-50 border-primary-200">
            <div className="text-center py-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Join MUST Science Innovators
              </h3>
              <p className="text-gray-600 mb-6">
                Register for events, join communities, and start your innovation journey today!
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/register">
                  <Button variant="primary" size="lg">
                    Join Now
                  </Button>
                </Link>
                <Link to="/login">
                  <Button variant="outline" size="lg">
                    Sign In
                  </Button>
                </Link>
              </div>
            </div>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default EventsPage;