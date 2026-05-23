<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Leaf, LogIn } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useMetgoStore } from '@/stores/metgo'

const router = useRouter()
const auth = useAuthStore()
const metgo = useMetgoStore()

const username = ref('')
const password = ref('')
const error = ref('')
const cargando = ref(false)

async function onSubmit() {
  error.value = ''
  cargando.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    await metgo.inicializar()
    router.push('/')
  } catch (e) {
    error.value = e.message ?? 'Error de inicio de sesión'
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-panel">
      <div class="login-brand">
        <div class="login-logo">
          <Leaf aria-hidden="true" />
        </div>
        <h1>METGO</h1>
        <p class="login-tagline">Monitoreo meteorológico y agrícola</p>
        <p class="login-region">Quillota · Región de Valparaíso</p>
      </div>

      <form class="login-form" @submit.prevent="onSubmit">
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
        <p v-if="error" class="error" role="alert">{{ error }}</p>
        <button type="submit" class="btn btn--full" :disabled="cargando">
          <LogIn class="btn-icon" aria-hidden="true" />
          {{ cargando ? 'Ingresando…' : 'Iniciar sesión' }}
        </button>
      </form>

      <p class="hint">Acceso restringido · credenciales configuradas en el servidor</p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: var(--color-bg);
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -20%, var(--color-primary-muted), transparent),
    linear-gradient(180deg, var(--color-primary-subtle) 0%, var(--color-bg) 45%);
}

.login-panel {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 2rem;
}

.login-brand {
  text-align: center;
  margin-bottom: 1.75rem;
}

.login-logo {
  width: 3rem;
  height: 3rem;
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: #fff;
  border-radius: var(--radius-md);
}

.login-logo svg {
  width: 1.5rem;
  height: 1.5rem;
}

.login-brand h1 {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--color-text);
}

.login-tagline {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-top: 0.35rem;
}

.login-region {
  font-size: 0.8rem;
  color: var(--color-muted);
  margin-top: 0.2rem;
}

.field {
  display: block;
  margin-bottom: 1rem;
}

.field span {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-muted);
  margin-bottom: 0.35rem;
}

.field input {
  width: 100%;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.95rem;
  font-family: inherit;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.field input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-primary-muted);
}

.error {
  color: var(--color-danger);
  font-size: 0.85rem;
  margin-bottom: 0.75rem;
}

.btn--full {
  width: 100%;
  padding: 0.7rem;
}

.btn-icon {
  width: 1rem;
  height: 1rem;
}

.hint {
  margin-top: 1.25rem;
  font-size: 0.72rem;
  color: var(--color-muted);
  text-align: center;
}
</style>
