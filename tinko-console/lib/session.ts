/**
 * Session Management Utilities
 * Handle secure HttpOnly cookies for session storage
 */

import { cookies } from 'next/headers';
import { SignJWT, jwtVerify } from 'jose';

const SESSION_COOKIE_NAME = process.env.SESSION_COOKIE_NAME || 'auth_session';
const SESSION_MAX_AGE = parseInt(process.env.SESSION_MAX_AGE || '86400', 10); // 24 hours
const SESSION_SECRET = process.env.SESSION_SECRET;

if (!SESSION_SECRET) {
  throw new Error('SESSION_SECRET environment variable is required');
}

const secret = new TextEncoder().encode(SESSION_SECRET);

export interface SessionData {
  accessToken: string;
  idToken: string;
  expiresAt: number;
  user?: {
    sub: string;
    email?: string;
    name?: string;
    picture?: string;
  };
}

/**
 * Create a session and set secure cookie
 */
export async function createSession(data: SessionData): Promise<void> {
  const expiresAt = Date.now() + SESSION_MAX_AGE * 1000;

  // Create JWT for session
  const token = await new SignJWT({ ...data, expiresAt })
    .setProtectedHeader({ alg: 'HS256' })
    .setExpirationTime(expiresAt)
    .setIssuedAt()
    .sign(secret);

  // Set secure HttpOnly cookie
  const cookieStore = await cookies();
  cookieStore.set(SESSION_COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: SESSION_MAX_AGE,
    path: '/',
  });
}

/**
 * Get session data from cookie
 */
export async function getSession(): Promise<SessionData | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE_NAME)?.value;

  if (!token) {
    return null;
  }

  try {
    const { payload } = await jwtVerify(token, secret);
    
    // Check if session is expired
    if (payload.expiresAt && typeof payload.expiresAt === 'number') {
      if (Date.now() > payload.expiresAt) {
        await destroySession();
        return null;
      }
    }

    return payload as unknown as SessionData;
  } catch (error) {
    // Invalid token
    await destroySession();
    return null;
  }
}

/**
 * Destroy session and clear cookie
 */
export async function destroySession(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete(SESSION_COOKIE_NAME);
}

/**
 * Require authentication - throw if no session
 */
export async function requireAuth(): Promise<SessionData> {
  const session = await getSession();
  
  if (!session) {
    throw new Error('Unauthorized');
  }

  return session;
}

/**
 * Update session data (e.g., refresh tokens)
 */
export async function updateSession(data: Partial<SessionData>): Promise<void> {
  const currentSession = await getSession();
  
  if (!currentSession) {
    throw new Error('No active session');
  }

  await createSession({
    ...currentSession,
    ...data,
  });
}
