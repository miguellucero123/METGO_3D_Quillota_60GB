import { reactive, computed } from 'vue'
import {
  login as apiLogin,
  fetchMe,
  getToken,
  getStoredUser,
  setSession,
  clearSession,
  SITIO,
} from '@/services/authApi'
import { useAccess } from '@/stores/access'
import { invalidateHubCache } from '@/stores/hubCache'

const state = reactive({
  token: getToken(),
  user: getStoredUser(),
})

export function useAuth() {
  const isAuthenticated = computed(() => Boolean(state.token))

  async function login(username, password, opts = {}) {
    const data = await apiLogin(username, password, opts)
    const sitioUser = data.user?.sitio
    const allowed = new Set([SITIO, 'spati', 'mantos_blancos'])
    if (sitioUser != null && !allowed.has(sitioUser)) {
      throw new Error(`Este acceso es para el sitio ${sitioUser}, no SPATI`)
    }
    state.token = data.access_token
    state.user = data.user
    setSession(data.access_token, data.user)
    useAccess().invalidate()
    invalidateHubCache()
    return data
  }

  function logout() {
    clearSession()
    state.token = ''
    state.user = null
    useAccess().invalidate()
    invalidateHubCache()
  }

  async function ensureValidSession() {
    // Releer storage por si otro módulo limpió el token (p. ej. 401 en authApi)
    state.token = getToken()
    if (!state.token) {
      state.user = null
      return false
    }
    try {
      const me = await fetchMe()
      const sitioUser = me?.sitio
      const allowed = new Set([SITIO, 'spati', 'mantos_blancos'])
      // admin global: sitio null → OK
      if (sitioUser != null && sitioUser !== '' && !allowed.has(sitioUser)) {
        logout()
        return false
      }
      state.token = getToken()
      state.user = me
      if (state.token) setSession(state.token, me)
      return Boolean(state.token)
    } catch {
      logout()
      return false
    }
  }

  return {
    state,
    isAuthenticated,
    login,
    logout,
    ensureValidSession,
  }
}
