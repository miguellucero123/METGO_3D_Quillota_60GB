<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  /** { variable, actual, prediccion, unidad } */
})

const rows = computed(() =>
  (props.items || []).filter((r) => r.prediccion != null && !Number.isNaN(Number(r.prediccion)))
)

const maxVal = computed(() => {
  const nums = rows.value.flatMap((r) => [Number(r.actual), Number(r.prediccion)].filter((n) => !Number.isNaN(n)))
  return Math.max(...nums, 1)
})

function pct(v) {
  return `${(Number(v) / maxVal.value) * 100}%`
}
</script>

<template>
  <div v-if="rows.length" class="ml-projection" role="img" aria-label="Proyecciones ML vs valor actual">
    <div class="ml-projection__legend">
      <span><i class="dot dot--actual" /> Actual</span>
      <span><i class="dot dot--pred" /> Modelo ML</span>
    </div>
    <div v-for="row in rows" :key="row.variable" class="ml-projection__row">
      <span class="ml-projection__label" :title="row.variable">{{ row.label || row.variable }}</span>
      <div class="ml-projection__bars">
        <div class="ml-projection__track">
          <div class="ml-projection__fill ml-projection__fill--actual" :style="{ width: pct(row.actual) }" />
        </div>
        <div class="ml-projection__track">
          <div class="ml-projection__fill ml-projection__fill--pred" :style="{ width: pct(row.prediccion) }" />
        </div>
      </div>
      <span class="ml-projection__vals">
        {{ row.actual ?? '—' }} → {{ Number(row.prediccion).toFixed(1) }}{{ row.unidad || '' }}
      </span>
    </div>
  </div>
  <p v-else class="muted">Sin proyecciones ML disponibles.</p>
</template>

<style scoped>
.ml-projection {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}
.ml-projection__legend {
  display: flex;
  gap: 1rem;
  font-size: 0.7rem;
  color: var(--color-muted);
}
.dot {
  display: inline-block;
  width: 0.55rem;
  height: 0.55rem;
  border-radius: 2px;
  margin-right: 0.25rem;
  vertical-align: middle;
}
.dot--actual {
  background: var(--color-primary);
}
.dot--pred {
  background: var(--color-sky);
}
.ml-projection__row {
  display: grid;
  grid-template-columns: 5.5rem 1fr 5.5rem;
  gap: 0.5rem;
  align-items: center;
  font-size: 0.72rem;
}
.ml-projection__label {
  color: var(--color-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ml-projection__bars {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.ml-projection__track {
  height: 0.45rem;
  background: var(--color-border);
  border-radius: 4px;
  overflow: hidden;
}
.ml-projection__fill {
  height: 100%;
  border-radius: 4px;
  min-width: 2px;
  transition: width 0.25s ease;
}
.ml-projection__fill--actual {
  background: var(--color-primary);
}
.ml-projection__fill--pred {
  background: var(--color-sky);
}
.ml-projection__vals {
  text-align: right;
  font-variant-numeric: tabular-nums;
  color: var(--color-text-secondary);
  font-size: 0.68rem;
}
.muted {
  color: var(--color-muted);
  font-size: 0.8rem;
}
</style>
