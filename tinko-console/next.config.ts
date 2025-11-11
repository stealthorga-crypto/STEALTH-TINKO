import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  
  // Configure for both standalone (Docker) and static export (SWA)
  output: process.env.BUILD_TARGET === 'static' ? 'export' : 'standalone',
  
  eslint: {
    ignoreDuringBuilds: true, // Temporarily bypass lint errors for builds
  },
  typescript: {
    ignoreBuildErrors: true, // Temporarily bypass TS errors for builds
  },
  
  // Static export configuration for Azure Static Web Apps
  trailingSlash: true,
  images: {
    unoptimized: process.env.BUILD_TARGET === 'static' // Required for static export
  },
  
  // Environment-specific configuration
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
  },
  
  // API routes proxy for backend integration
  async rewrites() {
    if (process.env.BUILD_TARGET === 'static') {
      return []; // No rewrites for static builds
    }
    return [
      {
        source: '/api/backend/:path*',
        destination: (process.env.NEXT_PUBLIC_BACKEND_URL || 'https://stealth-tinko-prod-app-1762804410.azurewebsites.net') + '/:path*',
      },
    ];
  },
};

export default nextConfig;
