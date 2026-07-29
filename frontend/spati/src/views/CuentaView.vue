<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { fetchCuenta, checkoutPlan, wakeApi } from '@/services/authApi'
import { useAuth } from '@/stores/auth'
import { useAccess } from '@/stores/access'

const site = inject('site')
const route = useRoute()
const auth = useAuth()
const accessStore = useAccess()
const faena = computed(() => String(route.params.faena || '').toLowerCase())
const blockedTab = computed(() => String(route.query.blocked || '').toLowerCase())
const blockedFaena = computed(() => String(route.query.blocked_faena || '').toLowerCase())

const loading = ref(true)
const error = ref('')
const msg = ref('')
const data = ref(null)
const applying = ref('')

const TAB_LABEL = {
  panel: 'Pronóstico 72 h',
  ambiente: 'Ambiente faena',
  dron: 'Calibración dron',
  umbrales: 'Umbrales',
}

onMounted(async () => {
  wakeApi().catch(() => {})
  await reload()
})

async function reload() {
  loading.value = true
  error.value = ''
  try {
    data.value = await fetchCuenta(faena.value)
    accessStore.invalidate(faena.value)
    await accessStore.refresh(faena.value, { force: true })
  } catch (e) {
    error.value = e.message || 'No se pudo cargar la cuenta'
  } finally {
    loading.value = false
  }
}

async function elegirPlan(planCode) {
  msg.value = ''
  applying.value = planCode
  try {
    const res = await checkoutPlan({
      plan_code: planCode,
      sitio: 'spati',
      faena: faena.value,
      org_id: auth.state.user?.org_id || data.value?.usuario?.org_id,
    })
    msg.value = res.message || (res.applied ? 'Plan aplicado' : 'OK')
    await reload()
  } catch (e) {
    error.value = e.message || 'Error al cambiar plan'
  } finally {
    applying.value = ''
  }
}

const planes = computed(() => data.value?.planes?.planes || [])
const sub = computed(() => data.value?.suscripcion)
const tabs = computed(() => data.value?.access?.tabs || {})
</script>

<template>
  <div class="cuenta">
    <header>
      <h1>Cuenta · {{ faena }}</h1>
      <p>Suscripción y acceso por pestaña para esta faena.</p>
    </header>

    <p v-if="blockedTab" class="warn" role="status">
      La pestaña <strong>{{ TAB_LABEL[blockedTab] || blockedTab }}</strong> no está
      incluida en tu plan actual. Elige un plan superior para habilitarla.
    </p>
    <p v-if="blockedFaena" class="warn" role="status">
      No tiene membresía en la faena <strong>{{ blockedFaena }}</strong>.
      Solo puede operar en las mineras de su contrato (plan Enterprise multi-faena o admin ven el catálogo completo).
    </p>

    <p v-if="loading">Cargando…</p>
    <p v-else-if="error" class="err" role="alert">{{ error }}</p>
    <p v-if="msg" class="ok">{{ msg }}</p>

    <section v-if="data" class="card">
      <h2>Usuario</h2>
      <dl>
        <div><dt>Email</dt><dd>{{ data.usuario?.email }}</dd></div>
        <div><dt>Estado</dt><dd>{{ data.usuario?.status }} · verificado: {{ data.usuario?.email_verified ? 'sí' : 'no' }}</dd></div>
        <div><dt>Sitio / faena</dt><dd>{{ data.usuario?.sitio }} / {{ data.usuario?.faena }}</dd></div>
      </dl>
    </section>

    <section v-if="sub" class="card">
      <h2>Suscripción actual</h2>
      <p>
        Plan <strong>{{ sub.plan_code }}</strong> ·
        estado <strong>{{ sub.status }}</strong>
        <template v-if="sub.current_period_end"> · hasta {{ String(sub.current_period_end).slice(0, 10) }}</template>
      </p>
      <ul class="tabs">
        <li v-for="(ok, tab) in tabs" :key="tab" :class="{ on: ok }">
          {{ tab }}: {{ ok ? 'habilitado' : 'bloqueado' }}
        </li>
      </ul>
    </section>

    <section class="card">
      <h2>Planes escalonados</h2>
      <p class="hint">Sin Stripe: el checkout mock aplica el plan de inmediato (S2).</p>
      <ul class="planes">
        <li v-for="p in planes" :key="p.plan_code">
          <div>
            <strong>{{ p.nombre }}</strong>
            <span v-if="p.precio_mensual_clp != null">
              ${{ p.precio_mensual_clp.toLocaleString('es-CL') }} CLP/mes
            </span>
            <span v-else>A convenir</span>
            <em>{{ (p.features || []).join(', ') }}</em>
          </div>
          <button
            type="button"
            class="btn"
            :disabled="!!applying || p.contacto || sub?.plan_code === p.plan_code"
            @click="elegirPlan(p.plan_code)"
          >
            {{ applying === p.plan_code ? '…' : sub?.plan_code === p.plan_code ? 'Actual' : 'Elegir' }}
          </button>
        </li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.cuenta { padding: 1.25rem; max-width: 820px; color: var(--color-text); }
header h1 { margin: 0 0 0.25rem; font-size: 1.35rem; }
header p, .hint { color: var(--color-muted); font-size: 0.9rem; }
.card {
  margin-top: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 1rem;
  background: rgba(17, 24, 39, 0.55);
}
dl { display: grid; gap: 0.5rem; margin: 0; }
dt { font-size: 0.7rem; text-transform: uppercase; color: var(--color-muted); }
dd { margin: 0; }
.tabs, .planes { list-style: none; padding: 0; margin: 0.75rem 0 0; }
.tabs li { font-size: 0.85rem; color: var(--color-muted); }
.tabs li.on { color: var(--color-primary); font-weight: 600; }
.planes li {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 0.65rem 0;
  border-top: 1px solid var(--color-border);
}
.planes em { display: block; font-style: normal; font-size: 0.8rem; color: var(--color-muted); }
.btn {
  border: none;
  border-radius: 8px;
  padding: 0.45rem 0.85rem;
  font-weight: 600;
  cursor: pointer;
  background: var(--color-primary);
  color: #0b1120;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.err { color: var(--color-danger); }
.ok { color: var(--color-primary); }
.warn {
  margin: 0.75rem 0;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border: 1px solid color-mix(in srgb, var(--color-primary) 45%, transparent);
  background: color-mix(in srgb, var(--color-primary) 12%, transparent);
  color: var(--color-text);
  font-size: 0.9rem;
}
</style>
