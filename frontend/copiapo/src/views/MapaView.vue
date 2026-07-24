<template>
  <div class="page">
    <header class="page-head">
      <h1>Mapa del airshed</h1>
      <p>7 puntos del valle de Copiapó — color según {{ modo === 'icap' ? 'ICAP' : 'potencial de dispersión' }}</p>
    </header>

    <div class="controls">
      <div class="tabs">
        <button type="button" :class="['tab', { active: modo === 'icap' }]" @click="setModo('icap')">ICAP</button>
        <button type="button" :class="['tab', { active: modo === 'dispersion' }]" @click="setModo('dispersion')">Dispersión</button>
      </div>
    </div>

    <div v-if="loading" class="state">Cargando red de estaciones…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>

    <template v-else>
      <MapaEstacionesChart
        :puntos="puntos"
        :valor-label="modo === 'icap' ? 'ICAP' : 'Índice dispersión'"
        @select="slugActivo = $event"
      />

      <ul class="leyenda">
        <li v-for="l in leyenda" :key="l.nivel">
          <span class="dot" :style="{ background: l.color }" />{{ l.label }}
        </li>
      </ul>

      <section v-if="detalle" class="detalle">
        <h2>{{ detalle.nombre }}</h2>
        <p v-if="modo === 'icap'">
          ICAP <strong>{{ Math.round(detalle.valor ?? 0) }}</strong> · {{ detalle.etiqueta }}
        </p>
        <p v-else>
          Índice dispersión <strong>{{ Math.round(detalle.valor ?? 0) }}/100</strong> · {{ detalle.etiqueta }}
        </p>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import MapaEstacionesChart from '@/components/aire/MapaEstacionesChart.vue'
import { wakeApi, fetchAireActual, fetchDispersionHoraria } from '@/services/aireApi'

const site = inject('site')
const loading = ref(true)
const error = ref(null)
const modo = ref('icap')
const slugActivo = ref(site.stations[0]?.slug || null)
const datos = ref({}) // slug -> { valor, nivel, etiqueta }

const COLOR_ICAP = {
  bueno: '#22c55e',
  regular: '#eab308',
  alerta: '#f97316',
  preemergencia: '#ef4444',
  emergencia: '#a21caf',
}
const COLOR_DISP = {
  muy_buena: '#22c55e',
  buena: '#4ade80',
  moderada: '#eab308',
  baja: '#f97316',
  muy_baja: '#ef4444',
}
const ETIQ_DISP = {
  muy_buena: 'Muy buena',
  buena: 'Buena',
  moderada: 'Moderada',
  baja: 'Baja',
  muy_baja: 'Muy baja',
}
const SIN_DATO = '#6b7280'

const leyenda = computed(() =>
  modo.value === 'icap'
    ? [
        { nivel: 'bueno', color: COLOR_ICAP.bueno, label: 'Bueno' },
        { nivel: 'regular', color: COLOR_ICAP.regular, label: 'Regular' },
        { nivel: 'alerta', color: COLOR_ICAP.alerta, label: 'Alerta' },
        { nivel: 'preemergencia', color: COLOR_ICAP.preemergencia, label: 'Preemergencia' },
        { nivel: 'emergencia', color: COLOR_ICAP.emergencia, label: 'Emergencia' },
      ]
    : [
        { nivel: 'muy_buena', color: COLOR_DISP.muy_buena, label: 'Muy buena' },
        { nivel: 'moderada', color: COLOR_DISP.moderada, label: 'Moderada' },
        { nivel: 'baja', color: COLOR_DISP.baja, label: 'Baja' },
        { nivel: 'muy_baja', color: COLOR_DISP.muy_baja, label: 'Muy baja' },
      ]
)

const puntos = computed(() =>
  site.stations.map((s) => {
    const d = datos.value[s.slug] || {}
    const palette = modo.value === 'icap' ? COLOR_ICAP : COLOR_DISP
    return {
      slug: s.slug,
      nombre: s.nombre,
      lat: s.lat,
      lon: s.lon,
      valor: d.valor,
      etiqueta: d.etiqueta,
      color: palette[d.nivel] || SIN_DATO,
      activo: s.slug === slugActivo.value,
    }
  })
)

const detalle = computed(() => {
  const s = site.stations.find((x) => x.slug === slugActivo.value)
  if (!s) return null
  return { nombre: s.nombre, ...(datos.value[s.slug] || {}) }
})

async function setModo(m) {
  if (modo.value === m && Object.keys(datos.value).length) return
  modo.value = m
  await cargar()
}

async function cargar() {
  loading.value = true
  error.value = null
  datos.value = {}
  try {
    await wakeApi()
    await Promise.all(
      site.stations.map(async (s) => {
        try {
          if (modo.value === 'icap') {
            const a = await fetchAireActual(s.slug)
            datos.value[s.slug] = { valor: a?.icap, nivel: a?.nivel, etiqueta: a?.etiqueta }
          } else {
            const serie = await fetchDispersionHoraria(s.slug, 24)
            const f = Array.isArray(serie) ? serie[0] : null
            datos.value[s.slug] = {
              valor: f?.indice_dispersion,
              nivel: f?.potencial_dispersion,
              etiqueta: ETIQ_DISP[f?.potencial_dispersion] || '—',
            }
          }
        } catch {
          datos.value[s.slug] = {}
        }
      })
    )
  } catch (err) {
    error.value = err?.message || 'No se pudo cargar el mapa'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.page { max-width: 1100px; }
.page-head { margin-bottom: 1rem; }
.page-head h1 { margin: 0 0 0.25rem; font-size: 1.6rem; }
.page-head p { margin: 0; color: var(--color-text-secondary); }
.controls { margin-bottom: 1rem; }
.tabs { display: flex; gap: 0.4rem; }
.tab {
  padding: 0.5rem 0.95rem;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: 6px;
  cursor: pointer;
}
.tab.active { background: var(--color-primary-muted); color: var(--color-primary); border-color: var(--color-primary); }
.leyenda {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  padding: 0.5rem 0 0;
  margin: 0;
  font-size: 0.82rem;
  color: var(--color-text-secondary);
}
.leyenda li { display: flex; align-items: center; gap: 0.4rem; }
.dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
.detalle {
  margin-top: 1rem;
  padding: 0.85rem 1rem;
  border: 1px solid var(--color-border);
  border-left: 4px solid var(--color-primary);
  border-radius: 10px;
}
.detalle h2 { margin: 0 0 0.35rem; font-size: 1.1rem; }
.detalle p { margin: 0; }
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
</style>
