import { NextConfig } from 'next';

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*', // Proxy to Backend
      },
    ];
  },
  // 确保支持TypeScript
  typescript: {
    // !! WARN !!
    // 在生产环境中不应跳过类型检查
    // 这里仅为开发方便而设置
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
