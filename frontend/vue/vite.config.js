import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  // Siempre 8080 salvo VITE_API_PORT en .env.development (no usar 8000: API antigua sin JWT)
  const apiPort = env.VITE_API_PORT || '8080'
  const apiTarget = `http://127.0.0.1:${apiPort}`
  console.log(`[vite] Proxy /api -> ${apiTarget}`)

  return {
    plugins: [vue()],
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
