import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { User, UserProfile, LoginCredentials, RegisterData } from '../types';
import { authAPI, handleApiError } from '../services/api';
import { toast } from 'react-toastify';

interface AuthState {
  user: User | null;
  profile: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  updateProfile: (profileData: any) => Promise<void>;
  clearError: () => void;
}

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; profile?: UserProfile } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_PROFILE'; payload: UserProfile }
  | { type: 'CLEAR_ERROR' }
  | { type: 'SET_LOADING'; payload: boolean };

const initialState: AuthState = {
  user: null,
  profile: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        profile: action.payload.profile || null,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        profile: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        profile: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    case 'UPDATE_PROFILE':
      return {
        ...state,
        profile: action.payload,
        user: action.payload.user,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    default:
      return state;
  }
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check for existing authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          dispatch({ type: 'AUTH_START' });
          const profileData = await authAPI.getUserData();
          dispatch({ 
            type: 'AUTH_SUCCESS', 
            payload: { 
              user: profileData.user, 
              profile: profileData 
            } 
          });
        } catch (error: any) {
          console.error('Auth check failed:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          dispatch({ type: 'AUTH_FAILURE', payload: 'Session expired' });
        }
      } else {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      dispatch({ type: 'AUTH_START' });
      const authResponse = await authAPI.login(credentials);
      
      // Store tokens
      localStorage.setItem('access_token', authResponse.access);
      localStorage.setItem('refresh_token', authResponse.refresh);
      
      // Get user profile
      const profileData = await authAPI.getUserData();
      
      dispatch({ 
        type: 'AUTH_SUCCESS', 
        payload: { 
          user: authResponse.user, 
          profile: profileData 
        } 
      });
      
      toast.success('Login successful!');
    } catch (error: any) {
      const errorMessage = handleApiError(error);
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      toast.error(errorMessage);
      throw error;
    }
  };

  const register = async (userData: RegisterData) => {
    try {
      dispatch({ type: 'AUTH_START' });
      const authResponse = await authAPI.register(userData);
      
      // Store tokens
      localStorage.setItem('access_token', authResponse.access);
      localStorage.setItem('refresh_token', authResponse.refresh);
      
      // Get user profile
      const profileData = await authAPI.getUserData();
      
      dispatch({ 
        type: 'AUTH_SUCCESS', 
        payload: { 
          user: authResponse.user, 
          profile: profileData 
        } 
      });
      
      toast.success('Registration successful!');
    } catch (error: any) {
      const errorMessage = handleApiError(error);
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      toast.error(errorMessage);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      // Even if logout fails on server, we still clear local data
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      dispatch({ type: 'LOGOUT' });
      toast.info('Logged out successfully');
    }
  };

  const updateProfile = async (profileData: any) => {
    try {
      const updatedProfile = await authAPI.updateProfile(profileData);
      dispatch({ type: 'UPDATE_PROFILE', payload: updatedProfile });
      toast.success('Profile updated successfully!');
    } catch (error: any) {
      const errorMessage = handleApiError(error);
      toast.error(errorMessage);
      throw error;
    }
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    updateProfile,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};