<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useHealthStore } from '@/stores/health'
import SectionCard from '@/components/ui/SectionCard.vue'
import { Activity, Cloud, Server, Clock, Layers } from 'lucide-vue-next'
import { fetchIntegracionEstado } from '@/api/metgoApi'

const { health, streamlitOk, cargando, iniciarPolling, detenerPolling, streamlitUrl } =
  useHealthStore()
const integracion = ref(null)

async function cargarIntegracion() {
  try {
    integracion.value = await fetchIntegracionEstado()
  } catch {
    integracion.value = null
  }
}

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
      titulo: 'Portal Streamlit',
      icon: Activity,
      estado:
        streamlitOk.value === null ? 'ok' : streamlitOk.value ? 'ok' : 'warn',
      detalle:
        streamlitOk.value === null
          ? 'Local: use /puertos o Render'
          : streamlitUrl,
    },
    {
      titulo: 'Observabilidad',
      icon: Activity,
      estado: h.observabilidad?.sentry ? 'ok' : 'warn',
      detalle: `Logs JSON · fase ${h.fase || '?'}`,
    },
    {
      titulo: 'Última actualización',
      icon: Clock,
      estado: 'ok',
      detalle: h.timestamp ? new Date(h.timestamp).toLocaleString('es-CL') : '—',
    },
  ]
})

onMounted(() => {
  iniciarPolling(30000)
  cargarIntegracion()
})
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

    <SectionCard
      v-if="integracion"
      title="Integración backend 01–12"
      :subtitle="`Promedio ${integracion.promedio_integracion}% · Fase ${integracion.fase || '5'}${integracion.integracion_completa ? ' · Integración completa' : ''}`"
    >
      <template #icon><Layers /></template>
      <ul class="mod-list">
        <li v-for="m in integracion.modulos" :key="m.id">
          <span class="mod-pct" :class="{ 'mod-pct--ok': m.porcentaje >= 95 }">{{ m.porcentaje }}%</span>
          <strong>{{ m.id }}</strong> {{ m.nombre }}
          <span class="mod-det">{{ m.detalle }} ({{ m.checks_ok }}/{{ m.checks_total }})</span>
        </li>
      </ul>
    </SectionCard>
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
.mod-list {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 0.8rem;
}
.mod-list li {
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--color-border);
}
.mod-pct {
  display: inline-block;
  min-width: 2.5rem;
  font-weight: 700;
  color: var(--color-primary);
}
.mod-pct--ok {
  color: var(--color-success);
}
.mod-det {
  display: block;
  color: var(--color-muted);
  font-size: 0.72rem;
}
</style>
