import axios, { AxiosResponse, AxiosError } from 'axios';
import { 
  AuthResponse, 
  LoginCredentials, 
  RegisterData, 
  User, 
  UserProfile,
  Event,
  EventRegistration,
  CommunityProfile,
  BlogPost,
  Comment,
  Testimonial,
  Partner,
  Feedback,
  ExecutiveMember,
  Club,
  NewsletterSubscription,
  ContactMessage,
  ApiResponse,
  ApiError,
  ProfileUpdateFormData
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${api.defaults.baseURL}/api/token/refresh/`, {
            refresh: refreshToken,
          });
          
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          
          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response: AxiosResponse<AuthResponse> = await api.post('/api/account/login/', credentials);
    return response.data;
  },

  register: async (userData: RegisterData): Promise<AuthResponse> => {
    const response: AxiosResponse<AuthResponse> = await api.post('/api/account/register/', userData);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/api/account/logout/');
  },

  getUserData: async (): Promise<UserProfile> => {
    const response: AxiosResponse<UserProfile> = await api.get('/api/account/get-user-data/');
    return response.data;
  },

  updateProfile: async (profileData: ProfileUpdateFormData): Promise<UserProfile> => {
    const response: AxiosResponse<UserProfile> = await api.put('/api/account/update-user-profile/', profileData);
    return response.data;
  },

  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    await api.post('/api/account/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
    });
  },

  requestPasswordReset: async (email: string): Promise<void> => {
    await api.post('/api/account/password-reset/request/', { email });
  },

  resetPassword: async (token: string, newPassword: string): Promise<void> => {
    await api.post('/api/account/password-reset/reset/', {
      token,
      new_password: newPassword,
    });
  },

  verifyOTP: async (otp: string): Promise<void> => {
    await api.post('/api/account/verify-otp/', { otp });
  },

  deleteAccount: async (): Promise<void> => {
    await api.delete('/api/account/delete-account/');
  },
};

// Admin API
export const adminAPI = {
  getAllUsers: async (): Promise<ApiResponse<UserProfile>> => {
    const response: AxiosResponse<ApiResponse<UserProfile>> = await api.get('/api/account/get-all-users/');
    return response.data;
  },
};

// Events API
export const eventsAPI = {
  getEvents: async (params?: Record<string, any>): Promise<ApiResponse<Event>> => {
    const response: AxiosResponse<ApiResponse<Event>> = await api.get('/api/events/', { params });
    return response.data;
  },

  getEvent: async (id: number): Promise<Event> => {
    const response: AxiosResponse<Event> = await api.get(`/api/events/${id}/`);
    return response.data;
  },

  createEvent: async (eventData: Partial<Event>): Promise<Event> => {
    const response: AxiosResponse<Event> = await api.post('/api/events/', eventData);
    return response.data;
  },

  updateEvent: async (id: number, eventData: Partial<Event>): Promise<Event> => {
    const response: AxiosResponse<Event> = await api.put(`/api/events/${id}/`, eventData);
    return response.data;
  },

  deleteEvent: async (id: number): Promise<void> => {
    await api.delete(`/api/events/${id}/`);
  },

  registerForEvent: async (eventId: number): Promise<EventRegistration> => {
    const response: AxiosResponse<EventRegistration> = await api.post(`/api/events/${eventId}/registrations/`);
    return response.data;
  },

  getEventRegistrations: async (eventId: number): Promise<ApiResponse<EventRegistration>> => {
    const response: AxiosResponse<ApiResponse<EventRegistration>> = await api.get(`/api/events/${eventId}/registrations/`);
    return response.data;
  },

  getUserRegistrations: async (): Promise<ApiResponse<EventRegistration>> => {
    const response: AxiosResponse<ApiResponse<EventRegistration>> = await api.get('/api/registrations/');
    return response.data;
  },
};

// Communities API
export const communitiesAPI = {
  getCommunities: async (): Promise<ApiResponse<CommunityProfile>> => {
    const response: AxiosResponse<ApiResponse<CommunityProfile>> = await api.get('/api/list-communities/');
    return response.data;
  },

  getCommunity: async (id: number): Promise<CommunityProfile> => {
    const response: AxiosResponse<CommunityProfile> = await api.get(`/api/get-community/${id}/`);
    return response.data;
  },

  createCommunity: async (communityData: Partial<CommunityProfile>): Promise<CommunityProfile> => {
    const response: AxiosResponse<CommunityProfile> = await api.post('/api/add-community/', communityData);
    return response.data;
  },

  updateCommunity: async (id: number, communityData: Partial<CommunityProfile>): Promise<CommunityProfile> => {
    const response: AxiosResponse<CommunityProfile> = await api.put(`/api/update-community/${id}/`, communityData);
    return response.data;
  },

  joinCommunity: async (id: number): Promise<void> => {
    await api.post(`/api/join-community/${id}/`);
  },

  getCommunityMembers: async (id: number): Promise<ApiResponse<User>> => {
    const response: AxiosResponse<ApiResponse<User>> = await api.get(`/api/community-members/${id}/`);
    return response.data;
  },

  searchCommunities: async (query: string): Promise<ApiResponse<CommunityProfile>> => {
    const response: AxiosResponse<ApiResponse<CommunityProfile>> = await api.get('/api/search-community/', {
      params: { q: query }
    });
    return response.data;
  },
};

// Blog API
export const blogAPI = {
  getBlogPosts: async (): Promise<ApiResponse<BlogPost>> => {
    const response: AxiosResponse<ApiResponse<BlogPost>> = await api.get('/api/home/blog/');
    return response.data;
  },
};

// Comments API
export const commentsAPI = {
  getEventComments: async (eventId: number): Promise<ApiResponse<Comment>> => {
    const response: AxiosResponse<ApiResponse<Comment>> = await api.get(`/api/comments/${eventId}/create/`);
    return response.data;
  },

  createComment: async (eventId: number, content: string): Promise<Comment> => {
    const response: AxiosResponse<Comment> = await api.post(`/api/comments/${eventId}/create/`, { content });
    return response.data;
  },

  updateComment: async (id: number, content: string): Promise<Comment> => {
    const response: AxiosResponse<Comment> = await api.put(`/api/comments/${id}/`, { content });
    return response.data;
  },

  deleteComment: async (id: number): Promise<void> => {
    await api.delete(`/api/comments/${id}/`);
  },

  createReply: async (commentId: number, content: string): Promise<Comment> => {
    const response: AxiosResponse<Comment> = await api.post(`/api/comments/${commentId}/replies/`, { content });
    return response.data;
  },
};

// Testimonials API
export const testimonialsAPI = {
  getTestimonials: async (): Promise<ApiResponse<Testimonial>> => {
    const response: AxiosResponse<ApiResponse<Testimonial>> = await api.get('/api/testimonies/testimonials/');
    return response.data;
  },

  createTestimonial: async (testimonialData: Partial<Testimonial>): Promise<Testimonial> => {
    const response: AxiosResponse<Testimonial> = await api.post('/api/testimonies/testimonials/', testimonialData);
    return response.data;
  },

  updateTestimonial: async (id: number, testimonialData: Partial<Testimonial>): Promise<Testimonial> => {
    const response: AxiosResponse<Testimonial> = await api.put(`/api/testimonies/testimonials/${id}/`, testimonialData);
    return response.data;
  },

  deleteTestimonial: async (id: number): Promise<void> => {
    await api.delete(`/api/testimonies/testimonials/${id}/`);
  },
};

// Partners API
export const partnersAPI = {
  getPartners: async (): Promise<ApiResponse<Partner>> => {
    const response: AxiosResponse<ApiResponse<Partner>> = await api.get('/api/partners/');
    return response.data;
  },

  createPartner: async (partnerData: Partial<Partner>): Promise<Partner> => {
    const response: AxiosResponse<Partner> = await api.post('/api/partners/', partnerData);
    return response.data;
  },

  updatePartner: async (id: number, partnerData: Partial<Partner>): Promise<Partner> => {
    const response: AxiosResponse<Partner> = await api.put(`/api/partners/${id}/`, partnerData);
    return response.data;
  },

  deletePartner: async (id: number): Promise<void> => {
    await api.delete(`/api/partners/${id}/`);
  },
};

// Feedback API
export const feedbackAPI = {
  getFeedbacks: async (): Promise<ApiResponse<Feedback>> => {
    const response: AxiosResponse<ApiResponse<Feedback>> = await api.get('/api/feedbacks/');
    return response.data;
  },

  createFeedback: async (feedbackData: Partial<Feedback>): Promise<Feedback> => {
    const response: AxiosResponse<Feedback> = await api.post('/api/feedbacks/', feedbackData);
    return response.data;
  },

  updateFeedback: async (id: number, feedbackData: Partial<Feedback>): Promise<Feedback> => {
    const response: AxiosResponse<Feedback> = await api.put(`/api/feedbacks/${id}/`, feedbackData);
    return response.data;
  },

  deleteFeedback: async (id: number): Promise<void> => {
    await api.delete(`/api/feedbacks/${id}/`);
  },
};

// Club API
export const clubAPI = {
  getClubDetails: async (): Promise<Club> => {
    const response: AxiosResponse<Club> = await api.get('/api/club/');
    return response.data;
  },

  getExecutives: async (): Promise<ApiResponse<ExecutiveMember>> => {
    const response: AxiosResponse<ApiResponse<ExecutiveMember>> = await api.get('/api/executives/');
    return response.data;
  },

  createExecutive: async (executiveData: Partial<ExecutiveMember>): Promise<ExecutiveMember> => {
    const response: AxiosResponse<ExecutiveMember> = await api.post('/api/executives/', executiveData);
    return response.data;
  },

  updateExecutive: async (id: number, executiveData: Partial<ExecutiveMember>): Promise<ExecutiveMember> => {
    const response: AxiosResponse<ExecutiveMember> = await api.put(`/api/executives/${id}/`, executiveData);
    return response.data;
  },

  deleteExecutive: async (id: number): Promise<void> => {
    await api.delete(`/api/executives/${id}/`);
  },
};

// Communications API
export const communicationsAPI = {
  subscribe: async (email: string): Promise<NewsletterSubscription> => {
    const response: AxiosResponse<NewsletterSubscription> = await api.post('/api/subscribe/', { email });
    return response.data;
  },

  sendContact: async (contactData: Partial<ContactMessage>): Promise<ContactMessage> => {
    const response: AxiosResponse<ContactMessage> = await api.post('/api/contact/', contactData);
    return response.data;
  },

  sendNewsletter: async (subject: string, message: string): Promise<void> => {
    await api.post('/api/newsletter/', { subject, message });
  },
};

// Utility functions
export const handleApiError = (error: AxiosError): string => {
  if (error.response?.data) {
    const apiError = error.response.data as ApiError;
    if (apiError.detail) return apiError.detail;
    if (apiError.message) return apiError.message;
    if (apiError.errors) {
      const firstError = Object.values(apiError.errors)[0];
      return Array.isArray(firstError) ? firstError[0] : firstError;
    }
  }
  return error.message || 'An unexpected error occurred';
};

export default api;