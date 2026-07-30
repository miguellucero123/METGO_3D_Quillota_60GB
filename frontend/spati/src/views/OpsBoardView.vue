<template>
  <div class="page">
    <header class="page-head">
      <div>
        <p class="eyebrow">M10 · Operaciones</p>
        <h1>Board multi-faena</h1>
        <p class="sub">
          Nivel operativo (izaje · caminos · botaderos) y estado observado de tus minas.
        </p>
      </div>
      <div class="actions">
        <button type="button" class="btn btn-ghost" :disabled="loading" @click="cargar(false)">
          Actualizar
        </button>
        <button type="button" class="btn" :disabled="loading" @click="cargar(true)">
          Refrescar modelo
        </button>
        <router-link class="btn btn-ghost" to="/">Hub</router-link>
      </div>
    </header>

    <p v-if="meta" class="meta">
      {{ meta.n_faenas }} faenas · generado {{ meta.generado_en }}
      <span v-if="meta.live_usados">· live {{ meta.live_usados }}</span>
    </p>

    <div v-if="loading" class="state">Cargando board…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar(false)">Reintentar</button>
    </div>

    <div v-else class="table-wrap">
      <table class="board">
        <thead>
          <tr>
            <th>Faena</th>
            <th>Nivel</th>
            <th>Izaje</th>
            <th>Caminos</th>
            <th>Botaderos</th>
            <th>Ráfaga</th>
            <th>Observado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in filas" :key="row.faena_id">
            <td>
              <strong>{{ row.nombre || row.faena_id }}</strong>
              <span class="slug">{{ row.faena_id }}</span>
              <span v-if="row.degradado" class="tag warn">estimado</span>
            </td>
            <td>
              <span class="pill" :class="'nv-' + (row.nivel_global || 'sin_dato')">
                {{ row.nivel_global || '—' }}
              </span>
            </td>
            <td>
              <span class="pill sm" :class="'nv-' + nivelAct(row, 'izaje')">{{
                nivelAct(row, 'izaje')
              }}</span>
              <p class="raz">{{ razones(row, 'izaje') }}</p>
            </td>
            <td>
              <span class="pill sm" :class="'nv-' + nivelAct(row, 'caminos')">{{
                nivelAct(row, 'caminos')
              }}</span>
              <p class="raz">{{ razones(row, 'caminos') }}</p>
            </td>
            <td>
              <span class="pill sm" :class="'nv-' + nivelAct(row, 'botaderos')">{{
                nivelAct(row, 'botaderos')
              }}</span>
              <p class="raz">{{ razones(row, 'botaderos') }}</p>
            </td>
            <td class="num" :class="{ crit: isCrit(row.rafaga_10m_ms) }">
              {{ fmt(row.rafaga_10m_ms) }}
              <span class="unit">m/s</span>
            </td>
            <td>
              <span class="pill sm" :class="obsClass(row)">{{
                row.observado?.estado_mvo || '—'
              }}</span>
              <p class="raz">
                pares {{ row.observado?.aire_pares ?? '—' }} · IoT
                {{ row.observado?.iot_lecturas ?? '—' }}
              </p>
            </td>
            <td class="links">
              <router-link :to="row.enlace || `/f/${row.faena_id}/`">Panel</router-link>
              <router-link :to="row.enlace_ambiente || `/f/${row.faena_id}/ambiente`"
                >Ambiente</router-link
              >
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!filas.length" class="state">Sin faenas en el board.</p>
      <p v-if="nota" class="nota">{{ nota }}</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchOpsBoard, wakeApi } from '@/services/authApi'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const filas = ref([])
const meta = ref(null)
const nota = ref('')

function nivelAct(row, key) {
  return row?.[key]?.nivel || 'sin_dato'
}

function razones(row, key) {
  const r = row?.[key]?.razones || []
  return r.length ? r.join(', ') : ''
}

