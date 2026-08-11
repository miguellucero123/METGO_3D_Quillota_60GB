<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchModulos, fetchSistemaResumen } from '@/api/metgoApi'
import ModuleCard from '@/components/ui/ModuleCard.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import { Grid3x3 } from 'lucide-vue-next'

const modulos = ref([])
const resumen = ref(null)
const filtro = ref('todos')
const cargando = ref(true)

const categorias = computed(() => resumen.value?.categorias ?? [])

const modulosFiltrados = computed(() => {
  if (filtro.value === 'todos') return modulos.value
  return modulos.value.filter((m) => m.categoria === filtro.value)
})

onMounted(async () => {
  try {
    const [m, r] = await Promise.all([fetchModulos(), fetchSistemaResumen()])
    modulos.value = m
    resumen.value = r
  } catch {
    modulos.value = []
  } finally {
    cargando.value = false
  }
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Catálogo de módulos METGO</h2>
      <p class="page-subtitle">
        Acceso interconectado a dashboards Vue, Streamlit y componentes del proyecto (01–12)
      </p>
      <div v-if="resumen" class="stats-row">
        <span class="stat">{{ resumen.total_modulos }} módulos</span>
        <span class="stat">{{ resumen.vue }} en Vue</span>
        <span class="stat">{{ resumen.streamlit }} Streamlit</span>
      </div>
    </header>

    <div class="filters">
      <button
        type="button"
        class="filter-btn"
        :class="{ active: filtro === 'todos' }"
        @click="filtro = 'todos'"
      >
        Todos
      </button>
      <button
        v-for="c in categorias"
        :key="c.id"
        type="button"
        class="filter-btn"
        :class="{ active: filtro === c.id }"
        @click="filtro = c.id"
      >
        {{ c.nombre }}
      </button>
    </div>

    <p v-if="cargando" class="skeleton">Cargando catálogo…</p>

    <div v-else class="modules-grid">
      <ModuleCard v-for="m in modulosFiltrados" :key="m.id" :modulo="m" />
    </div>

    <SectionCard
      class="help-card"
      title="Cómo interconectar módulos Streamlit"
      subtitle="Los dashboards Streamlit requieren ejecutarse en paralelo"
    >
      <template #icon><Grid3x3 /></template>
      <ol class="help-list">
        <li>Mantenga la API en el puerto <strong>8080</strong> y Vue en <strong>5173</strong>.</li>
        <li>Ejecute los dashboards Streamlit con el script del proyecto o puertos 8501–8513.</li>
        <li>Haga clic en una tarjeta <em>streamlit</em> para abrir ese módulo en una nueva pestaña.</li>
        <li>Use <router-link to="/configuracion">Configuración</router-link> para ver atributos por estación.</li>
      </ol>
      <p class="muted">
        Centro de servicios: use <strong>Iniciar</strong> en cada módulo Streamlit (API :8080).
        Script legacy: <code>python frontend/dashboards/ejecutar_todos_dashboards.py</code>
      </p>
    </SectionCard>
  </div>
</template>

<style scoped>
.page {
  max-width: 1400px;
}

.stats-row {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

.stat {
  font-size: 0.8rem;
  padding: 0.25rem 0.6rem;
  background: var(--color-primary-muted);
  color: var(--color-primary);
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1.25rem;
}

.filter-btn {
  padding: 0.4rem 0.85rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 999px;
  font-size: 0.78rem;
  font-family: inherit;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.filter-btn:hover,
.filter-btn.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.help-card {
  margin-top: 0.5rem;
}

.help-list {
  margin: 0.5rem 0 1rem 1.25rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.help-list a {
  color: var(--color-primary);
}
</style>
