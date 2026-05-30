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
          name: 'METGO Quillota',
          short_name: 'METGO',
          description: 'Monitoreo meteorológico y agrícola',
          theme_color: '#166534',
          background_color: '#f8fafc',
          display: 'standalone',
          start_url: '/',
          icons: [],
        },
        workbox: {
          cleanupOutdatedCaches: true,
          clientsClaim: true,
          skipWaiting: true,
          navigateFallback: '/index.html',
          navigateFallbackDenylist: [/^\/api\//, /^\/assets\//],
          runtimeCaching: [
            {
              urlPattern: ({ url }) => url.pathname.startsWith('/api/public'),
              handler: 'NetworkFirst',
              options: { cacheName: 'metgo-public-meteo', expiration: { maxEntries: 32 } },
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
