import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const STORAGE_KEY = 'metgo_preferences'

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

  function persist() {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ tempUnit: tempUnit.value, theme: theme.value })
    )
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

  watch(tempUnit, persist)

  return { tempUnit, theme, setTempUnit, setTheme, init }
})
