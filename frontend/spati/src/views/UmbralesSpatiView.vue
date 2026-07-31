<template>
  <div class="page">
    <header class="page-head">
      <h1>Umbrales {{ site.brandName || 'VENTORA' }}</h1>
      <p>
        Escalafón operacional de izaje · {{ faenaMeta?.nombre || sitioId }}
        <span v-if="fuente" class="muted"> ({{ fuente }})</span>
      </p>
    </header>

    <p v-if="error" class="err">{{ error }}</p>
    <p v-else-if="loading" class="muted">Cargando umbrales…</p>

    <template v-else>
      <table class="tbl">
        <thead>
          <tr>
            <th>Nivel</th>
            <th>Ráfaga</th>
            <th>F / F_límite</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          <tr class="n0">
            <td>0 VERDE</td>
            <td>&lt; {{ umb.verde_max_kmh ?? 26 }} km/h</td>
            <td>&lt; 40%</td>
            <td>Operación permitida</td>
          </tr>
          <tr class="n1">
            <td>1 AMARILLO</td>
            <td>{{ rango(umb.amarillo) }} km/h</td>
            <td>40 – {{ umb.fuerza_naranja_pct ?? 55 }}%</td>
            <td>Pre-alerta · verificar anemómetro</td>
          </tr>
          <tr class="n2">
            <td>2 NARANJA</td>
            <td>{{ rango(umb.naranja) }} km/h</td>
            <td>{{ umb.fuerza_naranja_pct ?? 55 }} – {{ umb.fuerza_rojo_pct ?? 80 }}%</td>
            <td>Restricción de cargas A·Cd elevado</td>
          </tr>
          <tr class="n3">
            <td>3 ROJO</td>
            <td>≥ {{ umb.rojo_min_kmh ?? 35 }} km/h</td>
            <td>&gt; {{ umb.fuerza_rojo_pct ?? 80 }}%</td>
            <td>Parada obligatoria · asegurar pluma</td>
          </tr>
        </tbody>
      </table>
      <p class="nota">
        {{
          umb.nota ||
          'Flag secundario: rayos / precipitación elevan al menos a Naranja. Física: F = ½ ρ v² A Cd.'
        }}
      </p>

      <section class="alertas-card">
        <h2>Destinos de alerta (M9)</h2>
        <p class="muted small">
          Por faena. El cron notifica solo si el nivel sube y es ≥ nivel mínimo.
          Requiere sesión (Bearer) para guardar en producción.
        </p>
        <form class="form" @submit.prevent="guardarAlertas">
          <label>
            Emails (separados por coma)
            <input v-model="form.emails" type="text" placeholder="ops@faena.cl, hse@faena.cl" />
          </label>
          <label>
            Webhook URL
            <input v-model="form.webhook" type="url" placeholder="https://hooks.ejemplo.com/…" />
          </label>
          <label>
            Nivel mínimo
            <select v-model.number="form.nivel">
              <option :value="1">1 Amarillo</option>
              <option :value="2">2 Naranja</option>
              <option :value="3">3 Rojo</option>
            </select>
          </label>
          <div class="form-actions">
            <button type="submit" class="btn" :disabled="saving">
              {{ saving ? 'Guardando…' : 'Guardar destinos' }}
            </button>
            <span v-if="saveMsg" class="ok">{{ saveMsg }}</span>
            <span v-if="saveErr" class="err">{{ saveErr }}</span>
          </div>
        </form>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { fetchSpatiUmbrales, putSpatiUmbrales } from '@/services/spatiApi'

const site = inject('site')
const route = useRoute()
const injectedFaena = inject('faena', null)
const injectedMeta = inject('faenaMeta', null)

const sitioId = computed(
  () =>
    (injectedFaena && injectedFaena.value) ||
    String(route.params.faena || site.spatiDefaultSitio || 'escondida').toLowerCase(),
)
const faenaMeta = computed(
  () =>
    (injectedMeta && injectedMeta.value) ||
    (site.stations || []).find((s) => s.slug === sitioId.value) || {
      slug: sitioId.value,
      nombre: sitioId.value,
    },
)

const umb = ref({})
const fuente = ref('')
const loading = ref(false)
const error = ref('')
const saving = ref(false)
const saveMsg = ref('')
const saveErr = ref('')
const form = reactive({
  emails: '',
  webhook: '',
  nivel: 2,
})

function rango(arr) {
  if (!Array.isArray(arr) || arr.length < 2) return '—'
  return `${arr[0]} – ${arr[1]}`
}

function aplicarAlertas(a) {
  form.emails = Array.isArray(a?.emails) ? a.emails.join(', ') : ''
  form.webhook = a?.webhook_url || ''
  form.nivel = a?.nivel_minimo ?? 2
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchSpatiUmbrales(sitioId.value)
    umb.value = data.umbrales || {}
    fuente.value = umb.value.fuente || ''
    aplicarAlertas(data.alertas || {})
  } catch (e) {
    error.value = e?.message || 'No se pudieron cargar umbrales'
    umb.value = {}
  } finally {
    loading.value = false
  }
}

async function guardarAlertas() {
  saving.value = true
  saveMsg.value = ''
  saveErr.value = ''
  try {
    const data = await putSpatiUmbrales(sitioId.value, {
      alertas: {
        emails: form.emails,
        webhook_url: form.webhook || null,
        nivel_minimo: form.nivel,
      },
    })
    aplicarAlertas(data.alertas || {})
    saveMsg.value = 'Destinos guardados'
  } catch (e) {
    saveErr.value = e?.message || 'No se pudo guardar'
  } finally {
    saving.value = false
  }
}

watch(sitioId, cargar)
onMounted(() => cargar())
</script>

<style scoped>
.page {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.25rem;
}
.page-head h1 {
  margin: 0 0 0.35rem;
}
.page-head p {
  margin: 0 0 1rem;
  color: var(--color-muted);
}
.tbl {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}
.tbl th,
.tbl td {
  padding: 0.65rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.9rem;
}
.tbl th {
  background: var(--color-surface);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-muted);
}
.n0 td:first-child {
  color: #86efac;
  font-weight: 600;
}
.n1 td:first-child {
  color: #fde68a;
  font-weight: 600;
}
.n2 td:first-child {
  color: #fdba74;
  font-weight: 600;
}
.n3 td:first-child {
  color: #fca5a5;
  font-weight: 600;
}
.nota {
  margin-top: 1rem;
  color: var(--color-muted);
  font-size: 0.9rem;
  line-height: 1.5;
}
.muted {
  color: var(--color-muted);
}
.small {
  font-size: 0.85rem;
}
.err {
  color: var(--color-danger, #f87171);
}
.ok {
  color: #4ade80;
  font-size: 0.85rem;
}
.alertas-card {
  margin-top: 1.5rem;
  padding: 1rem 1.1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}
.alertas-card h2 {
  margin: 0 0 0.35rem;
  font-size: 1.05rem;
}
.form {
  display: grid;
  gap: 0.75rem;
  margin-top: 0.75rem;
}
.form label {
  display: grid;
  gap: 0.3rem;
  font-size: 0.82rem;
  color: var(--color-text-secondary);
}
.form input,
.form select {
  padding: 0.5rem 0.65rem;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text);
  font-size: 0.92rem;
}
.form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  align-items: center;
}
.btn {
  padding: 0.5rem 0.9rem;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: #0f172a;
  font-weight: 600;
  cursor: pointer;
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
