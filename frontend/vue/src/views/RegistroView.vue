<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Leaf, UserPlus } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useMetgoStore } from '@/stores/metgo'
import { wakeApi } from '@/api/metgoApi'
import { sanitizeRedirectPath } from '@/utils/sanitizeRedirectPath'

const router = useRouter()
const auth = useAuthStore()
const metgo = useMetgoStore()

const username = ref('')
const email = ref('')
const password = ref('')
const password2 = ref('')
const error = ref('')
const okMsg = ref('')
const cargando = ref(false)

async function onSubmit() {
  error.value = ''
  okMsg.value = ''
  if (password.value !== password2.value) {
    error.value = 'Las contraseñas no coinciden'
    return
  }
  cargando.value = true
  try {
    try {
      await wakeApi()
    } catch (e) {
      error.value = e.message ?? 'No se pudo contactar la API.'
      return
    }
    await auth.register(username.value.trim(), password.value, email.value.trim() || undefined)
    await metgo.inicializar()
    okMsg.value = 'Cuenta creada. Redirigiendo…'
    const redirect = sanitizeRedirectPath(router.currentRoute.value.query.redirect, '/')
    router.push(redirect)
  } catch (e) {
    error.value = e.message ?? 'No se pudo completar el registro'
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
        <h1>Crear cuenta METGO</h1>
        <p class="auth-tagline">Acceso de lectura al monitoreo del valle</p>
        <p class="auth-region">Quillota · Región de Valparaíso</p>
      </div>

      <form class="auth-form" @submit.prevent="onSubmit">
        <label class="field">
          <span>Usuario</span>
          <input
            v-model="username"
            type="text"
            autocomplete="username"
            required
            minlength="3"
            maxlength="32"
            pattern="[a-z0-9_]+"
            placeholder="campo_norte"
          />
        </label>
        <label class="field">
          <span>Correo (opcional)</span>
          <input v-model="email" type="email" autocomplete="email" placeholder="usuario@ejemplo.cl" />
        </label>
        <label class="field">
          <span>Contraseña</span>
          <input
            v-model="password"
            type="password"
            autocomplete="new-password"
            required
            minlength="6"
          />
        </label>
        <label class="field">
          <span>Confirmar contraseña</span>
          <input
            v-model="password2"
            type="password"
            autocomplete="new-password"
            required
            minlength="6"
          />
        </label>
        <p v-if="error" class="auth-msg auth-msg--error" role="alert">{{ error }}</p>
        <p v-if="okMsg" class="auth-msg auth-msg--ok" role="status">{{ okMsg }}</p>
        <button type="submit" class="btn btn--full" :disabled="cargando">
          <UserPlus class="btn-icon" aria-hidden="true" />
          {{ cargando ? 'Registrando…' : 'Registrarse' }}
        </button>
      </form>

      <p class="auth-footer">
        ¿Ya tiene cuenta?
        <router-link to="/login">Iniciar sesión</router-link>
      </p>
      <p class="hint">Rol asignado: <strong>lectura</strong> · favoritos y preferencias de clima</p>
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/auth-page.css';
</style>
