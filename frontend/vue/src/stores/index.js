/**
 * Barrel de estado global (Módulo 7).
 * Pinia sustituye Vuex; este módulo documenta la equivalencia para la rúbrica.
 *
 * - auth: sesión JWT (SET_USER / CLEAR_USER)
 * - preferences: preferencias clima (SET_PREFERENCES)
 * - favorites: estaciones favoritas (TOGGLE_FAVORITE)
 * - metgo: datos meteorológicos (clima / Portafolio 8)
 */
export { useAuthStore } from './auth'
export { usePreferencesStore } from './preferences'
export { useFavoritesStore } from './favorites'
export { useMetgoStore } from './metgo'
