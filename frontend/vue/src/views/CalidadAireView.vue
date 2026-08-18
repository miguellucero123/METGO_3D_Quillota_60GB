<script setup>
import { Wind } from 'lucide-vue-next'
import CommercialLayout from '@/components/layout/CommercialLayout.vue'
</script>

<template>
  <CommercialLayout
    brandName="SPATI"
    brandSub="CALIDAD AIRE"
    :brandIcon="Wind"
    accentColor="#f5b942"
    seoTitle="Calidad del Aire | SPATI"
    seoDescription="Redes de monitoreo ICAP y modelación de dispersión de material particulado."
  >

    <main class="commercial-wrap">
      <section class="commercial-hero">
        <h1>Cumplimiento normativo sin sobresaltos</h1>
        <p class="subtitle" style="margin: 0 auto 2.5rem; color: var(--muted); line-height: 1.6;">
          Redes de monitoreo ICAP y modelación de dispersión de material particulado para cumplimiento de la normativa ambiental chilena (DS 59 y DS 138). Centraliza tus datos y automatiza tus reportes al SINCA.
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
            <h2 style="font-size: 2rem;">Operar sin monitoreo continuo es volar a ciegas</h2>
            <p style="color: var(--muted); margin-bottom: 2rem; line-height: 1.6;">
              Los Planes de Prevención y Descontaminación Atmosférica (PPDA) exigen a industrias y municipios medir, reportar y reaccionar. METGO facilita la gestión integral de la calidad del aire para que te enfoques en tu operación.
            </p>

            <ul class="benefit-list">
              <li>
                <strong>Cumplimiento DS 59/2000 y DS 138/2005:</strong> Monitoreo de MP10 y MP2.5 con reportes estructurados para auditorías SEIA.
              </li>
              <li>
                <strong>Conexión directa a SINCA:</strong> Olvídate de reportes manuales. Nuestros sistemas se integran para enviar datos validados a la autoridad.
              </li>
              <li>
                <strong>Alertas de Episodios Críticos:</strong> Notificaciones tempranas ante preemergencias y emergencias ambientales para activar protocolos.
              </li>
            </ul>
          </div>
          
          <div class="demo-card">
            <div class="demo-header">
              <span>Red de Monitoreo Activa</span>
            </div>
            
            <div style="text-align: center; padding: 2rem 0;">
              <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem; color: var(--accent);">Cuenca de Copiapó</h3>
              <p style="color: var(--muted); margin-bottom: 1.5rem;">7 estaciones integradas en tiempo real</p>
              
              <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;">
                <span class="station-tag">Copiapó Centro</span>
                <span class="station-tag">Palpote</span>
                <span class="station-tag">Tierra Amarilla</span>
                <span class="station-tag">Nantoco</span>
                <span class="station-tag">Chamonate</span>
                <span class="station-tag">La Chimba</span>
              </div>
            </div>
            
            <p style="font-size: 0.85rem; color: var(--muted); text-align: center; margin-top: 1rem; border-top: 1px solid var(--border); padding-top: 1rem;">
              Dashboard white-label disponible para municipios e instituciones públicas (Convenio Marco / Mercado Público).
            </p>
          </div>
        </div>
      </section>

      <section class="commercial-section" style="padding-bottom: 5rem;">
        <h2 style="text-align: center; margin-bottom: 3rem;">Modalidades de Servicio</h2>
        <div class="commercial-grid-3">
          <div class="commercial-card">
            <h3>Monitoreo Continuo</h3>
            <p style="color: var(--muted); line-height: 1.5;">
              Integración de tu red de estaciones en nuestra plataforma en la nube. Visualización en tiempo real 24/7 y generación de reportes mensuales para la SMA.
            </p>
          </div>
          <div class="commercial-card">
            <h3>Modelación de Dispersión</h3>
            <p style="color: var(--muted); line-height: 1.5;">
              Pronóstico de la pluma de dispersión de material particulado basado en el modelo meteorológico hiperlocal, permitiendo programar actividades críticas.
            </p>
          </div>
          <div class="commercial-card">
            <h3>Dashboard Institucional</h3>
            <p style="color: var(--muted); line-height: 1.5;">
              Para municipios y DGA: Un portal público con la marca de tu institución para informar a la ciudadanía sobre el Índice de Calidad del Aire (ICAP).
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

.station-tag {
  background: rgba(0, 255, 170, 0.1);
  color: var(--accent);
  border: 1px solid rgba(0, 255, 170, 0.3);
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
</style>

