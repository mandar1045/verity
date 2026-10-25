import { fileURLToPath, URL } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@contracts": fileURLToPath(new URL("../contracts", import.meta.url)),
    },
  },
  server: { port: 5173, host: true, fs: { allow: [".."] } },
  preview: { port: 4173, host: true },
});
