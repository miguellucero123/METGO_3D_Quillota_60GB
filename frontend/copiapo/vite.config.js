import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'METGO Copiapó',
        short_name: 'METGO Aire',
        description: 'Calidad del aire urbana — ICAP Copiapó',
        theme_color: '#fbbf24',
        background_color: '#0b1120',
        display: 'standalone',
        start_url: '/',
        lang: 'es',
        id: '/?v=landing-2026-08',
        icons: [
          {
            src: '/icons/icon-192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any',
          },
          {
            src: '/icons/icon-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable',
          },
        ],
      },
      workbox: {
        cleanupOutdatedCaches: true,
        clientsClaim: true,
        skipWaiting: true,
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/api\//, /^\/assets\//],
        runtimeCaching: [
          {
            urlPattern: ({ url }) =>
              url.pathname.startsWith('/api/') ||
              url.hostname.includes('metgo-api.onrender.com'),
            handler: 'NetworkFirst',
            options: {
              cacheName: 'metgo-api-aire-v2',
              networkTimeoutSeconds: 8,
              expiration: { maxEntries: 48, maxAgeSeconds: 6 * 3600 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5175,
    strictPort: false,
    host: true,
  },
})
