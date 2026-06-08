<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { MapPin, BarChart3, AlertTriangle, ChevronDown } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import AgricolaAlertStrip from '@/components/agricola/AgricolaAlertStrip.vue'
import AgricolaKpiGrid from '@/components/agricola/AgricolaKpiGrid.vue'
import AgricolaStatusCards from '@/components/agricola/AgricolaStatusCards.vue'
import RiegoBarChart from '@/components/agricola/RiegoBarChart.vue'
import RiegoTimeline from '@/components/agricola/RiegoTimeline.vue'
import ValleMapMini from '@/components/agricola/ValleMapMini.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import { CULTIVOS_CATALOG } from '@/utils/agroColors'

const store = useMetgoStore()
const router = useRouter()

const cultivoActivo = ref('palto')
const cargandoVista = ref(false)

const resumenMeteo = computed(() => store.resumenMeteo)
const comparativoEstaciones = computed(() => store.comparativoEstaciones ?? {})
const recomendaciones = computed(() => store.recomendacionesAgricolas ?? [])
const estacionNombre = computed(() => store.estacionNombre)
const estacionActiva = computed(() => store.estacionActiva)

const cultivoLabel = computed(
  () => CULTIVOS_CATALOG.find((c) => c.slug === cultivoActivo.value)?.label ?? cultivoActivo.value
)

const fechaHoy = computed(() =>
  new Date().toLocaleDateString('es-CL', { year: 'numeric', month: '2-digit', day: '2-digit' })
)

const riegoHoyMm = computed(() => store.riegoPorCultivo?.[cultivoActivo.value] ?? 0)

const riegoPorCultivo = computed(() =>
  CULTIVOS_CATALOG.map((c) => ({
    slug: c.slug,
    label: c.label,
    mm: store.riegoPorCultivo?.[c.slug] ?? 0,
  }))
)

const cronograma = computed(() => store.cronogramaRiego?.cronograma ?? [])

async function cambiarCultivo(slug) {
  cultivoActivo.value = slug
  await store.fetchCronograma(estacionActiva.value, slug)
}

async function cargarTodo() {
  cargandoVista.value = true
  try {
    await Promise.all([
      store.cargarDatosMeteo(),
      store.fetchComparativoEstaciones(),
      store.fetchRiegoPorCultivo(estacionActiva.value),
      store.fetchRecomendaciones(estacionActiva.value),
      store.fetchCronograma(estacionActiva.value, cultivoActivo.value),
    ])
  } finally {
    cargandoVista.value = false
  }
}

function irAEstacion(id) {
  store.setEstacion(id)
  router.push('/meteo')
}

watch(estacionActiva, cargarTodo)
onMounted(cargarTodo)
</script>

