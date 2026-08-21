import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  // Siempre 8080 salvo VITE_API_PORT en .env.development (no usar 8000: API antigua sin JWT)
  const apiPort = env.VITE_API_PORT || '8080'
  const apiTarget = `http://127.0.0.1:${apiPort}`
  console.log(`[vite] Proxy /api -> ${apiTarget}`)

  return {
    plugins: [
      vue(),
      VitePWA({
        registerType: 'autoUpdate',
        manifest: {
          name: 'METGO3D',
          short_name: 'METGO',
          description: 'Monitoreo meteorológico y agrícola',
          theme_color: '#00ffaa',
          background_color: '#0b1120',
          display: 'standalone',
          start_url: '/',
          lang: 'es',
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
                url.pathname.startsWith('/api/public') ||
                url.hostname.includes('metgo-api.onrender.com'),
              handler: 'NetworkFirst',
              options: {
                cacheName: 'metgo-api-public',
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
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      host: '127.0.0.1',
      port: 5173,
      strictPort: false,
      open: false,
      cors: true,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          secure: false,
        },
      },
    },
    preview: {
      host: '127.0.0.1',
      port: 5173,
      strictPort: false,
    },
  }
})
