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
        </div>
        <div class="nav-cta">
          <router-link class="btn btn-ghost" to="/login">Ingresar</router-link>
        </div>
      </nav>
    </header>

    <main class="commercial-wrap">
      <section class="commercial-hero">
        <h1>Continuidad operacional y cero accidentes en altura</h1>
        <p class="subtitle" style="margin: 0 auto 2.5rem;">
          Panel meteorolÃ³gico hiperlocal para faenas mineras en alta montaÃ±a. Protege a tu equipo y optimiza tu planificaciÃ³n con alertas tempranas de viento, tormentas elÃ©ctricas y visibilidad, cumpliendo con el DS 72.
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
            <h2 style="font-size: 2rem;">Monitoreo diseÃ±ado para la realidad de la faena</h2>
            <p style="color: var(--text-secondary); margin-bottom: 2rem; line-height: 1.6;">
              Los pronÃ³sticos generales fallan en alta montaÃ±a porque no consideran la topografÃ­a especÃ­fica de tu operaciÃ³n. METGO integra tus estaciones locales con modelos de alta resoluciÃ³n para entregar un pronÃ³stico que realmente sirve para la toma de decisiones.
            </p>

            <ul class="benefit-list">
              <li>
                <strong>Viento en perfil vertical:</strong> Fundamental para operaciones de izaje, tronaduras y dispersiÃ³n de polvo.
              </li>
              <li>
                <strong>Tormentas elÃ©ctricas:</strong> Alertas preventivas para protocolos de evacuaciÃ³n temprana y resguardo de personal.
              </li>
              <li>
                <strong>Caminos de acceso y visibilidad:</strong> PronÃ³stico de nieve y neblina densa para programar logÃ­stica y cambios de turno.
              </li>
            </ul>
          </div>
          
          <div class="demo-card">
            <div class="demo-header">
              <span>Alerta Temprana Â· Ejemplo</span>
            </div>
            
            <div class="alert-preview">
              <div class="alert-icon">âš¡</div>
              <div class="alert-content">
                <strong>Alerta Naranja: Tormenta ElÃ©ctrica</strong>
                <p>Probabilidad >80% de descargas elÃ©ctricas en un radio de 5km a partir de las 14:00 hrs. Se recomienda preparar protocolo de evacuaciÃ³n en rajo.</p>
                <span class="alert-time">Emitida hoy a las 08:15 AM</span>
              </div>
            </div>

            <div class="alert-preview warning" style="margin-top: 1rem;">
              <div class="alert-icon">ðŸ’¨</div>
              <div class="alert-content">
                <strong>Aviso: Viento Fuerte</strong>
                <p>RÃ¡fagas proyectadas sobre 65 km/h entre las 16:00 y 19:00 hrs en sector botadero. Evaluar suspensiÃ³n de trabajos en altura.</p>
                <span class="alert-time">Emitida hoy a las 06:30 AM</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="commercial-section" style="padding-bottom: 5rem;">
        <h2 style="text-align: center; margin-bottom: 3rem;">El diferencial METGO para MinerÃ­a</h2>
        <div class="commercial-grid-3">
          <div class="commercial-card">
            <h3>ResoluciÃ³n Hiperlocal</h3>
            <p style="color: var(--text-secondary); line-height: 1.5;">
              No usamos el dato del pueblo mÃ¡s cercano. Modelamos el clima exactamente sobre las coordenadas de tu rajo, relave o campamento usando downscaling.
            </p>
          </div>
          <div class="commercial-card">
            <h3>Cumplimiento DS 72</h3>
            <p style="color: var(--text-secondary); line-height: 1.5;">
              Respalda tus decisiones operativas ante fiscalizaciones. Cada evento crÃ­tico genera un reporte PDF automÃ¡tico con los datos pronosticados vs observados.
            </p>
          </div>
          <div class="commercial-card">
            <h3>IntegraciÃ³n TecnolÃ³gica</h3>
            <p style="color: var(--text-secondary); line-height: 1.5;">
              Nos conectamos a tus estaciones meteorolÃ³gicas existentes (Vaisala, Campbell, Davis) para calibrar nuestros modelos de pronÃ³stico especÃ­ficamente para tu faena.
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
  content: 'â†’';
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
  color: white;
  margin-bottom: 0.25rem;
}

.alert-content p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.alert-time {
  font-size: 0.75rem;
  color: var(--text-secondary);
  opacity: 0.7;
}
</style>

