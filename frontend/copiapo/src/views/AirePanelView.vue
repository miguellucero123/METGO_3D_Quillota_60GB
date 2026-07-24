<template>
  <div class="page">
    <header class="page-head">
      <h1>Calidad del aire</h1>
      <p>{{ site.tagline }} · modelo CAMS (Open-Meteo)</p>
    </header>

    <div v-if="loading" class="state">Cargando estaciones y lecturas…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>
    <template v-else>
      <AlertaAireBanner :alerta="alerta" />

      <IcapHero
        v-if="seleccionada"
        :icap="seleccionada.icap"
        :nivel="seleccionada.nivel"
        :etiqueta="seleccionada.etiqueta"
        :contaminante-rector="seleccionada.contaminante_rector"
        :recomendaciones="seleccionada.recomendaciones"
      />

      <section class="estaciones">
        <h2>Estaciones</h2>
        <div class="grid">
          <EstacionAireCard
            v-for="est in estaciones"
            :key="est.slug"
            :nombre="est.nombre"
            :aire="lecturas[est.slug]"
            :active="est.slug === slugActivo"
            @select="slugActivo = est.slug"
          />
        </div>
      </section>

      <p v-if="seleccionada" class="fuente">
        Fuente: {{ seleccionada.fuente || '—' }} ·
        actualizado {{ seleccionada.actualizado || '—' }} ·
        <TipoDatoBadge :tipo="seleccionada.tipo_dato || 'modelo'" />
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, reactive, ref } from 'vue'
import IcapHero from '@/components/aire/IcapHero.vue'
import EstacionAireCard from '@/components/aire/EstacionAireCard.vue'
import AlertaAireBanner from '@/components/aire/AlertaAireBanner.vue'
import TipoDatoBadge from '@/components/aire/TipoDatoBadge.vue'
import { wakeApi, fetchAireActual, fetchEstacionesSitio } from '@/services/aireApi'

const site = inject('site')
const loading = ref(true)
const error = ref(null)
const estaciones = ref([])
const lecturas = reactive({})
const slugActivo = ref(site.stations[0]?.slug || 'copiapo_centro')

const ICAP_UMBRAL = 200

const seleccionada = computed(() => lecturas[slugActivo.value] || null)

const alerta = computed(() => {
  const activas = estaciones.value
    .map((est) => ({ est, aire: lecturas[est.slug] }))
    .filter(({ aire }) => aire && aire.icap != null && aire.icap >= ICAP_UMBRAL)
    .map(({ est, aire }) => ({
      estacion_id: est.slug,
      nombre: est.nombre,
      icap: aire.icap,
      nivel: aire.nivel,
      etiqueta: aire.etiqueta,
      contaminante_rector: aire.contaminante_rector,
      recomendaciones: aire.recomendaciones || [],
    }))
  const peor = activas.length
    ? activas.reduce((a, b) => (b.icap > a.icap ? b : a))
    : null
  return {
    hay_alerta: activas.length > 0,
    umbral: ICAP_UMBRAL,
    nivel_max: peor?.nivel || null,
    estaciones: activas,
  }
})

async function cargar() {
  loading.value = true
  error.value = null
  try {
    await wakeApi()
    let lista = []
    try {
      lista = await fetchEstacionesSitio()
    } catch {
      lista = []
    }
    if (!Array.isArray(lista) || !lista.length) {
      lista = site.stations.map((s) => ({
        slug: s.slug,
        nombre: s.nombre,
        estacion_id: s.slug,
      }))
    }
    estaciones.value = lista.map((e) => ({
      slug: e.slug || e.estacion_id,
      nombre: e.nombre || e.slug,
    }))
    if (!estaciones.value.find((e) => e.slug === slugActivo.value)) {
      slugActivo.value = estaciones.value[0]?.slug
    }
    await Promise.all(
      estaciones.value.map(async (est) => {
        try {
          lecturas[est.slug] = await fetchAireActual(est.slug)
        } catch {
          lecturas[est.slug] = null
        }
      })
    )
  } catch (err) {
    error.value = err?.message || 'No se pudo cargar la calidad del aire'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.page { max-width: 1100px; }
.page-head { margin-bottom: 1.25rem; }
.page-head h1 { margin: 0 0 0.25rem; font-size: 1.6rem; }
.page-head p { margin: 0; color: var(--color-text-secondary); }
.estaciones { margin-top: 1.5rem; }
.estaciones h2 { font-size: 1.1rem; margin: 0 0 0.75rem; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.85rem;
}
.state {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-secondary);
}
.state.error { color: var(--color-danger); }
.btn {
  margin-top: 0.75rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-primary);
  background: var(--color-primary-muted);
  color: var(--color-primary);
  border-radius: 6px;
  cursor: pointer;
}
.fuente {
  margin-top: 1rem;
  font-size: 0.8rem;
  color: var(--color-muted);
}
</style>
