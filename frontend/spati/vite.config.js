import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      // Desactiva la PWA en este deploy para desalojar SW viejos (D_L8c-qw).
      // Los clientes que actualicen sw.js se auto-desregistran y cargan red limpia.
      selfDestroying: true,
      registerType: 'autoUpdate',
      manifest: {
        name: 'METGO VENTORA Izaje',
        short_name: 'VENTORA',
        description: 'Pronóstico 72 h y alertas de izaje',
        theme_color: '#10b981',
        background_color: '#0f172a',
        display: 'standalone',
        start_url: '/',
        lang: 'es',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' },
        ],
      },
      workbox: {
        cleanupOutdatedCaches: true,
        clientsClaim: true,
        skipWaiting: true,
      },
    }),
  ],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: { port: 5177, strictPort: false, host: true },
})
