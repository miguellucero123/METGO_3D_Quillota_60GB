<script setup>
import { Leaf } from 'lucide-vue-next'
import CommercialLayout from '@/components/layout/CommercialLayout.vue'

const posts = [
  {
    id: 1,
    slug: 'pronostico-helada-valle-aconcagua',
    title: 'Cómo interpretar el pronóstico de heladas en el Valle de Aconcagua',
    excerpt: 'Guía práctica para entender los umbrales de riesgo y activar sistemas de mitigación a tiempo en plantaciones de paltos y cítricos.',
    date: '2023-10-15',
    category: 'Agricultura',
    readTime: '5 min'
  },
  {
    id: 2,
    slug: 'viento-izaje-atacama',
    title: 'Gestión de ráfagas de viento para operaciones de izaje en Atacama',
    excerpt: 'Por qué el perfil vertical de viento es crítico para grúas torre y cómo anticipar ventanas operacionales seguras en alta montaña.',
    date: '2023-11-02',
    category: 'Minería e Izaje',
    readTime: '7 min'
  },
  {
    id: 3,
    slug: 'calidad-aire-quintero-puchuncavi',
    title: 'Monitoreo preventivo de MP10 y SO2: Más allá del cumplimiento normativo',
    excerpt: 'Estrategias de alerta temprana para episodios críticos ambientales usando redes IoT y modelación predictiva local.',
    date: '2023-11-20',
    category: 'Medioambiente',
    readTime: '6 min'
  }
]
</script>

<template>
  <CommercialLayout
    brandName="METGO3D"
    brandSub="BLOG"
    :brandIcon="Leaf"
    accentColor="#00ffaa"
    seoTitle="Blog | METGO3D"
    seoDescription="Artículos técnicos, guías y casos de estudio sobre inteligencia climática para operaciones en Chile."
  >
    <main class="commercial-wrap">
      <section class="commercial-hero">
        <p class="eyebrow">RECURSOS TÉCNICOS</p>
        <h1>Blog y Casos de Estudio</h1>
        <p class="subtitle" style="margin: 0 auto 3rem; color: var(--muted); max-width: 600px; line-height: 1.6;">
          Análisis, mejores prácticas e inteligencia climática aplicada a la realidad operacional de Chile.
        </p>
      </section>

      <div class="blog-grid">
        <article v-for="post in posts" :key="post.id" class="blog-card">
          <div class="blog-meta">
            <span class="blog-category">{{ post.category }}</span>
            <span class="blog-date">{{ new Date(post.date).toLocaleDateString('es-CL', { year: 'numeric', month: 'long', day: 'numeric' }) }}</span>
          </div>
          <h2>
            <router-link :to="`/blog/${post.slug}`" class="blog-title-link">
              {{ post.title }}
            </router-link>
          </h2>
          <p class="blog-excerpt">{{ post.excerpt }}</p>
          <div class="blog-footer">
            <router-link :to="`/blog/${post.slug}`" class="blog-read-more">
              Leer artículo →
            </router-link>
            <span class="blog-read-time">{{ post.readTime }} lectura</span>
          </div>
        </article>
      </div>
    </main>
  </CommercialLayout>
</template>

<style scoped>
.commercial-wrap {
  max-width: 900px;
  margin: 0 auto;
  padding: 4rem 28px;
}

.commercial-hero {
  text-align: center;
  margin-bottom: 3rem;
}

.eyebrow {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.8px;
  color: var(--accent);
  margin-bottom: 1rem;
}

h1 {
  font-size: clamp(2rem, 4vw, 2.85rem);
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: -0.5px;
  margin-bottom: 1rem;
}

.blog-grid {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.blog-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 2rem;
  transition: transform 0.2s, border-color 0.2s;
}

.blog-card:hover {
  transform: translateY(-2px);
  border-color: var(--border-accent);
}

.blog-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.85rem;
}

.blog-category {
  color: var(--accent);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.blog-date {
  color: var(--dim-color);
}

.blog-title-link {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  text-decoration: none;
  line-height: 1.3;
}

.blog-title-link:hover {
  text-decoration: underline;
  text-decoration-color: var(--accent);
}

.blog-excerpt {
  margin-top: 1rem;
  color: var(--muted-color);
  line-height: 1.6;
}

.blog-footer {
  margin-top: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.blog-read-more {
  color: var(--text-color);
  font-weight: 600;
  text-decoration: none;
  transition: color 0.15s;
}

.blog-read-more:hover {
  color: var(--accent);
}

.blog-read-time {
  color: var(--dim-color);
}
</style>
