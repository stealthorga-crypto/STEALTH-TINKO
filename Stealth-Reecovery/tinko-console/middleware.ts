import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Middleware for route protection and authentication
 * 
 * Protects console routes requiring authentication.
 * Adds security headers to all protected routes.
 * Redirects unauthenticated users to signin page.
 */

/**
 * Protected route patterns that require authentication
 */
const PROTECTED_ROUTES = [
  "/dashboard",
  "/onboarding",
  "/rules",
  "/templates",
  "/developer",
  "/settings",
];

/**
 * Public routes accessible without authentication
 */
const PUBLIC_ROUTES = [
  "/",
  "/pricing",
  "/contact",
  "/privacy",
  "/terms",
  "/auth/signin",
  "/auth/error",
  "/pay/retry",
];

/**
 * Check if path requires authentication
 */
function isProtectedRoute(pathname: string): boolean {
  return PROTECTED_ROUTES.some((route) => pathname.startsWith(route));
}

/**
 * Check if path is public
 */
function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.some((route) => pathname === route || pathname.startsWith(route));
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public routes
  if (isPublicRoute(pathname)) {
    return NextResponse.next();
  }

  // Check protected routes
  if (isProtectedRoute(pathname)) {
    // Get session token from cookie
    const sessionToken =
      request.cookies.get("next-auth.session-token")?.value ||
      request.cookies.get("__Secure-next-auth.session-token")?.value ||
      request.cookies.get("authjs.session-token")?.value ||
      request.cookies.get("__Secure-authjs.session-token")?.value;

    // Redirect to signin if no session
    if (!sessionToken) {
      const signinUrl = new URL("/auth/signin", request.url);
      signinUrl.searchParams.set("callbackUrl", pathname);
      return NextResponse.redirect(signinUrl);
    }

    // Add security headers for protected routes
    const response = NextResponse.next();
    response.headers.set("X-Frame-Options", "DENY");
    response.headers.set("X-Content-Type-Options", "nosniff");
    response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
    response.headers.set("X-XSS-Protection", "1; mode=block");
    return response;
  }

  // Allow all other routes
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api routes
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico, robots.txt, sw.js, etc.
     */
    "/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|sw.js|offline.html|icons).*)",
  ],
};
