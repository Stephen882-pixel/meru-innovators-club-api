// API Base URL
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Event Categories
export const EVENT_CATEGORIES = [
  { value: 'WEB', label: 'Web Development', color: 'bg-blue-100 text-blue-800' },
  { value: 'CYBERSEC', label: 'Cyber Security', color: 'bg-red-100 text-red-800' },
  { value: 'ANDROID', label: 'Android Development', color: 'bg-green-100 text-green-800' },
  { value: 'AI', label: 'Artificial Intelligence', color: 'bg-purple-100 text-purple-800' },
  { value: 'BLOCKCHAIN', label: 'Blockchain', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'IoT', label: 'Internet of Things', color: 'bg-indigo-100 text-indigo-800' },
  { value: 'CLOUD', label: 'Cloud Computing', color: 'bg-gray-100 text-gray-800' },
];

// Meeting Types
export const MEETING_TYPES = [
  { value: 'VIRTUAL', label: 'Virtual' },
  { value: 'PHYSICAL', label: 'Physical' },
  { value: 'HYBRID', label: 'Hybrid' },
];

// Feedback Categories
export const FEEDBACK_CATEGORIES = [
  { value: 'GENERAL', label: 'General Feedback' },
  { value: 'BUG', label: 'Bug Report' },
  { value: 'FEATURE', label: 'Feature Request' },
  { value: 'COMPLAINT', label: 'Complaint' },
  { value: 'SUGGESTION', label: 'Suggestion' },
];

// Feedback Status
export const FEEDBACK_STATUS = [
  { value: 'PENDING', label: 'Pending', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'REVIEWED', label: 'Reviewed', color: 'bg-blue-100 text-blue-800' },
  { value: 'RESOLVED', label: 'Resolved', color: 'bg-green-100 text-green-800' },
];

// Registration Status
export const REGISTRATION_STATUS = [
  { value: 'PENDING', label: 'Pending', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'CONFIRMED', label: 'Confirmed', color: 'bg-green-100 text-green-800' },
  { value: 'CANCELLED', label: 'Cancelled', color: 'bg-red-100 text-red-800' },
];

// Tech Stacks
export const TECH_STACKS = [
  'JavaScript',
  'TypeScript',
  'React',
  'Vue.js',
  'Angular',
  'Node.js',
  'Python',
  'Django',
  'Flask',
  'Java',
  'Spring Boot',
  'C#',
  '.NET',
  'PHP',
  'Laravel',
  'Ruby',
  'Rails',
  'Go',
  'Rust',
  'Swift',
  'Kotlin',
  'Flutter',
  'React Native',
  'MongoDB',
  'PostgreSQL',
  'MySQL',
  'Redis',
  'Docker',
  'Kubernetes',
  'AWS',
  'Azure',
  'GCP',
  'Git',
  'Linux',
];

// Courses (common courses at Meru University)
export const COURSES = [
  'Computer Science',
  'Information Technology',
  'Software Engineering',
  'Data Science',
  'Cybersecurity',
  'Network Engineering',
  'Electronics and Computer Engineering',
  'Mathematics and Computer Science',
  'Business Information Technology',
  'Other',
];

// Years of Study
export const YEARS_OF_STUDY = [
  { value: 1, label: 'First Year' },
  { value: 2, label: 'Second Year' },
  { value: 3, label: 'Third Year' },
  { value: 4, label: 'Fourth Year' },
  { value: 5, label: 'Fifth Year' },
];

// Days of the Week
export const DAYS_OF_WEEK = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
];

// Executive Positions
export const EXECUTIVE_POSITIONS = [
  'President',
  'Vice President',
  'Secretary',
  'Treasurer',
  'Organizing Secretary',
  'Technical Lead',
  'Community Lead',
  'Marketing Lead',
  'Member',
];

