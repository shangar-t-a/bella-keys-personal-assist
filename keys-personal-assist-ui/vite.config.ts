import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on mode (development, production, etc.)
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes('node_modules')) {
              return 'vendor';
            }
          },
        },
      },
      // Increase chunk size warning limit to 800kb
      // The vendor-markdown chunk (~780kb) is lazy-loaded only on chat page
      chunkSizeWarningLimit: 800,
    },
    server: {
      host: env.VITE_HOST || 'localhost',
      port: parseInt(env.VITE_PORT || '3000'),
      proxy: {
        '/api/bella-chat': {
          target: 'http://localhost:5000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api\/bella-chat/, ''),
        },
        '/api/ems': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api\/ems/, ''),
        },
      },
    },
  }
})
