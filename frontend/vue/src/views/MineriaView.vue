<script setup>
import { Mountain } from 'lucide-vue-next'
import CommercialLayout from '@/components/layout/CommercialLayout.vue'
</script>

<template>
  <CommercialLayout
    brandName="VENTORA"
    brandSub="MINERÍA"
    :brandIcon="Mountain"
    accentColor="#0ea5e9"
    seoTitle="Minería | VENTORA"
    seoDescription="Panel meteorológico hiperlocal para faenas mineras en alta montaña."
  >

    <main class="commercial-wrap">
      <section class="commercial-hero">
        <h1>Continuidad operacional y cero accidentes en altura</h1>
        <p class="subtitle" style="margin: 0 auto 2.5rem; color: var(--muted); line-height: 1.6;">
          Panel meteorológico hiperlocal para faenas mineras en alta montaña. Protege a tu equipo y optimiza tu planificación con alertas tempranas de viento, tormentas eléctricas y visibilidad, cumpliendo con el DS 72.
        </p>
        <div style="display: flex; gap: 1rem; justify-content: center;">
          <router-link to="/planes" class="btn btn-primary" style="height: 48px; font-size: 15px; padding: 0 2rem;">
            Ver planes y precios
          </router-link>
        </div>
      </section>

      <section class="commercial-section">
        <div class="commercial-grid-2">
          <div>
            <h2 style="font-size: 2rem;">Monitoreo diseñado para la realidad de la faena</h2>
            <p style="color: var(--muted); margin-bottom: 2rem; line-height: 1.6;">
              Los pronósticos generales fallan en alta montaña porque no consideran la topografía específica de tu operación. METGO integra tus estaciones locales con modelos de alta resolución para entregar un pronóstico que realmente sirve para la toma de decisiones.
            </p>

            <ul class="benefit-list">
              <li>
                <strong>Viento en perfil vertical:</strong> Fundamental para operaciones de izaje, tronaduras y dispersión de polvo.
              </li>
              <li>
                <strong>Tormentas eléctricas:</strong> Alertas preventivas para protocolos de evacuación temprana y resguardo de personal.
              </li>
              <li>
                <strong>Caminos de acceso y visibilidad:</strong> Pronóstico de nieve y neblina densa para programar logística y cambios de turno.
              </li>
            </ul>
          </div>
          
          <div class="demo-card">
            <div class="demo-header">
              <span>Alerta Temprana · Ejemplo</span>
            </div>
            
            <div class="alert-preview">
              <div class="alert-icon">⚡</div>
              <div class="alert-content">
                <strong>Alerta Naranja: Tormenta Eléctrica</strong>
                <p>Probabilidad >80% de descargas eléctricas en un radio de 5km a partir de las 14:00 hrs. Se recomienda preparar protocolo de evacuación en rajo.</p>
                <span class="alert-time">Emitida hoy a las 08:15 AM</span>
              </div>
            </div>

            <div class="alert-preview warning" style="margin-top: 1rem;">
              <div class="alert-icon">💨</div>
              <div class="alert-content">
                <strong>Aviso: Viento Fuerte</strong>
                <p>Ráfagas proyectadas sobre 65 km/h entre las 16:00 y 19:00 hrs en sector botadero. Evaluar suspensión de trabajos en altura.</p>
                <span class="alert-time">Emitida hoy a las 06:30 AM</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="commercial-section" style="padding-bottom: 5rem;">
        <h2 style="text-align: center; margin-bottom: 3rem;">El diferencial METGO para Minería</h2>
        <div class="commercial-grid-3">
          <div class="commercial-card">
            <h3>Resolución Hiperlocal</h3>
            <p style="color: var(--muted); line-height: 1.5;">
              No usamos el dato del pueblo más cercano. Modelamos el clima exactamente sobre las coordenadas de tu rajo, relave o campamento usando downscaling.
            </p>
          </div>
          <div class="commercial-card">
            <h3>Cumplimiento DS 72</h3>
            <p style="color: var(--muted); line-height: 1.5;">
              Respalda tus decisiones operativas ante fiscalizaciones. Cada evento crítico genera un reporte PDF automático con los datos pronosticados vs observados.
            </p>
          </div>
          <div class="commercial-card">
            <h3>Integración Tecnológica</h3>
            <p style="color: var(--muted); line-height: 1.5;">
              Nos conectamos a tus estaciones meteorológicas existentes (Vaisala, Campbell, Davis) para calibrar nuestros modelos de pronóstico específicamente para tu faena.
            </p>
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

.commercial-hero h1 {
  font-size: clamp(2rem, 4vw, 3rem);
  text-align: center;
}
.commercial-hero .subtitle {
  text-align: center;
  font-size: 1.1rem;
  max-width: 800px;
}

.commercial-grid-2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 4rem;
  margin-top: 2rem;
}

.commercial-grid-3 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.commercial-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 2rem;
  transition: transform 0.2s;
}
.commercial-card:hover {
  transform: translateY(-5px);
  border-color: var(--border-accent);
}

/* Page styles */
.benefit-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.benefit-list li {
  margin-bottom: 1.25rem;
  padding-left: 1.5rem;
  position: relative;
  color: var(--text);
  line-height: 1.5;
}
.benefit-list li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: var(--accent);
  font-weight: bold;
}

/* Demo Card */
.demo-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
}
.demo-header {
  margin-bottom: 1.5rem;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--muted);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.5rem;
}

.alert-preview {
  display: flex;
  gap: 1rem;
  background: rgba(245, 185, 66, 0.1);
  border: 1px solid rgba(245, 185, 66, 0.3);
  padding: 1rem;
  border-radius: 8px;
}

.alert-preview.warning {
  background: rgba(239, 91, 91, 0.1);
  border: 1px solid rgba(239, 91, 91, 0.3);
}

.alert-icon {
  font-size: 1.5rem;
  line-height: 1;
}

.alert-content strong {
  display: block;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.alert-content p {
  color: var(--muted);
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.alert-time {
  font-size: 0.75rem;
  color: var(--muted);
  opacity: 0.7;
}
</style>

