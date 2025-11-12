import { MockAuthAPI } from './mock-auth-api';

interface AuthResponse {
  success: boolean;
  token?: string;
  user?: {
    id: string;
    email: string;
    name: string;
  };
  message?: string;
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterCredentials {
  email: string;
  password: string;
  name: string;
  orgName?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://stealth-tinko-prod-app-1762804410.azurewebsites.net';

// For now, use mock API since backend auth endpoints are not deployed
// Change USE_MOCK_API to false when backend auth endpoints are working
const USE_MOCK_API = true;

export class AuthAPI {
  static async login(credentials: LoginCredentials): Promise<AuthResponse> {
    if (USE_MOCK_API) {
      return MockAuthAPI.login(credentials);
    }
    
    try {
      const response = await fetch(`${API_BASE}/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Login failed' }));
        return {
          success: false,
          message: errorData.message || `HTTP ${response.status}: Login failed`,
        };
      }

      const data = await response.json();
      
      // Handle different response formats from your backend
      if (data.token || data.access_token) {
        return {
          success: true,
          token: data.token || data.access_token,
          user: data.user || { id: data.id, email: credentials.email, name: data.name },
        };
      }
      
      return {
        success: false,
        message: data.message || 'Invalid credentials',
      };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        message: 'Network error. Please check your connection and try again.',
      };
    }
  }

  static async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    if (USE_MOCK_API) {
      return MockAuthAPI.register(credentials);
    }
    
    try {
      // Transform to backend expected format
      const payload = {
        full_name: credentials.name,
        email: credentials.email,
        password: credentials.password,
        ...(credentials.orgName && { org_name: credentials.orgName }),
      };

      const response = await fetch(`${API_BASE}/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Registration failed' }));
        return {
          success: false,
          message: errorData.message || `HTTP ${response.status}: Registration failed`,
        };
      }

      const data = await response.json();
      
      if (data.token || data.access_token) {
        return {
          success: true,
          token: data.token || data.access_token,
          user: data.user || { id: data.id, email: credentials.email, name: credentials.name },
        };
      }
      
      return {
        success: false,
        message: data.message || 'Registration failed',
      };
    } catch (error) {
      console.error('Register error:', error);
      return {
        success: false,
        message: 'Network error. Please check your connection and try again.',
      };
    }
  }

  static async validateToken(token: string): Promise<AuthResponse> {
    if (USE_MOCK_API) {
      return MockAuthAPI.validateToken(token);
    }
    
    try {
      const response = await fetch(`${API_BASE}/v1/auth/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        return {
          success: false,
          message: 'Session expired. Please login again.',
        };
      }

      const data = await response.json();
      
      if (data.valid || data.success) {
        return {
          success: true,
          user: data.user || data,
        };
      }
      
      return {
        success: false,
        message: 'Invalid session. Please login again.',
      };
    } catch (error) {
      console.error('Token validation error:', error);
      return {
        success: false,
        message: 'Session expired. Please login again.',
      };
    }
  }

  static async logout(): Promise<void> {
    if (USE_MOCK_API) {
      return MockAuthAPI.logout();
    }
    
    const token = localStorage.getItem('auth_token');
    
    // Clear local storage first
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    
    // Optional: Call backend logout endpoint if you have one
    try {
      if (token) {
        await fetch(`${API_BASE}/v1/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.log('Logout call failed, but clearing local session anyway');
    }
  }

  static async getProfile(token: string): Promise<AuthResponse> {
    if (USE_MOCK_API) {
      return MockAuthAPI.getProfile(token);
    }
    
    try {
      const response = await fetch(`${API_BASE}/v1/auth/profile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        return {
          success: false,
          message: 'Failed to fetch profile',
        };
      }

      const data = await response.json();
      return {
        success: true,
        user: data,
      };
    } catch (error) {
      console.error('Get profile error:', error);
      return {
        success: false,
        message: 'Failed to fetch profile',
      };
    }
  }
}