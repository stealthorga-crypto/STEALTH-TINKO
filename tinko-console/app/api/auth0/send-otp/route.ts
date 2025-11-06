/**
 * Auth0 Send OTP API Route
 * POST /api/auth0/send-otp
 */

import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { sendAuth0OTP } from '@/lib/auth0';
import { checkOTPSendRateLimit } from '@/lib/rate-limit';

const sendOTPSchema = z.object({
  email: z.string().email('Invalid email address').optional(),
  phone: z.string().regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number format').optional(),
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
    const validated = sendOTPSchema.parse(body);

    const channel = validated.channel || (process.env.OTP_CHANNEL as 'email' | 'sms') || 'email';
    const identifier = validated.email || validated.phone || '';
    
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimit = await checkOTPSendRateLimit(clientIP, identifier);

    if (!rateLimit.success) {
      return NextResponse.json(
        {
          success: false,
          error: 'Too many requests. Please try again later.',
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

    // Send OTP via Auth0
    await sendAuth0OTP({
      email: validated.email,
      phone: validated.phone,
      channel,
    });

    return NextResponse.json(
      {
        success: true,
        message: `OTP sent successfully via ${channel}`,
        channel,
      },
      {
        headers: {
          'X-RateLimit-Remaining': String(rateLimit.remaining - 1),
          'X-RateLimit-Reset': new Date(rateLimit.resetAt).toISOString(),
        },
      }
    );
  } catch (error) {
    console.error('Send OTP error:', error);

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
        error: 'Failed to send OTP',
      },
      { status: 500 }
    );
  }
}
