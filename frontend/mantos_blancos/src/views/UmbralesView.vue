<template>
  <div class="page">
    <header class="page-head">
      <h1>Umbrales operacionales</h1>
      <p>Límites (amarillo / rojo) por actividad — configurables por faena</p>
    </header>

    <div v-if="loading" class="state">Cargando umbrales desde la API…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>

    <template v-else>
      <p class="nota">{{ data?.nota }}</p>

      <section v-for="bloque in bloques" :key="bloque.id" class="bloque">
        <h2>{{ bloque.titulo }}</h2>
        <table class="data-table">
          <thead>
            <tr>
              <th>Variable</th>
              <th>Amarillo</th>
              <th>Rojo</th>
              <th>Unidad</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in bloque.filas" :key="row.clave">
              <td>{{ row.label }}</td>
              <td>{{ row.amarillo }}</td>
              <td>{{ row.rojo }}</td>
              <td>{{ row.unidad }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <p class="fuente">
        Fuente efectiva: <code>{{ data?.fuente }}</code>. Override en Render:
        <code>METGO_OP_UMBRALES_JSON</code>. Espejo local en <code>site.config.js</code>.
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { wakeApi, fetchUmbrales } from '@/services/operacionesApi'

const LABELS = {
  racha: 'Ráfaga',
  viento_sostenido: 'Viento sostenido',
  visibilidad: 'Visibilidad (inverso)',
  precipitacion: 'Precipitación',
  viento_min_dispersion: 'Viento mín. dispersión',
  uv_index: 'Índice UV',
  so2: 'SO₂',
}
const TITULOS = {
  tronadura: 'Tronadura',
  transporte: 'Transporte',
  izaje: 'Izaje',
  exposicion_uv: 'Exposición UV',
  so2: 'SO₂ (HSE / fundiciones)',
}

const loading = ref(true)
const error = ref(null)
const data = ref(null)

const bloques = computed(() => {
  const umb = data.value?.umbrales || {}
  const unidades = data.value?.unidades || {}
  return Object.keys(umb).map((id) => {
    const params = umb[id] || {}
    const filas = Object.entries(params).map(([clave, val]) => {
      const esPar = Array.isArray(val) && val.length >= 2
      return {
        clave,
        label: LABELS[clave] || clave,
        amarillo: esPar ? val[0] : val,
        rojo: esPar ? val[1] : '—',
        unidad: unidades[clave] || '',
      }
    })
    return { id, titulo: TITULOS[id] || id, filas }
  })
})

async function cargar() {
  loading.value = true
  error.value = null
  try {
    await wakeApi()
    data.value = await fetchUmbrales()
  } catch (err) {
    error.value = err?.message || 'No se pudieron cargar los umbrales'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.page { max-width: 900px; }
.page-head { margin-bottom: 1rem; }
.page-head h1 { margin: 0 0 0.25rem; font-size: 1.6rem; }
.page-head p { margin: 0; color: var(--color-text-secondary); }
.nota { font-size: 0.9rem; color: var(--color-text-secondary); margin-bottom: 1.25rem; }
.bloque { margin-bottom: 1.5rem; }
.bloque h2 { font-size: 1.05rem; margin: 0 0 0.5rem; color: var(--color-primary); }
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
.fuente code {
  font-size: 0.78rem;
  background: var(--color-surface);
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
}
</style>
