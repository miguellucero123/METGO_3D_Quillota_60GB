<script setup>
defineProps({
  x: { type: Number, default: 0 },
  y: { type: Number, default: 0 },
  visible: { type: Boolean, default: false },
})
</script>

<template>
  <div
    v-if="visible"
    class="chart-tip"
    :style="{ left: `${x}px`, top: `${y}px` }"
    role="tooltip"
  >
    <slot />
  </div>
</template>

<style scoped>
.chart-tip {
  position: fixed;
  z-index: 9999;
  pointer-events: none;
  transform: translate(-50%, calc(-100% - 10px));
  background: rgba(15, 23, 42, 0.92);
  color: #f8fafc;
  padding: 0.45rem 0.65rem;
  border-radius: 6px;
  font-size: 0.72rem;
  line-height: 1.35;
  max-width: 220px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
}
.chart-tip :deep(strong) {
  display: block;
  font-size: 0.78rem;
  margin-bottom: 0.15rem;
}
</style>
