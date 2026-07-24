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

const state = reactive({
  token: getToken(),
  user: getStoredUser(),
})

export function useAuth() {
  const isAuthenticated = computed(() => Boolean(state.token))

  async function login(username, password) {
    const data = await apiLogin(username, password)
    if (data.user?.sitio != null && data.user.sitio !== SITIO) {
      throw new Error(`Este acceso es para el sitio ${data.user.sitio}, no ${SITIO}`)
    }
    state.token = data.access_token
    state.user = data.user
    setSession(data.access_token, data.user)
    return data
  }

  function logout() {
    clearSession()
    state.token = ''
    state.user = null
  }

  async function ensureValidSession() {
    if (!state.token) return false
    try {
      const me = await fetchMe()
      if (me?.sitio != null && me.sitio !== SITIO) {
        logout()
        return false
      }
      state.user = me
      setSession(state.token, me)
      return true
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
