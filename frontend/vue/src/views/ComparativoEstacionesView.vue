<script setup>
import { onMounted } from 'vue'
import { GitCompare } from 'lucide-vue-next'
import SectionCard from '@/components/ui/SectionCard.vue'
import { useApiCall } from '@/composables/useApiCall'
import { fetchComparativo } from '@/api/metgoApi'

const { data: filas, loading, error, run } = useApiCall(fetchComparativo)

onMounted(run)
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Comparativo de estaciones</h2>
      <p class="page-subtitle">Valle de Aconcagua · pronóstico actual por estación</p>
    </header>

    <SectionCard title="Tabla comparativa" subtitle="5 estaciones principales">
      <template #icon><GitCompare /></template>
      <p v-if="loading" class="skeleton">Cargando…</p>
      <p v-else-if="error" class="error-text">{{ error }}</p>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Estación</th>
              <th>T° máx</th>
              <th>T° mín</th>
              <th>Lluvia</th>
              <th>Viento</th>
              <th>Humedad</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in filas" :key="r.estacion_id">
              <td>{{ r.estacion }}</td>
              <td>{{ r.temperatura_max }}°C</td>
              <td>{{ r.temperatura_min }}°C</td>
              <td>{{ r.precipitacion }} mm</td>
              <td>{{ r.viento }} km/h</td>
              <td>{{ r.humedad }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </SectionCard>
  </div>
</template>

<style scoped>
.table-wrap {
  overflow-x: auto;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.data-table th,
.data-table td {
  padding: 0.55rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}
.data-table th {
  color: var(--color-muted);
  font-weight: 600;
}
.error-text {
  color: var(--color-danger, #b91c1c);
}
</style>
