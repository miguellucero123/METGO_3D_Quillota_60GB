<script setup>
import { computed } from 'vue'
import { riegoColor } from '@/utils/agroColors'

const props = defineProps({
  datos: { type: Array, default: () => [] },
})

const maxMm = computed(() => Math.max(1, ...props.datos.map((d) => Number(d.mm) || 0)))
</script>

<template>
  <div class="riego-bars">
    <div v-for="d in datos" :key="d.slug" class="riego-row">
      <span class="riego-label">{{ d.label }}</span>
      <div class="riego-track">
        <div
          class="riego-fill"
          :style="{
            width: `${Math.max(8, ((Number(d.mm) || 0) / maxMm) * 100)}%`,
            background: riegoColor(d.mm),
          }"
        >
          {{ d.mm }} mm
        </div>
      </div>
    </div>
    <p v-if="!datos.length" class="muted">Sin datos de riego.</p>
  </div>
</template>

<style scoped>
.riego-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.riego-row {
  display: grid;
  grid-template-columns: 88px 1fr;
  align-items: center;
  gap: 8px;
}
.riego-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}
.riego-track {
  height: 22px;
  background: var(--color-primary-subtle);
  border-radius: 4px;
  overflow: hidden;
}
.riego-fill {
  height: 100%;
  min-width: 2.5rem;
  display: flex;
  align-items: center;
  padding: 0 8px;
  font-size: 11px;
  font-weight: 600;
  color: #0f3d2e;
  border-radius: 4px;
  transition: width 0.35s ease;
}
.muted {
  font-size: 0.85rem;
  color: var(--color-muted);
}
</style>
