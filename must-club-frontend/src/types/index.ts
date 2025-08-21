// User and Authentication Types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_active: boolean;
  date_joined: string;
}

export interface UserProfile {
  user: User;
  course: string;
  registration_no?: string;
  bio?: string;
  tech_stacks?: string[];
  social_media?: Record<string, string>;
  photo?: string;
  graduation_year?: number;
  projects?: string;
  skills?: string;
  year_of_study?: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  course: string;
  registration_no?: string;
  year_of_study?: number;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

// Event Types
export interface Event {
  id: number;
  name: string;
  category: 'WEB' | 'CYBERSEC' | 'ANDROID' | 'AI' | 'BLOCKCHAIN' | 'IoT' | 'CLOUD';
  title: string;
  description: string;
  image_url: string;
  date: string;
  location: string;
  organizer: string;
  contact_email?: string;
  is_virtual: boolean;
}

export interface EventRegistration {
  id: number;
  event: number;
  user: number;
  registration_date: string;
  status: 'PENDING' | 'CONFIRMED' | 'CANCELLED';
}

// Community Types
export interface CommunityProfile {
  id: number;
  name: string;
  club: number;
  community_lead?: User;
  co_lead?: User;
  secretary?: User;
  email?: string;
  phone_number?: string;
  description: string;
  meeting_type: 'VIRTUAL' | 'PHYSICAL' | 'HYBRID';
  meeting_day?: string;
  meeting_time?: string;
  meeting_link?: string;
  meeting_location?: string;
  member_count: number;
  created_at: string;
}

// Blog Types
export interface BlogPost {
  id: number;
  title: string;
  content: string;
  author: User;
  created_at: string;
  updated_at: string;
  published: boolean;
}

// Comment Types
export interface Comment {
  id: number;
  event: number;
  user: User;
  content: string;
  created_at: string;
  parent?: number;
  replies?: Comment[];
}

// Testimonial Types
export interface Testimonial {
  id: number;
  user: User;
  content: string;
  rating: number;
  created_at: string;
  is_approved: boolean;
}

// Partner Types
export interface Partner {
  id: number;
  name: string;
  logo: string;
  website?: string;
  description?: string;
  partnership_type: string;
  created_at: string;
}

// Feedback Types
export interface Feedback {
  id: number;
  user?: User;
  email?: string;
  subject: string;
  message: string;
  category: string;
  status: 'PENDING' | 'REVIEWED' | 'RESOLVED';
  created_at: string;
  screenshot?: string;
}

// Club Types
export interface ExecutiveMember {
  id: number;
  user: User;
  position: string;
  bio?: string;
  photo?: string;
  start_date: string;
  end_date?: string;
  is_active: boolean;
}

export interface Club {
  id: number;
  name: string;
  description: string;
  mission?: string;
  vision?: string;
  established_date: string;
  logo?: string;
}

// Communication Types
export interface NewsletterSubscription {
  id: number;
  email: string;
  subscribed_at: string;
  is_active: boolean;
}

export interface ContactMessage {
  id: number;
  name: string;
  email: string;
  subject: string;
  message: string;
  created_at: string;
  is_responded: boolean;
}

// API Response Types
export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
}

// Form Types
export interface LoginFormData {
  username: string;
  password: string;
}

export interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  first_name: string;
  last_name: string;
  course: string;
  registration_no?: string;
  year_of_study?: number;
}

export interface ProfileUpdateFormData {
  first_name: string;
  last_name: string;
  email: string;
  course: string;
  registration_no?: string;
  bio?: string;
  tech_stacks?: string[];
  graduation_year?: number;
  year_of_study?: number;
  skills?: string;
  projects?: string;
}

// Navigation Types
export interface NavigationItem {
  name: string;
  href: string;
  icon?: React.ComponentType<any>;
  current?: boolean;
}

// Theme Types
export type Theme = 'light' | 'dark';

// Loading States
export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}