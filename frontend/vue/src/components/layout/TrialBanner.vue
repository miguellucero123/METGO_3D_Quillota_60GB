<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { fetchCuenta } from '@/api/metgoApi'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const visible = ref(false)
const daysLeft = ref(null)
const planCode = ref('')

const label = computed(() => {
  if (daysLeft.value == null) return ''
  if (daysLeft.value <= 0) return 'El piloto terminó. Elige un plan para continuar.'
  if (daysLeft.value === 1) return 'Queda 1 día de piloto.'
  return `Quedan ${daysLeft.value} días de piloto.`
})

onMounted(async () => {
  if (!auth.isAuthenticated) return
  try {
    const data = await fetchCuenta()
    const sub = data?.suscripcion
    if (!sub || String(sub.status || '').toLowerCase() !== 'trialing') return
    planCode.value = sub.plan_code || 'trial'
    const end = sub.current_period_end ? new Date(sub.current_period_end) : null
    if (!end || Number.isNaN(end.getTime())) return
    daysLeft.value = Math.ceil((end.getTime() - Date.now()) / 86400000)
    visible.value = true
  } catch {
    /* silencioso */
  }
})
</script>

<template>
  <div v-if="visible" class="trial-banner" role="status">
    <span>{{ label }} <template v-if="planCode">({{ planCode }})</template></span>
    <RouterLink class="trial-banner__link" to="/cuenta">Ver planes</RouterLink>
  </div>
</template>

<style scoped>
.trial-banner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin: 0;
  padding: 0.65rem 1rem;
  font-size: 0.9rem;
  border-bottom: 1px solid color-mix(in srgb, var(--color-primary) 35%, transparent);
  background: color-mix(in srgb, var(--color-primary) 14%, transparent);
  color: var(--color-text);
}
.trial-banner__link {
  font-weight: 600;
  color: var(--color-primary);
  text-decoration: none;
}
.trial-banner__link:hover { text-decoration: underline; }
</style>
