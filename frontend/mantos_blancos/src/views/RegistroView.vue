<script setup>
import { computed, inject, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { HardHat } from 'lucide-vue-next'
import { fetchPlanes, registerV2, validateRegistro, wakeApi } from '@/services/authApi'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { setLocale } from '@/i18n'

const { t, locale } = useI18n()
const site = inject('site')
const router = useRouter()

const form = reactive({
  email: '',
  password: '',
  password_confirm: '',
  nombres: '',
  apellidos: '',
  telefono: '',
  razon_social: '',
  rut: '',
  almacenamiento_datos: false,
  tos: false,
  privacy: false,
  veracidad: false,
})

const errors = ref({})
const msg = ref('')
const cargando = ref(false)
const done = ref(false)
const registeredEmail = ref('')
const planes = ref([])
const brandName = computed(() => site.siteLabel || 'Mantos Blancos')

onMounted(async () => {
  wakeApi().catch(() => {})
  try {
    const data = await fetchPlanes(site.sitio)
    planes.value = (data.planes || []).filter((p) => p.plan_code !== 'preview')
  } catch {
    planes.value = []
  }
})

async function onSubmit() {
  msg.value = ''
  errors.value = {}
  cargando.value = true
  const body = {
    email: form.email.trim(),
    password: form.password,
    password_confirm: form.password_confirm,
    nombres: form.nombres.trim(),
    apellidos: form.apellidos.trim(),
    telefono: form.telefono.trim(),
    razon_social: form.razon_social.trim(),
    rut: form.rut.trim(),
    sitio: site.sitio,
    faena: site.faena?.id || undefined,
    consentimientos: {
      almacenamiento_datos: form.almacenamiento_datos,
      tos: form.tos,
      privacy: form.privacy,
      veracidad: form.veracidad,
    },
  }
  try {
    const v = await validateRegistro(body)
    if (!v.ok) {
      errors.value = v.errors || {}
      return
    }
    await registerV2(body)
    registeredEmail.value = body.email
    done.value = true
    msg.value = t('registro.ok')
  } catch (e) {
    if (e.data?.validation?.errors) errors.value = e.data.validation.errors
    else msg.value = e.message || t('registro.error')
  } finally {
    cargando.value = false
  }
}

function irLogin() {
  router.push({ path: '/login', query: { registered: '1', email: registeredEmail.value || undefined } })
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-panel wide">
      <div class="top">
        <ThemeToggle />
        <div class="lang-switch" role="group" :aria-label="t('lang.label')">
          <button type="button" :class="{ active: locale === 'es' }" @click="setLocale('es')">
            {{ t('lang.es') }}
          </button>
          <button type="button" :class="{ active: locale === 'en' }" @click="setLocale('en')">
            {{ t('lang.en') }}
          </button>
        </div>
        <router-link to="/">{{ t('app.home') }}</router-link>
      </div>

      <div v-if="done" class="success-panel" role="status">
        <h1>{{ t('registro.okTitle') }}</h1>
        <p class="ok">{{ msg || t('registro.ok') }}</p>
        <p v-if="registeredEmail" class="hint">Email: <strong>{{ registeredEmail }}</strong></p>
        <p class="hint">{{ t('registro.okHint') }}</p>
        <button type="button" class="btn-primary" @click="irLogin">{{ t('registro.goLogin') }}</button>
      </div>

      <template v-else>
      <div class="brand">
        <div class="logo"><HardHat aria-hidden="true" /></div>
        <h1>{{ t('registro.title', { name: brandName }) }}</h1>
        <p>{{ t('registro.sub') }}</p>
      </div>

      <form class="grid" @submit.prevent="onSubmit">
        <label><span>{{ t('registro.nombres') }}</span><input v-model="form.nombres" required autocomplete="given-name" /></label>
        <label><span>{{ t('registro.apellidos') }}</span><input v-model="form.apellidos" required autocomplete="family-name" /></label>
        <label><span>{{ t('registro.email') }}</span><input v-model="form.email" type="email" required autocomplete="email" /></label>
        <label><span>{{ t('registro.telefono') }}</span><input v-model="form.telefono" placeholder="+56912345678" autocomplete="tel" /></label>
        <label><span>{{ t('registro.razon') }}</span><input v-model="form.razon_social" required autocomplete="organization" /></label>
        <label><span>{{ t('registro.rut') }}</span><input v-model="form.rut" required placeholder="76.123.456-0" autocomplete="off" /></label>
        <label><span>{{ t('registro.password') }}</span><input v-model="form.password" type="password" required minlength="10" autocomplete="new-password" /></label>
        <label><span>{{ t('registro.confirm') }}</span><input v-model="form.password_confirm" type="password" required autocomplete="new-password" /></label>

        <fieldset class="consents">
          <legend>{{ t('registro.consentsLegend') }}</legend>
          <label class="check">
            <input v-model="form.almacenamiento_datos" type="checkbox" />
            {{ t('registro.consentStore') }}
          </label>
          <label class="check">
            <input v-model="form.tos" type="checkbox" />
            {{ t('registro.consentTos') }}
          </label>
          <label class="check">
            <input v-model="form.privacy" type="checkbox" />
            {{ t('registro.consentPrivacy') }}
          </label>
          <label class="check">
            <input v-model="form.veracidad" type="checkbox" />
            {{ t('registro.consentTruth') }}
          </label>
        </fieldset>

        <div v-if="Object.keys(errors).length" class="err" role="alert">
          <div v-for="(msgs, k) in errors" :key="k">
            <strong>{{ k }}:</strong> {{ msgs.join('; ') }}
          </div>
        </div>
        <p v-if="msg && !done" class="err">{{ msg }}</p>

        <button type="submit" class="btn-primary" :disabled="cargando">
          {{ cargando ? t('registro.loading') : t('registro.submit') }}
        </button>
      </form>

      <section v-if="planes.length" class="planes">
        <h2>{{ t('registro.plansTitle') }}</h2>
        <ul>
          <li v-for="p in planes" :key="p.plan_code">
            <strong>{{ p.nombre }}</strong>
            <span class="feats"> — {{ p.descripcion || (p.features || []).join(', ') }}</span>
          </li>
        </ul>
      </section>

      <p class="foot">
        {{ t('registro.haveAccount') }}
        <router-link to="/login">{{ t('registro.signIn') }}</router-link>
      </p>
      </template>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background: #0a0704;
  background-image: radial-gradient(ellipse 800px 400px at 10% 0%, rgba(249, 115, 22, 0.14), transparent 55%);
}
.auth-panel {
  width: min(640px, 100%);
  background: #181209;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 1.5rem;
  color: #f8f6f2;
}
.auth-panel.wide {
  width: min(720px, 100%);
}
.top {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 0.85rem;
}
.top a {
  color: #a89a86;
}
.lang-switch {
  display: inline-flex;
  gap: 0.25rem;
  margin-left: auto;
}
.lang-switch button {
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: transparent;
  color: #a89a86;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.45rem;
  border-radius: 6px;
  cursor: pointer;
}
.lang-switch button.active {
  color: #f97316;
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.12);
}
.brand {
  text-align: center;
  margin-bottom: 1.25rem;
}
.success-panel {
  text-align: center;
  padding: 1rem 0 0.5rem;
}
.success-panel h1 {
  margin: 0 0 0.75rem;
  font-size: 1.35rem;
}
.success-panel .hint {
  color: #94a3b8;
  font-size: 0.9rem;
  margin: 0.5rem 0;
}
.success-panel .btn-primary {
  margin-top: 1.25rem;
  width: 100%;
}
.logo {
  width: 3rem;
  height: 3rem;
  margin: 0 auto 0.75rem;
  display: grid;
  place-items: center;
  background: #f97316;
  color: #2a1502;
  border-radius: 10px;
}
.brand h1 {
  margin: 0;
  font-size: 1.25rem;
}
.brand p {
  margin: 0.4rem 0 0;
  color: #a89a86;
  font-size: 0.88rem;
}
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem 1rem;
}
.grid label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.78rem;
  color: #a89a86;
}
.grid input {
  padding: 0.55rem 0.65rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: #110c06;
  color: #f8f6f2;
}
.consents {
  grid-column: 1 / -1;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 0.75rem 1rem;
}
.consents legend {
  color: #e8d9c4;
  font-size: 0.85rem;
}
.check {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  margin: 0.45rem 0;
  color: #e8d9c4;
  font-size: 0.82rem;
}
.err {
  grid-column: 1 / -1;
  color: #f87171;
  font-size: 0.85rem;
}
.ok {
  grid-column: 1 / -1;
  color: #34d399;
}
.btn-primary {
  grid-column: 1 / -1;
  padding: 0.7rem 1rem;
  border: none;
  border-radius: 9px;
  background: #f97316;
  color: #2a1502;
  font-weight: 700;
  cursor: pointer;
}
.btn-primary:disabled {
  opacity: 0.6;
}
.planes {
  margin-top: 1.25rem;
}
.planes h2 {
  font-size: 0.95rem;
  margin: 0 0 0.5rem;
}
.feats {
  color: #a89a86;
  font-size: 0.82rem;
}
.foot {
  margin-top: 1rem;
  color: #a89a86;
  font-size: 0.88rem;
}
.foot a {
  color: #f97316;
}
@media (max-width: 560px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
