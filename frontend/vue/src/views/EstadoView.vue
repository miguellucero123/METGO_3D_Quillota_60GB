<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import { useHealthStore } from '@/stores/health'
import SectionCard from '@/components/ui/SectionCard.vue'
import { Activity, Cloud, Server, Clock } from 'lucide-vue-next'

const { health, streamlitOk, cargando, iniciarPolling, detenerPolling, streamlitUrl } =
  useHealthStore()

const tarjetas = computed(() => {
  const h = health.value || {}
  return [
    {
      titulo: 'API Backend',
      icon: Server,
      estado: h.status === 'ok' ? 'ok' : h.status === 'degraded' ? 'warn' : 'err',
      detalle: `v${h.version || '?'} · uptime ${h.uptime_s ?? '?'}s`,
    },
    {
      titulo: 'OpenMeteo',
      icon: Cloud,
      estado: h.openmeteo ? 'ok' : 'warn',
      detalle: `Latencia ${h.latencia_openmeteo_ms ?? '?'} ms · caché ${h.cache_hits ?? 0} hits`,
    },
    {
      titulo: 'Streamlit Cloud',
      icon: Activity,
      estado: streamlitOk.value ? 'ok' : 'warn',
      detalle: streamlitUrl,
    },
    {
      titulo: 'Última actualización',
      icon: Clock,
      estado: 'ok',
      detalle: h.timestamp ? new Date(h.timestamp).toLocaleString('es-CL') : '—',
    },
  ]
})

onMounted(() => iniciarPolling(30000))
onUnmounted(() => detenerPolling())
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Estado del sistema</h2>
      <p class="page-subtitle">
        Monitoreo en tiempo real (actualización cada 30 s). No requiere iniciar sesión.
      </p>
    </header>

    <p v-if="cargando && !health" class="muted">Comprobando servicios…</p>

    <div class="grid">
      <SectionCard
        v-for="t in tarjetas"
        :key="t.titulo"
        :title="t.titulo"
        :subtitle="t.detalle"
      >
        <template #icon><component :is="t.icon" /></template>
        <span :class="['badge', t.estado]">
          {{ t.estado === 'ok' ? 'Operativo' : t.estado === 'warn' ? 'Degradado' : 'Error' }}
        </span>
      </SectionCard>
    </div>

    <pre v-if="health" class="raw">{{ JSON.stringify(health, null, 2) }}</pre>
  </div>
</template>

<style scoped>
.page {
  max-width: 960px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}
.badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
}
.badge.ok {
  background: var(--color-success-bg);
  color: var(--color-success);
}
.badge.warn {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}
.badge.err {
  background: #fde8e8;
  color: var(--color-danger, #9b3d3d);
}
.raw {
  margin-top: 1.5rem;
  font-size: 0.72rem;
  background: var(--color-primary-subtle);
  padding: 1rem;
  border-radius: var(--radius-md);
  overflow: auto;
}
</style>
