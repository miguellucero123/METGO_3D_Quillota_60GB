<script setup>
import { computed, onMounted, ref } from 'vue'
import { fetchCuenta, checkoutPlan, wakeApi } from '@/api/metgoApi'
import { useAuthStore } from '@/stores/auth'

const SITIO = 'quillota'
const auth = useAuthStore()

const loading = ref(true)
const error = ref('')
const msg = ref('')
const data = ref(null)
const applying = ref('')

onMounted(async () => {
  wakeApi().catch(() => {})
  await reload()
})

async function reload() {
  loading.value = true
  error.value = ''
  try {
    data.value = await fetchCuenta()
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
      sitio: SITIO,
      org_id: auth.user?.org_id || data.value?.usuario?.org_id,
      success_url: `${window.location.origin}/cuenta?checkout=success`,
      cancel_url: `${window.location.origin}/cuenta?checkout=cancel`,
    })
    if (res.checkout_url) {
      window.location.href = res.checkout_url
      return
    }
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
      <h1>Cuenta · Quillota</h1>
      <p>Suscripción, piloto y planes del producto.</p>
    </header>

    <p v-if="loading">Cargando…</p>
    <p v-else-if="error" class="err" role="alert">{{ error }}</p>
    <p v-if="msg" class="ok">{{ msg }}</p>

    <section v-if="data" class="card">
      <h2>Usuario</h2>
      <dl>
        <div><dt>Email</dt><dd>{{ data.usuario?.email }}</dd></div>
        <div>
          <dt>Estado</dt>
          <dd>{{ data.usuario?.status }} · verificado: {{ data.usuario?.email_verified ? 'sí' : 'no' }}</dd>
        </div>
        <div><dt>Sitio</dt><dd>{{ data.usuario?.sitio }}</dd></div>
      </dl>
    </section>

    <section v-if="sub" class="card">
      <h2>Suscripción actual</h2>
      <p>
        Plan <strong>{{ sub.plan_code }}</strong> ·
        estado <strong>{{ sub.status }}</strong>
        <template v-if="sub.current_period_end"> · hasta {{ String(sub.current_period_end).slice(0, 10) }}</template>
      </p>
      <ul v-if="Object.keys(tabs).length" class="tabs">
        <li v-for="(ok, tab) in tabs" :key="tab" :class="{ on: ok }">
          {{ tab }}: {{ ok ? 'habilitado' : 'bloqueado' }}
        </li>
      </ul>
    </section>

    <section class="card">
      <h2>Planes</h2>
      <p class="hint">Sin Stripe: el checkout mock aplica el plan de inmediato.</p>
      <ul class="planes">
        <li v-for="p in planes" :key="p.plan_code">
          <div>
            <strong>{{ p.nombre }}</strong>
            <em>{{ p.descripcion || (p.features || []).join(', ') }}</em>
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
header p, .hint { color: var(--color-muted, var(--color-text-secondary)); font-size: 0.9rem; }
.card {
  margin-top: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 1rem;
  background: var(--color-surface, rgba(17, 24, 39, 0.55));
}
dl { display: grid; gap: 0.5rem; margin: 0; }
dt { font-size: 0.7rem; text-transform: uppercase; color: var(--color-muted, var(--color-text-secondary)); }
dd { margin: 0; }
.tabs, .planes { list-style: none; padding: 0; margin: 0.75rem 0 0; }
.tabs li { font-size: 0.85rem; color: var(--color-muted, var(--color-text-secondary)); }
.tabs li.on { color: var(--color-primary); font-weight: 600; }
.planes li {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 0.65rem 0;
  border-top: 1px solid var(--color-border);
}
.planes em { display: block; font-style: normal; font-size: 0.8rem; color: var(--color-muted, var(--color-text-secondary)); }
.btn {
  border: none;
  border-radius: 8px;
  padding: 0.45rem 0.85rem;
  font-weight: 600;
  cursor: pointer;
  background: var(--color-primary);
  color: #0f172a;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.err { color: var(--color-danger, #f87171); }
.ok { color: var(--color-primary); }
</style>
