<template>
  <div class="page">
    <header class="page-head">
      <h1>Calibración con dron</h1>
      <p>Perfil vertical → sesgo e(z) · decaimiento τ = 6 h</p>
    </header>

    <div class="controls">
      <label>
        Sitio
        <select v-model="sitioId">
          <option v-for="s in sitios" :key="s.slug" :value="s.slug">{{ s.nombre }}</option>
        </select>
      </label>
      <button type="button" class="btn" :disabled="loading" @click="correr">Aplicar perfil</button>
    </div>

    <label class="block">
      JSON perfil dron
      <textarea v-model="jsonText" rows="14" spellcheck="false"></textarea>
    </label>

    <div v-if="loading" class="state">Asimilando…</div>
    <div v-else-if="error" class="state error">{{ error }}</div>
    <div v-else-if="data" class="ok">
      <p>
        Sesgo calculado:
        <strong>{{ data.sesgo_dron_kmh != null ? data.sesgo_dron_kmh.toFixed(2) + ' km/h' : '—' }}</strong>
      </p>
      <p>Nivel máximo: {{ data.nivel_maximo_nombre }}</p>
      <pre class="resumen">{{ data.resumen_ejecutivo }}</pre>
    </div>
  </div>
</template>

<script setup>
import { inject, onMounted, ref } from 'vue'
import { fetchSpatiPronosticoConDron } from '@/services/spatiApi'

const site = inject('site')
const sitioId = ref(site.spatiDefaultSitio || 'escondida')
const sitios = ref(site.stations || [])
const loading = ref(false)
const error = ref(null)
const data = ref(null)

const ejemplo = {
  sitio_id: 'escondida',
  timestamp_vuelo: new Date().toISOString(),
  operador: 'piloto_demo',
  modelo_dron: 'DJI_M300_RTK',
  niveles: [
    { altura_m: 10, velocidad_kmh: 18.5, direccion_deg: 185 },
    { altura_m: 25, velocidad_kmh: 22.1, direccion_deg: 188 },
    { altura_m: 55, velocidad_kmh: 29.0, direccion_deg: 191 },
    { altura_m: 100, velocidad_kmh: 31.2, direccion_deg: 192 },
  ],
}
const jsonText = ref(JSON.stringify(ejemplo, null, 2))

async function correr() {
  loading.value = true
  error.value = null
  data.value = null
  try {
    const perfil = JSON.parse(jsonText.value)
    data.value = await fetchSpatiPronosticoConDron(sitioId.value, perfil, 6)
  } catch (e) {
    error.value = e?.message || 'Error'
  } finally {
    loading.value = false
  }
}

onMounted(() => {})
</script>

<style scoped>
.page { max-width: 800px; margin: 0 auto; padding: 1.25rem; }
.page-head h1 { margin: 0 0 0.35rem; }
.page-head p { margin: 0; color: var(--color-muted); }
.controls { display: flex; gap: 0.75rem; align-items: end; margin: 1rem 0; }
.controls label, .block { display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.85rem; width: 100%; }
textarea { font-family: ui-monospace, monospace; font-size: 0.8rem; padding: 0.75rem; border-radius: var(--radius-md); border: 1px solid var(--color-border); background: var(--color-surface); color: var(--color-text); }
.btn { padding: 0.5rem 1rem; border: none; border-radius: var(--radius-md); background: var(--color-primary); color: #0b1120; font-weight: 600; cursor: pointer; }
.state.error { color: #fca5a5; }
.resumen { white-space: pre-wrap; background: var(--color-surface); border: 1px solid var(--color-border); padding: 0.75rem; border-radius: var(--radius-md); font-size: 0.85rem; }
select { padding: 0.45rem; border-radius: var(--radius-md); border: 1px solid var(--color-border); background: var(--color-surface); color: var(--color-text); }
</style>
