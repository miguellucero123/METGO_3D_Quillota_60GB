<template>
  <div class="auth-page">
    <div class="auth-panel">
      <div class="auth-brand">
        <h1>{{ site.productName }} {{ site.brandName || 'VENTORA' }}</h1>
        <p class="auth-tagline">Nueva contraseña</p>
      </div>

      <div v-if="!token" class="auth-msg" role="alert">
        Enlace inválido: falta el token. Solicite uno nuevo desde
        <router-link :to="forgotLink">recuperar contraseña</router-link>.
      </div>
      <form v-else-if="!listo" class="auth-form" @submit.prevent="onSubmit">
        <label class="field">
          <span>Nueva contraseña (mín. 8 caracteres)</span>
          <input v-model="password" type="password" autocomplete="new-password" required minlength="8" />
        </label>
        <label class="field">
          <span>Confirmar contraseña</span>
          <input v-model="password2" type="password" autocomplete="new-password" required minlength="8" />
        </label>
        <p v-if="error" class="auth-msg" role="alert">{{ error }}</p>
        <button type="submit" class="btn-primary auth-btn" :disabled="cargando">
          {{ cargando ? 'Guardando…' : 'Guardar nueva contraseña' }}
        </button>
      </form>
      <div v-else class="auth-ok" role="status">
        Contraseña actualizada. Ya puede
        <router-link :to="loginLink">iniciar sesión</router-link>.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { useRoute } from 'vue-router'
import { resetearPassword } from '@/services/authApi'

const site = inject('site')
const route = useRoute()
const faenaFija = computed(() => {
  const p = route.params.puerto
  return p ? String(p).toLowerCase() : ''
})
const loginLink = computed(() => (faenaFija.value ? `/p/${faenaFija.value}/login` : '/login'))
const forgotLink = computed(() =>
  faenaFija.value ? `/p/${faenaFija.value}/olvide-password` : '/olvide-password',
)
const token = computed(() => (typeof route.query.token === 'string' ? route.query.token : ''))

const password = ref('')
const password2 = ref('')
const error = ref('')
const cargando = ref(false)
const listo = ref(false)

async function onSubmit() {
  error.value = ''
  if (password.value.length < 8) {
    error.value = 'La contraseña debe tener al menos 8 caracteres'
    return
  }
  if (password.value !== password2.value) {
    error.value = 'Las contraseñas no coinciden'
    return
  }
  cargando.value = true
  try {
    await resetearPassword({ token: token.value, password: password.value })
    listo.value = true
  } catch (e) {
    error.value = e.message || 'El enlace expiró o ya fue usado. Solicite uno nuevo.'
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: #0f172a;
}
.auth-panel {
  width: 100%;
  max-width: 400px;
  background: #111827;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 2.5rem 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 10px 15px -3px rgba(0, 0, 0, 0.2);
}
.auth-brand {
  text-align: center;
  margin-bottom: 1.5rem;
}
.auth-brand h1 {
  margin: 0;
  font-size: 1.35rem;
  color: #f8fafc;
}
.auth-tagline {
  margin: 0.35rem 0 0;
  color: #94a3b8;
  font-size: 0.85rem;
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
  color: #64748b;
  margin-bottom: 0.3rem;
}
.field input {
  width: 100%;
  padding: 0.75rem;
  border-radius: 4px;
  border: 1px solid #334155;
  background: #0b1220;
  color: #e2e8f0;
}
.field input:focus {
  outline: none;
  border-color: #0ea5e9;
}
.auth-msg {
  color: #f87171;
  font-size: 0.85rem;
  margin: 0 0 0.75rem;
}
.auth-msg a,
.auth-ok a {
  color: #0ea5e9;
  font-weight: 600;
}
.auth-ok {
  color: #34d399;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.35);
  border-radius: 8px;
  font-size: 0.85rem;
  margin: 0 0 1rem;
  padding: 0.75rem 0.85rem;
  line-height: 1.45;
}
.auth-btn {
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  background: #0ea5e9;
  color: #ffffff;
}
.auth-btn:disabled {
  opacity: 0.65;
}
</style>
