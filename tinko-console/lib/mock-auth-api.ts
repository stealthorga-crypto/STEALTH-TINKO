// Mock authentication API for testing frontend functionality
// This simulates successful authentication without requiring a working backend

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

export class MockAuthAPI {
  private static delay(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  static async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Simulate network delay
    await this.delay(1000);
    
    // Mock validation - accept any email/password for demo
    if (credentials.email && credentials.password) {
      const mockToken = `mock_token_${Date.now()}`;
      const mockUser = {
        id: '1',
        email: credentials.email,
        name: credentials.email.split('@')[0].replace('.', ' '),
      };

      return {
        success: true,
        token: mockToken,
        user: mockUser,
      };
    }

    return {
      success: false,
      message: 'Please enter both email and password',
    };
  }

  static async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    // Simulate network delay
    await this.delay(1200);
    
    // Mock validation
    if (credentials.email && credentials.password && credentials.name) {
      const mockToken = `mock_token_${Date.now()}`;
      const mockUser = {
        id: '1',
        email: credentials.email,
        name: credentials.name,
      };

      return {
        success: true,
        token: mockToken,
        user: mockUser,
      };
    }

    return {
      success: false,
      message: 'Please fill in all required fields',
    };
  }

  static async validateToken(token: string): Promise<AuthResponse> {
    // Simulate network delay
    await this.delay(500);
    
    // Mock token validation - accept any token that starts with 'mock_token_'
    if (token && token.startsWith('mock_token_')) {
      return {
        success: true,
        user: {
          id: '1',
          email: 'demo@tinko.com',
          name: 'Demo User',
        },
      };
    }

    return {
      success: false,
      message: 'Invalid token',
    };
  }

  static async getProfile(token: string): Promise<AuthResponse> {
    // Simulate network delay
    await this.delay(300);
    
    if (token && token.startsWith('mock_token_')) {
      return {
        success: true,
        user: {
          id: '1',
          email: 'demo@tinko.com',
          name: 'Demo User',
        },
      };
    }

    return {
      success: false,
      message: 'Failed to fetch profile',
    };
  }

  static async logout(): Promise<void> {
    // Simulate network delay
    await this.delay(200);
    // Mock logout - nothing needed for demo
  }
}