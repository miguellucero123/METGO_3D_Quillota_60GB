<script setup>
import { computed, inject, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HardHat } from 'lucide-vue-next'
import { fetchPlanes, registerV2, validateRegistro, wakeApi } from '@/services/authApi'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'

const site = inject('site')
const route = useRoute()
const router = useRouter()

const faenaParam = computed(() => String(route.params.faena || '').toLowerCase())
const faenaCodigo = ref('')
const faena = computed(() => faenaParam.value || String(faenaCodigo.value || '').trim().toLowerCase().replace(/\s+/g, '_'))
const faenaMeta = computed(() => (site.stations || []).find((s) => s.slug === faena.value))

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
    msg.value = 'Registro OK. Revise el email de verificación e inicie sesión.'
    router.replace(faena.value ? `/f/${faena.value}/login` : '/login')
  } catch (e) {
    if (e.data?.validation?.errors) errors.value = e.data.validation.errors
    else msg.value = e.message || 'Error de registro'
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
        <router-link :to="`/`">Inicio</router-link>
      </div>
      <div class="brand">
        <div class="logo"><HardHat aria-hidden="true" /></div>
        <h1>Registro · {{ faenaMeta?.nombre || faena || (site.brandName || 'VENTORA') }}</h1>
        <p>Cuenta por faena contratada. PII cifrada · consentimiento obligatorio.</p>
      </div>

      <form class="grid" @submit.prevent="onSubmit">
        <label v-if="!faenaParam" class="full">
          Código de faena *
          <input v-model="faenaCodigo" required placeholder="quebrada_blanca" />
        </label>
        <label><span>Nombres</span><input v-model="form.nombres" required /></label>
        <label><span>Apellidos</span><input v-model="form.apellidos" required /></label>
        <label><span>Email</span><input v-model="form.email" type="email" required /></label>
        <label><span>Teléfono (+56)</span><input v-model="form.telefono" placeholder="+56912345678" /></label>
        <label><span>Razón social</span><input v-model="form.razon_social" required /></label>
        <label><span>RUT empresa</span><input v-model="form.rut" required placeholder="76.123.456-0" /></label>
        <label><span>Contraseña</span><input v-model="form.password" type="password" required minlength="10" /></label>
        <label><span>Confirmar</span><input v-model="form.password_confirm" type="password" required /></label>

        <fieldset class="consents">
          <legend>Consentimientos (obligatorios)</legend>
          <label class="check">
            <input v-model="form.almacenamiento_datos" type="checkbox" />
            Autorizo guardar mi información personal y de la empresa de forma cifrada.
          </label>
          <label class="check">
            <input v-model="form.tos" type="checkbox" />
            Acepto los términos de uso.
          </label>
          <label class="check">
            <input v-model="form.privacy" type="checkbox" />
            Acepto la política de privacidad.
          </label>
          <label class="check">
            <input v-model="form.veracidad" type="checkbox" />
            Declaro que los datos entregados son verídicos y correctos.
          </label>
        </fieldset>

        <div v-if="Object.keys(errors).length" class="err" role="alert">
          <div v-for="(msgs, k) in errors" :key="k">
            <strong>{{ k }}:</strong> {{ msgs.join('; ') }}
          </div>
        </div>
        <p v-if="msg" class="ok">{{ msg }}</p>

        <button type="submit" class="btn-primary" :disabled="cargando">
          {{ cargando ? 'Validando…' : 'Crear cuenta' }}
        </button>
      </form>

      <section v-if="planes.length" class="planes">
        <h2>Planes escalonados ({{ faena }})</h2>
        <ul>
          <li v-for="p in planes" :key="p.plan_code">
            <strong>{{ p.nombre }}</strong>
            —
            {{
              p.precio_mensual_clp == null
                ? 'A convenir'
                : `${p.precio_etiqueta === 'desde' ? 'Desde ' : ''}$${p.precio_mensual_clp.toLocaleString('es-CL')} CLP/mes`
            }}
            <span v-if="p.descripcion" class="feats">{{ p.descripcion }}</span>
            <span v-else class="feats">{{ (p.features || []).join(', ') }}</span>
          </li>
        </ul>
      </section>

      <p class="foot">
        ¿Ya tiene cuenta?
        <router-link :to="faena ? `/f/${faena}/login` : '/login'">Ingresar</router-link>
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
  background-image:
    radial-gradient(ellipse 70% 50% at 15% 0%, rgba(16, 185, 129, 0.2), transparent 55%),
    radial-gradient(ellipse 50% 40% at 90% 20%, rgba(59, 130, 246, 0.12), transparent 50%);
}
.auth-panel {
  width: 100%;
  max-width: 720px;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(14px);
  border: 1px solid #1e293b;
  border-radius: 14px;
  padding: 1.5rem;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
}
.top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.top a {
  color: #10b981;
  text-decoration: none;
  font-size: 0.85rem;
}
.brand { text-align: center; margin-bottom: 1rem; }
.brand h1 { color: #e2e8f0; }
.brand p { color: #94a3b8; }
.logo {
  width: 3rem; height: 3rem; margin: 0 auto 0.75rem;
  display: grid; place-items: center;
  background: #10b981; color: #0f172a;
  border-radius: 12px;
}
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
label span {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  color: #94a3b8;
  margin-bottom: 0.2rem;
}
input {
  width: 100%;
  padding: 0.55rem 0.65rem;
  border-radius: 6px;
  border: 1px solid #1e293b;
  background: #0b1220;
  color: #e2e8f0;
}
.consents {
  grid-column: 1 / -1;
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 0.75rem;
  color: #cbd5e1;
}
.check {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  margin: 0.35rem 0;
  font-size: 0.85rem;
}
.check input { width: auto; }
.btn-primary {
  grid-column: 1 / -1;
  padding: 0.7rem;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  background: #10b981;
  color: #0f172a;
}
.btn-primary:hover { background: #059669; }
.err { grid-column: 1 / -1; color: #f87171; font-size: 0.85rem; }
.ok { grid-column: 1 / -1; color: #10b981; }
.planes { margin-top: 1.25rem; font-size: 0.85rem; color: #94a3b8; }
.feats { color: #64748b; margin-left: 0.35rem; }
.foot { text-align: center; margin-top: 1rem; font-size: 0.85rem; color: #94a3b8; }
.foot a { color: #10b981; }
@media (max-width: 640px) {
  .grid { grid-template-columns: 1fr; }
}
</style>
