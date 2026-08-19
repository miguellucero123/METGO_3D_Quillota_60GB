import { createI18n } from 'vue-i18n'
import es from './locales/es.json'
import en from './locales/en.json'
import de from './locales/de.json'
import fr from './locales/fr.json'
import it from './locales/it.json'
import ko from './locales/ko.json'

const STORAGE_KEY = 'metgo_locale'

function initialLocale() {
  if (typeof localStorage === 'undefined') return 'es'
  const saved = localStorage.getItem(STORAGE_KEY)
  if (['en', 'es', 'de', 'fr', 'it', 'ko'].includes(saved)) return saved
  const nav = (typeof navigator !== 'undefined' && navigator.language) || 'es'
  const prefix = nav.toLowerCase().substring(0, 2)
  return ['en', 'es', 'de', 'fr', 'it', 'ko'].includes(prefix) ? prefix : 'es'
}

export const i18n = createI18n({
  legacy: false,
  locale: initialLocale(),
  fallbackLocale: 'es',
  messages: { es, en, de, fr, it, ko },
})

export function setLocale(locale) {
  const next = ['en', 'es', 'de', 'fr', 'it', 'ko'].includes(locale) ? locale : 'es'
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
