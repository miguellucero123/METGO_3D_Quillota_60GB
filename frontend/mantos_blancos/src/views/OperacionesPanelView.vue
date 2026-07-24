<template>
  <div class="page">
    <header class="page-head">
      <h1>Panel de turno</h1>
      <p>{{ site.tagline }} · semáforo por actividad (tronadura · transporte · izaje)</p>
    </header>

    <div class="controls">
      <div class="tabs">
        <button type="button" :class="['tab', { active: turno === 'dia' }]" @click="cambiarTurno('dia')">
          Turno día (07–19)
        </button>
        <button type="button" :class="['tab', { active: turno === 'noche' }]" @click="cambiarTurno('noche')">
          Turno noche (19–07)
        </button>
      </div>
    </div>

    <div v-if="loading" class="state">Evaluando ventanas del turno…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>

    <template v-else>
      <AlertaTurnoBanner :alerta="alerta" :turno="turno" />

      <section v-if="alerta" class="resumen">
        <div class="resumen-item">
          <span>Ventana</span>
          <strong>{{ formatearRango(alerta.desde, alerta.hasta) }}</strong>
        </div>
        <div class="resumen-item">
          <span>Estado</span>
          <strong :class="alerta.hay_bloqueo ? 's-rojo' : 's-verde'">
            {{ alerta.hay_bloqueo ? 'Hay bloqueos' : 'Sin bloqueos críticos' }}
          </strong>
        </div>
        <div class="resumen-item">
          <span>Puntos</span>
          <strong>{{ alerta.estaciones?.length || 0 }} / {{ site.stations.length }}</strong>
        </div>
        <div v-if="so2Resumen != null" class="resumen-item">
          <span>SO₂ (CAMS)</span>
          <strong>{{ so2Resumen }} µg/m³</strong>
        </div>
      </section>

      <section class="puntos">
        <h2>Puntos de faena</h2>
        <div class="grid">
          <PuntoFaenaCard
            v-for="p in puntos"
            :key="p.slug"
            :nombre="p.nombre"
            :descripcion="p.descripcion"
            :nivel="p.nivel"
            :actividades="p.actividades"
            :active="p.slug === slugActivo"
            @select="slugActivo = p.slug"
          />
        </div>
      </section>

      <section v-if="detalle" class="detalle">
        <h2>{{ detalle.nombre }}</h2>
        <table class="data-table">
          <thead>
            <tr>
              <th>Actividad</th>
              <th>Peor nivel</th>
              <th>Horas rojo</th>
              <th>Horas amarillo</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="act in detalle.actividades" :key="act.id">
              <td>{{ act.label }}</td>
              <td :class="`s-${act.nivel}`">{{ etiquetaNivel(act.nivel) }}</td>
              <td>{{ act.horas_rojo }}</td>
              <td>{{ act.horas_amarillo }}</td>
              <td>{{ act.bloqueada ? 'Bloqueada' : 'Operable' }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <p class="fuente">
        Umbrales conservadores (viento / ráfaga / visibilidad / precipitación). Fuente: Open-Meteo Forecast.
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import AlertaTurnoBanner from '@/components/operaciones/AlertaTurnoBanner.vue'
import PuntoFaenaCard from '@/components/operaciones/PuntoFaenaCard.vue'
import { wakeApi, fetchAlertasTurno } from '@/services/operacionesApi'

const ACTIVIDADES = [
  { id: 'tronadura', label: 'Tronadura' },
  { id: 'transporte', label: 'Transporte' },
  { id: 'izaje', label: 'Izaje' },
  { id: 'exposicion_uv', label: 'Exposición UV' },
]

const site = inject('site')
const loading = ref(true)
const error = ref(null)
const turno = ref('dia')
const alerta = ref(null)
const slugActivo = ref(site.stations[0]?.slug || 'mb_rajo')

const puntos = computed(() =>
  site.stations.map((s) => {
    const est = (alerta.value?.estaciones || []).find((e) => e.estacion_id === s.slug)
    const acts = ACTIVIDADES.map((a) => {
      const raw = est?.actividades?.[a.id]
      return {
        id: a.id,
        label: a.label,
        nivel: raw?.nivel_peor || 'verde',
        horas_rojo: raw?.horas_rojo ?? 0,
        horas_amarillo: raw?.horas_amarillo ?? 0,
        bloqueada: !!raw?.bloqueada,
      }
    })
    return {
      slug: s.slug,
      nombre: s.nombre,
      descripcion: s.descripcion,
      nivel: est?.nivel_global || 'verde',
      actividades: acts,
    }
  })
)

const detalle = computed(() => puntos.value.find((p) => p.slug === slugActivo.value) || null)

const so2Resumen = computed(() => {
  const vals = (alerta.value?.estaciones || [])
    .map((e) => e.so2)
    .filter((v) => v != null)
  if (!vals.length) return null
  return Math.max(...vals)
})

function etiquetaNivel(n) {
  return { verde: 'Verde', amarillo: 'Amarillo', rojo: 'Rojo' }[n] || '—'
}

function formatearRango(desde, hasta) {
  if (!desde || !hasta) return '—'
  return `${String(desde).slice(0, 16).replace('T', ' ')} → ${String(hasta).slice(11, 16)}`
}

async function cambiarTurno(t) {
  turno.value = t
  await cargar()
}

async function cargar() {
  loading.value = true
  error.value = null
  try {
    await wakeApi()
    alerta.value = await fetchAlertasTurno(turno.value)
  } catch (err) {
    error.value =
      err?.status === 503
        ? 'Servicio de operaciones temporalmente no disponible.'
        : err?.message || 'No se pudo cargar el panel de turno'
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
.tabs { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.tab {
  padding: 0.5rem 0.95rem;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: 6px;
  cursor: pointer;
}
.tab.active {
  background: var(--color-primary-muted);
  color: var(--color-primary);
  border-color: var(--color-primary);
}
.resumen {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}
.resumen-item {
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.resumen-item span { font-size: 0.78rem; color: var(--color-text-secondary); text-transform: uppercase; }
.puntos h2, .detalle h2 { font-size: 1.1rem; margin: 0 0 0.75rem; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 0.85rem;
}
.detalle { margin-top: 1.5rem; }
.s-verde { color: var(--color-success); }
.s-amarillo { color: var(--color-warning); }
.s-rojo { color: var(--color-danger); }
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
