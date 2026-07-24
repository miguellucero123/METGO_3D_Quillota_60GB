<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { HardHat, LogIn } from 'lucide-vue-next'
import { useAuth } from '@/stores/auth'
import { wakeApi } from '@/services/authApi'

const site = inject('site')
const router = useRouter()
const route = useRoute()
const auth = useAuth()

const username = ref('')
const password = ref('')
const error = ref('')
const cargando = ref(false)

onMounted(() => {
  wakeApi().catch(() => {})
})

async function onSubmit() {
  error.value = ''
  cargando.value = true
  try {
    await wakeApi()
    await auth.login(username.value.trim(), password.value)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    router.replace(redirect.startsWith('/') ? redirect : '/')
  } catch (e) {
    error.value = e.message || 'Usuario o contraseña incorrectos'
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
          <HardHat aria-hidden="true" />
        </div>
        <h1>{{ site.productName }}</h1>
        <p class="auth-tagline">{{ site.tagline }}</p>
        <p class="auth-region">{{ site.region }}</p>
        <p class="login-hint">
          Demo: <strong>mantos</strong>/mantos123 · <strong>admin</strong>/admin123
        </p>
      </div>

      <form class="auth-form" @submit.prevent="onSubmit">
        <label class="field">
          <span>Usuario</span>
          <input v-model="username" type="text" autocomplete="username" required placeholder="mantos" />
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
        <p v-if="error" class="auth-msg" role="alert">{{ error }}</p>
        <button type="submit" class="btn-primary auth-btn" :disabled="cargando">
          <LogIn :size="18" aria-hidden="true" />
          {{ cargando ? 'Ingresando…' : 'Iniciar sesión' }}
        </button>
      </form>
      <p class="auth-footer">JWT · sitio <code>{{ site.sitio }}</code> · E9</p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: var(--color-bg);
  background-image:
    radial-gradient(circle at 18% 45%, rgba(251, 146, 60, 0.2), transparent 28%),
    radial-gradient(circle at 82% 18%, rgba(253, 186, 116, 0.12), transparent 24%);
}
.auth-panel {
  width: 100%;
  max-width: 420px;
  background: rgba(17, 24, 39, 0.75);
  backdrop-filter: blur(14px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 2.25rem 1.75rem;
  box-shadow: var(--shadow-lg);
}
.auth-brand {
  text-align: center;
  margin-bottom: 1.5rem;
}
.auth-logo {
  width: 3rem;
  height: 3rem;
  margin: 0 auto 0.85rem;
  display: grid;
  place-items: center;
  background: var(--color-primary);
  color: #0b1120;
  border-radius: var(--radius-md);
}
.auth-brand h1 {
  margin: 0;
  font-size: 1.35rem;
  color: var(--color-text);
}
.auth-tagline,
.auth-region,
.login-hint,
.auth-footer {
  margin: 0.35rem 0 0;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}
.login-hint {
  margin-top: 0.75rem;
  color: var(--color-muted);
}
.field {
  display: block;
  margin-bottom: 0.9rem;
}
.field span {
  display: block;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-muted);
  margin-bottom: 0.3rem;
}
.field input {
  width: 100%;
  padding: 0.65rem 0.75rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
}
.auth-msg {
  color: var(--color-danger);
  font-size: 0.85rem;
  margin: 0 0 0.75rem;
}
.auth-btn {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.7rem 1rem;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-weight: 600;
}
.auth-footer {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.75rem;
}
.auth-footer code {
  color: var(--color-primary);
}
</style>
