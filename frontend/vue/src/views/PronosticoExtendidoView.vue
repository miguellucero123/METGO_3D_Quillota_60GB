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
        <h1>¿Qué clima esperar los próximos 3 meses en tu región?</h1>
        <p class="subtitle" style="margin: 0 auto 2.5rem;">
          Anticipa la tendencia de la próxima temporada. Nuestro sistema de pronóstico subestacional te entrega proyecciones probabilísticas con 20 a 90 días de margen para que planifiques cosechas, contratos de agua o mantenciones mineras sin sorpresas.
        </p>
        <div style="display: flex; gap: 1rem; justify-content: center;">
          <router-link to="/planes" class="commercial-btn primary">
            Ver Planes y Precios
          </router-link>
        </div>
      </section>

      <section class="commercial-section">
        <h2 style="text-align: center; margin-bottom: 3rem;">Por qué importa el largo plazo</h2>
        <div class="commercial-grid-3">
          <div class="commercial-card">
            <h3>Planificación Agrícola</h3>
            <p style="color: var(--text-secondary); line-height: 1.5;">
              Saber si la temporada será más seca o lluviosa que el promedio con 3 meses de anticipación permite negociar contratos de agua, ajustar fertilización y programar la cosecha con un margen de maniobra real.
            </p>
          </div>
          <div class="commercial-card">
            <h3>Operaciones Mineras</h3>
            <p style="color: var(--text-secondary); line-height: 1.5;">
              Planifica las mantenciones mayores (paradas de planta) y la logística de insumos pesados eligiendo los meses con menor probabilidad de eventos climáticos extremos en alta montaña.
            </p>
          </div>
          <div class="commercial-card">
            <h3>Energías Renovables</h3>
            <p style="color: var(--text-secondary); line-height: 1.5;">
              Proyecta la producción energética a largo plazo en plantas fotovoltaicas o eólicas, ajustando tus compromisos de despacho según la tendencia climática del trimestre.
            </p>
          </div>
        </div>
      </section>

      <section class="commercial-section">
        <div class="commercial-grid-2">
          <div>
            <h2 style="font-size: 2rem;">¿Cómo funciona y qué te entregamos?</h2>
            <p style="color: var(--text-secondary); margin-bottom: 2rem; line-height: 1.6;">
              A diferencia del pronóstico de 7 días, el pronóstico subestacional no te dice exactamente "cuándo lloverá", sino que proyecta la <strong>tendencia general de la temporada</strong> (probabilidad de que la precipitación o temperatura esté sobre o bajo el promedio histórico).
            </p>

            <ul class="benefit-list">
              <li>
                <strong>Reporte Trimestral:</strong> Un informe claro en lenguaje de negocio con las anomalías proyectadas para los próximos 90 días en tu zona geográfica específica.
              </li>
              <li>
                <strong>Calibración Local:</strong> Mientras los modelos globales fallan en capturar la geografía chilena, nosotros utilizamos algoritmos entrenados específicamente con la climatología de tu región.
              </li>
              <li>
                <strong>Base Probabilística:</strong> Conocerás el grado de certeza de cada tendencia para poder sopesar el riesgo en tus decisiones.
              </li>
            </ul>
            
            <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 1rem; border-radius: 8px; margin-top: 2rem;">
              <p style="color: var(--text-primary); font-size: 0.9rem; margin: 0;">
                <strong>Transparencia:</strong> Este es un pronóstico de <em>tendencia probabilística</em>. Está diseñado para planificación estratégica con margen, no para reemplazar el pronóstico operativo de 72 horas.
              </p>
            </div>
          </div>
          
          <div class="demo-card">
            <h3 style="margin-bottom: 1.5rem; color: var(--text-primary);">Ejemplo de Entrega</h3>
            
            <div style="margin-bottom: 1.5rem;">
              <h4 style="font-size: 1rem; color: var(--accent-secondary); margin-bottom: 0.5rem;">Tendencia de Precipitaciones (Trimestre JJA)</h4>
              <p style="font-size: 0.9rem; color: var(--text-secondary);">
                <strong>Probabilidad:</strong> 75% de escenario "Bajo lo normal"<br>
                <strong>Impacto esperado:</strong> Déficit hídrico en cuenca media. Recomendación de asegurar derechos de agua temprano en la temporada.
              </p>
            </div>
            
            <div style="margin-bottom: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color);">
              <h4 style="font-size: 1rem; color: var(--accent-secondary); margin-bottom: 0.5rem;">Tendencia de Temperaturas Mínimas (Trimestre JJA)</h4>
              <p style="font-size: 0.9rem; color: var(--text-secondary);">
                <strong>Probabilidad:</strong> 60% de escenario "Bajo lo normal"<br>
                <strong>Impacto esperado:</strong> Mayor frecuencia de eventos de heladas tardías. Recomendación de adelantar mantención de sistemas antiheladas.
              </p>
            </div>
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

.demo-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 2rem;
}
</style>
