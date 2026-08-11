<script setup>
import { computed } from 'vue'
import { AlertTriangle, Leaf, Snowflake, CloudRain } from 'lucide-vue-next'

const props = defineProps({
  /** Alertas API (`generar_alertas` / combinadas) */
  alertas: { type: Array, default: () => [] },
  /** Recomendaciones módulo 02 */
  recomendaciones: { type: Array, default: () => [] },
  /** Resumen meteo (para helada local) */
  resumen: { type: Object, default: null },
  cultivo: { type: String, default: 'palto' },
  loading: { type: Boolean, default: false },
})

const items = computed(() => {
  const out = []
  const tMin = props.resumen?.temperatura_min
  if (tMin != null && Number(tMin) <= 7) {
    const nivel = Number(tMin) <= 0 ? 'critico' : Number(tMin) <= 3 ? 'alto' : 'moderado'
    out.push({
      id: 'helada-local',
      tipo: 'helada',
      nivel,
      titulo: `Riesgo helada · T° mín ${tMin}°C`,
      detalle: `Cultivo ${props.cultivo}: revisar protección térmica y riego por aspersión.`,
      origen: 'resumen_meteo',
    })
  }
  for (const a of props.alertas || []) {
    out.push({
      id: `alerta-${a.id ?? a.mensaje}`,
      tipo: 'alerta',
      nivel: a.nivel === 'warning' || a.nivel === 'danger' ? 'alto' : a.nivel || 'info',
      titulo: a.mensaje || a.titulo || 'Alerta meteorológica',
      detalle: a.estacion_id ? `Estación: ${a.estacion_id}` : '',
      origen: 'generar_alertas',
    })
  }
  for (const [i, r] of (props.recomendaciones || []).entries()) {
    out.push({
      id: `rec-${r.codigo || i}`,
      tipo: 'recomendacion',
      nivel: r.prioridad === 'alta' || r.nivel === 'alto' ? 'alto' : 'info',
      titulo: r.texto || r.accion || r.cultivo || 'Recomendación agrícola',
      detalle: r.motivo || r.codigo || '',
      origen: 'modulo_02',
    })
  }
  const orden = { critico: 0, alto: 1, warning: 1, danger: 1, moderado: 2, info: 3 }
  return out.sort((a, b) => (orden[a.nivel] ?? 9) - (orden[b.nivel] ?? 9))
})

function iconFor(tipo) {
  if (tipo === 'helada') return Snowflake
  if (tipo === 'alerta') return AlertTriangle
  if (tipo === 'recomendacion') return Leaf
  return CloudRain
}
</script>

<template>
  <div class="ops-tl">
    <div class="ops-head">
      <h3 class="ops-title">Timeline operativa</h3>
      <p class="ops-meta">Alertas API + heladas + recomendaciones módulo 02</p>
    </div>
    <div v-if="loading" class="muted">Cargando timeline…</div>
    <ul v-else-if="items.length" class="ops-list">
      <li
        v-for="it in items"
        :key="it.id"
        class="ops-item"
        :class="`ops-item--${it.nivel}`"
      >
        <component :is="iconFor(it.tipo)" class="ops-icon" :size="16" aria-hidden="true" />
        <div class="ops-body">
          <p class="ops-item-title">{{ it.titulo }}</p>
          <p v-if="it.detalle" class="ops-item-detail">{{ it.detalle }}</p>
          <span class="ops-origen">{{ it.origen }} · {{ it.tipo }}</span>
        </div>
      </li>
    </ul>
    <p v-else class="muted">Sin alertas ni recomendaciones activas.</p>
  </div>
</template>

<style scoped>
.ops-tl {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.ops-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
}
.ops-meta {
  margin: 0.2rem 0 0;
  font-size: 0.75rem;
  color: var(--color-muted);
}
.ops-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.ops-item {
  display: flex;
  gap: 0.65rem;
  padding: 0.65rem 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}
.ops-item--critico,
.ops-item--alto {
  border-color: #f09595;
  background: #fcebeb;
}
.ops-item--moderado {
  border-color: #fac775;
  background: #faeeda;
}
.ops-icon {
  flex-shrink: 0;
  margin-top: 2px;
}
.ops-item-title {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 600;
}
.ops-item-detail {
  margin: 0.2rem 0 0;
  font-size: 0.78rem;
  color: var(--color-text-secondary, #555);
}
.ops-origen {
  display: inline-block;
  margin-top: 0.25rem;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-muted);
}
.muted {
  color: var(--color-muted);
  font-size: 0.85rem;
}
</style>