<template>
  <div class="agricola-view page">
    <header class="view-header page-header">
      <div class="header-left">
        <div class="breadcrumb">
          <MapPin :size="14" aria-hidden="true" />
          {{ estacionNombre }} · Valle de Aconcagua · {{ fechaHoy }}
        </div>
        <h1 class="page-title">Gestión agrícola</h1>
        <p class="view-subtitle page-subtitle">Recomendaciones operativas · Motor módulo 02</p>
      </div>
      <div class="cultivo-tabs">
        <button
          v-for="c in CULTIVOS_CATALOG"
          :key="c.slug"
          type="button"
          class="cultivo-tab"
          :class="{ active: cultivoActivo === c.slug }"
          @click="cambiarCultivo(c.slug)"
        >
          {{ c.label }}
        </button>
      </div>
    </header>

    <AgricolaAlertStrip
      v-if="resumenMeteo && resumenMeteo.temperatura_min != null && resumenMeteo.temperatura_min <= 7"
      :t-min="resumenMeteo.temperatura_min"
      :cultivo="cultivoActivo"
    />

    <section aria-label="Indicadores meteorológicos del día">
      <p class="section-label">
        <BarChart3 :size="14" aria-hidden="true" />
        Indicadores del día
      </p>
      <AgricolaKpiGrid
        v-if="resumenMeteo"
        :resumen="resumenMeteo"
        :riego-mm="riegoHoyMm"
        :cultivo="cultivoActivo"
      />
      <SkeletonLoader v-else :lines="4" :height="90" />
    </section>

    <section aria-label="Estado de condiciones agrícolas">
      <p class="section-label">
        <AlertTriangle :size="14" aria-hidden="true" />
        Estado de condiciones
      </p>
      <AgricolaStatusCards
        v-if="resumenMeteo"
        :resumen="resumenMeteo"
        :recomendaciones="recomendaciones"
        :cultivo="cultivoActivo"
      />
      <SkeletonLoader v-else :lines="4" :height="80" />
    </section>

    <div class="two-col">
      <div class="card">
        <div class="card-header">
          <h3>Riego por cultivo hoy</h3>
          <span class="card-meta">mm · {{ estacionNombre }}</span>
        </div>
        <RiegoBarChart :datos="riegoPorCultivo" />
      </div>

      <div class="card">
        <div class="card-header">
          <h3>Mapa del Valle</h3>
          <span class="card-meta">T° máx hoy</span>
        </div>
        <ValleMapMini :comparativo="comparativoEstaciones" @estacion-click="irAEstacion" />
      </div>
    </div>

    <div class="card">
      <RiegoTimeline
        :cronograma="cronograma"
        :cultivo-label="cultivoLabel"
        :loading="store.loadingCronograma || cargandoVista"
      />
    </div>

    <div class="card">
      <details class="recs-details">
        <summary class="card-header recs-summary">
          <div class="recs-summary-row">
            <h3>Recomendaciones módulo 02</h3>
            <ChevronDown :size="16" aria-hidden="true" />
          </div>
          <span class="card-meta">Motor avanzado · heladas, plagas, cosecha</span>
        </summary>
        <div v-if="recomendaciones.length" class="recs-list">
          <div v-for="(rec, i) in recomendaciones" :key="rec.codigo || i" class="rec-item">
            <div>
              <span class="rec-codigo">{{ rec.codigo || rec.cultivo }}</span>
              <p class="rec-texto">{{ rec.texto || rec.accion }}</p>
              <p v-if="rec.motivo" class="rec-motivo">{{ rec.motivo }}</p>
            </div>
          </div>
        </div>
        <p v-else class="rec-empty">Sin alertas críticas en motor avanzado 02</p>
      </details>
    </div>
  </div>
</template>

<style scoped>
.agricola-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 1280px;
}
.view-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.breadcrumb {
  font-size: 12px;
  color: var(--color-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}
.view-subtitle {
  margin: 0;
}
.cultivo-tabs {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.cultivo-tab {
  padding: 5px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  font-size: 12px;
  cursor: pointer;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  transition: all 0.15s;
}
.cultivo-tab.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
  font-weight: 600;
}
.section-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.section-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--color-border);
}
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1rem 1.25rem;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 4px;
}
.card-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}
.card-meta {
  font-size: 11px;
  color: var(--color-muted);
}
.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.recs-details summary {
  list-style: none;
  cursor: pointer;
}
.recs-summary {
  margin-bottom: 0;
}
.recs-summary-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}
.recs-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 12px;
}
.rec-item {
  padding: 8px 10px;
  background: var(--color-primary-subtle);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-primary);
}
.rec-codigo {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-muted);
}
.rec-texto {
  font-size: 13px;
  color: var(--color-text);
  margin: 4px 0 0;
}
.rec-motivo {
  font-size: 11px;
  color: var(--color-muted);
  margin: 2px 0 0;
}
.rec-empty {
  font-size: 13px;
  color: var(--color-muted);
  padding: 8px 0 0;
}
@media (max-width: 640px) {
  .two-col {
    grid-template-columns: 1fr;
  }
}
</style>
