<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Leaf, LogIn } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useMetgoStore } from '@/stores/metgo'
import { wakeApi } from '@/api/metgoApi'
import { sanitizeRedirectPath } from '@/utils/sanitizeRedirectPath'
import { AUTH_ERROR_INVALID } from '@/services/authService'

const router = useRouter()
const auth = useAuthStore()
const metgo = useMetgoStore()

const username = ref('')
const password = ref('')
const error = ref('')
const cargando = ref(false)

onMounted(() => {
  // Despertar la API de forma silenciosa al entrar a la página (Render Cold Start)
  wakeApi().catch(() => {})
})

async function onSubmit() {
  error.value = ''
  cargando.value = true
  try {
    try {
      await wakeApi()
    } catch (e) {
      error.value = e.message ?? 'No se pudo contactar la API. Reintente en un minuto.'
      return
    }
    await auth.login(username.value.trim(), password.value)
    const { usePreferencesStore } = await import('@/stores/preferences')
    const { useFavoritesStore } = await import('@/stores/favorites')
    await Promise.all([
      usePreferencesStore().syncFromServer(),
      useFavoritesStore().syncFromServer(),
    ])
    await metgo.inicializar()
    const redirect = sanitizeRedirectPath(router.currentRoute.value.query.redirect, '/')
    router.push(redirect)
  } catch (e) {
    error.value = e.message ?? AUTH_ERROR_INVALID
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-panel">
      <div class="auth-brand">
        <div class="auth-logo">
          <Leaf aria-hidden="true" />
        </div>
        <h1>METGO</h1>
        <p class="auth-tagline">Monitoreo meteorológico y agrícola</p>
        <p class="auth-region">Quillota · Región de Valparaíso</p>
        <p class="login-hint muted">
          Demo: <strong>admin</strong>/admin123 · <strong>agronomo</strong>/agro123 ·
          <strong>operador</strong>/op123 · <strong>lector</strong>/lec123
        </p>
      </div>

      <form class="auth-form" @submit.prevent="onSubmit">
        <label class="field">
          <span>Usuario</span>
          <input
            v-model="username"
            type="text"
            autocomplete="username"
            required
            placeholder="admin"
          />
        </label>
        <label class="field">
          <span>Contraseña</span>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            required
          />
        </label>
        <p v-if="error" class="auth-msg auth-msg--error" role="alert">{{ error }}</p>
        <button type="submit" class="btn btn--full" :disabled="cargando">
          <LogIn class="btn-icon" aria-hidden="true" />
          {{ cargando ? 'Ingresando…' : 'Iniciar sesión' }}
        </button>
      </form>

      <p class="auth-footer">
        ¿No tiene cuenta?
        <router-link to="/registro">Registrarse</router-link>
      </p>
      <p class="hint">Acceso restringido · JWT en servidor METGO</p>
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/auth-page.css';
</style>
