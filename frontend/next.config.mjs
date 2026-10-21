import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const apiBase = process.env.NEXT_PUBLIC_API_URL || "";
const djangoOrigin = apiBase.replace(/\/api\/v1\/?$/, "");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // N'annonce pas « X-Powered-By: Next.js ».
  poweredByHeader: false,
  // Sortie autonome : image Docker légère (voir Dockerfile).
  output: "standalone",
  experimental: {
    // Next 15 ne garde plus les pages dynamiques dans le cache du routeur client (0 s) ;
    // 30 s conserve la navigation de Next 14.
    staleTimes: { dynamic: 30 },
  },
  images: {
    // Autoriser plus tard les images servies par le backend Django (media).
    remotePatterns: [],
  },
  sassOptions: {
    includePaths: [path.join(__dirname)],
  },
  async rewrites() {
    if (!djangoOrigin) return [];

    return [
      {
        source: "/media/:path*",
        destination: `${djangoOrigin}/media/:path*`,
      },
      {
        source: "/api/:path*",
        destination: `${djangoOrigin}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
