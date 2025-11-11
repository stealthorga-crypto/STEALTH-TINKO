/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  reactStrictMode: true,
  poweredByHeader: false,
  
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  
  // Static export configuration for Azure Static Web Apps
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  
  // Handle dynamic routes in static export mode
  generateBuildId: async () => {
    return 'azure-swa-build'
  }
};

module.exports = nextConfig;
