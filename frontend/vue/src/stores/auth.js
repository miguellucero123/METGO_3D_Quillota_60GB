import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as authLogin, register as authRegister } from '@/services/authService'
import { fetchMe } from '@/api/metgoApi'

const TOKEN_KEY = 'metgo_access_token'
const USER_KEY = 'metgo_user'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))

  const isAuthenticated = computed(() => Boolean(token.value))

  function setSession(accessToken, userData) {
    token.value = accessToken
    user.value = userData
    localStorage.setItem(TOKEN_KEY, accessToken)
    localStorage.setItem(USER_KEY, JSON.stringify(userData))
  }

  function clearSession() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  async function login(username, password) {
    const data = await authLogin(username, password)
    setSession(data.access_token, data.user)
    return data
  }

  async function register(username, password, email) {
    const data = await authRegister({ username, password, email })
    setSession(data.access_token, data.user)
    return data
  }

  function logout() {
    clearSession()
  }

  /** Valida JWT guardado; si expiró, limpia sesión. */
  async function ensureValidSession() {
    if (!token.value) return false
    try {
      const me = await fetchMe()
      user.value = me
      localStorage.setItem(USER_KEY, JSON.stringify(me))
      return true
    } catch {
      clearSession()
      return false
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    register,
    logout,
    clearSession,
    ensureValidSession,
  }
})
