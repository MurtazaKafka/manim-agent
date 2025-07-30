/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // WebSocket proxy still needed
  async rewrites() {
    return [
      {
        source: '/ws/:path*',
        destination: 'http://localhost:8000/ws/:path*',
      },
    ];
  },
};

module.exports = nextConfig;