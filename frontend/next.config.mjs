/** @type {import('next').NextConfig} */
const nextConfig = {
  // Exclude server-only packages from the client bundle
  experimental: {},
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Don't bundle server-only packages on the client
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
        dns: false,
        crypto: false,
      };
    }
    return config;
  },
};

export default nextConfig;
