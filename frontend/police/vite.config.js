import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const dir = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@shared': path.resolve(dir, '../shared') },
  },
  server: {
    // 5176 avoids 5174 (often taken by Docker/other Vite) and tourist SOS on 5175
    port: 5176,
    strictPort: true,
    fs: { allow: [path.resolve(dir, '..')] },
    proxy: {
      // Unified Tour Ceylon API
      '/api': 'http://127.0.0.1:5002',
      '/uploads': 'http://127.0.0.1:5002',
    },
  },
})
