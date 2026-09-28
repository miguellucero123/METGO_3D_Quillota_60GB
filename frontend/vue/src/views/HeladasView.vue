<script setup>
import { onMounted } from 'vue'
import { Snowflake } from 'lucide-vue-next'
import CommercialLayout from '@/components/layout/CommercialLayout.vue'
import { trackEvent } from '@/utils/analytics'

onMounted(() => {
  trackEvent('heladas_landing_view')
})

function pedirPiloto(plan) {
  trackEvent('heladas_cta', { plan })
}
</script>

<template>
  <CommercialLayout
    brandName="METGO3D"
    brandSub="HELADAS"
    :brandIcon="Snowflake"
    accentColor="#38bdf8"
    seoTitle="Alertas de heladas por predio | METGO3D"
    seoDescription="Cada tarde, la mínima prevista en tu predio, la probabilidad de helada, la hora más fría y qué hacer. Por WhatsApp o correo."
  >
    <main class="commercial-wrap">
      <section class="commercial-hero">
        <p class="eyebrow">Temporada de heladas primaverales · floración y brotación</p>
        <h1>Una sola helada te puede costar la temporada. Sábelo la tarde anterior.</h1>
        <p class="subtitle">
          Cada tarde te llega por WhatsApp o correo la temperatura mínima prevista en
          <strong>tu predio</strong>, la probabilidad de helada, la hora más fría y una
          recomendación simple: <em>prende control</em> o <em>tranquilo</em>. Si el riesgo sube
          en la noche, te llega una alerta extra.
        </p>
        <div class="hero-ctas">
          <router-link
            to="/contacto?sector=heladas&plan=piloto"
            class="btn btn-primary btn-cta"
            @click="pedirPiloto('piloto')"
          >
            Pedir piloto gratis (14 días)
          </router-link>
          <a href="#precios" class="btn btn-ghost btn-cta">Ver precios</a>
        </div>
      </section>

      <section class="commercial-section">
        <div class="commercial-grid-2">
          <div>
            <h2>No es el pronóstico de la comuna. Es el de tu cuartel.</h2>
            <p class="lead">
              Las apps del clima te dan la mínima de la ciudad. El frío de una helada radiativa se
              junta en los bajos del predio y puede estar 2 a 4 °C más abajo.
            </p>
            <ul class="benefit-list">
              <li>
                <strong>Tus coordenadas, tu cultivo:</strong> calculamos la noche en el punto exacto
                de tu predio y con el umbral de daño de tu especie (cerezo, vid, palto, cítricos, hortalizas).
              </li>
              <li>
                <strong>Tres modelos, no uno:</strong> combinamos los modelos europeo (ECMWF), alemán (ICON)
                y estadounidense (GFS). Cuando no se ponen de acuerdo, te lo decimos con un rango.
              </li>
              <li>
                <strong>Calibrado con tu termómetro:</strong> durante el piloto comparamos el pronóstico
                con tu lectura real y ajustamos tu predio. Cada semana acierta mejor.
              </li>
              <li>
                <strong>Revisado por un meteorólogo:</strong> cada boletín pasa por criterio humano antes
                de salir. No es un bot mandando números.
              </li>
            </ul>
          </div>

          <div class="demo-card">
            <div class="demo-header">
              <span>Así llega el mensaje</span>
              <span class="demo-tag">Ejemplo</span>
            </div>
            <pre class="wa-bubble">🌡️ METGO 3D · Heladas — Cerezos Don Juan
Noche del mar 29/09

Mínima prevista: -2,4 °C (entre -4,1 y -0,7)
Hora más fría: ~06:00
Probabilidad de helada (≤ 0 °C): 92 %
Probabilidad de bajar de -1,0 °C (cerezo): 79 %

🔴 PRENDE CONTROL. Deja listo tu sistema (hélices, aspersión o calefactores) y enciéndelo cuando tu termómetro de referencia marque -1,0 °C, probablemente cerca de las 03:00.

