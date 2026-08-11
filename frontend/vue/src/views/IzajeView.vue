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
          <router-link to="/izaje" class="router-link-active">Izaje</router-link>
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
        <h1>Una grúa parada por viento cuesta miles de dólares. Anticípalo.</h1>
        <p class="subtitle" style="margin: 0 auto 2.5rem;">
          Anticipa ventanas seguras con 24h de margen. Nuestro semáforo operacional reduce las paradas no planificadas y evita multas por incumplimiento en construcción y gran minería.
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
            <h2>¿Por qué el viento en superficie no sirve?</h2>
            <p style="color: var(--text-secondary); margin-bottom: 2rem; line-height: 1.6;">
              Los pronósticos tradicionales (y los anemómetros básicos) solo miden el viento a nivel de suelo (10m). Pero una grúa torre o un izaje industrial operan a 50m o 100m de altura, donde la cizalladura y turbulencia mecánica cambian completamente las reglas del juego.
            </p>

            <ul class="benefit-list">
              <li>
                <strong>Cumplimiento DS 44/2023:</strong> Trabajo seguro en altura respaldado por datos certificados.
              </li>
              <li>
                <strong>Perfil vertical completo:</strong> Pronóstico simultáneo a 10m, 50m y 100m sobre el terreno.
              </li>
              <li>
                <strong>Alertas push automáticas:</strong> Notificación a tu equipo 12h antes si el viento proyectado supera tu umbral operativo.
              </li>
            </ul>
          </div>
          
          <div class="demo-card">
            <div class="demo-header">
              <span>Semáforo Operacional · Ventana 12h</span>
              <span class="live-dot"><span class="pulse"></span> Demo</span>
            </div>
            
            <div class="traffic-light-grid">
              <div class="tl-hour">
                <span>08:00</span>
                <div class="tl-status green" title="<26 km/h">Viento calmo</div>
              </div>
              <div class="tl-hour">
                <span>09:00</span>
                <div class="tl-status green" title="<26 km/h">Viento calmo</div>
              </div>
              <div class="tl-hour">
                <span>10:00</span>
                <div class="tl-status yellow" title="26-34 km/h">Precaución</div>
              </div>
              <div class="tl-hour">
                <span>11:00</span>
                <div class="tl-status red" title=">35 km/h">Parada por norma</div>
              </div>
              <div class="tl-hour">
                <span>12:00</span>
                <div class="tl-status red" title=">35 km/h">Parada por norma</div>
              </div>
              <div class="tl-hour">
                <span>13:00</span>
                <div class="tl-status yellow" title="26-34 km/h">Precaución</div>
              </div>
            </div>
            
            <p style="font-size: 0.85rem; color: var(--text-secondary); text-align: center; margin-top: 1rem;">
              Ejemplo de panel. El cliente puede definir sus propios umbrales operativos (ej: 26 km/h, 35 km/h, 60 km/h).
            </p>
          </div>
        </div>
      </section>

      <section class="commercial-section">
        <h2 style="text-align: center; margin-bottom: 3rem;">Para quién es esto</h2>
        <div class="commercial-grid-3">
          <div class="commercial-card">
            <h3>Grúas Torre en Construcción</h3>
            <p style="color: var(--text-secondary); line-height: 1.5;">
              Para constructoras en obras urbanas de gran altura que necesitan planificar los izajes del día siguiente con precisión, evitando equipos inactivos y protegiendo al personal.
            </p>
          </div>
          <div class="commercial-card">
            <h3>Izaje Industrial Minero</h3>
            <p style="color: var(--text-secondary); line-height: 1.5;">
              Para mantenciones mayores en plantas industriales y faenas (paradas de planta) donde el costo por hora de retraso es crítico y la seguridad es innegociable.
            </p>
          </div>
          <div class="commercial-card">
            <h3>Transporte Excepcional</h3>
            <p style="color: var(--text-secondary); line-height: 1.5;">
              Para logística de cargas sobredimensionadas que requieren evaluar las condiciones de viento en la ruta completa, especialmente en cruces de alta exposición o parques eólicos.
            </p>
          </div>
        </div>
      </section>
      
      <!-- Opcional Iframe -->
      <section class="commercial-section" style="padding-bottom: 5rem;">
        <div style="text-align: center; margin-bottom: 2rem;">
          <h2>Explora el panel en vivo</h2>
          <p class="subtitle" style="margin: 0 auto;">Interactúa con el semáforo operativo real (demo nacional)</p>
        </div>
        <div class="iframe-container">
          <iframe src="https://metgo-spati.pages.dev" width="100%" height="600" frameborder="0"></iframe>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* Navigation styles (duplicated temporarily) */
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

/* Traffic Light Demo */
.demo-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
}
.demo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  font-weight: 600;
  font-size: 0.9rem;
}
.live-dot {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--accent-secondary);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.pulse {
  width: 8px;
  height: 8px;
  background-color: var(--accent-secondary);
  border-radius: 50%;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
  70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
  100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.traffic-light-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}
@media (min-width: 600px) {
  .traffic-light-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.tl-hour {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.75rem;
  text-align: center;
}
.tl-hour span {
  display: block;
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}
.tl-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
}
.tl-status.green {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}
.tl-status.yellow {
  background: rgba(245, 185, 66, 0.15);
  color: #f5b942;
  border: 1px solid rgba(245, 185, 66, 0.3);
}
.tl-status.red {
  background: rgba(239, 91, 91, 0.15);
  color: #ef5b5b;
  border: 1px solid rgba(239, 91, 91, 0.3);
}

.iframe-container {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}
</style>
