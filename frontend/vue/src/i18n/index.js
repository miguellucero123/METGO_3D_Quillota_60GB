import { createI18n } from 'vue-i18n'
import es from './locales/es.json'
import en from './locales/en.json'

const STORAGE_KEY = 'metgo_locale'

function initialLocale() {
  if (typeof localStorage === 'undefined') return 'es'
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'en' || saved === 'es') return saved
  const nav = (typeof navigator !== 'undefined' && navigator.language) || 'es'
  return nav.toLowerCase().startsWith('en') ? 'en' : 'es'
}

export const i18n = createI18n({
  legacy: false,
  locale: initialLocale(),
  fallbackLocale: 'es',
  messages: { es, en },
})

export function setLocale(locale) {
  const next = locale === 'en' ? 'en' : 'es'
  i18n.global.locale.value = next
  try {
    localStorage.setItem(STORAGE_KEY, next)
  } catch {
    /* ignore */
  }
  if (typeof document !== 'undefined') {
    document.documentElement.lang = next
  }
}

export default i18n
