import { defineConfig } from 'electron-vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
    main: {
        build: {
            rollupOptions: {
                input: {
                    index: path.resolve(__dirname, 'electron/main/index.ts'),
                },
            },
        },
    },
    preload: {
        build: {
            rollupOptions: {
                input: {
                    index: path.resolve(__dirname, 'electron/preload/index.ts'),
                },
            },
        },
    },
    renderer: {
        root: '.',
        build: {
            rollupOptions: {
                input: {
                    index: path.resolve(__dirname, 'index.html'),
                },
                output: {
                    manualChunks: {
                        'vendor-react': ['react', 'react-dom'],
                        'vendor-router': ['react-router-dom'],
                        'vendor-mui': ['@mui/material', '@emotion/react', '@emotion/styled'],
                        'vendor-mui-icons': ['@mui/icons-material'],
                        'vendor-markdown': ['react-markdown', 'react-syntax-highlighter', 'remark-breaks', 'remark-gfm'],
                        'vendor-forms': ['react-hook-form', '@hookform/resolvers', 'zod'],
                        'vendor-utils': ['axios', 'date-fns', 'sonner'],
                    },
                },
            },
            chunkSizeWarningLimit: 800,
        },
        plugins: [react()],
        resolve: {
            alias: {
                '@': path.resolve(__dirname, './src'),
            },
        },
        define: {
            'import.meta.env.VITE_APP_ENV': '"electron"',
        },
        server: {
            port: 3000,
        },
    },
})
