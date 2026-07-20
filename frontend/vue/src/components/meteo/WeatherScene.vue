<script setup>
import { computed } from 'vue'
import { classifyWeather, WEATHER_LABELS } from '@/utils/weatherCondition'
import FrostBadge from '@/components/meteo/FrostBadge.vue'

const props = defineProps({
  datos: { type: Object, default: null },
  condition: { type: String, default: '' },
  compact: { type: Boolean, default: false },
})

const estado = computed(() => props.condition || classifyWeather(props.datos || {}))
const label = computed(() => WEATHER_LABELS[estado.value] || estado.value)
</script>

<template>
  <div
    class="weather-scene"
    :class="[`weather-scene--${estado}`, { 'weather-scene--compact': compact }]"
    role="img"
    :aria-label="label"
  >
    <div class="weather-scene__sky" />
    <div v-if="estado !== 'nublado' && estado !== 'lluvioso' && estado !== 'helada'" class="weather-scene__sun" />
    <div
      v-if="estado === 'parcial' || estado === 'nublado' || estado === 'lluvioso' || estado === 'helada'"
      class="weather-scene__cloud weather-scene__cloud--a"
    />
    <div
      v-if="estado === 'nublado' || estado === 'lluvioso' || estado === 'helada'"
      class="weather-scene__cloud weather-scene__cloud--b"
    />
    <div v-if="estado === 'lluvioso'" class="weather-scene__rain">
      <span v-for="n in 8" :key="n" class="weather-scene__drop" :style="{ '--i': n }" />
    </div>
    <FrostBadge v-if="estado === 'helada'" class="weather-scene__frost" size="lg" />
    <p class="weather-scene__label">{{ label }}</p>
  </div>
</template>

<style scoped>
.weather-scene {
  position: relative;
  width: 100%;
  max-width: 320px;
  height: 140px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: linear-gradient(180deg, var(--color-sky-light) 0%, var(--color-sky-muted) 100%);
  box-shadow: var(--shadow-sm);
}
.weather-scene--compact {
  max-width: 200px;
  height: 96px;
}
.weather-scene__sky {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, var(--color-sky-light) 40%, var(--color-primary-subtle) 100%);
}
.weather-scene--lluvioso .weather-scene__sky,
.weather-scene--nublado .weather-scene__sky,
.weather-scene--helada .weather-scene__sky {
  background: linear-gradient(180deg, #b8cfe0 0%, #dce8ef 55%, var(--color-primary-subtle) 100%);
}
.weather-scene__sun {
  position: absolute;
  top: 22px;
  right: 28px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #ffeaa7, #f4c430);
  box-shadow: 0 0 24px rgba(244, 196, 48, 0.45);
  animation: sun-pulse 4s ease-in-out infinite;
}
.weather-scene--compact .weather-scene__sun {
  width: 36px;
  height: 36px;
  top: 14px;
  right: 18px;
}
.weather-scene__cloud {
  position: absolute;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 999px;
  filter: drop-shadow(0 4px 8px rgba(26, 46, 34, 0.08));
  animation: cloud-drift 12s ease-in-out infinite alternate;
}
.weather-scene__cloud--a {
  width: 72px;
  height: 28px;
  top: 36px;
  left: 18%;
}
.weather-scene__cloud--a::before,
.weather-scene__cloud--a::after {
  content: '';
  position: absolute;
  background: inherit;
  border-radius: 50%;
}
.weather-scene__cloud--a::before {
  width: 34px;
  height: 34px;
  top: -16px;
  left: 8px;
}
.weather-scene__cloud--a::after {
  width: 42px;
  height: 42px;
  top: -20px;
  right: 6px;
}
.weather-scene__cloud--b {
  width: 86px;
  height: 32px;
  top: 58px;
  right: 12%;
  opacity: 0.88;
  animation-duration: 16s;
  animation-delay: -4s;
}
.weather-scene__cloud--b::before,
.weather-scene__cloud--b::after {
  content: '';
  position: absolute;
  background: inherit;
  border-radius: 50%;
}
.weather-scene__cloud--b::before {
  width: 38px;
  height: 38px;
  top: -18px;
  left: 10px;
}
.weather-scene__cloud--b::after {
  width: 46px;
  height: 46px;
  top: -22px;
  right: 8px;
}
.weather-scene__rain {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.weather-scene__drop {
  position: absolute;
  top: 58%;
  left: calc(12% + var(--i) * 9%);
  width: 2px;
  height: 14px;
  border-radius: 2px;
  background: linear-gradient(180deg, transparent, var(--color-sky));
  animation: rain-fall 0.9s linear infinite;
  animation-delay: calc(var(--i) * -0.11s);
  opacity: 0.75;
}
.weather-scene__frost {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
.weather-scene__label {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  margin: 0;
  padding: 0.45rem 0.65rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  background: linear-gradient(180deg, transparent, var(--color-surface, #1e293b));
  text-align: center;
}
@keyframes sun-pulse {
  0%,
  100% {
    transform: scale(1);
    box-shadow: 0 0 24px rgba(244, 196, 48, 0.45);
  }
  50% {
    transform: scale(1.06);
    box-shadow: 0 0 32px rgba(244, 196, 48, 0.6);
  }
}
@keyframes cloud-drift {
  from {
    transform: translateX(-6px);
  }
  to {
    transform: translateX(10px);
  }
}
@keyframes rain-fall {
  from {
    transform: translateY(-8px);
    opacity: 0;
  }
  30% {
    opacity: 0.85;
  }
  to {
    transform: translateY(28px);
    opacity: 0;
  }
}
</style>
