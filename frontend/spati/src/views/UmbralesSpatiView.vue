<template>
  <div class="page">
    <header class="page-head">
      <h1>Umbrales SPATI</h1>
      <p>
        Escalafón operacional de izaje
        <span v-if="sitioId">· {{ sitioId }}</span>
        <span v-if="fuente" class="muted"> ({{ fuente }})</span>
      </p>
    </header>

    <label class="field">
      Sitio
      <select v-model="sitioId" @change="cargar">
        <option v-for="s in sitios" :key="s.sitio_id" :value="s.sitio_id">
          {{ s.nombre }}
        </option>
      </select>
    </label>

    <p v-if="error" class="err">{{ error }}</p>
    <p v-else-if="loading" class="muted">Cargando umbrales…</p>

    <table v-else class="tbl">
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
          <td>≥ {{ umb.rojo_min_kmh ?? 35 }} km/h (flag {{ umb.flag_critico_kmh ?? 36 }})</td>
          <td>&gt; {{ umb.fuerza_rojo_pct ?? 80 }}%</td>
          <td>Parada obligatoria · asegurar pluma</td>
        </tr>
      </tbody>
    </table>
    <p class="nota">
      {{ umb.nota || 'Flag secundario: rayos / precipitación elevan al menos a Naranja. Física: F = ½ ρ v² A Cd.' }}
      <span v-if="alertas"> · Alertas desde nivel {{ alertas.nivel_minimo ?? 2 }}.</span>
    </p>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { fetchSpatiSitios, fetchSpatiUmbrales } from '@/services/spatiApi'
import site from '@/site.config'

const sitios = ref([])
const sitioId = ref(site.spatiDefaultSitio || 'escondida')
const umb = ref({})
const alertas = ref(null)
const fuente = ref('')
const loading = ref(false)
const error = ref('')

function rango(arr) {
  if (!Array.isArray(arr) || arr.length < 2) return '—'
  return `${arr[0]} – ${arr[1]}`
}

async function cargarSitios() {
  try {
    sitios.value = await fetchSpatiSitios({ altaMontana: false })
    if (!sitios.value.find((s) => s.sitio_id === sitioId.value) && sitios.value[0]) {
      sitioId.value = sitios.value[0].sitio_id
    }
  } catch {
    sitios.value = [{ sitio_id: sitioId.value, nombre: sitioId.value }]
  }
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchSpatiUmbrales(sitioId.value)
    umb.value = data.umbrales || {}
    alertas.value = data.alertas || null
    fuente.value = umb.value.fuente || ''
  } catch (e) {
    error.value = e?.message || 'No se pudieron cargar umbrales'
    umb.value = {}
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await cargarSitios()
  await cargar()
})
</script>

<style scoped>
.page { max-width: 800px; margin: 0 auto; padding: 1.25rem; }
.page-head h1 { margin: 0 0 0.35rem; }
.page-head p { margin: 0 0 1rem; color: var(--color-muted); }
.field { display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 1rem; font-size: 0.85rem; color: var(--color-muted); }
.field select {
  max-width: 20rem;
  padding: 0.45rem 0.6rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
}
.tbl { width: 100%; border-collapse: collapse; border: 1px solid var(--color-border); border-radius: var(--radius-md); overflow: hidden; }
.tbl th, .tbl td { padding: 0.65rem 0.75rem; text-align: left; border-bottom: 1px solid var(--color-border); font-size: 0.9rem; }
.tbl th { background: var(--color-surface); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--color-muted); }
.n0 td:first-child { color: #86efac; font-weight: 600; }
.n1 td:first-child { color: #fde68a; font-weight: 600; }
.n2 td:first-child { color: #fdba74; font-weight: 600; }
.n3 td:first-child { color: #fca5a5; font-weight: 600; }
.nota { margin-top: 1rem; color: var(--color-muted); font-size: 0.9rem; line-height: 1.5; }
.muted { color: var(--color-muted); }
.err { color: var(--color-danger); }
</style>
