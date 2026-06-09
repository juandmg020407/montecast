import path from "node:path";
import { fileURLToPath } from "node:url";
import type { NextConfig } from "next";

const root = path.dirname(fileURLToPath(import.meta.url));

const nextConfig: NextConfig = {
  // Pin the workspace root to this folder so Turbopack doesn't pick up a
  // stray lockfile from a parent directory when inferring the root.
  turbopack: { root },
};

export default nextConfig;
