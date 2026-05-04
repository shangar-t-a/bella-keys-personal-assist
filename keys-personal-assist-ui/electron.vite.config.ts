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
                    manualChunks(id) {
                        if (id.includes('node_modules')) {
                            return 'vendor';
                        }
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
