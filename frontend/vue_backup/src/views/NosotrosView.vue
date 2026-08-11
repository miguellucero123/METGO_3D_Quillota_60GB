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
          <router-link to="/calidad-del-aire">Calidad del Aire</router-link>
        </div>
        <div class="nav-cta">
          <router-link class="btn btn-ghost" to="/login">Ingresar</router-link>
        </div>
      </nav>
    </header>

    <main class="commercial-wrap">
      <section class="commercial-hero">
        <h1>Inteligencia climática construida para Chile</h1>
        <p class="subtitle" style="margin: 0 auto 2.5rem;">
          Los sistemas climáticos globales no están diseñados para las faenas reales de Atacama, el Valle del Aconcagua o los proyectos de izaje en Santiago. METGO nació para llenar ese vacío: datos precisos, alertas útiles y pronósticos que se ajustan al microclima donde operas.
        </p>
      </section>

      <section class="commercial-section">
        <div class="commercial-grid-2">
          <div>
            <h2 style="font-size: 2rem;">Por qué existimos</h2>
            <p style="color: var(--text-secondary); margin-bottom: 2rem; line-height: 1.6;">
              Vimos un problema recurrente en el mercado chileno: las operaciones agrícolas y mineras basan decisiones millonarias en datos climáticos genéricos. Un modelo que dice que "habrá viento en Santiago" no sirve para decidir si operar una grúa torre a 100 metros de altura en un cuadrante específico.
            </p>
            <p style="color: var(--text-secondary); line-height: 1.6;">
              Decidimos construir la primera plataforma enfocada exclusivamente en la toma de decisiones operativas. No somos una app del tiempo; somos una herramienta de continuidad operacional y gestión de riesgos.
            </p>
          </div>
          
          <div class="demo-card">
            <h3 style="margin-bottom: 1.5rem; color: var(--accent-primary);">Nuestra filosofía de trabajo</h3>
            
            <ul class="benefit-list">
              <li>
                <strong>Datos reales antes que demos:</strong> Construimos sobre tecnología que ya funciona en Quillota y Copiapó.
              </li>
              <li>
                <strong>Alertas útiles antes que dashboards bonitos:</strong> Si no genera una decisión en terreno, es ruido.
              </li>
              <li>
                <strong>Tecnología abierta e integrable:</strong> Nuestra API está diseñada para conectar con tu SCADA, no para aislar tus datos.
              </li>
            </ul>
          </div>
        </div>
      </section>

      <section class="commercial-section">
        <h2 style="text-align: center; margin-bottom: 3rem;">Equipo y Tecnología</h2>
        <div class="commercial-grid-2" style="align-items: start;">
          <div class="commercial-card">
            <h3>El Equipo</h3>
            <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 1.5rem;">
              METGO 3D SpA es impulsada por profesionales con profunda especialización en meteorología aplicada y desarrollo tecnológico.
            </p>
            <div style="background: rgba(15, 23, 42, 0.5); padding: 1.5rem; border-radius: 8px; border: 1px solid var(--border-color);">
              <h4 style="margin-bottom: 0.5rem;">Meteorólogo y Científico de Datos</h4>
              <p style="font-size: 0.9rem; color: var(--text-secondary);">
                Magíster en Estadística con experiencia en análisis de datos climáticos aplicados a industria. Especialización en modelación regional para Chile y sistemas de pronóstico subestacional.
              </p>
            </div>
            <div style="margin-top: 1.5rem; text-align: center;">
              <router-link to="/contacto" style="color: var(--accent-primary); font-weight: 500; text-decoration: none;">
                ¿Quieres conversar con nuestro equipo técnico? Contáctanos →
              </router-link>
            </div>
          </div>
          
          <div class="commercial-card">
            <h3>Stack Tecnológico y Alianzas</h3>
            <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 1.5rem;">
              No reinventamos la rueda, la optimizamos para la geografía local usando modelos globales probados y Machine Learning propietario (Downscaling).
            </p>
            <div style="display: flex; flex-wrap: wrap; gap: 1rem;">
              <span class="tech-tag">Open-Meteo</span>
              <span class="tech-tag">ERA5 / GFS</span>
              <span class="tech-tag">Python & FastAPI</span>
              <span class="tech-tag">Vue.js</span>
              <span class="tech-tag">Cloudflare</span>
              <span class="tech-tag">WRF</span>
            </div>
          </div>
        </div>
      </section>
      
      <section class="commercial-section" style="padding-bottom: 5rem;">
        <div style="background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color); padding: 3rem; text-align: center; max-width: 800px; margin: 0 auto;">
          <h2>Hablemos de tu operación</h2>
          <p style="color: var(--text-secondary); margin-bottom: 2rem;">
            No importa si estás en minería, agricultura, construcción o el sector público. Si el clima afecta tus costos o la seguridad de tu equipo, podemos ayudarte.
          </p>
          <router-link to="/contacto" class="commercial-btn primary">
            Ir al formulario de contacto
          </router-link>
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

.demo-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 2rem;
}

.tech-tag {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
}
</style>
