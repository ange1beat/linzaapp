import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

import { fileURLToPath, URL } from "url";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 3000,
  },
  build: {
    outDir: "./build",
    sourcemap: true,
  },
  resolve: {
    alias: [
      {
        find: "@/app",
        replacement: fileURLToPath(new URL("./src/app", import.meta.url)),
      },
      {
        find: "@/entities",
        replacement: fileURLToPath(new URL("./src/entities", import.meta.url)),
      },
      {
        find: "@/features",
        replacement: fileURLToPath(new URL("./src/features", import.meta.url)),
      },
      {
        find: "@/pages",
        replacement: fileURLToPath(new URL("./src/pages", import.meta.url)),
      },
      {
        find: "@/shared",
        replacement: fileURLToPath(new URL("./src/shared", import.meta.url)),
      },
      {
        find: "@/widgets",
        replacement: fileURLToPath(new URL("./src/widgets", import.meta.url)),
      },
    ],
  },
});
