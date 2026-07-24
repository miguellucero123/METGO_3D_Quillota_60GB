import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { fetchPreferencias, savePreferencias } from '@/api/metgoApi'
import { useAuthStore } from '@/stores/auth'

const STORAGE_KEY = 'metgo_preferences'
/** SPA Quillota: sitio de producto fijo (E9). */
export const SITIO_QUILLOTA = 'quillota'

function loadPrefs() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
  } catch {
    return {}
  }
}

function applyTheme(theme) {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  if (theme === 'dark') {
    root.setAttribute('data-theme', 'dark')
  } else {
    root.removeAttribute('data-theme')
  }
}

export const usePreferencesStore = defineStore('preferences', () => {
  const saved = loadPrefs()
  const tempUnit = ref(saved.tempUnit === 'F' ? 'F' : 'C')
  const theme = ref(saved.theme === 'dark' ? 'dark' : 'light')
  const syncing = ref(false)
  let skipServer = false

  function persistLocal() {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ tempUnit: tempUnit.value, theme: theme.value })
    )
  }

  async function persistServer() {
    const auth = useAuthStore()
    if (!auth.isAuthenticated || syncing.value) return
    try {
      await savePreferencias({
        sitio: SITIO_QUILLOTA,
        prefs: { tempUnit: tempUnit.value, theme: theme.value },
      })
    } catch {
      // localStorage ya persistió; Supabase puede no estar disponible
    }
  }

  function persist() {
    persistLocal()
    if (!skipServer) {
      void persistServer()
    }
  }

  function setTempUnit(unit) {
    tempUnit.value = unit === 'F' ? 'F' : 'C'
    persist()
  }

  function setTheme(value) {
    theme.value = value === 'dark' ? 'dark' : 'light'
    applyTheme(theme.value)
    persist()
  }

  function init() {
    applyTheme(theme.value)
  }

  /** Carga prefs del servidor (usuario+sitio) y las aplica localmente. */
  async function syncFromServer() {
    const auth = useAuthStore()
    if (!auth.isAuthenticated) return
    syncing.value = true
    skipServer = true
    try {
      const data = await fetchPreferencias(SITIO_QUILLOTA)
      const prefs = data?.prefs || {}
      if (prefs.tempUnit === 'F' || prefs.tempUnit === 'C') {
        tempUnit.value = prefs.tempUnit
      }
      if (prefs.theme === 'dark' || prefs.theme === 'light') {
        theme.value = prefs.theme
        applyTheme(theme.value)
      }
      persistLocal()
      // Primera vez: subir local al servidor
      if (!data?.existe) {
        skipServer = false
        await persistServer()
      }
    } catch {
      // Mantener localStorage
    } finally {
      skipServer = false
      syncing.value = false
    }
  }

  watch(tempUnit, () => {
    if (!skipServer) persistLocal()
  })

  return { tempUnit, theme, setTempUnit, setTheme, init, syncFromServer, syncing }
})
