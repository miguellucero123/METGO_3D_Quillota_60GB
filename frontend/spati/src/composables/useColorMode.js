/**
 * Modo claro/oscuro (singleton por SPA).
 * Persistencia: localStorage `${storagePrefix}_theme`
 */
import { ref } from 'vue'
import site from '@/site.config'

const key = `${site.storagePrefix || site.sitio || 'metgo'}_theme`
const theme = ref('dark')

export function applyColorMode(mode) {
  if (typeof document === 'undefined') return
  document.documentElement.setAttribute(
    'data-theme',
    mode === 'light' ? 'light' : 'dark',
  )
}

export function setTheme(value) {
  theme.value = value === 'light' ? 'light' : 'dark'
  applyColorMode(theme.value)
  try {
    localStorage.setItem(key, theme.value)
  } catch {
    /* ignore */
  }
}

export function toggleTheme() {
  setTheme(theme.value === 'dark' ? 'light' : 'dark')
}

export function initTheme() {
  let saved = null
  try {
    saved = localStorage.getItem(key)
  } catch {
    /* ignore */
  }
  if (saved === 'light' || saved === 'dark') theme.value = saved
  applyColorMode(theme.value)
}

export function useColorMode() {
  return { theme, setTheme, toggleTheme, initTheme }
}
