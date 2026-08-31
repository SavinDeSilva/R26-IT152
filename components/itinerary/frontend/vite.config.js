import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(dir, '../../shared/frontend');

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@shared': frontendRoot,
      'react-router-dom': path.resolve(dir, 'node_modules/react-router-dom'),
      react: path.resolve(dir, 'node_modules/react'),
      'react-dom': path.resolve(dir, 'node_modules/react-dom'),
    },
  },
  server: {
    port: 5180,
    strictPort: true,
    fs: { allow: [dir, frontendRoot] },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5002',
        changeOrigin: true,
      },
      // Same unified backend — keep /sos-api alias for existing client code
      '/sos-api': {
        target: 'http://127.0.0.1:5002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/sos-api/, ''),
      },
      '/sos-uploads': {
        target: 'http://127.0.0.1:5002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/sos-uploads/, '/uploads'),
      },
      '/uploads': {
        target: 'http://127.0.0.1:5002',
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: 5180,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5002',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'http://127.0.0.1:5002',
        changeOrigin: true,
      },
    },
  },
});
