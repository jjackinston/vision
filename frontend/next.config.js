/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  // jspdf / html2canvas are browser-only libs. Alias them to false on the
  // server so webpack never bundles their Node.js builds during SSR / SSG.
  webpack: (config, { isServer }) => {
    if (isServer) {
      config.resolve.alias = {
        ...config.resolve.alias,
        jspdf:        false,
        html2canvas:  false,
        canvg:        false,
      };
    }
    return config;
  },
  images: {
    domains: ["images-na.ssl-images-amazon.com", "m.media-amazon.com", "cdn.shopify.com"],
    formats: ["image/avif", "image/webp"],
  },
  headers: async () => [
    {
      source: "/(.*)",
      headers: [
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "X-Frame-Options", value: "DENY" },
        { key: "X-XSS-Protection", value: "1; mode=block" },
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains; preload" },
      ],
    },
  ],
};

module.exports = nextConfig;
