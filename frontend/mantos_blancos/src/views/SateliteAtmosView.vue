<template>
  <div class="page">
    <header class="page-head">
      <h1>Satélite atmosférico</h1>
      <p>GOES VIS · IR · vapor de agua · sector rajo {{ site.faena?.nombre || site.siteLabel }}</p>
    </header>

    <div v-if="loading" class="state">Cargando frames NOAA…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>

    <template v-else-if="data">
      <p class="nota">{{ data.nota }}</p>
      <div class="diag" :class="data.diagnostico?.etiqueta">
        <strong>{{ etiquetaDiag(data.diagnostico?.etiqueta) }}</strong>
        <span>{{ data.diagnostico?.detalle }}</span>
        <span v-if="data.diagnostico?.nubosidad_baja != null">
          Nub. baja {{ data.diagnostico.nubosidad_baja }}% · Vis
          {{ data.diagnostico.visibilidad_km ?? '—' }} km
        </span>
      </div>

      <div class="bandas">
        <article v-for="b in data.bandas || []" :key="b.id" class="banda">
          <header>
            <h2>{{ b.nombre }}</h2>
            <span>{{ b.descripcion }}</span>
          </header>
          <div v-if="!b.disponible" class="empty">Sin frames (CDN / red)</div>
          <template v-else>
            <img
              :src="frameUrl(b)"
              :alt="`${b.nombre} GOES`"
              class="frame"
              loading="lazy"
            />
            <label class="scrub" v-if="(b.frames || []).length > 1">
              Periodo
              <input
                type="range"
                min="0"
                :max="b.frames.length - 1"
                :value="idxBanda[b.id] ?? b.frames.length - 1"
                @input="setIdx(b.id, $event.target.value, b.frames.length)"
              />
            </label>
            <p class="meta-frame">{{ frameId(b) }}</p>
          </template>
        </article>
      </div>
    </template>
  </div>
</template>

<script setup>
import { inject, onMounted, reactive, ref } from 'vue'
import { fetchSateliteAtmos, ESTACION_ANCLA } from '@/services/aireApi'

const site = inject('site')
const loading = ref(true)
const error = ref(null)
const data = ref(null)
const idxBanda = reactive({})

function etiquetaDiag(id) {
  const map = {
    despejado: 'Despejado',
    incursion_parcial: 'Incursión parcial',
    nubes_bajas_valle: 'Nubes bajas en valle',
    neblina: 'Neblina',
    niebla: 'Niebla',
    llovizna: 'Llovizna',
    lluvia_debil: 'Lluvia débil',
    sin_dato: 'Sin dato',
  }
  return map[id] || id || '—'
}

function setIdx(id, val, len) {
  idxBanda[id] = Math.max(0, Math.min(Number(val), len - 1))
}

function frameUrl(b) {
  const frames = b.frames || []
  if (!frames.length) return ''
  const i = idxBanda[b.id] ?? frames.length - 1
  return frames[i]?.url || ''
}

function frameId(b) {
  const frames = b.frames || []
  if (!frames.length) return ''
  const i = idxBanda[b.id] ?? frames.length - 1
  return frames[i]?.id || ''
}

async function cargar() {
  loading.value = true
  error.value = null
  try {
    data.value = await fetchSateliteAtmos({ estacion: site.faena?.estacionAncla || ESTACION_ANCLA })
    for (const b of data.value?.bandas || []) {
      if (b.frames?.length) idxBanda[b.id] = b.frames.length - 1
    }
  } catch (e) {
    error.value = e?.message || 'No se pudo cargar satélite'
    data.value = null
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 1.25rem; }
.page-head h1 { margin: 0 0 0.35rem; }
.page-head p { margin: 0; color: var(--color-text-secondary); }
.nota { font-size: 0.8rem; color: var(--color-muted); margin: 0.85rem 0; }
.diag {
  display: flex; flex-direction: column; gap: 0.25rem;
  padding: 0.85rem 1rem; border-radius: 10px; border: 1px solid var(--color-border);
  background: var(--color-surface); margin-bottom: 1rem; font-size: 0.85rem;
}
.diag.niebla, .diag.nubes_bajas_valle { border-color: #94a3b8; background: #f1f5f9; }
.diag.llovizna, .diag.lluvia_debil { border-color: #38bdf8; background: #e0f2fe; }
.bandas {
  display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.85rem;
}
.banda {
  border: 1px solid var(--color-border); border-radius: 12px; overflow: hidden;
  background: var(--color-surface);
}
.banda header { padding: 0.65rem 0.75rem; }
.banda h2 { margin: 0; font-size: 0.95rem; }
.banda header span { font-size: 0.72rem; color: var(--color-muted); }
.frame { width: 100%; aspect-ratio: 1; object-fit: cover; display: block; background: #0f172a; }
.scrub { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.75rem; font-size: 0.75rem; }
.scrub input { flex: 1; }
.meta-frame { margin: 0 0.75rem 0.65rem; font-size: 0.7rem; color: var(--color-muted); }
.empty { padding: 2rem 1rem; text-align: center; color: var(--color-muted); font-size: 0.85rem; }
.btn { border: none; border-radius: 8px; padding: 0.45rem 0.9rem; background: var(--color-primary); font-weight: 600; cursor: pointer; }
.state { padding: 2rem; text-align: center; color: var(--color-text-secondary); }
.state.error { color: #b91c1c; }
@media (max-width: 900px) {
  .bandas { grid-template-columns: 1fr; }
}
</style>
