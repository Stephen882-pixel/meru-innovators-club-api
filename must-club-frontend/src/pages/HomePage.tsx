import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Calendar, 
  Users, 
  BookOpen, 
  Star, 
  ArrowRight, 
  Code, 
  Shield, 
  Smartphone,
  Brain,
  Blocks,
  Wifi,
  Cloud
} from 'lucide-react';
import Layout from '../components/common/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { useAuth } from '../context/AuthContext';
import { eventsAPI, testimonialsAPI, partnersAPI } from '../services/api';
import { Event, Testimonial, Partner } from '../types';
import { formatDateTime, getCategoryColor, getCategoryLabel } from '../utils/helpers';

const HomePage: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const [upcomingEvents, setUpcomingEvents] = useState<Event[]>([]);
  const [testimonials, setTestimonials] = useState<Testimonial[]>([]);
  const [partners, setPartners] = useState<Partner[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        const [eventsResponse, testimonialsResponse, partnersResponse] = await Promise.all([
          eventsAPI.getEvents({ limit: 3 }),
          testimonialsAPI.getTestimonials(),
          partnersAPI.getPartners(),
        ]);

        setUpcomingEvents(eventsResponse.results);
        setTestimonials(testimonialsResponse.results.slice(0, 3));
        setPartners(partnersResponse.results.slice(0, 6));
      } catch (error) {
        console.error('Error fetching home data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHomeData();
  }, []);

  const categories = [
    { icon: Code, name: 'Web Development', color: 'text-blue-600', bgColor: 'bg-blue-100' },
    { icon: Shield, name: 'Cybersecurity', color: 'text-red-600', bgColor: 'bg-red-100' },
    { icon: Smartphone, name: 'Mobile Dev', color: 'text-green-600', bgColor: 'bg-green-100' },
    { icon: Brain, name: 'AI & ML', color: 'text-purple-600', bgColor: 'bg-purple-100' },
    { icon: Blocks, name: 'Blockchain', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { icon: Wifi, name: 'IoT', color: 'text-indigo-600', bgColor: 'bg-indigo-100' },
    { icon: Cloud, name: 'Cloud Computing', color: 'text-gray-600', bgColor: 'bg-gray-100' },
  ];

  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-500 via-primary-600 to-secondary-600 text-white py-20 px-4 sm:px-6 lg:px-8 rounded-2xl mb-12">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Welcome to <span className="text-secondary-200">MUST</span> Science Innovators
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-primary-100 max-w-3xl mx-auto">
            Join Meru University's premier technology community. Learn, innovate, and build the future together.
          </p>
          
          {!isAuthenticated ? (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/register">
                <Button variant="secondary" size="lg" className="text-lg px-8 py-3">
                  Join the Community
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </Link>
              <Link to="/events">
                <Button variant="outline" size="lg" className="text-lg px-8 py-3 border-white text-white hover:bg-white hover:text-primary-600">
                  Explore Events
                </Button>
              </Link>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to={user?.is_staff ? "/admin" : "/dashboard"}>
                <Button variant="secondary" size="lg" className="text-lg px-8 py-3">
                  Go to Dashboard
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </Link>
              <Link to="/events">
                <Button variant="outline" size="lg" className="text-lg px-8 py-3 border-white text-white hover:bg-white hover:text-primary-600">
                  Browse Events
                </Button>
              </Link>
            </div>
          )}
        </div>

        {/* Decorative elements */}
        <div className="absolute top-10 left-10 w-20 h-20 bg-secondary-400 rounded-full opacity-20 animate-pulse"></div>
        <div className="absolute bottom-10 right-10 w-32 h-32 bg-primary-400 rounded-full opacity-20 animate-pulse"></div>
        <div className="absolute top-1/2 left-1/4 w-16 h-16 bg-secondary-300 rounded-full opacity-30 animate-bounce"></div>
      </section>

      {/* Tech Categories */}
      <section className="mb-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Explore Tech Communities</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Join specialized communities focused on cutting-edge technologies and innovation
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {categories.map((category, index) => {
            const Icon = category.icon;
            return (
              <Link
                key={index}
                to="/communities"
                className="group"
              >
                <Card className="text-center p-6 hover:shadow-lg transition-all duration-300 group-hover:scale-105">
                  <div className={`w-12 h-12 ${category.bgColor} rounded-lg flex items-center justify-center mx-auto mb-3`}>
                    <Icon className={`w-6 h-6 ${category.color}`} />
                  </div>
                  <h3 className="font-medium text-gray-900 text-sm">{category.name}</h3>
                </Card>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Upcoming Events */}
      <section className="mb-16">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Upcoming Events</h2>
            <p className="text-gray-600">Don't miss out on these exciting learning opportunities</p>
          </div>
          <Link to="/events">
            <Button variant="outline">
              View All Events
              <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
          </Link>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {upcomingEvents.map((event) => (
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
                    <Badge variant="primary" size="sm">
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
                  
                  <div className="flex items-center text-sm text-gray-500">
                    <Calendar className="w-4 h-4 mr-2" />
                    {formatDateTime(event.date)}
                  </div>
                  
                  <div className="flex items-center justify-between pt-2">
                    <span className="text-sm text-gray-500">by {event.organizer}</span>
                    <Link to={`/events/${event.id}`}>
                      <Button variant="primary" size="sm">
                        Learn More
                      </Button>
                    </Link>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>

      {/* Testimonials */}
      <section className="mb-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">What Our Members Say</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Hear from students who have transformed their careers through our community
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {testimonials.map((testimonial) => (
            <Card key={testimonial.id} className="text-center">
              <div className="flex justify-center mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-5 h-5 ${
                      i < testimonial.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              
              <p className="text-gray-600 mb-4 italic">"{testimonial.content}"</p>
              
              <div className="flex items-center justify-center">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mr-3">
                  <span className="text-white font-medium text-sm">
                    {testimonial.user.first_name?.[0] || testimonial.user.username?.[0]}
                  </span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">
                    {testimonial.user.first_name && testimonial.user.last_name
                      ? `${testimonial.user.first_name} ${testimonial.user.last_name}`
                      : testimonial.user.username
                    }
                  </p>
                  <p className="text-sm text-gray-500">MUST Student</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Partners */}
      {partners.length > 0 && (
        <section className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Our Partners</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Collaborating with industry leaders to provide the best opportunities
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {partners.map((partner) => (
              <Card key={partner.id} className="text-center p-6 hover:shadow-lg transition-shadow duration-300">
                <img
                  src={partner.logo}
                  alt={partner.name}
                  className="w-16 h-16 mx-auto mb-3 object-contain"
                />
                <h3 className="font-medium text-gray-900 text-sm">{partner.name}</h3>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-secondary-500 to-primary-500 text-white rounded-2xl p-8 md:p-12 text-center">
        <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Start Your Journey?</h2>
        <p className="text-lg md:text-xl mb-8 text-secondary-100 max-w-2xl mx-auto">
          Join hundreds of students already building their future in technology. Your innovation journey starts here.
        </p>
        
        {!isAuthenticated ? (
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register">
              <Button variant="secondary" size="lg" className="text-lg px-8 py-3">
                Get Started Today
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Link to="/about">
              <Button variant="outline" size="lg" className="text-lg px-8 py-3 border-white text-white hover:bg-white hover:text-primary-600">
                Learn More
              </Button>
            </Link>
          </div>
        ) : (
          <Link to="/communities">
            <Button variant="secondary" size="lg" className="text-lg px-8 py-3">
              Explore Communities
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </Link>
        )}
      </section>
    </Layout>
  );
};

export default HomePage;