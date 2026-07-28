<template>
  <div class="page">
    <header class="page-head">
      <h1>Olas de calor</h1>
      <p>Percentil 90 climatológico (Archive) · otoño / invierno · faena {{ site.faena?.nombre || site.siteLabel }}</p>
    </header>

    <div class="controls">
      <label>
        Estación
        <select v-model="estacion">
          <option v-for="est in site.stations" :key="est.slug" :value="est.slug">
            {{ est.nombre }}
          </option>
        </select>
      </label>
      <label>
        Estación del año
        <select v-model="estacionAno">
          <option value="otono">Otoño (MAM)</option>
          <option value="invierno">Invierno (JJA)</option>
          <option value="todas">Todas</option>
        </select>
      </label>
      <button type="button" class="btn" @click="cargar" :disabled="loading">Calcular</button>
    </div>

    <div v-if="loading" class="state">Analizando histórico (~7 años)…</div>
    <div v-else-if="error" class="state error">{{ error }}</div>
    <template v-else-if="data">
      <div class="alerta" v-if="data.alerta_reciente" role="alert">
        Señal reciente: {{ data.dias_sobre_umbral_14d }} día(s) sobre umbral P90 en 14 d.
      </div>
      <section class="meta">
        <div><span>Eventos</span><strong>{{ data.n_eventos }}</strong></div>
        <div>
          <span>Definición</span>
          <strong>P{{ data.definicion?.percentil }} · ≥{{ data.definicion?.min_dias_consecutivos }} d · +{{ data.definicion?.anomalia_min_c }} °C</strong>
        </div>
        <div>
          <span>Histórico</span>
          <strong>{{ data.historico?.n ?? '—' }} días</strong>
        </div>
      </section>
      <table class="tbl" v-if="(data.eventos || []).length">
        <thead>
          <tr>
            <th>Inicio</th>
            <th>Fin</th>
            <th>Días</th>
            <th>Tmáx</th>
            <th>Anom.</th>
            <th>Intensidad</th>
            <th>Noche cálida</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(e, i) in data.eventos" :key="i">
            <td>{{ e.inicio }}</td>
            <td>{{ e.fin }}</td>
            <td>{{ e.duracion_dias }}</td>
            <td>{{ e.tmax_max }} °C</td>
            <td>+{{ e.anomalia_media }} °C</td>
            <td><span class="tag" :class="e.intensidad">{{ e.intensidad }}</span></td>
            <td>{{ e.noche_calida ? 'sí' : 'no' }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="state">Sin eventos que cumplan la definición en el periodo.</p>
    </template>
  </div>
</template>

<script setup>
import { inject, onMounted, ref, watch } from 'vue'
import { fetchOlasCalor, ESTACION_ANCLA } from '@/services/aireApi'

const site = inject('site')
const estacion = ref(site.faena?.estacionAncla || ESTACION_ANCLA)
const estacionAno = ref('otono')
const loading = ref(false)
const error = ref(null)
const data = ref(null)

async function cargar() {
  loading.value = true
  error.value = null
  try {
    data.value = await fetchOlasCalor({
      estacion: estacion.value,
      estacionAno: estacionAno.value,
      anios: 7,
    })
  } catch (e) {
    error.value = e?.message || 'No se pudo calcular olas de calor'
    data.value = null
  } finally {
    loading.value = false
  }
}

watch([estacion, estacionAno], cargar)
onMounted(cargar)
</script>

<style scoped>
.page { max-width: 960px; margin: 0 auto; padding: 1.25rem; }
.page-head h1 { margin: 0 0 0.35rem; }
.page-head p { margin: 0; color: var(--color-text-secondary); }
.controls { display: flex; flex-wrap: wrap; gap: 0.85rem; align-items: end; margin: 1rem 0; }
.controls label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.85rem; }
.controls select { padding: 0.4rem 0.55rem; border-radius: 8px; border: 1px solid var(--color-border); }
.btn { border: none; border-radius: 8px; padding: 0.45rem 0.9rem; background: var(--color-primary); font-weight: 600; cursor: pointer; }
.meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.75rem; margin-bottom: 1rem; }
.meta span { display: block; font-size: 0.7rem; color: var(--color-muted); }
.alerta { background: #fef3c7; border: 1px solid #f59e0b; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.85rem; }
.tbl { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.tbl th, .tbl td { border: 1px solid var(--color-border); padding: 0.45rem 0.55rem; text-align: left; }
.tag { padding: 0.15rem 0.45rem; border-radius: 4px; font-weight: 600; font-size: 0.75rem; }
.tag.leve { background: #fde68a; }
.tag.moderada { background: #fdba74; }
.tag.fuerte { background: #fca5a5; }
.state { padding: 1.5rem; text-align: center; color: var(--color-text-secondary); }
.state.error { color: #b91c1c; }
</style>
