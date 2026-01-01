import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable Fast Refresh (Hot Module Replacement)
  reactStrictMode: true,
  
  // Enable standalone output for Docker
  output: 'standalone',
  
  // File watching configuration for WSL/Windows
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      // Enable polling for file watching (works in WSL/Windows)
      config.watchOptions = {
        poll: 1000, // Check for changes every second
        aggregateTimeout: 300, // Delay before rebuilding after the first change
        ignored: ['**/node_modules', '**/.git', '**/.next'],
      };
    }
    return config;
  },
  
  // Empty turbopack config to silence warning (we're using webpack for file watching)
  turbopack: {},
};

export default nextConfig;
