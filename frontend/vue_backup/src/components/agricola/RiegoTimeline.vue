<script setup>
import { computed } from 'vue'
import { Download } from 'lucide-vue-next'
import { exportarDatosCSV } from '@/utils/exportData'

const props = defineProps({
  cronograma: { type: Array, default: () => [] },
  cultivoLabel: { type: String, default: 'Palto' },
  loading: { type: Boolean, default: false },
})

const filas = computed(() =>
  (props.cronograma || []).map((d) => ({
    ...d,
    esHoy: d.es_hoy ?? d.esHoy ?? false,
  }))
)

function formatFecha(fechaStr) {
  if (!fechaStr) return '—'
  const d = new Date(`${String(fechaStr).slice(0, 10)}T12:00:00`)
  return d.toLocaleDateString('es-CL', { weekday: 'short', day: 'numeric', month: 'short' })
}

function barClass(dia) {
  if (!dia.regar) return 'bar-suspender'
  if (dia.lluvia > 0) return 'bar-lluvia'
  return 'bar-riego'
}

function barWidth(dia) {
  if (!dia.regar) return 100
  const max = 10
  return Math.max(20, Math.min(100, ((dia.mm_sugeridos || 0) / max) * 100))
}

function barLabel(dia) {
  if (!dia.regar && String(dia.razon || '').toLowerCase().includes('helada')) {
    return `Suspendido · Helada ${dia.t_min}°C`
  }
  if (!dia.regar && dia.lluvia > 0) return `Lluvia esperada · ${dia.lluvia} mm`
  return `Riego · ${dia.mm_sugeridos} mm`
}

function badgeClass(dia) {
  if (!dia.regar && String(dia.razon || '').toLowerCase().includes('helada')) return 'badge-danger'
  if (!dia.regar && dia.lluvia > 0) return 'badge-info'
  return 'badge-success'
}

function badgeLabel(dia) {
  if (!dia.regar && String(dia.razon || '').toLowerCase().includes('helada')) return 'Suspender'
  if (!dia.regar && dia.lluvia > 0) return 'Lluvia cubre'
  return `Regar ${dia.mm_sugeridos} mm`
}

function exportar() {
  exportarDatosCSV(filas.value, `cronograma-riego-${props.cultivoLabel.toLowerCase()}`)
}
</script>

<template>
  <div class="timeline-wrap">
    <div class="tl-header">
      <div>
        <h3 class="tl-title">Cronograma de riego — {{ cultivoLabel }}</h3>
        <p class="tl-meta">Próximos 7 días · Ajustado por helada y pronóstico lluvia</p>
      </div>
      <button type="button" class="export-btn" title="Exportar CSV" @click="exportar">
        <Download :size="14" aria-hidden="true" /> CSV
      </button>
    </div>

    <div v-if="loading" class="tl-skeleton">
      <div v-for="i in 7" :key="i" class="tl-skeleton-row" />
    </div>

    <div v-else-if="filas.length" class="tl-grid">
      <div class="tl-head-row">
        <span>Fecha</span>
        <span>Estado</span>
        <span>Acción</span>
      </div>
      <div
        v-for="dia in filas"
        :key="dia.fecha"
        class="tl-row"
        :class="{ 'tl-row-today': dia.esHoy }"
      >
        <span class="tl-date">
          {{ formatFecha(dia.fecha) }}
          <span v-if="dia.esHoy" class="tl-today-badge">Hoy</span>
        </span>

        <div class="tl-bar-wrap">
          <div class="tl-bar" :class="barClass(dia)" :style="{ width: barWidth(dia) + '%' }">
            {{ barLabel(dia) }}
          </div>
        </div>

        <span class="tl-badge" :class="badgeClass(dia)">{{ badgeLabel(dia) }}</span>
      </div>
    </div>
    <p v-else class="muted">Sin cronograma disponible (verifique la API).</p>
  </div>
</template>

<style scoped>
.timeline-wrap {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.tl-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}
.tl-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}
.tl-meta {
  margin: 3px 0 0;
  font-size: 11px;
  color: var(--color-muted);
}
.export-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  font-size: 11px;
  cursor: pointer;
  background: var(--color-surface);
  color: var(--color-muted);
}
.tl-grid {
  display: flex;
  flex-direction: column;
}
.tl-head-row {
  display: grid;
  grid-template-columns: 100px 1fr 108px;
  gap: 8px;
  padding: 4px 0;
  font-size: 10px;
  font-weight: 600;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 4px;
}
.tl-row {
  display: grid;
  grid-template-columns: 100px 1fr 108px;
  align-items: center;
  gap: 8px;
  padding: 5px 0;
  border-bottom: 1px solid var(--color-border);
}
.tl-row:last-child {
  border-bottom: none;
}
.tl-row-today {
  background: var(--color-primary-subtle);
  border-radius: 4px;
  padding: 5px 6px;
}
.tl-date {
  font-size: 11px;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}
.tl-today-badge {
  font-size: 9px;
  padding: 1px 5px;
  border-radius: 100px;
  background: var(--color-info-bg);
  color: var(--color-info);
}
.tl-bar-wrap {
  height: 18px;
  background: var(--color-primary-subtle);
  border-radius: 4px;
  overflow: hidden;
}
.tl-bar {
  height: 100%;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding-left: 6px;
  font-size: 10px;
  font-weight: 600;
  white-space: nowrap;
  min-width: 30px;
  transition: width 0.4s ease;
}
.bar-riego {
  background: #5dcaa5;
  color: #085041;
}
.bar-suspender {
  background: #f7c1c1;
  color: #791f1f;
}
.bar-lluvia {
  background: #85b7eb;
  color: #0c447c;
}
.tl-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 100px;
  white-space: nowrap;
  text-align: center;
}
.badge-success {
  background: #eaf3de;
  color: #3b6d11;
}
.badge-danger {
  background: #fcebeb;
  color: #a32d2d;
}
.badge-info {
  background: #e6f1fb;
  color: #185fa5;
}
.tl-skeleton-row {
  height: 24px;
  background: var(--color-primary-subtle);
  border-radius: 4px;
  margin-bottom: 4px;
  animation: pulse 1.4s ease-in-out infinite;
}
.muted {
  color: var(--color-muted);
  font-size: 0.85rem;
}
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.45;
  }
}
</style>
