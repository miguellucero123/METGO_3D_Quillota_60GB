<template>
  <div class="page">
    <header class="page-head">
      <h1>METGO Airshed Modeler</h1>
      <p>
        Campo de concentración + viento + terreno — proxy innovador tipo AERMOD/CALPUFF para el
        airshed Copiapó
      </p>
    </header>

    <section class="pipeline" aria-label="Pipeline de modelación">
      <article
        v-for="paso in pipeline"
        :key="paso.id"
        :class="['pipe-card', { highlight: paso.paso === 3 || paso.paso === 4 }]"
      >
        <span class="pipe-n">{{ String(paso.paso).padStart(2, '0') }}</span>
        <h2>{{ paso.titulo }}</h2>
        <p>{{ paso.detalle }}</p>
        <ul class="tags">
          <li v-for="t in paso.tags" :key="t">{{ t }}</li>
        </ul>
      </article>
    </section>

    <div class="features">
      <div class="feat">
        <strong>Evolución temporal</strong>
        <span>Variación horaria de la concentración proxy</span>
      </div>
      <div class="feat">
        <strong>Campo meteorológico</strong>
        <span>Dirección y velocidad del viento</span>
      </div>
      <div class="feat">
        <strong>Análisis integrado</strong>
        <span>Concentración · satélite · fuentes seed</span>
      </div>
    </div>

    <div v-if="loading" class="state">Ejecutando pipeline MAM (meteo + pluma gaussiana)…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>

    <template v-else-if="modelo">
      <p class="nota" role="note">{{ modelo.nota }}</p>

      <div class="map-panel">
        <AirshedModelMap
          :heat-geojson="frameActivo?.grid?.heat_geojson"
          :wind-vectors="frameActivo?.grid?.wind_vectors || []"
          :fuentes="frameActivo?.grid?.fuentes || []"
          :max-value="frameActivo?.grid?.max?.value"
        />
        <aside class="leyenda" aria-label="Leyenda y máximos">
          <h3>Concentración (µg/m³ proxy)</h3>
          <div class="escala" role="img" aria-label="Escala verde a naranja">
            <span>0.15</span>
            <span>0.5</span>
            <span>1.0</span>
            <span>≥2</span>
          </div>
          <dl>
            <div>
              <dt>Máximo</dt>
              <dd>
                {{ fmtMax(frameActivo?.grid?.max) }}
              </dd>
            </div>
            <div>
              <dt>Estabilidad</dt>
              <dd>{{ frameActivo?.meteo?.clase_estabilidad || '—' }}</dd>
            </div>
            <div>
              <dt>Viento</dt>
              <dd>
                {{ frameActivo?.meteo?.viento_velocidad ?? '—' }} m/s ·
                {{ Math.round(frameActivo?.meteo?.viento_direccion ?? 0) }}°
              </dd>
            </div>
            <div>
              <dt>Inversión</dt>
              <dd>{{ frameActivo?.meteo?.inversion ? 'Sí' : 'No' }}</dd>
            </div>
          </dl>
          <p class="modelo-id">{{ modelo.modelo }} · {{ modelo.inspiracion }}</p>
        </aside>
      </div>

      <div class="timeline" v-if="frames.length">
        <div class="tl-controls">
          <button type="button" class="btn" @click="togglePlay" :aria-pressed="playing">
            {{ playing ? 'Pausar' : 'Animar' }}
          </button>
          <label class="scrub">
            Frame
            <input
              type="range"
              min="0"
              :max="frames.length - 1"
              step="1"
              v-model.number="frameIdx"
            />
            <span>{{ frameIdx + 1 }} / {{ frames.length }}</span>
          </label>
        </div>
        <p class="tl-meta">
          {{ frameActivo?.fecha_hora || '—' }} · potencial
          {{ frameActivo?.meteo?.potencial_dispersion || '—' }}
        </p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AirshedModelMap from '@/components/aire/AirshedModelMap.vue'
import { fetchAirshedModel } from '@/services/aireApi'

const loading = ref(true)
const error = ref(null)
const modelo = ref(null)
const frameIdx = ref(0)
const playing = ref(false)
let timer = null

const pipeline = computed(() => modelo.value?.pipeline || [])
const frames = computed(() => modelo.value?.frames || [])
const frameActivo = computed(() => frames.value[frameIdx.value] || null)

