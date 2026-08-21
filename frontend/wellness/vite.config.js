import { defineConfig } from 'vite';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  appType: 'mpa',
  resolve: {
    alias: { '@shared': path.resolve(dir, '../shared') },
  },
  server: {
    port: 5181,
    strictPort: true,
    fs: { allow: [path.resolve(dir, '..')] },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5002',
        changeOrigin: true,
        cookieDomainRewrite: '',
      },
    },
  },
  plugins: [
    {
      name: 'wellness-admin-index',
      configureServer(server) {
        server.middlewares.use((req, _res, next) => {
          if (req.url === '/admin' || req.url === '/admin/') {
            req.url = '/admin/index.html';
          }
          next();
        });
      },
    },
  ],
});
