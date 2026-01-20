/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  images: {
    domains: ['portal.ganakys.com'],
  },
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Warning: This allows production builds to successfully complete even if
    // your project has type errors.
    ignoreBuildErrors: true,
  },
  // API routing is handled by nginx in production
  // In development with Docker, use Docker network name
  async rewrites() {
    // Skip rewrites in production (nginx handles /api/ routing)
    if (process.env.NODE_ENV === 'production') {
      return []
    }
    // Use Docker network name 'backend' and internal port 8000
    const backendUrl = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000'
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
