"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: number;
  email?: string;
  mobile_number?: string;
  full_name?: string;
  avatar_url?: string;
  auth_provider: string;
}

interface AuthResult {
  success: boolean;
  message?: string;
  user?: User;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  
  // Authentication methods
  signup: (userData: Record<string, unknown>) => Promise<AuthResult>;
  loginWithEmail: (email: string, password: string) => Promise<AuthResult>;
  googleLogin: (credential: string) => Promise<AuthResult>;
  sendOTP: (mobileNumber: string) => Promise<AuthResult>;
  verifyOTP: (mobileNumber: string, otp: string) => Promise<AuthResult>;
  logout: () => Promise<void>;
  
  // Utility methods
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // API base URL - adjust based on environment
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://stealth-tinko-prod-app-1762804410.azurewebsites.net';

  const isAuthenticated = user !== null;

  // Initialize auth state on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (token) {
        // Verify token and get user data
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData.user);
        } else {
          // Token invalid, remove it
          localStorage.removeItem('auth_token');
        }
      }
    } catch (error) {
      console.error('Auth initialization failed:', error);
      localStorage.removeItem('auth_token');
    } finally {
      setLoading(false);
    }
  };

  const makeAuthRequest = async (endpoint: string, body: Record<string, unknown>): Promise<Record<string, unknown>> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Request failed');
    }

    return data;
  };

  const handleAuthSuccess = (authData: Record<string, unknown>): AuthResult => {
    const { access_token, user: userData } = authData;
    
    if (access_token) {
      localStorage.setItem('auth_token', access_token);
    }
    
    if (userData) {
      setUser(userData);
    }

    return {
      success: true,
      user: userData,
    };
  };

  const signup = async (userData: {
    full_name: string;
    email?: string;
    mobile_number?: string;
    password?: string;
  }): Promise<AuthResult> => {
    try {
      setLoading(true);
      const response = await makeAuthRequest('/auth/signup', userData);
      
      return {
        success: true,
        message: response.message || 'Account created successfully',
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Signup failed',
      };
    } finally {
      setLoading(false);
    }
  };

  const loginWithEmail = async (email: string, password: string): Promise<AuthResult> => {
    try {
      setLoading(true);
      const response = await makeAuthRequest('/auth/login', { email, password });
      return handleAuthSuccess(response);
    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Login failed',
      };
    } finally {
      setLoading(false);
    }
  };

  const googleLogin = async (credential: string): Promise<AuthResult> => {
    try {
      setLoading(true);
      const response = await makeAuthRequest('/auth/google', { 
        access_token: credential 
      });
      return handleAuthSuccess(response);
    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Google login failed',
      };
    } finally {
      setLoading(false);
    }
  };

  const sendOTP = async (mobileNumber: string): Promise<AuthResult> => {
    try {
      setLoading(true);
      const response = await makeAuthRequest('/auth/mobile/send-otp', {
        mobile_number: mobileNumber,
      });
      
      return {
        success: true,
        message: response.message || 'OTP sent successfully',
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Failed to send OTP',
      };
    } finally {
      setLoading(false);
    }
  };

  const verifyOTP = async (mobileNumber: string, otp: string): Promise<AuthResult> => {
    try {
      setLoading(true);
      const response = await makeAuthRequest('/auth/mobile/verify-otp', {
        mobile_number: mobileNumber,
        otp,
      });
      return handleAuthSuccess(response);
    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Invalid OTP',
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      // Call logout endpoint if available
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });
        } catch (error) {
          console.error('Logout API call failed:', error);
        }
      }
    } finally {
      // Always clear local state
      localStorage.removeItem('auth_token');
      setUser(null);
    }
  };

  const refreshUser = async (): Promise<void> => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) return;

      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData.user);
      } else {
        await logout();
      }
    } catch (error) {
      console.error('Failed to refresh user:', error);
      await logout();
    }
  };

  const contextValue: AuthContextType = {
    user,
    loading,
    isAuthenticated,
    signup,
    loginWithEmail,
    googleLogin,
    sendOTP,
    verifyOTP,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}