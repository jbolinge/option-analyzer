/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  define: {
    global: 'globalThis',
  },
  optimizeDeps: {
    include: [
      'plotly.js/lib/core',
      'plotly.js/lib/bar',
      'plotly.js/lib/candlestick',
      'plotly.js/lib/surface',
      'react-plotly.js/factory',
    ],
  },
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: './src/test-setup.ts',
    css: true,
  },
})
