<template>
  <div class="page">
    <header class="page-head">
      <h1>Dispersión de contaminantes</h1>
      <p>Inversión térmica · viento · capa límite · polvo en suspensión — airshed {{ site.faena?.nombre || site.siteLabel }}</p>
    </header>

    <div class="controls">
      <label>
        Estación
        <select v-model="slugActivo">
          <option v-for="est in site.stations" :key="est.slug" :value="est.slug">
            {{ est.nombre }}
          </option>
        </select>
      </label>
      <div class="tabs">
        <button
          v-for="h in horizontes"
          :key="h.id"
          type="button"
          :class="['tab', { active: horizonte === h.id }]"
          @click="horizonte = h.id"
        >
          {{ h.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="state">Calculando condiciones de dispersión…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>

    <template v-else>
      <section v-if="actual" class="resumen" :class="`pot-${actual.potencial_dispersion || 'na'}`">
        <div class="resumen-main">
          <span class="pot-label">Potencial de dispersión</span>
          <strong class="pot-valor">{{ etiquetaPotencial(actual.potencial_dispersion) }}</strong>
          <span class="pot-indice">Índice {{ Math.round(actual.indice_dispersion ?? 0) }}/100</span>
        </div>
        <ul class="factores">
          <li>
            <span>Viento</span>
            <strong>{{ actual.viento_categoria || '—' }}
              <em v-if="actual.viento_velocidad != null">({{ actual.viento_velocidad }} m/s)</em>
            </strong>
          </li>
          <li>
            <span>Inversión térmica</span>
            <strong :class="{ warn: actual.inversion }">
              {{ actual.inversion ? `Sí (${actual.inversion_intensidad ?? '?'} °C)` : 'No' }}
            </strong>
          </li>
          <li>
            <span>Nubosidad baja</span>
            <strong :class="{ warn: actual.niebla }">{{ etiquetaNubosidad(actual.tipo_nubosidad) }}</strong>
          </li>
          <li v-if="actual.altura_capa_limite != null">
            <span>Capa límite</span>
            <strong>{{ Math.round(actual.altura_capa_limite) }} m</strong>
          </li>
        </ul>
      </section>

      <section v-if="proyeccion" class="proyeccion">
        <p class="conf">Proyección estadística (climatología) · confianza <strong>baja</strong> · días {{ proyeccion.dia_desde }}–{{ proyeccion.dia_hasta }}</p>
        <p>
          Potencial esperado: <strong>{{ etiquetaPotencial(proyeccion.potencial_dispersion) }}</strong>
          · viento medio {{ proyeccion.viento_velocidad }} m/s
          · inversión probable: {{ proyeccion.inversion_probable ? 'sí' : 'no' }}
        </p>
      </section>

      <div v-if="ventanasAlerta.length" class="alerta" role="alert">
        <strong>⚠️ {{ ventanasAlerta.length }} {{ ventanasAlerta.length === 1 ? 'ventana' : 'ventanas' }} de mala dispersión</strong>
        <span>Riesgo de acumulación de contaminantes (índice &lt; {{ UMBRAL }}).</span>
      </div>

      <section v-if="labels.length" class="grafico">
        <AireSeriesChart :labels="labels" :series="series" y-name="Índice / viento" />
      </section>

      <p class="fuente">Fuente: Open-Meteo Forecast (modelo). Índice 0-100: mayor = mejor dispersión.</p>
    </template>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import AireSeriesChart from '@/components/aire/AireSeriesChart.vue'
import {
  wakeApi,
  fetchDispersionHoraria,
  fetchDispersionDiaria,
  fetchDispersionProyeccion,
  ESTACION_ANCLA,
} from '@/services/aireApi'

const site = inject('site')
const UMBRAL = 40

const horizontes = [
  { id: 'horaria', label: '72 horas' },
  { id: 'diaria', label: '7 días' },
  { id: 'proyeccion', label: '16-30 días' },
]

const loading = ref(true)
const error = ref(null)
const slugActivo = ref(site.faena?.estacionAncla || site.stations[0]?.slug || ESTACION_ANCLA)
const horizonte = ref('horaria')
const serie = ref([])
const proyeccion = ref(null)

const POTENCIAL = {
  muy_baja: 'Muy baja',
  baja: 'Baja',
  moderada: 'Moderada',
  buena: 'Buena',
  muy_buena: 'Muy buena',
}
const NUBOSIDAD = { niebla: 'Niebla', neblina: 'Neblina', estratos: 'Estratos', despejado: 'Despejado' }

function etiquetaPotencial(v) {
  return POTENCIAL[v] || '—'
}
function etiquetaNubosidad(v) {
  return NUBOSIDAD[v] || '—'
}

const actual = computed(() => (horizonte.value !== 'proyeccion' ? serie.value[0] || null : null))
const ventanasAlerta = computed(() => serie.value.filter((f) => f.alerta_dispersion))

const labels = computed(() =>
  serie.value.map((f) => {
    const t = String(f.fecha_hora || '')
    return horizonte.value === 'horaria' ? t.slice(5, 16).replace('T', ' ') : t.slice(0, 10)
  })
)
const series = computed(() => [
  {
    name: 'Índice dispersión',
    type: 'line',
    data: serie.value.map((f) => f.indice_dispersion),
    color: '#fb923c',
  },
  {
    name: 'Viento (m/s)',
    type: 'bar',
    data: serie.value.map((f) => f.viento_velocidad),
    color: '#38bdf8',
  },
])

async function cargar() {
  loading.value = true
  error.value = null
  serie.value = []
  proyeccion.value = null
  try {
    await wakeApi()
    if (horizonte.value === 'proyeccion') {
      proyeccion.value = await fetchDispersionProyeccion(slugActivo.value)
    } else if (horizonte.value === 'diaria') {
      serie.value = (await fetchDispersionDiaria(slugActivo.value, 7)) || []
    } else {
      serie.value = (await fetchDispersionHoraria(slugActivo.value, 72)) || []
    }
  } catch (err) {
    error.value =
      err?.status === 503
        ? 'Servicio de dispersión temporalmente no disponible (Open-Meteo).'
        : err?.message || 'No se pudo cargar la dispersión'
  } finally {
    loading.value = false
  }
}

watch([slugActivo, horizonte], cargar)
onMounted(cargar)
</script>

<style scoped>
.page { max-width: 1100px; }
.page-head { margin-bottom: 1rem; }
.page-head h1 { margin: 0 0 0.25rem; font-size: 1.6rem; }
.page-head p { margin: 0; color: var(--color-text-secondary); }
.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1.25rem;
}
.controls label { display: flex; flex-direction: column; gap: 0.25rem; font-size: 0.8rem; color: var(--color-text-secondary); }
.controls select {
  padding: 0.5rem 0.65rem;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 6px;
}
.tabs { display: flex; gap: 0.4rem; }
.tab {
  padding: 0.5rem 0.85rem;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: 6px;
  cursor: pointer;
}
.tab.active { background: var(--color-primary-muted); color: var(--color-primary); border-color: var(--color-primary); }
.resumen {
  border: 1px solid var(--color-border);
  border-left: 4px solid var(--color-primary);
  border-radius: 10px;
  padding: 1rem 1.15rem;
  margin-bottom: 1rem;
}
.resumen.pot-muy_baja, .resumen.pot-baja { border-left-color: #ef4444; }
.resumen.pot-moderada { border-left-color: #f59e0b; }
.resumen.pot-buena, .resumen.pot-muy_buena { border-left-color: #22c55e; }
.resumen-main { display: flex; flex-direction: column; gap: 0.15rem; margin-bottom: 0.75rem; }
.pot-label { font-size: 0.78rem; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 0.04em; }
.pot-valor { font-size: 1.5rem; }
.pot-indice { font-size: 0.85rem; color: var(--color-text-secondary); }
.factores { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.75rem; }
.factores li { display: flex; flex-direction: column; gap: 0.15rem; font-size: 0.85rem; }
.factores span { color: var(--color-text-secondary); }
.factores .warn { color: #f59e0b; }
.proyeccion { border: 1px dashed var(--color-border); border-radius: 10px; padding: 0.85rem 1rem; margin-bottom: 1rem; font-size: 0.9rem; }
.proyeccion .conf { margin: 0 0 0.4rem; font-size: 0.8rem; color: var(--color-text-secondary); }
.alerta {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  border: 1px solid #ef4444;
  background: rgba(239, 68, 68, 0.12);
  border-radius: 10px;
  padding: 0.85rem 1rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}
.grafico { margin-top: 0.5rem; }
.state { padding: 2rem; text-align: center; color: var(--color-text-secondary); }
.state.error { color: var(--color-danger); }
.btn {
  margin-top: 0.75rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-primary);
  background: var(--color-primary-muted);
  color: var(--color-primary);
  border-radius: 6px;
  cursor: pointer;
}
.fuente { margin-top: 1rem; font-size: 0.8rem; color: var(--color-muted); }
</style>
