<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Sprout, Droplets, ThermometerSnowflake, Tractor } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import MetricCard from '@/components/ui/MetricCard.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import HorizontalBarChart from '@/components/charts/HorizontalBarChart.vue'
import {
  fetchRecomendacionesAgricolas,
  fetchAgricolaRiego,
  fetchAgricolaCultivos,
  fetchAgricolaEconomico,
  fetchCronogramaRiego,
} from '@/api/metgoApi'
import {
  CULTIVOS_QUILLOTA,
  riesgoHeladaPorCultivo,
  necesidadRiego,
  condicionViento,
  cultivoHeladaSlug,
  cultivoApiSlug,
} from '@/utils/agroInsights'
import { hoyChile } from '@/utils/meteoDates'

const store = useMetgoStore()
const recomendaciones = ref([])
const cultivosApi = ref([])
const riegoApi = ref(null)
const riegoPorCultivo = ref([])
const economico = ref(null)
const cronograma = ref(null)
const cultivoSel = ref('palto')
const cargando = ref(false)

const d = computed(() => store.datosMeteo)
const helada = computed(() =>
  riesgoHeladaPorCultivo(d.value?.temperatura_min, cultivoHeladaSlug(cultivoSel.value))
)
const riego = computed(() => necesidadRiego(d.value?.humedad, d.value?.precipitacion))
const viento = computed(() => condicionViento(d.value?.viento))

const opcionesCultivo = computed(() => {
  if (cultivosApi.value?.length) {
    return cultivosApi.value.map((c) => ({
      id: c.id || c.nombre?.toLowerCase(),
      nombre: c.nombre || c.id,
    }))
  }
  return [
    { id: 'palto', nombre: 'Palto' },
    { id: 'uva', nombre: 'Uva de mesa' },
    { id: 'citricos', nombre: 'Cítricos' },
    { id: 'hortalizas', nombre: 'Hortalizas' },
  ]
})

const labelsRiego = computed(() => riegoPorCultivo.value.map((r) => r.nombre))
const valuesRiego = computed(() => riegoPorCultivo.value.map((r) => r.mm))

async function cargarRiegoTodos() {
  const filas = []
  for (const c of opcionesCultivo.value) {
    try {
      const r = await fetchAgricolaRiego(store.estacionActiva, cultivoApiSlug(c.id))
      filas.push({
        id: c.id,
        nombre: c.nombre,
        mm: Number(r.mm_sugeridos_hoy) || 0,
        accion: r.accion,
      })
    } catch {
      filas.push({ id: c.id, nombre: c.nombre, mm: 0, accion: '—' })
    }
  }
  riegoPorCultivo.value = filas
}

async function cargar() {
  cargando.value = true
  try {
    recomendaciones.value = await fetchRecomendacionesAgricolas(store.estacionActiva)
    cultivosApi.value = await fetchAgricolaCultivos()
    riegoApi.value = await fetchAgricolaRiego(
      store.estacionActiva,
      cultivoApiSlug(cultivoSel.value)
    )
    economico.value = await fetchAgricolaEconomico(store.estacionActiva)
    try {
      cronograma.value = await fetchCronogramaRiego(
        store.estacionActiva,
        cultivoApiSlug(cultivoSel.value)
      )
    } catch {
      cronograma.value = null
    }
    await cargarRiegoTodos()
  } catch {
    recomendaciones.value = []
    cultivosApi.value = []
    riegoApi.value = null
    economico.value = null
    riegoPorCultivo.value = []
  } finally {
    cargando.value = false
  }
}

async function onCultivoChange() {
  try {
    riegoApi.value = await fetchAgricolaRiego(
      store.estacionActiva,
      cultivoApiSlug(cultivoSel.value)
    )
    try {
      cronograma.value = await fetchCronogramaRiego(
        store.estacionActiva,
        cultivoApiSlug(cultivoSel.value)
      )
    } catch {
      cronograma.value = null
    }
  } catch {
    riegoApi.value = null
  }
}

