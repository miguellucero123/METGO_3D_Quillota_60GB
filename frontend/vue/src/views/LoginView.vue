<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Leaf, LogIn } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useMetgoStore } from '@/stores/metgo'
import { wakeApi } from '@/api/metgoApi'
import { sanitizeRedirectPath } from '@/utils/sanitizeRedirectPath'
import { AUTH_ERROR_INVALID } from '@/services/authService'
import { setLocale } from '@/i18n'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'

const { t, locale } = useI18n()
const router = useRouter()
const auth = useAuthStore()
const metgo = useMetgoStore()

const username = ref('')
const password = ref('')
const error = ref('')
const cargando = ref(false)
const allowSelfRegister = import.meta.env.VITE_ALLOW_SELF_REGISTER === '1'

onMounted(() => {
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
      <div class="auth-lang" role="group" :aria-label="t('lang.label')">
        <ThemeToggle />
        <button type="button" :class="{ active: locale === 'es' }" @click="setLocale('es')">
          {{ t('lang.es') }}
        </button>
        <button type="button" :class="{ active: locale === 'en' }" @click="setLocale('en')">
          {{ t('lang.en') }}
        </button>
      </div>
      <div class="auth-brand">
        <div class="auth-logo">
          <Leaf aria-hidden="true" />
        </div>
        <h1>{{ t('login.title') }}</h1>
        <p class="auth-tagline">{{ t('login.subtitle') }}</p>
        <p class="auth-region">Quillota · Región de Valparaíso</p>
      </div>

      <form class="auth-form" @submit.prevent="onSubmit">
        <label class="field">
          <span>{{ t('login.user') }}</span>
          <input
            v-model="username"
            type="text"
            autocomplete="username"
            required
          />
        </label>
        <label class="field">
          <span>{{ t('login.password') }}</span>
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
          {{ cargando ? t('login.loading') : t('login.submit') }}
        </button>
      </form>

      <p v-if="allowSelfRegister" class="auth-footer">
        ¿No tiene cuenta?
        <router-link to="/registro">Registrarse</router-link>
      </p>
      <p class="hint">Acceso restringido · JWT en servidor METGO</p>
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/auth-page.css';
.auth-lang {
  display: flex;
  justify-content: flex-end;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
}
.auth-lang button {
  border: 1px solid var(--color-border, #334155);
  background: transparent;
  color: var(--color-muted, #94a3b8);
  border-radius: 6px;
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
  cursor: pointer;
}
.auth-lang button.active {
  color: var(--color-primary, #00ffaa);
  border-color: var(--color-primary, #00ffaa);
}
</style>
