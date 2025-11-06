/**
 * Auth0 Verify OTP API Route
 * POST /api/auth0/verify-otp
 */

import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { verifyAuth0OTP, getAuth0UserInfo } from '@/lib/auth0';
import { createSession } from '@/lib/session';
import { checkOTPVerifyRateLimit } from '@/lib/rate-limit';

const verifyOTPSchema = z.object({
  email: z.string().email('Invalid email address').optional(),
  phone: z.string().regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number format').optional(),
  otp: z.string().length(6, 'OTP must be 6 digits').regex(/^\d{6}$/, 'OTP must be numeric'),
  channel: z.enum(['email', 'sms']).optional(),
}).refine(
  (data) => data.email || data.phone,
  'Either email or phone must be provided'
);

function getClientIP(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  const realIP = request.headers.get('x-real-ip');
  
  if (forwarded) {
    return forwarded.split(',')[0].trim();
  }
  
  if (realIP) {
    return realIP.trim();
  }
  
  return 'unknown';
}

export async function POST(request: NextRequest) {
  try {
    // Parse and validate request body
    const body = await request.json();
    const validated = verifyOTPSchema.parse(body);

    const channel = validated.channel || (process.env.OTP_CHANNEL as 'email' | 'sms') || 'email';
    const identifier = validated.email || validated.phone || '';

    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimit = await checkOTPVerifyRateLimit(clientIP, identifier);

    if (!rateLimit.success) {
      return NextResponse.json(
        {
          success: false,
          error: 'Too many verification attempts. Please try again later.',
          retryAfter: Math.ceil((rateLimit.resetAt - Date.now()) / 1000),
        },
        {
          status: 429,
          headers: {
            'Retry-After': String(Math.ceil((rateLimit.resetAt - Date.now()) / 1000)),
            'X-RateLimit-Remaining': String(rateLimit.remaining),
            'X-RateLimit-Reset': new Date(rateLimit.resetAt).toISOString(),
          },
        }
      );
    }

    // Verify OTP and get tokens
    const tokens = await verifyAuth0OTP({
      email: validated.email,
      phone: validated.phone,
      otp: validated.otp,
      channel,
    });

    // Get user info
    const userInfo = await getAuth0UserInfo(tokens.access_token);

    // Create session with HttpOnly cookie
    await createSession({
      accessToken: tokens.access_token,
      idToken: tokens.id_token,
      expiresAt: Date.now() + tokens.expires_in * 1000,
      user: {
        sub: userInfo.sub,
        email: userInfo.email,
        name: userInfo.name,
        picture: userInfo.picture,
      },
    });

    return NextResponse.json(
      {
        success: true,
        message: 'OTP verified successfully',
        user: {
          sub: userInfo.sub,
          email: userInfo.email,
          name: userInfo.name,
          picture: userInfo.picture,
        },
      },
      {
        headers: {
          'X-RateLimit-Remaining': String(rateLimit.remaining - 1),
          'X-RateLimit-Reset': new Date(rateLimit.resetAt).toISOString(),
        },
      }
    );
  } catch (error) {
    console.error('Verify OTP error:', error);

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          success: false,
          error: 'Validation error',
          details: error.issues,
        },
        { status: 400 }
      );
    }

    if (error instanceof Error) {
      // Provide user-friendly error messages
      if (error.message.includes('Invalid or expired')) {
        return NextResponse.json(
          {
            success: false,
            error: 'Invalid or expired OTP code. Please request a new one.',
          },
          { status: 400 }
        );
      }

      if (error.message.includes('Too many')) {
        return NextResponse.json(
          {
            success: false,
            error: 'Too many failed attempts. Please request a new OTP code.',
          },
          { status: 429 }
        );
      }

      return NextResponse.json(
        {
          success: false,
          error: error.message,
        },
        { status: 400 }
      );
    }

    return NextResponse.json(
      {
        success: false,
        error: 'Failed to verify OTP',
      },
      { status: 500 }
    );
  }
}
