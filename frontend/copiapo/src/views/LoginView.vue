<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Wind, LogIn } from 'lucide-vue-next'
import { useAuth } from '@/stores/auth'
import { wakeApi, reenviarVerificacion } from '@/services/authApi'
import { setLocale } from '@/i18n'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'

const site = inject('site')
const router = useRouter()
const route = useRoute()
const auth = useAuth()
const { t, locale } = useI18n()

const username = ref('')
const password = ref('')
const error = ref('')
const cargando = ref(false)
const registeredBanner = ref('')
const reenviando = ref(false)
const resendMsg = ref('')

onMounted(() => {
  wakeApi().catch(() => {})
  if (route.query.registered === '1' || route.query.registered === 'true') {
    registeredBanner.value = t('login.registeredOk')
    if (typeof route.query.email === 'string' && route.query.email) {
      username.value = route.query.email
    }
  }
})

async function onSubmit() {
  error.value = ''
  resendMsg.value = ''
  cargando.value = true
  try {
    await wakeApi()
    await auth.login(username.value.trim(), password.value)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/app'
    router.replace(redirect.startsWith('/') && redirect !== '/login' ? redirect : '/app')
  } catch (e) {
    if (e.code === 'email_not_verified') error.value = t('login.emailNotVerified')
    else if (e.code === 'subscription_expired') error.value = e.message || 'Piloto o suscripción vencida'
    else error.value = e.message || t('login.errorGeneric')
  } finally {
    cargando.value = false
  }
}

async function onResend() {
  error.value = ''
  resendMsg.value = ''
  if (!username.value.trim() || !password.value) {
    error.value = t('login.resendNeedPass')
    return
  }
  reenviando.value = true
  try {
    const res = await reenviarVerificacion({
      email: username.value.trim(),
      password: password.value,
      sitio: site.sitio || 'copiapo',
    })
    if (res.already_verified) resendMsg.value = 'Email ya verificado. Puede iniciar sesión.'
    else {
      resendMsg.value = t('login.resendOk')
      if (res.email && res.email.sent === false) {
        error.value = res.email.error || 'No se pudo confirmar el envío del correo'
      }
    }
  } catch (e) {
    error.value = e.message || t('login.errorGeneric')
  } finally {
    reenviando.value = false
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
          <Wind aria-hidden="true" />
        </div>
        <h1>{{ site.productName }}</h1>
        <p class="auth-tagline">{{ t('login.subtitle') }}</p>
        <p class="auth-region">{{ site.region }}</p>
        <p class="login-hint">{{ t('login.hint') }}</p>
      </div>

      <p v-if="registeredBanner" class="auth-ok" role="status">{{ registeredBanner }}</p>

      <form class="auth-form" @submit.prevent="onSubmit">
        <label class="field">
          <span>{{ t('login.user') }}</span>
          <input v-model="username" type="email" autocomplete="username" required />
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
        <button type="button" class="linkish" :disabled="reenviando" @click="onResend">
          {{ reenviando ? '…' : t('login.resend') }}
        </button>
        ·
        <router-link to="/">{{ t('app.home') }}</router-link>
        ·
        <router-link to="/registro">{{ t('app.register') }}</router-link>
      </p>
      <p v-if="resendMsg" class="auth-ok" role="status">{{ resendMsg }}</p>
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
    radial-gradient(circle at 20% 40%, rgba(251, 191, 36, 0.18), transparent 28%),
    radial-gradient(circle at 80% 20%, rgba(251, 146, 60, 0.12), transparent 26%);
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
  background: rgba(251, 191, 36, 0.12);
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
  border-radius: 8px;
  border: 1px solid var(--color-border);
  background: rgba(0, 0, 0, 0.25);
  color: var(--color-text);
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
}
.auth-footer {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.8rem;
}
.auth-footer a,
.auth-footer .linkish {
  color: var(--color-primary);
  font-weight: 600;
  background: none;
  border: none;
  font-size: inherit;
  font-family: inherit;
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
}
.auth-footer .linkish:disabled {
  opacity: 0.6;
  cursor: wait;
}
</style>
