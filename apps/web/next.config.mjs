/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // The shared package ships raw TypeScript; let Next transpile it.
  transpilePackages: ["@is-it-local/shared"],
};

export default nextConfig;
