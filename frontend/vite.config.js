import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The Flask backend serves ../frontend/build as the SPA (see backend/app.py),
// so the build output directory is kept at "build".
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'build',
    emptyOutDir: true,
  },
  server: {
    port: 3000,
    // During development, forward API calls to a locally running backend.
    proxy: {
      '/api': 'http://127.0.0.1:5001',
    },
  },
});