Es un pronóstico, no una garantía: confirma siempre con tu termómetro en terreno.
— METGO 3D</pre>
            <p class="demo-note">Mensaje de ejemplo con datos ilustrativos. El tuyo usa las coordenadas y el cultivo de tu predio.</p>
          </div>
        </div>
      </section>

      <section class="commercial-section">
        <h2 class="center">Cómo funciona</h2>
        <div class="commercial-grid-3">
          <div class="commercial-card">
            <span class="step">1</span>
            <h3>Nos mandas tu ubicación</h3>
            <p>Un pin de Google Maps por cuartel, el cultivo y el estado fenológico. Nada que instalar.</p>
          </div>
          <div class="commercial-card">
            <span class="step">2</span>
            <h3>Cada tarde, tu boletín</h3>
            <p>Mínima, probabilidad, hora más fría y qué hacer. Si en la noche el riesgo sube, te volvemos a escribir.</p>
          </div>
          <div class="commercial-card">
            <span class="step">3</span>
            <h3>Tú nos cuentas qué pasó</h3>
            <p>Con la lectura de tu termómetro a la mañana siguiente afinamos el umbral de tu predio.</p>
          </div>
        </div>
      </section>

      <section id="precios" class="commercial-section">
        <h2 class="center">Precios simples, por mes</h2>
        <p class="lead center">Los primeros 14 días son gratis. Sin contrato anual: pagas por la temporada que usas.</p>
        <div class="commercial-grid-2 pricing">
          <div class="commercial-card pricing-card">
            <h3>Plan Básico</h3>
            <p class="plan-target">Un predio, un cultivo</p>
            <div class="plan-price"><span class="price-value">$50</span><span class="price-period">USD/mes</span></div>
            <p class="plan-unit">≈ $47 mil CLP · facturable en pesos</p>
            <ul class="plan-features">
              <li>Boletín diario de la tarde (WhatsApp o correo)</li>
              <li>Alerta nocturna extra si el riesgo sube</li>
              <li>Umbral de acción según tu cultivo</li>
              <li>Calibración con tu termómetro</li>
            </ul>
            <router-link
              to="/contacto?sector=heladas&plan=basico"
              class="btn btn-ghost btn-block"
              @click="pedirPiloto('basico')"
            >Empezar piloto Básico</router-link>
          </div>

          <div class="commercial-card pricing-card featured">
            <div class="featured-badge">Para campos con varios cuarteles</div>
            <h3>Plan Pro</h3>
            <p class="plan-target">Hasta 5 cuarteles o sectores</p>
            <div class="plan-price"><span class="price-value">$150</span><span class="price-period">USD/mes</span></div>
            <p class="plan-unit">≈ $142 mil CLP · facturable en pesos</p>
            <ul class="plan-features">
              <li>Todo lo del Básico, por cada cuartel</li>
              <li>Llamada de consulta con el meteorólogo en noches críticas</li>
              <li>Umbral propio por cuartel y estado fenológico</li>
              <li>Resumen de temporada: noches de riesgo y aciertos</li>
            </ul>
            <router-link
              to="/contacto?sector=heladas&plan=pro"
              class="btn btn-primary btn-block"
              @click="pedirPiloto('pro')"
            >Empezar piloto Pro</router-link>
          </div>
        </div>
        <p class="asesores">
          ¿Eres asesor agrícola o cooperativa con varios productores?
          <router-link to="/contacto?sector=heladas&plan=asesor" @click="pedirPiloto('asesor')">Conversemos un precio por volumen.</router-link>
        </p>
      </section>

      <section class="commercial-section faq">
        <h2 class="center">Preguntas frecuentes</h2>
        <div class="commercial-grid-2">
          <div>
            <h4>¿Esto garantiza que no voy a tener daño?</h4>
            <p>No. Es un pronóstico, no una garantía. Te da información para decidir a tiempo; la decisión de encender el control y la lectura del termómetro en terreno siguen siendo tuyas.</p>
          </div>
          <div>
            <h4>¿Tengo que instalar algo?</h4>
            <p>No. Solo necesitamos la ubicación de tus cuarteles. Si tienes un termómetro o estación propia, mejor: con esos datos calibramos tu predio.</p>
          </div>
          <div>
            <h4>¿Qué pasa cuando terminan las heladas?</h4>
            <p>Desde noviembre el mismo servicio cambia a lo que importa en verano: olas de calor en cosecha, lluvias que afectan la fruta y pronóstico a varias semanas.</p>
          </div>
          <div>
            <h4>¿Qué zonas cubren?</h4>
            <p>Partimos en el Valle de Aconcagua (Quillota, San Felipe, Los Andes, Limache), pero el cálculo funciona para cualquier predio de Chile. Pregúntanos por el tuyo.</p>
          </div>
        </div>
      </section>
    </main>
  </CommercialLayout>
