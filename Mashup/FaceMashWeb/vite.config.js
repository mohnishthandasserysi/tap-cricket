import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks: {
          phaser: ['phaser'],
          faceapi: ['face-api.js']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['phaser', 'face-api.js']
  },
  assetsInclude: ['**/*.dat', '**/*.bin']
})