function fmt(v) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return Number(v).toFixed(1)
}

function isCrit(v) {
  try {
    return Number(v) >= 10
  } catch {
    return false
  }
}

function obsClass(row) {
  const e = row?.observado?.estado_mvo
  if (e === 'ok') return 'nv-verde'
  if (e === 'parcial') return 'nv-amarillo'
  if (e === 'error' || e === 'sin_datos') return 'nv-rojo'
  return 'nv-sin_dato'
}

async function cargar(refresh) {
  loading.value = true
  error.value = ''
  try {
    wakeApi().catch(() => {})
    const data = await fetchOpsBoard({ refresh: Boolean(refresh) })
    filas.value = data.filas || []
    meta.value = {
      n_faenas: data.n_faenas,
      generado_en: data.generado_en,
      live_usados: data.live_usados,
    }
    nota.value = data.nota || ''
  } catch (e) {
    if (e?.status === 403) {
      error.value =
        e.message || 'El board requiere admin, plan multi-faena o membresía en ≥2 faenas.'
      // Volver al hub tras un momento si es 403
      setTimeout(() => router.replace('/'), 2500)
    } else {
      error.value = e?.message || 'No se pudo cargar el board'
    }
    filas.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => cargar(false))
</script>

<style scoped>
.page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 1.25rem 1.25rem 2.5rem;
}
.page-head {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}
.eyebrow {
  margin: 0;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-muted);
}
.page-head h1 {
  margin: 0.15rem 0 0.35rem;
  font-size: 1.55rem;
}
.sub {
  margin: 0;
  color: var(--color-text-secondary);
  max-width: 36rem;
}
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.btn {
  padding: 0.45rem 0.85rem;
  border-radius: var(--radius-md);
  border: none;
  background: var(--color-primary);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}
.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.btn-ghost {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
}
.meta {
  font-size: 0.85rem;
  color: var(--color-muted);
  margin: 0 0 1rem;
}
.state {
  padding: 1.5rem 0;
  color: var(--color-text-secondary);
}
.state.error {
  color: #f87171;
}
.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}
.board {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
.board th,
.board td {
  padding: 0.7rem 0.75rem;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
  vertical-align: top;
}
.board th {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-muted);
  font-weight: 600;
  background: color-mix(in srgb, var(--color-surface) 90%, #000 4%);
}
.slug {
  display: block;
  font-size: 0.75rem;
  color: var(--color-muted);
}
.tag.warn {
  display: inline-block;
  margin-top: 0.25rem;
  font-size: 0.68rem;
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  background: #f59e0b22;
  color: #fbbf24;
  border: 1px solid #f59e0b55;
}
.pill {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.75rem;
}
.pill.sm {
  font-size: 0.7rem;
}
.nv-rojo {
  background: #ef444422;
  color: #f87171;
}
.nv-amarillo {
  background: #eab30822;
  color: #facc15;
}
.nv-verde {
  background: #22c55e22;
  color: #4ade80;
}
.nv-sin_dato,
.nv-neutro {
  background: #94a3b822;
  color: #94a3b8;
}
.raz {
  margin: 0.25rem 0 0;
  font-size: 0.72rem;
  color: var(--color-muted);
  max-width: 9rem;
}
.num {
  font-variant-numeric: tabular-nums;
  font-weight: 700;
  white-space: nowrap;
}
.num.crit {
  color: #f87171;
}
.unit {
  font-weight: 500;
  color: var(--color-muted);
  font-size: 0.75rem;
}
.links {
  white-space: nowrap;
}
.links a {
  display: block;
  color: var(--color-primary);
  font-size: 0.82rem;
  margin-bottom: 0.2rem;
}
.nota {
  margin: 0.75rem;
  font-size: 0.78rem;
  color: var(--color-muted);
}
@media (max-width: 800px) {
  .board th:nth-child(6),
  .board td:nth-child(6) {
    display: none;
  }
}
</style>
