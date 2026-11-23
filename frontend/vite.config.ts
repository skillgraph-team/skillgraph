/**
 * Vite settings: dev server, dev proxy to the backend, and the test runner (Vitest).
 *
 * Settings come from the single `.env` in the repo root (one level up), like the backend.
 * In development the browser calls `/api/...` on the Vite server, and Vite forwards it to
 * the backend at BACKEND_URL with `/api` removed. Same origin for the browser, so the
 * backend needs no CORS setup.
 */
import react from "@vitejs/plugin-react";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

const ENV_DIR = "..";

export default defineConfig(({ mode }) => {
  // "" = read every variable, not only VITE_ ones (BACKEND_URL is for this file only).
  const env = loadEnv(mode, ENV_DIR, "");
  const backendUrl = env.BACKEND_URL || "http://localhost:8000";

  return {
    plugins: [react()],
    envDir: ENV_DIR,
    server: {
      proxy: {
        "/api": {
          target: backendUrl,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ""),
        },
      },
    },
    test: {
      environment: "jsdom",
    },
  };
});
