import { format, parseISO, isValid } from 'date-fns';
import { DATE_FORMATS } from './constants';

// Date formatting utilities
export const formatDate = (date: string | Date, formatStr: string = DATE_FORMATS.display): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return isValid(dateObj) ? format(dateObj, formatStr) : 'Invalid date';
  } catch (error) {
    return 'Invalid date';
  }
};

export const formatDateTime = (date: string | Date): string => {
  return formatDate(date, DATE_FORMATS.displayWithTime);
};

export const formatDateForInput = (date: string | Date): string => {
  return formatDate(date, DATE_FORMATS.input);
};

export const formatDateTimeForInput = (date: string | Date): string => {
  return formatDate(date, DATE_FORMATS.inputWithTime);
};

// String utilities
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

export const capitalizeFirst = (text: string): string => {
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

export const slugify = (text: string): string => {
  return text
    .toLowerCase()
    .replace(/[^\w ]+/g, '')
    .replace(/ +/g, '-');
};

// Validation utilities
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidPhone = (phone: string): boolean => {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
  return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
};

export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

// Array utilities
export const removeDuplicates = <T>(array: T[], key?: keyof T): T[] => {
  if (!key) {
    return [...new Set(array)];
  }
  
  const seen = new Set();
  return array.filter(item => {
    const value = item[key];
    if (seen.has(value)) {
      return false;
    }
    seen.add(value);
    return true;
  });
};

export const sortByKey = <T>(array: T[], key: keyof T, direction: 'asc' | 'desc' = 'asc'): T[] => {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    
    if (aVal < bVal) return direction === 'asc' ? -1 : 1;
    if (aVal > bVal) return direction === 'asc' ? 1 : -1;
    return 0;
  });
};

// Object utilities
export const omit = <T extends Record<string, any>, K extends keyof T>(
  obj: T,
  keys: K[]
): Omit<T, K> => {
  const result = { ...obj };
  keys.forEach(key => delete result[key]);
  return result;
};

export const pick = <T extends Record<string, any>, K extends keyof T>(
  obj: T,
  keys: K[]
): Pick<T, K> => {
  const result = {} as Pick<T, K>;
  keys.forEach(key => {
    if (key in obj) {
      result[key] = obj[key];
    }
  });
  return result;
};

// Local storage utilities
export const getFromStorage = <T>(key: string, defaultValue: T): T => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch {
    return defaultValue;
  }
};

export const setToStorage = <T>(key: string, value: T): void => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error('Error saving to localStorage:', error);
  }
};

export const removeFromStorage = (key: string): void => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error('Error removing from localStorage:', error);
  }
};

// File utilities
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const isImageFile = (file: File): boolean => {
  return file.type.startsWith('image/');
};

export const readFileAsDataURL = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

// URL utilities
export const buildUrl = (baseUrl: string, params: Record<string, any>): string => {
  const url = new URL(baseUrl);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      url.searchParams.append(key, String(value));
    }
  });
  return url.toString();
};

export const getQueryParams = (): Record<string, string> => {
  const params = new URLSearchParams(window.location.search);
  const result: Record<string, string> = {};
  params.forEach((value, key) => {
    result[key] = value;
  });
  return result;
};

// Color utilities
export const hexToRgb = (hex: string): { r: number; g: number; b: number } | null => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
};

export const rgbToHex = (r: number, g: number, b: number): string => {
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
};

// Debounce utility
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

// Throttle utility
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let lastCall = 0;
  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      func(...args);
    }
  };
};

// Generate random ID
export const generateId = (length: number = 8): string => {
  return Math.random().toString(36).substring(2, 2 + length);
};

// Check if user is admin
export const isAdmin = (user: any): boolean => {
  return user?.is_staff === true || user?.is_superuser === true;
};

// Format user display name
export const formatUserName = (user: any): string => {
  if (user?.first_name && user?.last_name) {
    return `${user.first_name} ${user.last_name}`;
  }
  return user?.username || 'Unknown User';
};

// Get initials from name
export const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
};

// Event category helpers
export const getCategoryColor = (category: string): string => {
  const categoryMap: Record<string, string> = {
    WEB: 'bg-blue-100 text-blue-800',
    CYBERSEC: 'bg-red-100 text-red-800',
    ANDROID: 'bg-green-100 text-green-800',
    AI: 'bg-purple-100 text-purple-800',
    BLOCKCHAIN: 'bg-yellow-100 text-yellow-800',
    IoT: 'bg-indigo-100 text-indigo-800',
    CLOUD: 'bg-gray-100 text-gray-800',
  };
  return categoryMap[category] || 'bg-gray-100 text-gray-800';
};

export const getCategoryLabel = (category: string): string => {
  const categoryMap: Record<string, string> = {
    WEB: 'Web Development',
    CYBERSEC: 'Cyber Security',
    ANDROID: 'Android Development',
    AI: 'Artificial Intelligence',
    BLOCKCHAIN: 'Blockchain',
    IoT: 'Internet of Things',
    CLOUD: 'Cloud Computing',
  };
  return categoryMap[category] || category;
};

// Status helpers
export const getStatusColor = (status: string): string => {
  const statusMap: Record<string, string> = {
    PENDING: 'bg-yellow-100 text-yellow-800',
    CONFIRMED: 'bg-green-100 text-green-800',
    CANCELLED: 'bg-red-100 text-red-800',
    REVIEWED: 'bg-blue-100 text-blue-800',
    RESOLVED: 'bg-green-100 text-green-800',
  };
  return statusMap[status] || 'bg-gray-100 text-gray-800';
};

export default {
  formatDate,
  formatDateTime,
  formatDateForInput,
  formatDateTimeForInput,
  truncateText,
  capitalizeFirst,
  slugify,
  isValidEmail,
  isValidPhone,
  isValidUrl,
  removeDuplicates,
  sortByKey,
  omit,
  pick,
  getFromStorage,
  setToStorage,
  removeFromStorage,
  formatFileSize,
  isImageFile,
  readFileAsDataURL,
  buildUrl,
  getQueryParams,
  hexToRgb,
  rgbToHex,
  debounce,
  throttle,
  generateId,
  isAdmin,
  formatUserName,
  getInitials,
  getCategoryColor,
  getCategoryLabel,
  getStatusColor,
};