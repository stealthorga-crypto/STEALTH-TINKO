/**
 * API configuration for STEALTH-TINKO
 * Handles different environments and service endpoints
 */

interface ApiConfig {
  backendUrl: string;
  staticApiUrl: string;
  isProduction: boolean;
}

const getApiConfig = (): ApiConfig => {
  const isProduction = process.env.NODE_ENV === 'production';
  
  // Backend API - your existing Azure App Service
  const backendUrl = isProduction
    ? (process.env.NEXT_PUBLIC_BACKEND_URL || 'https://stealth-tinko-prod-app-1762804410.azurewebsites.net')
    : 'http://localhost:8000';
    
  // Static Web App API functions for lightweight operations
  const staticApiUrl = isProduction
    ? '/api' // SWA API routes
    : 'http://localhost:7071/api'; // Local Azure Functions

  return { 
    backendUrl, 
    staticApiUrl, 
    isProduction 
  };
};

export const API_CONFIG = getApiConfig();

export const API_ENDPOINTS = {
  // Authentication endpoints (via backend)
  AUTH: {
    GOOGLE_LOGIN: `${API_CONFIG.backendUrl}/auth/google`,
    MOBILE_SEND_OTP: `${API_CONFIG.backendUrl}/auth/mobile/send-otp`,
    MOBILE_VERIFY_OTP: `${API_CONFIG.backendUrl}/auth/mobile/verify-otp`,
    SIGNUP: `${API_CONFIG.backendUrl}/auth/signup`,
    LOGIN: `${API_CONFIG.backendUrl}/auth/login`,
    REFRESH: `${API_CONFIG.backendUrl}/auth/refresh`,
    LOGOUT: `${API_CONFIG.backendUrl}/auth/logout`,
    ME: `${API_CONFIG.backendUrl}/auth/me`,
  },
  
  // Core business logic (via backend)
  RECOVERY: {
    CREATE: `${API_CONFIG.backendUrl}/recovery/create`,
    VALIDATE: `${API_CONFIG.backendUrl}/recovery/validate`,
    COMPLETE: `${API_CONFIG.backendUrl}/recovery/complete`,
  },
  
  // Analytics and reporting (via backend)
  ANALYTICS: {
    DASHBOARD: `${API_CONFIG.backendUrl}/analytics/dashboard`,
    RECOVERY_STATS: `${API_CONFIG.backendUrl}/analytics/recovery-stats`,
  },
  
  // Lightweight operations (via SWA API)
  STATIC: {
    VALIDATE_TOKEN: `${API_CONFIG.staticApiUrl}/validate-token`,
    HEALTH: `${API_CONFIG.staticApiUrl}/health`,
    CONFIG: `${API_CONFIG.staticApiUrl}/config`,
  }
};

/**
 * Helper function to make authenticated API requests
 */
export const apiRequest = async (
  endpoint: string, 
  options: RequestInit = {},
  useAuth: boolean = true
) => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (useAuth && typeof window !== 'undefined') {
    const token = localStorage.getItem('tinko_auth_token');
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(endpoint, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
  }

  return response.json();
};

export default API_CONFIG;