/**
 * Auth0 Signup API Route
 * POST /api/auth0/signup
 */

import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { createAuth0User } from '@/lib/auth0';

const signupSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  company: z.string().min(1, 'Company name is required'),
  phone: z.string().regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number format'),
});

export async function POST(request: NextRequest) {
  try {
    // Parse and validate request body
    const body = await request.json();
    const validated = signupSchema.parse(body);

    // Create user in Auth0
    const user = await createAuth0User(validated);

    return NextResponse.json({
      success: true,
      message: 'User created successfully',
      user: {
        id: user._id,
        email: user.email,
      },
    });
  } catch (error) {
    console.error('Signup error:', error);

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
      // Check for specific Auth0 errors
      if (error.message.includes('already exists')) {
        return NextResponse.json(
          {
            success: false,
            error: 'Email already registered',
          },
          { status: 409 }
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
        error: 'Failed to create user',
      },
      { status: 500 }
    );
  }
}
