import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enables static HTML export to the `out` folder
  output: "export",
  // Disables default image optimization required for static exports
  images: {
    unoptimized: true,
  },
  // Strict mode for catching React bugs early
  reactStrictMode: true,
};

export default nextConfig;
