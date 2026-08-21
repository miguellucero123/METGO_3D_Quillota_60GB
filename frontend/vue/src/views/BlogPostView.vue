<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Leaf, ArrowLeft } from 'lucide-vue-next'
import CommercialLayout from '@/components/layout/CommercialLayout.vue'

const route = useRoute()
const slug = computed(() => route.params.slug)

// En una implementación real, esto vendría de una API o CMS
const post = computed(() => {
  return {
    title: 'Gestión de ráfagas de viento para operaciones de izaje en Atacama',
    date: '2023-11-02',
    author: 'Miguel Lucero',
    category: 'Minería e Izaje',
    content: `
      <p>El perfil vertical de viento en zonas de alta cordillera es notoriamente difícil de pronosticar utilizando solo modelos globales. Para proyectos de infraestructura que dependen de grúas torre, operar a ciegas no es una opción.</p>
      
      <h3>El problema de la cizalladura</h3>
      <p>La velocidad del viento a nivel del suelo (10m) rara vez refleja lo que experimenta la pluma de una grúa a 100m de altura. Este gradiente o "cizalladura" puede provocar oscilaciones peligrosas en la carga.</p>
      
      <p>Nuestra experiencia en faenas de la Región de Atacama muestra que <strong>más del 40% de las paradas preventivas</strong> se basan en ráfagas repentinas que los modelos estándar (como el GFS directo) subestiman severamente.</p>
      
      <h3>La solución: Modelación local (Downscaling)</h3>
      <p>Al implementar un modelo numérico regional ajustado topográficamente, logramos resolver el flujo del viento canalizado por valles específicos. Esto nos permite generar perfiles de viento a 10m, 50m y 100m con alta fiabilidad.</p>
    `
  }
})
</script>

<template>
  <CommercialLayout
    brandName="METGO3D"
    brandSub="BLOG"
    :brandIcon="Leaf"
    accentColor="#00ffaa"
    :seoTitle="`${post.title} | Blog METGO3D`"
    seoDescription="Análisis detallado sobre inteligencia climática aplicada."
  >
    <main class="commercial-wrap">
      <article class="post-container">
        <router-link to="/blog" class="back-link">
          <ArrowLeft :size="16" /> Volver al blog
        </router-link>

        <header class="post-header">
          <div class="post-meta">
            <span class="post-category">{{ post.category }}</span>
            <span class="post-date">{{ new Date(post.date).toLocaleDateString('es-CL', { year: 'numeric', month: 'long', day: 'numeric' }) }}</span>
            <span class="post-author">Por {{ post.author }}</span>
          </div>
          <h1 class="post-title">{{ post.title }}</h1>
        </header>

        <div class="post-layout">
          <div class="post-content" v-html="post.content"></div>
          
          <aside class="post-sidebar">
            <div class="sidebar-widget">
              <h3>¿Protegiendo tu operación?</h3>
              <p>Evita paradas no planificadas con pronósticos de alta resolución para tu faena.</p>
              <router-link to="/planes" class="btn btn-primary" style="width: 100%; margin-top: 1rem;">
                Ver planes METGO3D
              </router-link>
            </div>
          </aside>
        </div>
      </article>
    </main>
  </CommercialLayout>
</template>

<style scoped>
.commercial-wrap {
  max-width: 1120px;
  margin: 0 auto;
  padding: 4rem 28px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--muted-color);
  text-decoration: none;
  font-weight: 500;
  margin-bottom: 2rem;
  transition: color 0.15s;
}

.back-link:hover {
  color: var(--text-color);
}

.post-header {
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--border-color);
}

.post-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.post-category {
  color: var(--accent);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.post-date, .post-author {
  color: var(--dim-color);
}

.post-title {
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -0.5px;
}

.post-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 4rem;
}

@media (max-width: 900px) {
  .post-layout {
    grid-template-columns: 1fr;
  }
}

.post-content {
  font-size: 1.1rem;
  line-height: 1.8;
  color: var(--text-color);
}

.post-content :deep(h2), 
.post-content :deep(h3) {
  margin-top: 2.5rem;
  margin-bottom: 1rem;
  font-weight: 700;
  color: var(--text-color);
}

.post-content :deep(p) {
  margin-bottom: 1.5rem;
  color: var(--muted-color);
}

.sidebar-widget {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  position: sticky;
  top: 100px;
}

.sidebar-widget h3 {
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
}

.sidebar-widget p {
  font-size: 0.9rem;
  color: var(--muted-color);
  line-height: 1.5;
}
</style>