onMounted(cargar)
watch(() => store.estacionActiva, cargar)
watch(cultivoSel, onCultivoChange)
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Gestión agrícola</h2>
      <p class="page-subtitle">
        Recomendaciones operativas · {{ store.estacionNombre }} · {{ hoyChile() }} (Chile)
      </p>
      <div class="page-meta">
        <label class="inline-select">
          Cultivo foco:
          <select v-model="cultivoSel">
            <option v-for="c in opcionesCultivo" :key="c.id" :value="c.id">
              {{ c.nombre }}
            </option>
          </select>
        </label>
      </div>
    </header>

    <div v-if="d" class="card-grid card-grid--wide">
      <MetricCard
        label="Riesgo heladas"
        :value="helada.label"
        :variant="helada.nivel === 'high' ? 'alert' : helada.nivel === 'medium' ? 'warning' : 'default'"
      >
        <template #icon><ThermometerSnowflake /></template>
      </MetricCard>
      <MetricCard
        label="Manejo de riego"
        :value="riego.label"
        :variant="riego.nivel === 'high' ? 'warning' : 'default'"
      >
        <template #icon><Droplets /></template>
      </MetricCard>
      <MetricCard label="Aplicaciones / viento" :value="viento.label">
        <template #icon><Tractor /></template>
      </MetricCard>
      <MetricCard
        v-if="riegoApi"
        :label="`Riego hoy · ${cultivoSel}`"
        :value="riegoApi.mm_sugeridos_hoy"
        unit="mm"
        :hint="`${riegoApi.accion} — ${riegoApi.motivo}`"
      >
        <template #icon><Droplets /></template>
      </MetricCard>
    </div>

    <SectionCard
      v-if="labelsRiego.length"
      title="Riego sugerido por cultivo"
      :subtitle="`Comparación en ${store.estacionNombre} (mm hoy)`"
    >
      <HorizontalBarChart
        :labels="labelsRiego"
        :values="valuesRiego"
        unit=" mm"
        kind="precip"
      />
    </SectionCard>

    <div class="layout-split">
      <SectionCard
        title="Recomendaciones por cultivo"
        subtitle="Motor avanzado módulo 02 (heladas, plagas, cosecha)"
      >
        <template #icon><Sprout /></template>
        <p v-if="cargando" class="skeleton">Analizando condiciones…</p>
        <div v-else-if="recomendaciones.length" class="reco-cards">
          <article v-for="(r, i) in recomendaciones" :key="i" class="reco-card">
            <h4>{{ r.cultivo }}</h4>
            <p class="reco-card__accion">{{ r.accion }}</p>
            <p class="reco-card__motivo">{{ r.motivo }}</p>
          </article>
        </div>
        <p v-else class="muted">Sin recomendaciones (verifique la API en :8080).</p>
      </SectionCard>

      <SectionCard title="Cultivos principales — Quillota" subtitle="Catálogo módulo 02">
        <template #icon><Sprout /></template>
        <table class="data-table">
          <thead>
            <tr>
              <th>Cultivo</th>
              <th>ID</th>
              <th>Riego ref. (mm/d)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in opcionesCultivo" :key="c.id">
              <td><strong>{{ c.nombre }}</strong></td>
              <td>{{ c.id }}</td>
              <td>
                {{
                  riegoPorCultivo.find((r) => r.id === c.id)?.mm ??
                  cultivosApi.find((x) => x.id === c.id)?.riego_mm_dia_base ??
                  '—'
                }}
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="d" class="muted footnote">
          Condiciones actuales: {{ d.temperatura }}°C media · {{ d.humedad }}% HR ·
          {{ d.precipitacion }} mm precip. · T° mín {{ d.temperatura_min }}°C
        </p>
      </SectionCard>
    </div>

    <SectionCard
      v-if="cronograma"
      title="Cronograma de riego inteligente"
      subtitle="Ajustado por lluvia y helada (próximas 72 h)"
    >
      <template #icon><Droplets /></template>
      <p class="cron-accion"><strong>{{ cronograma.accion || cronograma.recomendacion }}</strong></p>
      <p v-if="cronograma.motivo" class="muted">{{ cronograma.motivo }}</p>
      <ul v-if="cronograma.dias?.length" class="cron-list">
        <li v-for="(dia, i) in cronograma.dias" :key="i">
          <strong>{{ dia.fecha || dia.dia }}</strong> — {{ dia.accion || dia.riego_mm }} mm
          <span v-if="dia.nota" class="muted"> ({{ dia.nota }})</span>
        </li>
      </ul>
      <p v-else-if="cronograma.resumen" class="muted">{{ cronograma.resumen }}</p>
      <router-link to="/meteo/precipitacion" class="link-meteo">Ver precipitación y heladas →</router-link>
    </SectionCard>

    <SectionCard
      v-if="economico"
      title="Proyección económica"
      subtitle="Módulo 02 · referencia regional"
    >
      <p class="eco-line">
        <span v-if="economico.ahorro_estimado_clp_mes">
          Ahorro estimado: ${{ economico.ahorro_estimado_clp_mes?.toLocaleString('es-CL') }} CLP/mes
        </span>
        <span v-else>{{ economico.nota || economico.resumen || 'Sin detalle' }}</span>
      </p>
      <p v-if="economico.fuente" class="muted small">Fuente: {{ economico.fuente }}</p>
    </SectionCard>
  </div>
</template>

<style scoped>
.page {
  max-width: 1280px;
}

.page-meta {
  margin-top: 0.5rem;
}

.inline-select {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--color-muted);
}

.inline-select select {
  padding: 0.3rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: inherit;
}

.metric-foot {
  font-size: 0.7rem;
  color: var(--color-muted);
  display: block;
  margin-top: 0.25rem;
}

.reco-cards {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.reco-card {
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-primary-subtle);
  border-left: 3px solid var(--color-primary);
}

.reco-card h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-primary);
}

.reco-card__accion {
  font-size: 0.875rem;
  margin-top: 0.35rem;
  color: var(--color-text);
}

.reco-card__motivo {
  font-size: 0.78rem;
  color: var(--color-muted);
  margin-top: 0.25rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.data-table th,
.data-table td {
  padding: 0.5rem 0.65rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.footnote {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.eco-line {
  font-size: 0.95rem;
  margin: 0;
}

.small {
  font-size: 0.75rem;
  margin-top: 0.35rem;
}

.cron-accion {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
}

.cron-list {
  margin: 0.5rem 0 0;
  padding-left: 1.25rem;
  font-size: 0.85rem;
}

.link-meteo {
  display: inline-block;
  margin-top: 0.75rem;
  font-size: 0.8rem;
  color: var(--color-primary);
}
</style>