function fmtMax(m) {
  if (!m || m.value == null) return '—'
  return `${Number(m.value).toFixed(2)} en (${m.lon}, ${m.lat})`
}

function stopPlay() {
  playing.value = false
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function togglePlay() {
  if (playing.value) {
    stopPlay()
    return
  }
  playing.value = true
  timer = setInterval(() => {
    if (!frames.value.length) return
    frameIdx.value = (frameIdx.value + 1) % frames.value.length
  }, 1100)
}

async function cargar() {
  loading.value = true
  error.value = null
  stopPlay()
  try {
    modelo.value = await fetchAirshedModel({ nx: 28, ny: 28, frames: 6 })
    frameIdx.value = 0
  } catch (e) {
    error.value = e?.message || 'No se pudo ejecutar el modelo airshed'
    modelo.value = null
  } finally {
    loading.value = false
  }
}

watch(frameIdx, () => {
  /* MapLibre reacciona por props del frame activo */
})

onMounted(cargar)
onBeforeUnmount(stopPlay)
</script>

<style scoped>
.page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 1.25rem 1.25rem 2.5rem;
}
.page-head h1 {
  margin: 0 0 0.35rem;
  font-size: 1.55rem;
}
.page-head p {
  margin: 0;
  color: var(--color-text-secondary);
  max-width: 52rem;
  line-height: 1.45;
}
.pipeline {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0.65rem;
  margin: 1.35rem 0 1rem;
}
.pipe-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 0.75rem 0.7rem;
  min-height: 100%;
}
.pipe-card.highlight {
  background: color-mix(in srgb, var(--color-primary) 14%, var(--color-surface));
  border-color: color-mix(in srgb, var(--color-primary) 35%, var(--color-border));
}
.pipe-n {
  display: block;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--color-muted);
  margin-bottom: 0.35rem;
}
.pipe-card h2 {
  margin: 0 0 0.35rem;
  font-size: 0.88rem;
}
.pipe-card p {
  margin: 0 0 0.5rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  line-height: 1.35;
}
.tags {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}
.tags li {
  font-size: 0.65rem;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  background: var(--color-primary-subtle);
  color: var(--color-text-secondary);
}
.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.1rem;
}
.feat {
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 0.75rem 0.85rem;
  background: var(--color-surface);
}
.feat strong {
  display: block;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
}
.feat span {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}
.nota {
  font-size: 0.8rem;
  color: var(--color-muted);
  margin: 0 0 0.85rem;
  line-height: 1.4;
}
.map-panel {
  display: grid;
  grid-template-columns: 1fr minmax(200px, 240px);
  gap: 0.85rem;
  align-items: start;
}
.leyenda {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 0.9rem;
}
.leyenda h3 {
  margin: 0 0 0.55rem;
  font-size: 0.85rem;
}
.escala {
  height: 12px;
  border-radius: 6px;
  margin-bottom: 0.55rem;
  background: linear-gradient(90deg, #166534, #22c55e, #eab308, #ea580c);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding: 0 2px 14px;
  font-size: 0.65rem;
  color: var(--color-muted);
}
.leyenda dl {
  margin: 0;
}
.leyenda dl > div {
  margin-bottom: 0.55rem;
}
.leyenda dt {
  font-size: 0.7rem;
  color: var(--color-muted);
}
.leyenda dd {
  margin: 0.1rem 0 0;
  font-size: 0.82rem;
  font-weight: 600;
}
.modelo-id {
  margin: 0.75rem 0 0;
  font-size: 0.68rem;
  color: var(--color-muted);
  line-height: 1.35;
}
.timeline {
  margin-top: 1rem;
  padding: 0.85rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-surface);
}
.tl-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
}
.scrub {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  flex: 1;
  font-size: 0.85rem;
}
.scrub input {
  flex: 1;
  min-width: 120px;
}
.tl-meta {
  margin: 0.55rem 0 0;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}
.state {
  padding: 2rem 1rem;
  text-align: center;
  color: var(--color-text-secondary);
}
.state.error {
  color: #b91c1c;
}
.btn {
  border: none;
  border-radius: 8px;
  padding: 0.45rem 0.9rem;
  background: var(--color-primary);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}
@media (max-width: 960px) {
  .pipeline {
    grid-template-columns: 1fr 1fr;
  }
  .map-panel {
    grid-template-columns: 1fr;
  }
  .features {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 640px) {
  .pipeline {
    grid-template-columns: 1fr;
  }
}
</style>
