<template>
  <div class="auth-page">
    <div class="auth-panel">
      <div class="auth-brand">
        <h1>{{ site.productName }} {{ site.brandName || 'VENTORA' }}</h1>
        <p class="auth-tagline">Recuperar contraseña</p>
      </div>

      <form v-if="!enviado" class="auth-form" @submit.prevent="onSubmit">
        <label class="field">
          <span>Email</span>
          <input v-model="email" type="email" autocomplete="username" required />
        </label>
        <p v-if="error" class="auth-msg" role="alert">{{ error }}</p>
        <button type="submit" class="btn-primary auth-btn" :disabled="cargando">
          {{ cargando ? 'Enviando…' : 'Enviar enlace de recuperación' }}
        </button>
      </form>
      <p v-else class="auth-ok" role="status">
        Si el correo está registrado, recibirá un enlace para restablecer su contraseña
        (revise también spam). El enlace expira en 1 hora.
      </p>

      <p class="auth-footer">
        <router-link :to="loginLink">Volver a iniciar sesión</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { useRoute } from 'vue-router'
import { solicitarResetPassword } from '@/services/authApi'

const site = inject('site')
const route = useRoute()
const faenaFija = computed(() => {
  const p = route.params.puerto
  return p ? String(p).toLowerCase() : ''
})
const loginLink = computed(() => (faenaFija.value ? `/p/${faenaFija.value}/login` : '/login'))

const email = ref('')
const error = ref('')
const cargando = ref(false)
const enviado = ref(false)

async function onSubmit() {
  error.value = ''
  cargando.value = true
  try {
    await solicitarResetPassword({ email: email.value.trim(), faena: faenaFija.value || undefined })
    enviado.value = true
  } catch (e) {
    error.value = e.message || 'No se pudo procesar la solicitud. Intente de nuevo.'
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
.auth-footer {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.8rem;
}
.auth-footer a {
  color: #0ea5e9;
  text-decoration: none;
  font-weight: 600;
}
</style>
