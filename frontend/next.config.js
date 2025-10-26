/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  allowedDevOrigins: ['hurl.lol', 'www.hurl.lol'],
  webpack: (config, { dev, isServer }) => {
    // Fix for webpack-hmr in dev mode
    if (dev && !isServer) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      }
    }
    return config
  },
}

module.exports = nextConfig
