import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(dir, '../../shared/frontend');
const unifiedRoot = path.resolve(dir, '../../../tourism-unified');
const unifiedSrc = path.resolve(unifiedRoot, 'src');

export default defineConfig({
  plugins: [
    react(),
  ],
  optimizeDeps: {
    esbuildOptions: {
      loader: { '.js': 'jsx' },
    },
  },
  esbuild: {
    include: /\.(js|jsx)$/,
    exclude: [],
    loader: 'jsx',
  },
  publicDir: path.resolve(unifiedRoot, 'public'),
  resolve: {
    alias: {
      '@shared': frontendRoot,
      '@risk': unifiedSrc,
      react: path.resolve(dir, 'node_modules/react'),
      'react-dom': path.resolve(dir, 'node_modules/react-dom'),
      'react-router-dom': path.resolve(dir, 'node_modules/react-router-dom'),
      'lucide-react': path.resolve(dir, 'node_modules/lucide-react'),
      recharts: path.resolve(dir, 'node_modules/recharts'),
    },
    dedupe: ['react', 'react-dom', 'react-router-dom', 'lucide-react', 'recharts'],
  },
  server: {
    port: 5182,
    strictPort: true,
    fs: { allow: [dir, frontendRoot, unifiedRoot] },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5002',
        changeOrigin: true,
      },
    },
  },
});
