import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    server: {
      port: 3001,
      strictPort: true,
      host: '0.0.0.0',
      proxy: {
        // All API calls must start with /api
        '/api': {
          // IMPORTANT: use backend service name, not localhost
          target: env.VITE_API_URL || 'http://backend:5000',
          changeOrigin: true,
          secure: false,
          // rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
    build: {
      outDir: 'build',
      assetsDir: 'static',
    },
  };
});