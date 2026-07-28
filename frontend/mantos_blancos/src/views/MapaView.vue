<template>
  <div class="page">
    <header class="page-head">
      <h1>Mapa del airshed</h1>
      <p>
        Faena {{ site.faena?.nombre || site.siteLabel }} · fondo satelital ·
        {{ modo === 'icap' ? 'ICAP + viento' : 'potencial de dispersión + plumas' }}
      </p>
    </header>

    <div class="controls">
      <div class="tabs" role="tablist" aria-label="Capa del mapa">
        <button
          type="button"
          role="tab"
          :aria-selected="modo === 'icap'"
          :class="['tab', { active: modo === 'icap' }]"
          @click="setModo('icap')"
        >
          ICAP
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="modo === 'dispersion'"
          :class="['tab', { active: modo === 'dispersion' }]"
          @click="setModo('dispersion')"
        >
          Dispersión
        </button>
      </div>
    </div>

    <div v-if="loading" class="state">Cargando red de estaciones…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>

    <template v-else>
      <div class="layout" :class="{ 'layout--open': detalle }">
        <div class="map-col">
          <AirshedMapLibre
            :puntos="puntos"
            :modo="modo"
            :slug-activo="slugActivo"
            @select="onSelect"
          />
          <ul class="leyenda">
            <li v-for="l in leyenda" :key="l.nivel">
              <span class="dot" :style="{ background: l.color }" />{{ l.label }}
            </li>
          </ul>
        </div>

        <aside v-if="detalle" class="panel" aria-label="Detalle de estación">
          <button type="button" class="panel-close" aria-label="Cerrar panel" @click="slugActivo = null">
            ×
          </button>
          <h2>{{ detalle.nombre }}</h2>
          <p class="coords">
            {{ detalle.lat?.toFixed(3) }}, {{ detalle.lon?.toFixed(3) }}
          </p>

          <div class="kpi">
            <template v-if="modo === 'icap'">
              <span class="kpi-label">ICAP</span>
              <strong class="kpi-val" :style="{ color: detalle.color }">
                {{ detalle.valor != null ? Math.round(detalle.valor) : '—' }}
              </strong>
              <span class="kpi-sub">{{ detalle.etiqueta || '—' }}</span>
            </template>
            <template v-else>
              <span class="kpi-label">Dispersión</span>
              <strong class="kpi-val" :style="{ color: detalle.color }">
                {{ detalle.valor != null ? Math.round(detalle.valor) : '—' }}/100
              </strong>
              <span class="kpi-sub">{{ detalle.etiqueta || '—' }}</span>
            </template>
          </div>

          <p v-if="detalle.pm25 != null" class="meta">
            PM2.5 <strong>{{ detalle.pm25 }}</strong> µg/m³
            <span v-if="detalle.pm10 != null"> · PM10 <strong>{{ detalle.pm10 }}</strong></span>
          </p>

          <div v-if="detalle.vientoTexto" class="viento-block">
            <h3>Viento</h3>
            <p class="viento-txt">{{ detalle.vientoTexto }}</p>
            <div
              class="mini-rose"
              role="img"
              :aria-label="`Dirección del viento ${detalle.vientoTexto}`"
            >
              <span
                class="mini-rose__arrow"
                :style="{ transform: `rotate(${detalle.vientoRot}deg)` }"
              />
              <span class="mini-rose__n">N</span>
            </div>
          </div>
          <p v-else class="meta muted">Sin dato de viento en esta estación</p>

          <div v-if="sparkPoints.length" class="spark-block">
            <h3>{{ modo === 'icap' ? 'ICAP · 24 h' : 'Índice · 24 h' }}</h3>
            <svg
              class="spark"
              viewBox="0 0 200 48"
              preserveAspectRatio="none"
              role="img"
              :aria-label="`Serie ${sparkPoints.length} puntos`"
            >
              <polyline
                fill="none"
                stroke="var(--color-primary)"
                stroke-width="2"
                :points="sparkPolyline"
              />
            </svg>
          </div>
        </aside>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import AirshedMapLibre from '@/components/aire/AirshedMapLibre.vue'
import {
  wakeApi,
  fetchAireActual,
  fetchDispersionHoraria,
  ESTACION_ANCLA,
} from '@/services/aireApi'
import { textoViento, rotacionFlechaHacia } from '@/utils/faenaMap'

const site = inject('site')
const loading = ref(true)
const error = ref(null)
const modo = ref('icap')
const slugActivo = ref(site.faena?.estacionAncla || site.stations[0]?.slug || ESTACION_ANCLA)
const datos = ref({})

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
      pm25: d.pm25,
      pm10: d.pm10,
      viento_velocidad: d.viento_velocidad,
      viento_direccion: d.viento_direccion,
      serie: d.serie || [],
    }
  })
)

const detalle = computed(() => {
  if (!slugActivo.value) return null
  const p = puntos.value.find((x) => x.slug === slugActivo.value)
  if (!p) return null
  const vientoTexto = textoViento(p.viento_velocidad, p.viento_direccion)
  return {
    ...p,
    vientoTexto,
    vientoRot: rotacionFlechaHacia(p.viento_direccion),
  }
})

