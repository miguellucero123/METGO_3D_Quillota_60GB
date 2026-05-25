import { ref } from 'vue'
import { fetchHealth } from '@/api/metgoApi'

const health = ref(null)
const streamlitOk = ref(null)
const cargando = ref(false)
let pollTimer = null

const STREAMLIT_URL =
  import.meta.env.VITE_METGO_STREAMLIT_URL ||
  'https://metgo-3d-quillota-60gb.streamlit.app'

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
    try {
      const r = await fetch(STREAMLIT_URL, { mode: 'no-cors' })
      streamlitOk.value = r.type === 'opaque' || r.ok
    } catch {
      streamlitOk.value = false
    } finally {
      cargando.value = false
    }
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
  }
}
