<script setup>
defineProps({
  height: { type: [Number, String], default: 120 },
  lines: { type: Number, default: 0 },
})
</script>

<template>
  <div class="skel" :style="{ minHeight: typeof height === 'number' ? `${height}px` : height }">
    <div v-if="!lines" class="skel-block" />
    <template v-else>
      <div v-for="n in lines" :key="n" class="skel-line" :style="{ width: `${55 + (n * 11) % 40}%` }" />
    </template>
  </div>
</template>

<style scoped>
.skel {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  justify-content: center;
}
.skel-block,
.skel-line {
  background: linear-gradient(90deg, #e8ecef 25%, #f4f6f8 50%, #e8ecef 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease infinite;
  border-radius: 6px;
}
.skel-block {
  height: 100%;
  min-height: 4rem;
}
.skel-line {
  height: 0.85rem;
}
@keyframes shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}
</style>