// Navigation Items for User Dashboard
export const USER_NAV_ITEMS = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Events', href: '/events' },
  { name: 'Communities', href: '/communities' },
  { name: 'Blog', href: '/blog' },
  { name: 'Profile', href: '/profile' },
];

// Navigation Items for Admin Dashboard
export const ADMIN_NAV_ITEMS = [
  { name: 'Dashboard', href: '/admin' },
  { name: 'Users', href: '/admin/users' },
  { name: 'Events', href: '/admin/events' },
  { name: 'Communities', href: '/admin/communities' },
  { name: 'Blog', href: '/admin/blog' },
  { name: 'Feedback', href: '/admin/feedback' },
  { name: 'Partners', href: '/admin/partners' },
  { name: 'Testimonials', href: '/admin/testimonials' },
  { name: 'Executives', href: '/admin/executives' },
];

// Theme Colors
export const THEME_COLORS = {
  primary: {
    50: '#fefce8',
    100: '#fef3c7',
    200: '#fde68a',
    300: '#fcd34d',
    400: '#fbbf24',
    500: '#f59e0b', // Main yellow
    600: '#d97706',
    700: '#b45309',
    800: '#92400e',
    900: '#78350f',
  },
  secondary: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e', // Main green
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
  },
};

// Default Profile Photo
export const DEFAULT_PROFILE_PHOTO = '/images/default-avatar.png';

// Pagination
export const DEFAULT_PAGE_SIZE = 10;

// File Upload Limits
export const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
export const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

// Date Formats
export const DATE_FORMATS = {
  display: 'MMM dd, yyyy',
  displayWithTime: 'MMM dd, yyyy hh:mm a',
  input: 'yyyy-MM-dd',
  inputWithTime: "yyyy-MM-dd'T'HH:mm",
};

// Social Media Platforms
export const SOCIAL_MEDIA_PLATFORMS = [
  { name: 'LinkedIn', icon: 'linkedin', baseUrl: 'https://linkedin.com/in/' },
  { name: 'GitHub', icon: 'github', baseUrl: 'https://github.com/' },
  { name: 'Twitter', icon: 'twitter', baseUrl: 'https://twitter.com/' },
  { name: 'Instagram', icon: 'instagram', baseUrl: 'https://instagram.com/' },
  { name: 'Facebook', icon: 'facebook', baseUrl: 'https://facebook.com/' },
  { name: 'Website', icon: 'globe', baseUrl: '' },
];

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  FORBIDDEN: 'Access denied.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  UNKNOWN_ERROR: 'An unexpected error occurred.',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN: 'Login successful!',
  REGISTER: 'Registration successful!',
  LOGOUT: 'Logged out successfully',
  PROFILE_UPDATED: 'Profile updated successfully!',
  EVENT_CREATED: 'Event created successfully!',
  EVENT_UPDATED: 'Event updated successfully!',
  EVENT_DELETED: 'Event deleted successfully!',
  COMMUNITY_JOINED: 'Successfully joined the community!',
  FEEDBACK_SUBMITTED: 'Feedback submitted successfully!',
  NEWSLETTER_SUBSCRIBED: 'Successfully subscribed to newsletter!',
};

export default {
  API_BASE_URL,
  EVENT_CATEGORIES,
  MEETING_TYPES,
  FEEDBACK_CATEGORIES,
  FEEDBACK_STATUS,
  REGISTRATION_STATUS,
  TECH_STACKS,
  COURSES,
  YEARS_OF_STUDY,
  DAYS_OF_WEEK,
  EXECUTIVE_POSITIONS,
  USER_NAV_ITEMS,
  ADMIN_NAV_ITEMS,
  THEME_COLORS,
  DEFAULT_PROFILE_PHOTO,
  DEFAULT_PAGE_SIZE,
  MAX_FILE_SIZE,
  ALLOWED_IMAGE_TYPES,
  DATE_FORMATS,
  SOCIAL_MEDIA_PLATFORMS,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
};