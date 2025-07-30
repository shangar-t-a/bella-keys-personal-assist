import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_');

  return {
    plugins: [react()],
    server: {
      host: env.VITE_APP_HOST || 'localhost',
      port: parseInt(env.VITE_APP_PORT || '3000', 10),
    },
    // Explicitly define the directory for .env files
    envDir: './',
  };
});