const sparkPoints = computed(() => {
  const serie = detalle.value?.serie || []
  return serie
    .map((r) => (modo.value === 'icap' ? r.icap : r.indice_dispersion ?? r.icap))
    .filter((v) => v != null && !Number.isNaN(Number(v)))
    .map(Number)
})

const sparkPolyline = computed(() => {
  const vals = sparkPoints.value
  if (!vals.length) return ''
  const min = Math.min(...vals)
  const max = Math.max(...vals)
  const span = max - min || 1
  return vals
    .map((v, i) => {
      const x = vals.length === 1 ? 100 : (i / (vals.length - 1)) * 200
      const y = 44 - ((v - min) / span) * 40
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(' ')
})

function onSelect(slug) {
  slugActivo.value = slug
}

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
        const slug = s.slug
        if (!slug || slug === 'undefined') return
        try {
          if (modo.value === 'icap') {
            const a = await fetchAireActual(slug)
            let viento_velocidad = a?.viento_velocidad
            let viento_direccion = a?.viento_direccion
            if (viento_velocidad == null || viento_direccion == null) {
              try {
                const serie = await fetchDispersionHoraria(slug, 3)
                const f = Array.isArray(serie) ? serie[0] : null
                viento_velocidad = f?.viento_velocidad ?? viento_velocidad
                viento_direccion = f?.viento_direccion ?? viento_direccion
              } catch {
                /* ignore */
              }
            }
            datos.value[slug] = {
              valor: a?.icap,
              nivel: a?.nivel,
              etiqueta: a?.etiqueta,
              pm25: a?.pm2_5,
              pm10: a?.pm10,
              viento_velocidad,
              viento_direccion,
              serie: a?.serie_24h || [],
            }
          } else {
            const serie = await fetchDispersionHoraria(slug, 24)
            const f = Array.isArray(serie) ? serie[0] : null
            datos.value[slug] = {
              valor: f?.indice_dispersion,
              nivel: f?.potencial_dispersion,
              etiqueta: ETIQ_DISP[f?.potencial_dispersion] || '—',
              viento_velocidad: f?.viento_velocidad,
              viento_direccion: f?.viento_direccion,
              serie: Array.isArray(serie)
                ? serie.slice(0, 24).map((r) => ({
                    icap: r.indice_dispersion,
                    indice_dispersion: r.indice_dispersion,
                  }))
                : [],
            }
          }
        } catch {
          datos.value[slug] = {}
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
.page { max-width: 1200px; }
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
  font-family: inherit;
}
.tab.active {
  background: var(--color-primary-muted);
  color: var(--color-primary);
  border-color: var(--color-primary);
}
.layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}
@media (min-width: 900px) {
  .layout--open {
    grid-template-columns: 1fr minmax(240px, 300px);
    align-items: start;
  }
}
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

.panel {
  position: relative;
  padding: 1rem 1.1rem;
  border: 1px solid var(--color-border);
  border-left: 4px solid var(--color-primary);
  border-radius: 12px;
  background: var(--color-surface, #111827);
}
.panel-close {
  position: absolute;
  top: 0.4rem;
  right: 0.55rem;
  border: none;
  background: transparent;
  color: var(--color-muted);
  font-size: 1.35rem;
  cursor: pointer;
  line-height: 1;
}
.panel h2 { margin: 0 0 0.2rem; font-size: 1.15rem; padding-right: 1.5rem; }
.coords {
  margin: 0 0 0.75rem;
  font-size: 0.78rem;
  color: var(--color-muted);
  font-variant-numeric: tabular-nums;
}
.kpi { display: flex; flex-direction: column; gap: 0.15rem; margin-bottom: 0.65rem; }
.kpi-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--color-muted); }
.kpi-val { font-size: 1.75rem; line-height: 1.1; }
.kpi-sub { font-size: 0.9rem; color: var(--color-text-secondary); }
.meta { margin: 0 0 0.75rem; font-size: 0.85rem; }
.meta.muted { color: var(--color-muted); }

.viento-block { margin: 0.75rem 0; }
.viento-block h3,
.spark-block h3 {
  margin: 0 0 0.35rem;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-muted);
  font-weight: 600;
}
.viento-txt { margin: 0 0 0.5rem; font-size: 1rem; font-weight: 600; }
.mini-rose {
  position: relative;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: #0f172a;
}
.mini-rose__n {
  position: absolute;
  top: 2px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.65rem;
  color: var(--color-muted);
}
.mini-rose__arrow {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 0;
  height: 0;
  margin: -14px 0 0 -5px;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-bottom: 22px solid rgba(255, 255, 255, 0.85);
  transform-origin: 50% 100%;
}

.spark-block { margin-top: 0.75rem; }
.spark {
  width: 100%;
  height: 48px;
  display: block;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 6px;
}

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
