<script setup>
import { ref, onMounted, inject, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { HardHat, LogIn } from 'lucide-vue-next'
import { useAuth } from '@/stores/auth'
import { wakeApi } from '@/services/authApi'
import { setLocale } from '@/i18n'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'

const site = inject('site')
const router = useRouter()
const route = useRoute()
const auth = useAuth()
const { t, locale } = useI18n()

const faena = computed(() => String(route.params.faena || site.spatiDefaultSitio || 'escondida'))
const faenaMeta = computed(() => (site.stations || []).find((s) => s.slug === faena.value))

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
    await auth.login(username.value.trim(), password.value, {
      faena: faena.value,
      sitio: 'spati',
    })
    let redirect =
      typeof route.query.redirect === 'string' ? route.query.redirect : `/f/${faena.value}/ahora`
    // Nunca dejar al operador en el hub público tras login
    if (redirect === '/' || redirect.startsWith('/?')) {
      redirect = `/f/${faena.value}/ahora`
    }
    // Entrada por defecto: vista Ahora (mapa + horas), no el panel denso
    if (redirect === `/f/${faena.value}/` || redirect === `/f/${faena.value}`) {
      redirect = `/f/${faena.value}/ahora`
    }
    await router.replace(redirect.startsWith('/') ? redirect : `/f/${faena.value}/ahora`)
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
          <HardHat aria-hidden="true" />
        </div>
        <h1>{{ site.productName }}</h1>
        <p class="auth-tagline">{{ t('login.subtitle') }}</p>
        <p class="auth-region">{{ faenaMeta?.nombre || faena }} · {{ faenaMeta?.region || site.region }}</p>
        <p class="login-hint">{{ t('login.hint') }}</p>
      </div>

      <form class="auth-form" @submit.prevent="onSubmit">
        <label class="field">
          <span>{{ t('login.user') }}</span>
          <input v-model="username" type="text" autocomplete="username" required />
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
        <p v-if="error" class="auth-msg" role="alert">{{ error }}</p>
        <button type="submit" class="btn-primary auth-btn" :disabled="cargando">
          <LogIn :size="18" aria-hidden="true" />
          {{ cargando ? t('login.loading') : t('login.submit') }}
        </button>
      </form>
      <p class="auth-footer">
        Faena <code>{{ faena }}</code> ·
        <router-link :to="`/f/${faena}/registro`">Registrarse</router-link>
      </p>
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
    radial-gradient(circle at 20% 40%, rgba(249, 115, 22, 0.16), transparent 28%),
    radial-gradient(circle at 80% 20%, rgba(234, 179, 8, 0.1), transparent 26%);
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
.auth-lang {
  display: flex;
  justify-content: flex-end;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
}
.auth-lang button {
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-muted);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
}
.auth-lang button.active {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: rgba(249, 115, 22, 0.12);
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
