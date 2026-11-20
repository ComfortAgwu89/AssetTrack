import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    port: 5173,
    // Same-origin API during development so httpOnly auth cookies work without CORS.
    proxy: { '/api': { target: 'http://127.0.0.1:5000', changeOrigin: false } },
  },
})
