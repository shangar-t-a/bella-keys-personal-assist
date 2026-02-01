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
          manualChunks: {
            // Core vendor libraries
            'vendor-react': ['react', 'react-dom'],
            'vendor-router': ['react-router-dom'],
            // MUI core components and styling
            'vendor-mui': ['@mui/material', '@emotion/react', '@emotion/styled'],
            // MUI icons (separate chunk due to size)
            'vendor-mui-icons': ['@mui/icons-material'],
            // Markdown rendering (only loaded on chat page)
            'vendor-markdown': ['react-markdown', 'react-syntax-highlighter', 'remark-breaks', 'remark-gfm'],
            // Form and validation libraries
            'vendor-forms': ['react-hook-form', '@hookform/resolvers', 'zod'],
            // Utilities
            'vendor-utils': ['axios', 'date-fns', 'sonner'],
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
