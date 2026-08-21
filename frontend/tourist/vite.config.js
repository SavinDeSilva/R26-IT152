import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const dir = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['sos-icon.svg'],
      manifest: {
        name: 'Tourist SOS',
        short_name: 'SOS',
        description: 'One-tap emergency SOS for tourists in Sri Lanka',
        theme_color: '#b91c1c',
        background_color: '#0f172a',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          {
            src: 'sos-icon.svg',
            sizes: 'any',
            type: 'image/svg+xml',
            purpose: 'any maskable',
          },
        ],
      },
      workbox: {
        navigateFallback: '/index.html',
        runtimeCaching: [
          {
            urlPattern: ({ url }) => url.pathname.startsWith('/api/'),
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 5,
            },
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: { '@shared': path.resolve(dir, '../shared') },
  },
  server: {
    // Dedicated SOS tourist port (Tour Ceylon uses 5180)
    port: 5175,
    strictPort: true,
    fs: { allow: [path.resolve(dir, '..')] },
    proxy: {
      '/api': 'http://127.0.0.1:5002',
      '/uploads': 'http://127.0.0.1:5002',
    },
  },
})
