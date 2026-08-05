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
        <h1>{{ site.productName }} {{ site.brandName || 'VENTORA' }}</h1>
        <p class="auth-tagline">{{ t('login.tagline') }}</p>
        <p v-if="faenaFija" class="auth-region">
          {{ faenaMeta?.nombre || faenaFija }} · {{ faenaMeta?.region || '' }}
        </p>
        <p v-else class="login-hint">
          {{ t('login.hint') }}
        </p>
      </div>

      <p v-if="registeredBanner" class="auth-ok" role="status">{{ registeredBanner }}</p>

      <form class="auth-form" @submit.prevent="onSubmit" aria-labelledby="login-heading">
        <h2 id="login-heading" class="sr-only">{{ t('login.submit') }}</h2>
        <label v-if="!faenaFija" class="field">
          <span>{{ t('login.faenaCode') }}</span>
          <input
            v-model="faenaCodigo"
            type="text"
            :placeholder="t('login.faenaPlaceholder')"
            autocomplete="off"
            spellcheck="false"
          />
        </label>
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
        <router-link :to="registroLink">{{ t('app.register') }}</router-link>
      </p>
      <p v-if="resendMsg" class="auth-ok" role="status">{{ resendMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { HardHat, LogIn } from 'lucide-vue-next'
import { useAuth } from '@/stores/auth'
import { wakeApi, fetchMisFaenas, fetchMe, reenviarVerificacion } from '@/services/authApi'
import { setLocale } from '@/i18n'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'

const site = inject('site')
const router = useRouter()
const route = useRoute()
const auth = useAuth()
const { t, locale } = useI18n()

const faenaFija = computed(() => {
  const p = route.params.faena
  return p ? String(p).toLowerCase() : ''
})
const faenaMeta = computed(() => (site.stations || []).find((s) => s.slug === faenaFija.value))
const registroLink = computed(() =>
  faenaFija.value ? `/f/${faenaFija.value}/registro` : '/registro',
)

const username = ref('')
const password = ref('')
const faenaCodigo = ref('')
const error = ref('')
const cargando = ref(false)
const registeredBanner = ref('')
const reenviando = ref(false)
const resendMsg = ref('')

onMounted(() => {
  wakeApi().catch(() => {})
  if (typeof route.query.faena === 'string') {
    faenaCodigo.value = route.query.faena
  }
  if (route.query.registered === '1' || route.query.registered === 'true') {
    registeredBanner.value = t('login.registeredOk')
    if (typeof route.query.email === 'string' && route.query.email) {
      username.value = route.query.email
    }
  }
  try {
    const msg = sessionStorage.getItem('metgo_session_msg')
    if (msg) {
      error.value = msg
      sessionStorage.removeItem('metgo_session_msg')
    }
  } catch {
    /* ignore */
  }
})

async function resolvePostLogin(preferredFaena) {
  let faenas = []
  let catalogo = false
  try {
    const hub = await fetchMisFaenas()
    faenas = hub.faenas || []
    catalogo = Boolean(hub.catalogo_completo)
  } catch {
    try {
      const me = await fetchMe()
      faenas = me.hub?.faenas || (me.faena ? [{ slug: me.faena }] : me.faenas || [])
      catalogo = Boolean(me.catalogo_completo || me.hub?.catalogo_completo)
    } catch {
      /* ignore */
    }
  }
  const slugs = faenas.map((f) => String(f.slug || f).toLowerCase()).filter(Boolean)
  if (preferredFaena && (catalogo || slugs.includes(preferredFaena) || !slugs.length)) {
    return `/f/${preferredFaena}/ahora`
  }
  if (!catalogo && slugs.length === 1) return `/f/${slugs[0]}/ahora`
  if (slugs.length > 1 || catalogo) return '/app'
  if (preferredFaena) return `/f/${preferredFaena}/ahora`
  return '/app'
}

async function onSubmit() {
  error.value = ''
  resendMsg.value = ''
  cargando.value = true
  try {
    await wakeApi()
    const faena =
      faenaFija.value ||
      String(faenaCodigo.value || '')
        .trim()
        .toLowerCase()
        .replace(/\s+/g, '_') ||
      undefined
    await auth.login(username.value.trim(), password.value, {
      faena,
      sitio: 'spati',
    })
    let redirect =
      typeof route.query.redirect === 'string' ? route.query.redirect : ''
    if (!redirect || redirect === '/' || redirect.startsWith('/?') || redirect === '/login') {
      redirect = await resolvePostLogin(faena)
    } else if (faena && (redirect === `/f/${faena}/` || redirect === `/f/${faena}`)) {
      redirect = `/f/${faena}/ahora`
    }
    await router.replace(redirect.startsWith('/') ? redirect : await resolvePostLogin(faena))
  } catch (e) {
    if (e.code === 'email_not_verified') {
      error.value = t('login.emailNotVerified')
    } else if (e.code === 'subscription_expired') {
      error.value = e.message || 'Piloto o suscripción vencida'
    } else {
      error.value = e.message || t('login.errorGeneric')
    }
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
    const faena =
      faenaFija.value ||
      String(faenaCodigo.value || '')
        .trim()
        .toLowerCase()
        .replace(/\s+/g, '_') ||
      undefined
    const res = await reenviarVerificacion({
      email: username.value.trim(),
      password: password.value,
      sitio: 'spati',
      faena,
    })
    if (res.already_verified) {
      resendMsg.value = 'Email ya verificado. Puede iniciar sesión.'
    } else {
      resendMsg.value = t('login.resendOk')
      if (res.email && res.email.sent === false) {
        error.value = res.email.error || t('registro.okMailFail')
      }
    }
  } catch (e) {
    error.value = e.message || t('login.errorGeneric')
  } finally {
    reenviando.value = false
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
  background-image:
    radial-gradient(ellipse 70% 50% at 15% 0%, rgba(16, 185, 129, 0.2), transparent 55%),
    radial-gradient(ellipse 50% 40% at 90% 20%, rgba(59, 130, 246, 0.12), transparent 50%);
}
.auth-panel {
  width: 100%;
  max-width: 420px;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(14px);
  border: 1px solid #1e293b;
  border-radius: 14px;
  padding: 2.25rem 1.75rem;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
}
.auth-lang {
  display: flex;
  justify-content: flex-end;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
}
.auth-lang button {
  border: 1px solid #334155;
  background: transparent;
  color: #94a3b8;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
}
.auth-lang button.active {
  color: #10b981;
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.12);
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
  background: #10b981;
  color: #0f172a;
  border-radius: 10px;
}
.auth-brand h1 {
  margin: 0;
  font-size: 1.35rem;
  color: #f8fafc;
}
.auth-tagline,
.auth-region,
.login-hint,
.auth-footer {
  margin: 0.35rem 0 0;
  color: #94a3b8;
  font-size: 0.85rem;
}
.login-hint {
  margin-top: 0.75rem;
  line-height: 1.45;
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
  padding: 0.65rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #0b1220;
  color: #e2e8f0;
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
  padding: 0.7rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  background: #10b981;
  color: #0f172a;
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
  color: #10b981;
  text-decoration: none;
  font-weight: 600;
}
.auth-footer .linkish {
  background: none;
  border: none;
  color: #10b981;
  font-weight: 600;
  font-size: inherit;
  font-family: inherit;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}
.auth-footer .linkish:disabled {
  opacity: 0.6;
  cursor: wait;
}
</style>