</template>

<style scoped>
.commercial-wrap {
  max-width: 1120px;
  margin: 0 auto;
  padding: 4rem 28px;
}
h1, h2, h3 {
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -0.5px;
  margin-bottom: 1rem;
}
.center { text-align: center; }
.eyebrow {
  text-align: center;
  color: var(--accent);
  font-weight: 600;
  font-size: 0.9rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 1rem;
}
.commercial-hero h1 {
  font-size: clamp(2rem, 4vw, 3rem);
  text-align: center;
}
.commercial-hero .subtitle {
  text-align: center;
  font-size: 1.1rem;
  max-width: 800px;
  margin: 0 auto 2.5rem;
  color: var(--muted);
  line-height: 1.6;
}
.hero-ctas {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}
.btn-cta {
  height: 48px;
  font-size: 15px;
  padding: 0 2rem;
}
.commercial-section { margin-top: 5rem; }
.lead {
  color: var(--muted);
  margin-bottom: 2rem;
  line-height: 1.6;
}
.commercial-grid-2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 3rem;
  margin-top: 2rem;
}
.commercial-grid-3 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 2rem;
}
.commercial-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 2rem;
  position: relative;
}
.commercial-card p { color: var(--muted); line-height: 1.5; }
.step {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent);
  color: #0b1220;
  font-weight: 800;
  margin-bottom: 1rem;
}
.benefit-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.benefit-list li {
  margin-bottom: 1.25rem;
  padding-left: 1.5rem;
  position: relative;
  line-height: 1.5;
}
.benefit-list li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: var(--accent);
  font-weight: bold;
}
.demo-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
}
.demo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-weight: 600;
  font-size: 0.9rem;
}
.demo-tag {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
  border: 1px solid var(--border-color);
  border-radius: 999px;
  padding: 0.15rem 0.6rem;
}
.wa-bubble {
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: 0.92rem;
  line-height: 1.5;
  background: rgba(37, 211, 102, 0.1);
  border: 1px solid rgba(37, 211, 102, 0.3);
  border-radius: 12px 12px 12px 2px;
  padding: 1rem 1.1rem;
  margin: 0;
  color: var(--text);
}
.demo-note {
  font-size: 0.8rem;
  color: var(--muted);
  text-align: center;
  margin-top: 0.75rem;
}
.pricing { max-width: 820px; margin-left: auto; margin-right: auto; }
.pricing-card.featured { border-color: var(--accent); }
.featured-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--accent);
  color: #0b1220;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.8rem;
  border-radius: 999px;
  white-space: nowrap;
}
.plan-target { margin-bottom: 1rem; }
.plan-price { display: flex; align-items: baseline; gap: 0.4rem; }
.price-value { font-size: 2.6rem; font-weight: 800; }
.price-period { color: var(--muted); }
.plan-unit { font-size: 0.85rem; margin-bottom: 1.25rem; }
.plan-features {
  list-style: none;
  padding: 0;
  margin: 0 0 1.5rem;
}
.plan-features li {
  padding-left: 1.4rem;
  position: relative;
  margin-bottom: 0.6rem;
  line-height: 1.4;
}
.plan-features li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--accent);
  font-weight: 700;
}
.btn-block { width: 100%; justify-content: center; }
.asesores {
  text-align: center;
  color: var(--muted);
  margin-top: 2rem;
}
.asesores a { color: var(--accent); font-weight: 600; }
.faq h4 { margin-bottom: 0.5rem; font-size: 1.05rem; }
.faq p { color: var(--muted); line-height: 1.6; margin-bottom: 1.5rem; }
@media (max-width: 480px) {
  .commercial-wrap { padding: 2.5rem 16px; }
}
</style>
