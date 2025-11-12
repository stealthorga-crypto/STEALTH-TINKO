'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AuthAPI } from '@/lib/auth-api';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; message?: string }>;
  register: (email: string, password: string, name: string, orgName?: string) => Promise<{ success: boolean; message?: string }>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Check for existing session on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        let token = localStorage.getItem('auth_token');
        
        // If no token in localStorage, check cookies
        if (!token) {
          const cookies = document.cookie.split(';');
          const authCookie = cookies.find(cookie => cookie.trim().startsWith('auth_token='));
          if (authCookie) {
            token = authCookie.split('=')[1];
            // Store in localStorage for consistency
            localStorage.setItem('auth_token', token);
          }
        }
        
        if (token) {
          // Try to validate the existing token
          const response = await AuthAPI.validateToken(token);
          if (response.success && response.user) {
            setUser(response.user);
            
            // Ensure cookie is set
            document.cookie = `auth_token=${token}; path=/; max-age=86400; samesite=lax; secure=${window.location.protocol === 'https:'}`;
            
            // Try to get fresh profile data
            const profileResponse = await AuthAPI.getProfile(token);
            if (profileResponse.success && profileResponse.user) {
              setUser(profileResponse.user);
              localStorage.setItem('user_data', JSON.stringify(profileResponse.user));
            }
          } else {
            // Invalid token, clear it
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_data');
            document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
          }
        } else {
          // No token, check if we have cached user data (for development)
          const cachedUser = localStorage.getItem('user_data');
          if (cachedUser) {
            try {
              setUser(JSON.parse(cachedUser));
            } catch (error) {
              localStorage.removeItem('user_data');
            }
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        // Clear potentially corrupted data
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await AuthAPI.login({ email, password });
      
      if (response.success && response.token && response.user) {
        localStorage.setItem('auth_token', response.token);
        localStorage.setItem('user_data', JSON.stringify(response.user));
        
        // Set auth token in cookie for middleware to access
        document.cookie = `auth_token=${response.token}; path=/; max-age=86400; samesite=lax; secure=${window.location.protocol === 'https:'}`;
        
        setUser(response.user);
        return { success: true };
      } else {
        return { 
          success: false, 
          message: response.message || 'Login failed' 
        };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        message: 'Network error. Please try again.' 
      };
    }
  };

  const register = async (email: string, password: string, name: string, orgName?: string) => {
    try {
      const response = await AuthAPI.register({ email, password, name, orgName });
      
      if (response.success && response.token && response.user) {
        localStorage.setItem('auth_token', response.token);
        localStorage.setItem('user_data', JSON.stringify(response.user));
        
        // Set auth token in cookie for middleware to access
        document.cookie = `auth_token=${response.token}; path=/; max-age=86400; samesite=lax; secure=${window.location.protocol === 'https:'}`;
        
        setUser(response.user);
        return { success: true };
      } else {
        return { 
          success: false, 
          message: response.message || 'Registration failed' 
        };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        message: 'Network error. Please try again.' 
      };
    }
  };

  const logout = async () => {
    try {
      await AuthAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear localStorage
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
      
      // Clear auth cookie
      document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
      
      setUser(null);
      router.push('/');
    }
  };

  const refreshProfile = async () => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      try {
        const response = await AuthAPI.getProfile(token);
        if (response.success && response.user) {
          setUser(response.user);
          localStorage.setItem('user_data', JSON.stringify(response.user));
        }
      } catch (error) {
        console.error('Profile refresh error:', error);
      }
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};