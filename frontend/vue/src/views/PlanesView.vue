<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { createCheckoutSession } from '@/api/metgoApi'
import { Leaf } from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()
const cargando = ref(false)

async function iniciarCheckout(planCode) {
  if (!auth.isAuthenticated) {
    // Si no está logueado, mandarlo a registro con el plan en mente
    router.push({ path: '/registro', query: { plan: planCode } })
    return
  }

  try {
    cargando.value = true
    const { url } = await createCheckoutSession(
      planCode,
      auth.user?.email,
      auth.user?.id
    )
    if (url && url.startsWith('http')) {
      window.location.href = url
    } else {
      router.push(url || '/dashboard') // fallback para mock
    }
  } catch (error) {
    alert(error.message || 'Error al conectar con Stripe')
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <CommercialLayout
    brandName="METGO"
    brandSub="QUILLOTA"
    :brandIcon="Leaf"
    accentColor="#00ffaa"
    seoTitle="Planes y Precios | METGO Quillota"
    seoDescription="Precio fijo mensual por zona o faena. Sin sorpresas. Sin costo por alerta."
  >
    <div class="commercial-wrap commercial-section">
      <div style="text-align: center; margin-bottom: 4rem;">
        <h1>Planes diseñados para faenas reales</h1>
        <p class="subtitle" style="margin: 0 auto; color: var(--muted); max-width: 600px; line-height: 1.6;">
          Precio fijo mensual por zona o faena. Sin sorpresas. Sin costo por alerta.
          Comienza a tomar decisiones con datos que protegen tu operación.
        </p>
      </div>

      <div class="commercial-grid-3">
        <!-- Plan Campo -->
        <div class="commercial-card pricing-card">
          <h3 class="plan-name">Plan Campo</h3>
          <p class="plan-target">Agricultura de precisión</p>
          <div class="plan-price">
            <span class="price-from">desde</span>
            <span class="price-value">$99</span>
            <span class="price-period">USD/mes</span>
          </div>
          <p class="plan-unit">por zona de cultivo</p>
          
          <ul class="plan-features">
            <li><span class="check">✓</span> Panel operativo en tiempo real para tu zona</li>
            <li><span class="check">✓</span> Alertas de helada, lluvia y viento por WhatsApp</li>
            <li><span class="check">✓</span> Pronóstico 72h con resolución de 1-3 km</li>
            <li><span class="check">✓</span> Informe semanal descargable</li>
            <li><span class="check">✓</span> 14 días de prueba sin costo</li>
          </ul>
          
          <button type="button" @click="iniciarCheckout('pro')" :disabled="cargando" class="btn btn-primary" style="width: 100%; margin-top: 1.5rem; cursor: pointer;">
            {{ cargando ? 'Redirigiendo...' : 'Comenzar Prueba Gratis (14 Días)' }}
          </button>
        </div>

        <!-- Plan Faena -->
        <div class="commercial-card pricing-card featured">
          <div class="featured-badge">Más popular</div>
          <h3 class="plan-name">Plan Faena</h3>
          <p class="plan-target">Minería, izaje y alta montaña</p>
          <div class="plan-price">
            <span class="price-from">desde</span>
            <span class="price-value">$299</span>
            <span class="price-period">USD/mes</span>
          </div>
          <p class="plan-unit">por faena (VENTORA / SPATI)</p>
          
          <ul class="plan-features">
            <li><span class="check">✓</span> Semáforo operacional hora a hora</li>
            <li><span class="check">✓</span> Viento en perfil vertical (10m, 50m, 100m)</li>
            <li><span class="check">✓</span> Alertas de tormenta eléctrica y cizalladura</li>
            <li><span class="check">✓</span> Pronóstico subestacional 20-90 días</li>
            <li><span class="check">✓</span> Soporte técnico directo</li>
          </ul>
          
          <button type="button" @click="iniciarCheckout('faena')" :disabled="cargando" class="btn btn-primary" style="width: 100%; margin-top: 1.5rem; cursor: pointer;">
            {{ cargando ? 'Redirigiendo...' : 'Contratar Plan Faena' }}
          </button>
        </div>

        <!-- Plan Municipio -->
        <div class="commercial-card pricing-card">
          <h3 class="plan-name">Plan Municipio</h3>
          <p class="plan-target">Calidad del aire y sector público</p>
          <div class="plan-price">
            <span class="price-from">desde</span>
            <span class="price-value">$399</span>
            <span class="price-period">USD/mes</span>
          </div>
          <p class="plan-unit">por red de estaciones · cotización formal</p>
          
          <ul class="plan-features">
            <li><span class="check">✓</span> Dashboard de calidad del aire con tu logo</li>
            <li><span class="check">✓</span> Red de estaciones integrada en la plataforma</li>
            <li><span class="check">✓</span> Alertas de episodios críticos (DS 59/DS 138)</li>
            <li><span class="check">✓</span> Informes exportables para SINCA y fiscalización</li>
            <li><span class="check">✓</span> Cotización formal por Mercado Público</li>
          </ul>
          
          <router-link to="/contacto?sector=calidad-aire" class="btn btn-ghost" style="width: 100%; margin-top: 1.5rem;">
            Solicitar cotización formal
          </router-link>
        </div>
      </div>

      <div class="faq-section" style="margin-top: 6rem;">
        <h2 style="text-align: center; margin-bottom: 3rem;">Preguntas frecuentes</h2>
        
        <div class="faq-grid">
          <div class="faq-item">
            <h4>¿Los precios son en USD o CLP?</h4>
            <p>
              La lista pública es en <strong>USD</strong>. El precio de lista es una fracción
              (~15-25 %) del valor del stack completo (panel, alertas, pronóstico, informes, API).
              En Chile podemos facturar en CLP al tipo de cambio del día.
            </p>
          </div>
          <div class="faq-item">
            <h4>¿Hay contrato mínimo?</h4>
            <p>Ofrecemos contratos mes a mes para máxima flexibilidad. Sin embargo, los contratos anuales o por temporada (ej. 6 meses de cosecha) incluyen descuentos significativos.</p>
          </div>
          <div class="faq-item">
            <h4>¿Qué pasa si mi zona no está cubierta actualmente?</h4>
            <p>Desplegamos nuestro modelo en nuevas zonas constantemente. Solicita una evaluación gratuita de tu faena y te confirmaremos si podemos activarla (usualmente toma &lt;72h).</p>
          </div>
          <div class="faq-item">
            <h4>Garantía: Primer mes sin costo</h4>
            <p>Entendemos que necesitas validar que la herramienta es útil para tu operación. El primer mes de piloto es sin costo. Si no te ahorramos dinero o tiempo, no pagas.</p>
          </div>
        </div>
      </div>
    </div>
  </CommercialLayout>
</template>

<script setup>
import CommercialLayout from '@/components/layout/CommercialLayout.vue'

<style scoped>

.commercial-wrap {
  max-width: 1120px;
  margin: 0 auto;
  padding: 4rem 28px;
}

h1 {
  font-size: clamp(2rem, 4vw, 2.85rem);
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: -0.5px;
}

.commercial-grid-3 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

/* Pricing specific styles */
.commercial-card, .pricing-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 2.5rem 2rem;
}

.pricing-card.featured {
  border-color: var(--border-accent);
  box-shadow: 0 0 30px rgba(0, 255, 170, 0.1);
}

.featured-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--accent);
  color: #04140e;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.plan-name {
  font-size: 1.75rem;
  margin-bottom: 0.25rem;
  color: var(--text-color);
}

.plan-target {
  color: var(--muted);
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.plan-price {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
  margin-bottom: 0.25rem;
}

.price-from {
  color: var(--muted);
  font-size: 0.9rem;
}

.price-value {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-color);
  letter-spacing: -0.02em;
}

.price-period {
  color: var(--muted);
  font-weight: 500;
}

.plan-unit {
  color: var(--muted);
  font-size: 0.85rem;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}

.plan-features {
  list-style: none;
  padding: 0;
  margin: 0;
  flex-grow: 1;
}

.plan-features li {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1rem;
  font-size: 0.95rem;
  color: var(--text);
  line-height: 1.4;
}

.check {
  color: var(--accent);
  font-weight: bold;
  flex-shrink: 0;
}

/* FAQ */
.faq-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.faq-item h4 {
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
  color: var(--text-color);
}

.faq-item p {
  color: var(--muted);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .faq-grid {
    grid-template-columns: 1fr;
  }
}
</style>

