<script setup>
defineProps({
  size: { type: String, default: 'md' }, // sm | md | lg
  label: { type: String, default: 'Helada' },
  showLabel: { type: Boolean, default: false },
})
</script>

<template>
  <div class="frost-badge" :class="`frost-badge--${size}`" role="img" :aria-label="label">
    <svg viewBox="0 0 64 64" class="frost-badge__icon" aria-hidden="true">
      <g class="frost-badge__crystal">
        <path
          d="M32 4 L32 60 M32 32 L8 18 M32 32 L56 18 M32 32 L8 46 M32 32 L56 46 M32 16 L20 32 M32 16 L44 32 M32 48 L20 32 M32 48 L44 32"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
        />
        <circle cx="32" cy="32" r="4" fill="currentColor" />
      </g>
    </svg>
    <span v-if="showLabel" class="frost-badge__text">{{ label }}</span>
  </div>
</template>

<style scoped>
.frost-badge {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  color: var(--color-sky-deep);
}
.frost-badge__icon {
  width: 2rem;
  height: 2rem;
  filter: drop-shadow(0 2px 6px rgba(91, 155, 213, 0.35));
}
.frost-badge--sm .frost-badge__icon {
  width: 1.25rem;
  height: 1.25rem;
}
.frost-badge--lg .frost-badge__icon {
  width: 3.5rem;
  height: 3.5rem;
}
.frost-badge__crystal {
  animation: frost-shimmer 3s ease-in-out infinite;
  transform-origin: center;
}
.frost-badge__text {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-sky-deep);
}
@keyframes frost-shimmer {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.88;
    transform: scale(1.04) rotate(4deg);
  }
}
</style>
