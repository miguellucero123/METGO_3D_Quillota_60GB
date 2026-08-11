<script setup>
import { computed } from 'vue'
import { CircleDollarSign, FileJson, Download } from 'lucide-vue-next'
import { exportarDatosJSON } from '@/utils/exportData'

const props = defineProps({
  economico: { type: Object, default: null },
  reporteAvanzado: { type: Object, default: null },
  estacionId: { type: String, default: 'quillota' },
  loading: { type: Boolean, default: false },
})

const ahorro = computed(() => props.economico?.ahorro_estimado_clp_mes)
const nota = computed(
  () =>
    props.economico?.nota ||
    props.economico?.resumen ||
    'Sin proyección económica cargada'
)
const fuente = computed(() => props.economico?.fuente || 'api/agricola/economico')

const resumenReporte = computed(() => {
  const r = props.reporteAvanzado
  if (!r || r.error) return null
  const keys = Object.keys(r).filter((k) => k !== 'error')
  return {
    claves: keys.length,
    preview: keys.slice(0, 6).join(', '),
  }
})

function exportarReporte() {
  if (!props.reporteAvanzado) return
  exportarDatosJSON(props.reporteAvanzado, `reporte_agricola_${props.estacionId}`)
}
</script>

<template>
  <div class="eco-panel">
    <div class="eco-block">
      <div class="eco-head">
        <CircleDollarSign :size="16" aria-hidden="true" />
        <h3>Análisis económico</h3>
      </div>
      <p v-if="loading" class="muted">Cargando…</p>
      <template v-else-if="economico">
        <p class="eco-nota">{{ nota }}</p>
        <p v-if="ahorro != null" class="eco-kpi">
          Ahorro estimado:
          <strong>{{ Number(ahorro).toLocaleString('es-CL') }} CLP/mes</strong>
        </p>
        <p class="eco-fuente">Fuente: {{ fuente }}</p>
      </template>
      <p v-else class="muted">Sin datos económicos (API `/agricola/.../economico`).</p>
    </div>

    <div class="eco-block">
      <div class="eco-head">
        <FileJson :size="16" aria-hidden="true" />
        <h3>Reporte módulo 02</h3>
      </div>
      <p v-if="loading" class="muted">Cargando…</p>
      <template v-else-if="resumenReporte">
        <p class="eco-nota">
          Reporte integral disponible ({{ resumenReporte.claves }} campos):
          {{ resumenReporte.preview }}…
        </p>
        <button type="button" class="btn-export" @click="exportarReporte">
          <Download :size="14" aria-hidden="true" /> Exportar JSON
        </button>
      </template>
      <p v-else class="muted">
        {{ reporteAvanzado?.error || 'Sin reporte avanzado.' }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.eco-panel {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
@media (max-width: 800px) {
  .eco-panel {
    grid-template-columns: 1fr;
  }
}
.eco-block {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.85rem 1rem;
  background: var(--color-surface);
}
.eco-head {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.5rem;
}
.eco-head h3 {
  margin: 0;
  font-size: 0.9rem;
}
.eco-nota {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-text-secondary, #444);
}
.eco-kpi {
  margin: 0.5rem 0 0;
  font-size: 0.9rem;
}
.eco-fuente {
  margin: 0.35rem 0 0;
  font-size: 0.7rem;
  color: var(--color-muted);
}
.btn-export {
  margin-top: 0.6rem;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  padding: 0.3rem 0.65rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  cursor: pointer;
}
.muted {
  color: var(--color-muted);
  font-size: 0.85rem;
}
</style>
