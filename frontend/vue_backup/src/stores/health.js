import { ref } from 'vue'
import { fetchHealth } from '@/api/metgoApi'

const health = ref(null)
const streamlitOk = ref(null)
const cargando = ref(false)
let pollTimer = null

/** Render (embebible); no usar *.streamlit.app aquí (bucle /-/login en consola). */
const STREAMLIT_URL =
  import.meta.env.VITE_METGO_STREAMLIT_URL ||
  import.meta.env.VITE_METGO_STREAMLIT_RENDER_URL ||
  'https://metgo-streamlit.onrender.com'

const STREAMLIT_PUBLIC =
  import.meta.env.VITE_METGO_STREAMLIT_PUBLIC_URL ||
  'https://metgo-3d-quillota-60gb.streamlit.app'

function esEntornoLocal() {
  if (typeof window === 'undefined') return false
  return ['localhost', '127.0.0.1'].includes(window.location.hostname)
}

export function useHealthStore() {
  async function refrescar() {
    cargando.value = true
    try {
      health.value = await fetchHealth()
    } catch (e) {
      health.value = {
        status: 'error',
        error: e.message,
        timestamp: new Date().toISOString(),
      }
    }
    if (esEntornoLocal()) {
      streamlitOk.value = null
    } else {
      try {
        const base = STREAMLIT_URL.replace(/\/$/, '')
        const r = await fetch(`${base}/_stcore/health`, { mode: 'no-cors' })
        streamlitOk.value = r.type === 'opaque' || r.ok
      } catch {
        streamlitOk.value = false
      }
    }
    cargando.value = false
  }

  function iniciarPolling(ms = 30000) {
    detenerPolling()
    refrescar()
    pollTimer = setInterval(refrescar, ms)
  }

  function detenerPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  return {
    health,
    streamlitOk,
    cargando,
    refrescar,
    iniciarPolling,
    detenerPolling,
    streamlitUrl: STREAMLIT_URL,
    streamlitPublicUrl: STREAMLIT_PUBLIC,
  }
}
