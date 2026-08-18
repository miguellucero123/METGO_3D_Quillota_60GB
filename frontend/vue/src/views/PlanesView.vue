<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { createCheckoutSession } from '@/api/metgoApi'

const auth = useAuthStore()
const router = useRouter()
const cargando = ref(false)

async function iniciarCheckout(planCode) {
  if (!auth.isAuthenticated) {
    // Si no estÃ¡ logueado, mandarlo a registro con el plan en mente
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
  <div class="commercial-page">
    <header class="top">
      <nav class="nav" aria-label="Principal">
        <router-link to="/" class="brand">
          <span class="brand-text">
            <span class="brand-name">METGO</span>
            <span class="brand-sub">3D</span>
          </span>
        </router-link>
        <div class="nav-links">
          <router-link to="/planes" class="router-link-active">Planes</router-link>
        </div>
        <div class="nav-cta">
          <router-link class="btn btn-ghost" to="/login">Ingresar</router-link>
        </div>
      </nav>
    </header>

    <main class="commercial-wrap commercial-section">
      <div style="text-align: center; margin-bottom: 4rem;">
        <h1>Planes diseÃ±ados para faenas reales</h1>
        <p class="subtitle" style="margin: 0 auto;">
          Precio fijo mensual por zona o faena. Sin sorpresas. Sin costo por alerta.
          Comienza a tomar decisiones con datos que protegen tu operaciÃ³n.
        </p>
      </div>

      <div class="commercial-grid-3">
        <!-- Plan Campo -->
        <div class="commercial-card pricing-card">
          <h3 class="plan-name">Plan Campo</h3>
          <p class="plan-target">Agricultura de precisiÃ³n</p>
          <div class="plan-price">
            <span class="price-from">desde</span>
            <span class="price-value">$99</span>
            <span class="price-period">USD/mes</span>
          </div>
          <p class="plan-unit">por zona de cultivo</p>
          
          <ul class="plan-features">
            <li><span class="check">âœ“</span> Panel operativo en tiempo real para tu zona</li>
            <li><span class="check">âœ“</span> Alertas de helada, lluvia y viento por WhatsApp</li>
            <li><span class="check">âœ“</span> PronÃ³stico 72h con resoluciÃ³n de 1â€“3 km</li>
            <li><span class="check">âœ“</span> Informe semanal descargable</li>
            <li><span class="check">âœ“</span> 14 dÃ­as de prueba sin costo</li>
          </ul>
          
          <button type="button" @click="iniciarCheckout('pro')" :disabled="cargando" class="commercial-btn primary" style="width: 100%; margin-top: 1.5rem; cursor: pointer;">
            {{ cargando ? 'Redirigiendo...' : 'Comenzar Prueba Gratis (14 DÃ­as)' }}
          </button>
        </div>

        <!-- Plan Faena -->
        <div class="commercial-card pricing-card featured">
          <div class="featured-badge">MÃ¡s popular</div>
          <h3 class="plan-name">Plan Faena</h3>
          <p class="plan-target">MinerÃ­a, izaje y alta montaÃ±a</p>
          <div class="plan-price">
            <span class="price-from">desde</span>
            <span class="price-value">$299</span>
            <span class="price-period">USD/mes</span>
          </div>
          <p class="plan-unit">por faena (VENTORA / SPATI)</p>
          
          <ul class="plan-features">
            <li><span class="check">âœ“</span> SemÃ¡foro operacional hora a hora</li>
            <li><span class="check">âœ“</span> Viento en perfil vertical (10m, 50m, 100m)</li>
            <li><span class="check">âœ“</span> Alertas de tormenta elÃ©ctrica y cizalladura</li>
            <li><span class="check">âœ“</span> PronÃ³stico subestacional 20â€“90 dÃ­as</li>
            <li><span class="check">âœ“</span> Soporte tÃ©cnico directo</li>
          </ul>
          
          <button type="button" @click="iniciarCheckout('faena')" :disabled="cargando" class="commercial-btn primary" style="width: 100%; margin-top: 1.5rem; cursor: pointer;">
            {{ cargando ? 'Redirigiendo...' : 'Contratar Plan Faena' }}
          </button>
        </div>

        <!-- Plan Municipio -->
        <div class="commercial-card pricing-card">
          <h3 class="plan-name">Plan Municipio</h3>
          <p class="plan-target">Calidad del aire y sector pÃºblico</p>
          <div class="plan-price">
            <span class="price-from">desde</span>
            <span class="price-value">$399</span>
            <span class="price-period">USD/mes</span>
          </div>
          <p class="plan-unit">por red de estaciones Â· cotizaciÃ³n formal</p>
          
          <ul class="plan-features">
            <li><span class="check">âœ“</span> Dashboard de calidad del aire con tu logo</li>
            <li><span class="check">âœ“</span> Red de estaciones integrada en la plataforma</li>
            <li><span class="check">âœ“</span> Alertas de episodios crÃ­ticos (DS 59/DS 138)</li>
            <li><span class="check">âœ“</span> Informes exportables para SINCA y fiscalizaciÃ³n</li>
            <li><span class="check">âœ“</span> CotizaciÃ³n formal por Mercado PÃºblico</li>
          </ul>
          
          <router-link to="/contacto?sector=calidad-aire" class="commercial-btn secondary" style="width: 100%; margin-top: 1.5rem;">
            Solicitar cotizaciÃ³n formal
          </router-link>
        </div>
      </div>

      <div class="faq-section" style="margin-top: 6rem;">
        <h2 style="text-align: center; margin-bottom: 3rem;">Preguntas frecuentes</h2>
        
        <div class="faq-grid">
          <div class="faq-item">
            <h4>Â¿Los precios son en USD o CLP?</h4>
            <p>
              La lista pÃºblica es en <strong>USD</strong>. El precio de lista es una fracciÃ³n
              (~15â€“25 %) del valor del stack completo (panel, alertas, pronÃ³stico, informes, API).
              En Chile podemos facturar en CLP al tipo de cambio del dÃ­a.
            </p>
          </div>
          <div class="faq-item">
            <h4>Â¿Hay contrato mÃ­nimo?</h4>
            <p>Ofrecemos contratos mes a mes para mÃ¡xima flexibilidad. Sin embargo, los contratos anuales o por temporada (ej. 6 meses de cosecha) incluyen descuentos significativos.</p>
          </div>
          <div class="faq-item">
            <h4>Â¿QuÃ© pasa si mi zona no estÃ¡ cubierta actualmente?</h4>
            <p>Desplegamos nuestro modelo en nuevas zonas constantemente. Solicita una evaluaciÃ³n gratuita de tu faena y te confirmaremos si podemos activarla (usualmente toma &lt;72h).</p>
          </div>
          <div class="faq-item">
            <h4>GarantÃ­a: Primer mes sin costo</h4>
            <p>Entendemos que necesitas validar que la herramienta es Ãºtil para tu operaciÃ³n. El primer mes de piloto es sin costo. Si no te ahorramos dinero o tiempo, no pagas.</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Navigation styles (duplicated temporarily until we extract a Layout component for commercial pages) */
.top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  background: rgba(8, 12, 20, 0.82);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
}
.nav {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 28px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.nav-links {
  display: none;
  gap: 1.5rem;
}
@media (min-width: 768px) {
  .nav-links {
    display: flex;
  }
}
.nav-links a {
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.2s;
  text-decoration: none;
}
.nav-links a:hover,
.nav-links a.router-link-active {
  color: var(--text-primary);
}
.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-primary);
  text-decoration: none;
}
.brand-name {
  font-weight: 700;
  letter-spacing: 0.05em;
}
.brand-sub {
  color: var(--accent-primary);
  font-weight: 700;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  font-weight: 600;
  border-radius: 6px;
  text-decoration: none;
  transition: all 0.2s;
}
.btn-ghost {
  color: var(--text-primary);
}
.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Pricing specific styles */
.pricing-card {
  position: relative;
  display: flex;
  flex-direction: column;
}

.pricing-card.featured {
  border-color: var(--accent-primary);
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.1);
}

.featured-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--accent-primary);
  color: white;
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
  color: white;
}

.plan-target {
  color: var(--text-secondary);
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
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.price-value {
  font-size: 2.5rem;
  font-weight: 800;
  color: white;
  letter-spacing: -0.02em;
}

.price-period {
  color: var(--text-secondary);
  font-weight: 500;
}

.plan-unit {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
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
  color: var(--text-primary);
  line-height: 1.4;
}

.check {
  color: var(--accent-secondary);
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
  color: white;
}

.faq-item p {
  color: var(--text-secondary);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .faq-grid {
    grid-template-columns: 1fr;
  }
}
</style>

