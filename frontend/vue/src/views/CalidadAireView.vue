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
          <router-link to="/planes">Planes</router-link>
          <router-link to="/izaje">Izaje</router-link>
          <router-link to="/mineria">Minería</router-link>
          <router-link to="/calidad-del-aire" class="router-link-active">Calidad del Aire</router-link>
        </div>
        <div class="nav-cta">
          <router-link class="btn btn-ghost" to="/login">Ingresar</router-link>
        </div>
      </nav>
    </header>

    <main class="commercial-wrap">
      <section class="commercial-hero">
        <h1>Cumplimiento normativo sin sobresaltos</h1>
        <p class="subtitle" style="margin: 0 auto 2.5rem;">
          Redes de monitoreo ICAP y modelación de dispersión de material particulado para cumplimiento de la normativa ambiental chilena (DS 59 y DS 138). Centraliza tus datos y automatiza tus reportes al SINCA.
        </p>
        <div style="display: flex; gap: 1rem; justify-content: center;">
          <router-link to="/planes" class="commercial-btn primary">
            Ver planes y precios
          </router-link>
        </div>
      </section>

      <section class="commercial-section">
        <div class="commercial-grid-2">
          <div>
            <h2 style="font-size: 2rem;">Operar sin monitoreo continuo es volar a ciegas</h2>
            <p style="color: var(--text-secondary); margin-bottom: 2rem; line-height: 1.6;">
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
              <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem; color: var(--accent-primary);">Cuenca de Copiapó</h3>
              <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">7 estaciones integradas en tiempo real</p>
              
              <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;">
                <span class="station-tag">Copiapó Centro</span>
                <span class="station-tag">Palpote</span>
                <span class="station-tag">Tierra Amarilla</span>
                <span class="station-tag">Nantoco</span>
                <span class="station-tag">Chamonate</span>
                <span class="station-tag">La Chimba</span>
              </div>
            </div>
            
            <p style="font-size: 0.85rem; color: var(--text-secondary); text-align: center; margin-top: 1rem; border-top: 1px solid var(--border-color); padding-top: 1rem;">
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
            <p style="color: var(--text-secondary); line-height: 1.5;">
              Integración de tu red de estaciones en nuestra plataforma en la nube. Visualización en tiempo real 24/7 y generación de reportes mensuales para la SMA.
            </p>
          </div>
          <div class="commercial-card">
            <h3>Modelación de Dispersión</h3>
            <p style="color: var(--text-secondary); line-height: 1.5;">
              Pronóstico de la pluma de dispersión de material particulado basado en el modelo meteorológico hiperlocal, permitiendo programar actividades críticas.
            </p>
          </div>
          <div class="commercial-card">
            <h3>Dashboard Institucional</h3>
            <p style="color: var(--text-secondary); line-height: 1.5;">
              Para municipios y DGA: Un portal público con la marca de tu institución para informar a la ciudadanía sobre el Índice de Calidad del Aire (ICAP).
            </p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* Navigation styles */
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
  color: var(--text-primary);
  line-height: 1.5;
}
.benefit-list li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: var(--accent-primary);
  font-weight: bold;
}

/* Demo Card */
.demo-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
}
.demo-header {
  margin-bottom: 1.5rem;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.5rem;
}

.station-tag {
  background: rgba(59, 130, 246, 0.1);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
}
</style>
