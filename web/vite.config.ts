/// <reference types="vitest/config" />
import { resolve } from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

const ROOT_DIR = resolve(import.meta.dirname, "..");

function requireEnv(env: Record<string, string>, name: string): string {
  const value = env[name];
  if (!value) throw new Error(`Variable manquante dans .env : ${name}`);
  return value;
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ROOT_DIR, "");
  const apiPort = requireEnv(env, "API_PORT");
  const frontPort = Number(requireEnv(env, "FRONT_PORT"));
  return {
    plugins: [react()],
    server: { port: frontPort, strictPort: true },
    test: { environment: "jsdom", setupFiles: ["./src/test-setup.ts"] },
    define: {
      "import.meta.env.VITE_API_URL": JSON.stringify(`http://127.0.0.1:${apiPort}`),
    },
  };
});
