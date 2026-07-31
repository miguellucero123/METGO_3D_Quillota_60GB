<script setup>
import { computed, inject, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { HardHat } from 'lucide-vue-next'
import { fetchPlanes, registerV2, validateRegistro, wakeApi } from '@/services/authApi'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { setLocale } from '@/i18n'

const { t, locale } = useI18n()
const site = inject('site')
const route = useRoute()
const router = useRouter()

const faenaParam = computed(() => String(route.params.faena || '').toLowerCase())
const faenaCodigo = ref('')
const faena = computed(() => faenaParam.value || String(faenaCodigo.value || '').trim().toLowerCase().replace(/\s+/g, '_'))
const faenaMeta = computed(() => (site.stations || []).find((s) => s.slug === faena.value))
const brandName = computed(() => faenaMeta.value?.nombre || faena.value || site.brandName || 'VENTORA')

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
const warnings = ref([])
const msg = ref('')
const cargando = ref(false)
const planes = ref([])

onMounted(async () => {
  wakeApi().catch(() => {})
  try {
    const data = await fetchPlanes('spati', faena.value)
    planes.value = data.planes || []
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
    sitio: 'spati',
    faena: faena.value,
    consentimientos: {
      almacenamiento_datos: form.almacenamiento_datos,
      tos: form.tos,
      privacy: form.privacy,
      veracidad: form.veracidad,
    },
  }
  try {
    const v = await validateRegistro(body)
    warnings.value = v.warnings || []
    if (!v.ok) {
      errors.value = v.errors || {}
      return
    }
    await registerV2(body)
    msg.value = t('registro.ok')
    router.replace(faena.value ? `/f/${faena.value}/login` : '/login')
  } catch (e) {
    if (e.data?.validation?.errors) errors.value = e.data.validation.errors
    else msg.value = e.message || t('registro.error')
  } finally {
    cargando.value = false
  }
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
        <router-link :to="`/`">{{ t('app.home') }}</router-link>
      </div>
      <div class="brand">
        <div class="logo"><HardHat aria-hidden="true" /></div>
        <h1>{{ t('registro.title', { name: brandName }) }}</h1>
        <p>{{ t('registro.sub') }}</p>
      </div>

      <form class="grid" @submit.prevent="onSubmit">
        <label v-if="!faenaParam" class="full">
          {{ t('registro.faenaCode') }}
          <input v-model="faenaCodigo" required placeholder="quebrada_blanca" />
        </label>
        <label><span>{{ t('registro.nombres') }}</span><input v-model="form.nombres" required /></label>
        <label><span>{{ t('registro.apellidos') }}</span><input v-model="form.apellidos" required /></label>
        <label><span>{{ t('registro.email') }}</span><input v-model="form.email" type="email" required /></label>
        <label><span>{{ t('registro.telefono') }}</span><input v-model="form.telefono" placeholder="+56912345678" /></label>
        <label><span>{{ t('registro.razon') }}</span><input v-model="form.razon_social" required /></label>
        <label><span>{{ t('registro.rut') }}</span><input v-model="form.rut" required placeholder="76.123.456-0" /></label>
        <label><span>{{ t('registro.password') }}</span><input v-model="form.password" type="password" required minlength="10" /></label>
        <label><span>{{ t('registro.confirm') }}</span><input v-model="form.password_confirm" type="password" required /></label>

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
        <p v-if="msg" class="ok">{{ msg }}</p>

        <button type="submit" class="btn-primary" :disabled="cargando">
          {{ cargando ? t('registro.loading') : t('registro.submit') }}
        </button>
      </form>

      <section v-if="planes.length" class="planes">
        <h2>{{ t('registro.plansTitle', { faena }) }}</h2>
        <ul>
          <li v-for="p in planes" :key="p.plan_code">
            <strong>{{ p.nombre }}</strong>
            <span v-if="p.descripcion" class="feats"> — {{ p.descripcion }}</span>
            <span v-else class="feats"> — {{ (p.features || []).join(', ') }}</span>
          </li>
        </ul>
      </section>

      <p class="foot">
        {{ t('registro.haveAccount') }}
        <router-link :to="faena ? `/f/${faena}/login` : '/login'">{{ t('registro.signIn') }}</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background: #0f172a;
}
.auth-panel {
  width: min(640px, 100%);
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 14px;
  padding: 1.5rem;
  color: #e2e8f0;
}
.auth-panel.wide { width: min(720px, 100%); }
.top {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 0.85rem;
}
.top a { color: #94a3b8; }
.lang-switch { display: inline-flex; gap: 0.25rem; margin-left: auto; }
.lang-switch button {
  border: 1px solid #334155;
  background: transparent;
  color: #94a3b8;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.45rem;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
}
.lang-switch button.active {
  color: #10b981;
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.12);
}
.brand { text-align: center; margin-bottom: 1.25rem; }
.logo {
  width: 3rem; height: 3rem; margin: 0 auto 0.75rem;
  display: grid; place-items: center;
  background: #10b981; color: #0f172a; border-radius: 10px;
}
.brand h1 { margin: 0; font-size: 1.25rem; }
.brand p { margin: 0.4rem 0 0; color: #94a3b8; font-size: 0.88rem; }
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem 1rem;
}
.grid label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.78rem; color: #94a3b8; }
.grid label.full { grid-column: 1 / -1; }
.grid input {
  padding: 0.55rem 0.65rem; border-radius: 8px;
  border: 1px solid #334155; background: #0b1220; color: #e2e8f0;
}
.consents {
  grid-column: 1 / -1;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  margin: 0.25rem 0;
}
.consents legend { padding: 0 0.35rem; color: #cbd5e1; font-size: 0.85rem; }
.check { display: flex; gap: 0.5rem; align-items: flex-start; margin: 0.45rem 0; color: #cbd5e1; font-size: 0.82rem; }
.err { grid-column: 1 / -1; color: #f87171; font-size: 0.85rem; }
.ok { grid-column: 1 / -1; color: #34d399; }
.btn-primary {
  grid-column: 1 / -1;
  margin-top: 0.25rem;
  padding: 0.7rem 1rem;
  border: none; border-radius: 9px;
  background: #10b981; color: #0f172a; font-weight: 700; cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: wait; }
.planes { margin-top: 1.25rem; }
.planes h2 { font-size: 0.95rem; margin: 0 0 0.5rem; }
.feats { color: #94a3b8; font-size: 0.82rem; }
.foot { margin-top: 1rem; color: #94a3b8; font-size: 0.88rem; }
.foot a { color: #10b981; }
@media (max-width: 560px) {
  .grid { grid-template-columns: 1fr; }
}
</style>
