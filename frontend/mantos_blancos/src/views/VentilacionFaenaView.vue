<template>
  <div class="page">
    <header class="page-head">
      <h1>Ventilación faena · {{ site.faena?.nombre || site.siteLabel }}</h1>
      <p>
        Ventilación atmosférica · códigos
        <span class="badge N">N</span>
        <span class="badge R">R</span>
        <span class="badge M">M</span>
        · corridas 06 / 18 UTC
      </p>
    </header>

    <div class="actions">
      <button type="button" class="btn btn-ghost" @click="cargar" :disabled="loading">Actualizar</button>
    </div>

    <div v-if="loading" class="state">Calculando ventilación {{ site.faena?.nombre || 'faena' }}…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>

    <template v-else-if="pkg">
      <section class="meta-bar">
        <div>
          <span class="lbl">Corrida</span>
          <strong>{{ pkg.corrida_utc }} UTC</strong>
        </div>
        <div>
          <span class="lbl">Generado</span>
          <strong>{{ pkg.generado_en }}</strong>
        </div>
        <div>
          <span class="lbl">Próxima</span>
          <strong>{{ pkg.proxima_corrida_utc }} UTC</strong>
        </div>
        <div v-if="pkg.resumen_72h">
          <span class="lbl">72 h</span>
          <strong>
            N {{ pkg.resumen_72h.n }} · R {{ pkg.resumen_72h.r }} · M {{ pkg.resumen_72h.m }}
          </strong>
        </div>
      </section>

      <p class="sinop">
        Sinóptica:
        <strong>{{ (pkg.sinoptica_predominante || []).join(', ') || '—' }}</strong>
      </p>

      <div class="tabs">
        <button
          v-for="t in tabs"
          :key="t.id"
          type="button"
          :class="['tab', { active: tab === t.id }]"
          @click="tab = t.id"
        >
          {{ t.label }}
        </button>
      </div>

      <section v-show="tab === '72h'">
        <h2>Ventilación horaria (72 h)</h2>
        <div class="grid-codes" role="list">
          <div
            v-for="(f, i) in pkg.horaria || []"
            :key="i"
            class="cell"
            :class="f.ventilacion"
            role="listitem"
            :title="f.fecha_hora"
          >
            <span class="code">{{ f.ventilacion }}</span>
            <span class="hour">{{ horaCorta(f.fecha_hora) }}</span>
          </div>
        </div>
      </section>

      <section v-show="tab === 'tramos'">
        <h2>24 h · tramos 3 h</h2>
        <table class="tbl">
          <thead>
            <tr>
              <th>Inicio</th>
              <th>V</th>
              <th>Viento</th>
              <th>Nubosidad</th>
              <th>Cielo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(t, i) in pkg.tramos_3h_24h || []" :key="i">
              <td>{{ t.inicio }}</td>
              <td><span class="badge" :class="t.ventilacion">{{ t.ventilacion }}</span></td>
              <td>{{ t.viento_velocidad ?? '—' }} m/s · {{ t.viento_direccion ?? '—' }}°</td>
              <td>{{ t.nubosidad_baja ?? '—' }}%</td>
              <td>{{ t.icono }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section v-show="tab === '14d'">
        <h2>14 días</h2>
        <div class="dias">
          <article v-for="d in pkg.diaria || []" :key="d.fecha" class="dia-card">
            <header>
              <strong>{{ d.fecha }}</strong>
              <span class="badge" :class="d.ventilacion">{{ d.ventilacion }}</span>
            </header>
            <p class="icono">{{ iconoLabel(d.icono) }}</p>
            <p>{{ d.caracteristica }}</p>
          </article>
        </div>
      </section>

      <section v-show="tab === 'stm'">
        <h2>Proyección 30–90 días</h2>
        <p class="note">{{ pkg.proyeccion?.stm_nota }}</p>
        <table class="tbl">
          <thead>
            <tr>
              <th>Periodo</th>
              <th>V</th>
              <th>Viento superficie</th>
              <th>Confianza</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in pkg.proyeccion?.bloques || []" :key="b.periodo">
              <td>{{ b.periodo }}</td>
              <td><span class="badge" :class="b.ventilacion">{{ b.ventilacion }}</span></td>
              <td>{{ b.viento_superficie_ms ?? '—' }} m/s</td>
              <td>{{ b.confianza }}</td>
            </tr>
          </tbody>
        </table>
        <div class="vientos-niveles" v-if="pkg.proyeccion?.vientos_predominantes">
          <h3>Vientos por nivel</h3>
          <pre>{{ JSON.stringify(pkg.proyeccion.vientos_predominantes, null, 2) }}</pre>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { inject, onMounted, ref } from 'vue'
import { fetchFaenaPaquete } from '@/services/aireApi'

const site = inject('site')
const loading = ref(true)
const error = ref(null)
const pkg = ref(null)
const tab = ref('72h')
const tabs = [
  { id: '72h', label: '72 h' },
  { id: 'tramos', label: '24 h / 3 h' },
  { id: '14d', label: '14 días' },
  { id: 'stm', label: '30–90 d' },
]

function horaCorta(ts) {
  if (!ts) return '—'
  const m = String(ts).match(/T(\d{2}):/)
  return m ? `${m[1]}h` : String(ts).slice(5, 13)
}

function iconoLabel(id) {
  const map = {
    despejado: 'Despejado',
    parcialmente_nublado: 'Parc. nublado',
    cubierto: 'Cubierto',
    niebla: 'Niebla',
    neblina: 'Neblina',
    lluvia: 'Lluvia',
  }
  return map[id] || id || '—'
}

async function cargar() {
  loading.value = true
  error.value = null
  try {
    pkg.value = await fetchFaenaPaquete()
  } catch (e) {
    error.value = e?.message || `No se pudo cargar ventilación ${site.faena?.nombre || 'faena'}`
    pkg.value = null
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.25rem 1.25rem 2.5rem;
}
.page-head h1 {
  margin: 0 0 0.35rem;
}
.page-head p {
  margin: 0;
  color: var(--color-text-secondary);
}
.badge {
  display: inline-block;
  min-width: 1.4rem;
  text-align: center;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-weight: 700;
  font-size: 0.8rem;
}
.N {
  background: #bbf7d0;
  color: #14532d;
}
.R {
  background: #fde68a;
  color: #78350f;
}
.M {
  background: #fecaca;
  color: #7f1d1d;
}
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1rem 0;
}
.btn {
  border: none;
  border-radius: 8px;
  padding: 0.45rem 0.9rem;
  background: var(--color-primary);
  color: #111;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
}
.btn-ghost {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
}
.meta-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
  padding: 0.85rem;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  background: var(--color-surface);
  margin-bottom: 0.75rem;
}
.lbl {
  display: block;
  font-size: 0.7rem;
  color: var(--color-muted);
}
.sinop {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}
.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin: 1rem 0;
}
.tab {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 8px;
  padding: 0.4rem 0.75rem;
  cursor: pointer;
}
.tab.active {
  background: var(--color-primary-muted);
  color: var(--color-primary);
  border-color: transparent;
}
.grid-codes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(44px, 1fr));
  gap: 0.35rem;
}
.cell {
  border-radius: 6px;
  padding: 0.35rem 0.2rem;
  text-align: center;
  font-size: 0.7rem;
}
.cell .code {
  display: block;
  font-weight: 800;
  font-size: 0.95rem;
}
.cell.N {
  background: #bbf7d0;
}
.cell.R {
  background: #fde68a;
}
.cell.M {
  background: #fecaca;
}
.tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.tbl th,
.tbl td {
  border: 1px solid var(--color-border);
  padding: 0.45rem 0.55rem;
  text-align: left;
}
.dias {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.65rem;
}
.dia-card {
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 0.75rem;
  background: var(--color-surface);
}
.dia-card header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.35rem;
}
.dia-card p {
  margin: 0.25rem 0 0;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}
.icono {
  font-weight: 600;
  color: var(--color-text) !important;
}
.note {
  font-size: 0.8rem;
  color: var(--color-muted);
}
.vientos-niveles pre {
  font-size: 0.75rem;
  overflow: auto;
  background: var(--color-surface);
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--color-border);
}
.state {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-secondary);
}
.state.error {
  color: #b91c1c;
}
h2 {
  font-size: 1rem;
  margin: 0 0 0.75rem;
}
</style>
