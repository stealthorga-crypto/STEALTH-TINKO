/**
 * Sentry configuration for client-side error tracking.
 * 
 * Set NEXT_PUBLIC_SENTRY_DSN in environment variables to enable.
 */

import * as Sentry from '@sentry/nextjs';

export function initSentry() {
  const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;

  if (SENTRY_DSN) {
    Sentry.init({
      dsn: SENTRY_DSN,
      environment: process.env.NEXT_PUBLIC_ENVIRONMENT || 'development',
      
      // Adjust this value in production, or use tracesSampler for greater control
      tracesSampleRate: parseFloat(process.env.NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE || '0.1'),
      
      // Setting this option to true will print useful information to the console while you're setting up Sentry.
      debug: process.env.NODE_ENV === 'development',
      
      // Only capture errors in production
      enabled: process.env.NODE_ENV === 'production',
      
      beforeSend(event, hint) {
        // Filter out specific errors if needed
        if (event.exception) {
          const error = hint.originalException;
          
          // Example: Don't send errors from browser extensions
          if (error && error.message && error.message.includes('chrome-extension://')) {
            return null;
          }
        }
        
        return event;
      },
    });
  }
}

/**
 * Set user context for Sentry error tracking.
 */
export function setSentryUser(user: { id: string; email: string; org_id?: string }) {
  if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
    Sentry.setUser({
      id: user.id,
      email: user.email,
      org_id: user.org_id,
    });
  }
}

/**
 * Clear user context (on logout).
 */
export function clearSentryUser() {
  if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
    Sentry.setUser(null);
  }
}

/**
 * Manually capture an exception.
 */
export function captureException(error: Error, context?: Record<string, any>) {
  if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
    Sentry.captureException(error, {
      extra: context,
    });
  }
}

/**
 * Manually capture a message.
 */
export function captureMessage(message: string, level: 'info' | 'warning' | 'error' = 'info') {
  if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
    Sentry.captureMessage(message, level);
  }
}
