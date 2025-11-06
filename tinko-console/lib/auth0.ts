/**
 * Auth0 Helper Functions
 * Server-side utilities for interacting with Auth0 APIs
 */

interface Auth0Config {
  domain: string;
  clientId: string;
  clientSecret: string;
  issuerBaseUrl: string;
}

export function getAuth0Config(): Auth0Config {
  const domain = process.env.AUTH0_DOMAIN;
  const clientId = process.env.AUTH0_CLIENT_ID;
  const clientSecret = process.env.AUTH0_CLIENT_SECRET;
  const issuerBaseUrl = process.env.AUTH0_ISSUER_BASE_URL;

  if (!domain || !clientId || !clientSecret || !issuerBaseUrl) {
    throw new Error('Missing required Auth0 environment variables');
  }

  return { domain, clientId, clientSecret, issuerBaseUrl };
}

export interface SignupPayload {
  email: string;
  password: string;
  company: string;
  phone: string;
}

/**
 * Create a new user in Auth0 database connection
 */
export async function createAuth0User(payload: SignupPayload): Promise<{ _id: string; email: string }> {
  const { domain, clientId } = getAuth0Config();

  const response = await fetch(`https://${domain}/dbconnections/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      client_id: clientId,
      email: payload.email,
      password: payload.password,
      connection: 'Username-Password-Authentication',
      user_metadata: {
        company: payload.company,
        phone: payload.phone,
      },
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error_description || error.error || 'Failed to create user');
  }

  return response.json();
}

interface SendOTPPayload {
  email?: string;
  phone?: string;
  channel: 'email' | 'sms';
}

/**
 * Send OTP via Auth0 Passwordless (SMS or Email)
 */
export async function sendAuth0OTP(payload: SendOTPPayload): Promise<{ success: boolean }> {
  const { domain, clientId } = getAuth0Config();
  const channel = payload.channel || process.env.OTP_CHANNEL || 'email';

  const body: any = {
    client_id: clientId,
    send: 'code',
  };

  if (channel === 'sms') {
    if (!payload.phone) {
      throw new Error('Phone number required for SMS OTP');
    }
    body.connection = 'sms';
    body.phone_number = payload.phone;
  } else {
    if (!payload.email) {
      throw new Error('Email required for Email OTP');
    }
    body.connection = 'email';
    body.email = payload.email;
  }

  const response = await fetch(`https://${domain}/passwordless/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error_description || error.error || 'Failed to send OTP');
  }

  return { success: true };
}

interface VerifyOTPPayload {
  email?: string;
  phone?: string;
  otp: string;
  channel: 'email' | 'sms';
}

interface Auth0TokenResponse {
  access_token: string;
  id_token: string;
  token_type: string;
  expires_in: number;
}

/**
 * Verify OTP and exchange for tokens
 */
export async function verifyAuth0OTP(payload: VerifyOTPPayload): Promise<Auth0TokenResponse> {
  const { domain, clientId, clientSecret } = getAuth0Config();
  const channel = payload.channel || process.env.OTP_CHANNEL || 'email';

  const body: any = {
    grant_type: 'http://auth0.com/oauth/grant-type/passwordless/otp',
    client_id: clientId,
    client_secret: clientSecret,
    realm: channel,
    otp: payload.otp,
    scope: 'openid profile email',
  };

  if (channel === 'sms') {
    if (!payload.phone) {
      throw new Error('Phone number required for SMS OTP verification');
    }
    body.username = payload.phone;
  } else {
    if (!payload.email) {
      throw new Error('Email required for Email OTP verification');
    }
    body.username = payload.email;
  }

  const response = await fetch(`https://${domain}/oauth/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    
    // Provide user-friendly error messages
    if (error.error === 'invalid_grant') {
      throw new Error('Invalid or expired OTP code');
    }
    if (error.error === 'too_many_attempts') {
      throw new Error('Too many failed attempts. Please request a new code.');
    }
    
    throw new Error(error.error_description || error.error || 'Failed to verify OTP');
  }

  return response.json();
}

/**
 * Get user info from Auth0
 */
export async function getAuth0UserInfo(accessToken: string): Promise<any> {
  const { domain } = getAuth0Config();

  const response = await fetch(`https://${domain}/userinfo`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to get user info');
  }

  return response.json();
}

/**
 * Exchange authorization code for tokens (for Google OAuth flow)
 */
export async function exchangeCodeForTokens(code: string, redirectUri: string): Promise<Auth0TokenResponse> {
  const { domain, clientId, clientSecret } = getAuth0Config();

  const response = await fetch(`https://${domain}/oauth/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      grant_type: 'authorization_code',
      client_id: clientId,
      client_secret: clientSecret,
      code,
      redirect_uri: redirectUri,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error_description || error.error || 'Failed to exchange code');
  }

  return response.json();
}
