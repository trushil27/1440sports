import type { NextConfig } from "next";

/**
 * The API origin. Baked in at build time: the rewrites below proxy `/api/*` and
 * `/auth/*` to it so the session cookie is first-party to the web app (WebAuthn and
 * SameSite=Lax cookies both need that). Set it before `next build` on Vercel.
 */
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(
  /\/+$/,
  "",
);

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${API_BASE_URL}/api/:path*` },
      { source: "/auth/:path*", destination: `${API_BASE_URL}/auth/:path*` },
    ];
  },
  async redirects() {
    // The emailed magic link points at `{API_BASE_URL}/auth/magic-link/verify?token=…`.
    // When the operator sets the API's API_BASE_URL to this web origin, a browser
    // navigation (Accept: text/html) lands here; hand it to the sign-in page, which
    // calls the same endpoint with Accept: application/json (not redirected) and then
    // routes to `next`.
    return [
      {
        source: "/auth/magic-link/verify",
        has: [
          { type: "header", key: "accept", value: ".*text/html.*" },
          { type: "query", key: "token" },
        ],
        destination: "/signin/verify?token=:token",
        permanent: false,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/sw.js",
        headers: [
          { key: "Service-Worker-Allowed", value: "/" },
          { key: "Cache-Control", value: "no-cache" },
        ],
      },
    ];
  },
  webpack: (config) => {
    // pdf.js optionally requires `canvas` for Node; the browser build never needs it.
    config.resolve.alias = { ...(config.resolve.alias ?? {}), canvas: false };
    return config;
  },
};

export default nextConfig;
