<template>
  <div class="landing">
    <header class="top">
      <a class="brand" href="#inicio">
        <span class="brand-mark">SPATI</span>
        <span class="brand-sub">METGO 3D</span>
      </a>
      <nav class="nav" aria-label="Secciones">
        <a href="#como">Cómo funciona</a>
        <a href="#alertas">Alertas</a>
        <a href="#precios">Precios</a>
        <a href="#faq">FAQ</a>
      </nav>
      <div class="top-cta">
        <router-link class="btn ghost" :to="loginPath">Ingresar</router-link>
        <router-link class="btn solid" :to="registroPath">Piloto 15 días</router-link>
      </div>
    </header>

    <section id="inicio" class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Inteligencia climática · Izaje</p>
        <h1>El viento no avisa.<br /><em>SPATI sí.</em></h1>
        <p class="lede">
          Pronóstico hiperlocalizado 72 h para el punto GPS de su faena. Alertas
          con 18+ h de anticipación y respaldo documental para operar con
          certeza.
        </p>
        <div class="hero-actions">
          <router-link class="btn solid lg" :to="registroPath">Empezar piloto gratis</router-link>
          <a class="btn ghost lg" href="#precios">Ver planes</a>
        </div>
        <ul class="stats">
          <li><strong>72 h</strong><span>horizonte</span></li>
          <li><strong>18+ h</strong><span>anticipación</span></li>
          <li><strong>88–94%</strong><span>exactitud</span></li>
          <li><strong>&lt;5 min</strong><span>latencia alerta</span></li>
        </ul>
      </div>
      <div class="hero-visual" aria-hidden="true">
        <div class="wind-card">
          <div class="wind-sky">
            <span v-for="n in 12" :key="n" class="streak" :style="streakStyle(n)" />
          </div>
          <div class="wind-readout">
            <span class="lvl amarillo">AMARILLO</span>
            <strong>29 km/h</strong>
            <span class="muted">Ráfaga 34 · Dir SSO · +18 h</span>
          </div>
        </div>
      </div>
    </section>

    <section id="como" class="section">
      <h2>Cómo funciona</h2>
      <p class="section-sub">De la faena a la decisión en cinco pasos.</p>
      <ol class="steps">
        <li><strong>Registro</strong> Coordenadas GPS y grúa en el panel.</li>
        <li><strong>Pronóstico</strong> Modelo hiperlocal 72 h, actualización ~3 h.</li>
        <li><strong>Alertas</strong> Email / WhatsApp antes del umbral.</li>
        <li><strong>Decisión</strong> Ejecutar, postergar o suspender con datos.</li>
        <li><strong>Informe</strong> PDF de respaldo al cierre de la operación.</li>
      </ol>
    </section>

    <section id="alertas" class="section alt">
      <h2>Umbrales de izaje</h2>
      <p class="section-sub">Tres niveles claros. Editables desde plan Pro.</p>
      <div class="umbral-grid">
        <article class="umbral verde"><h3>≥26 km/h</h3><p>Precaución</p></article>
        <article class="umbral amarillo"><h3>≥31 km/h</h3><p>Suspensión recomendada</p></article>
        <article class="umbral rojo"><h3>≥36 km/h</h3><p>Suspensión obligatoria</p></article>
      </div>
    </section>

    <section id="precios" class="section">
      <h2>Planes</h2>
      <p class="section-sub">Sin tarifa por informe. Precios mensuales sin IVA.</p>
      <div class="plans">
        <article v-for="p in planesUi" :key="p.code" class="plan" :class="{ featured: p.featured }">
          <p class="plan-name">{{ p.nombre }}</p>
          <p class="plan-price">
            <template v-if="p.desde">Desde </template>
            <strong>{{ p.precioLabel }}</strong>
            <span v-if="p.precioLabel !== 'A convenir'">/mes</span>
          </p>
          <p class="plan-desc">{{ p.descripcion }}</p>
          <ul>
            <li v-for="(f, i) in p.bullets" :key="i">{{ f }}</li>
          </ul>
          <router-link class="btn" :class="p.featured ? 'solid' : 'ghost'" :to="registroPath">
            {{ p.cta }}
          </router-link>
        </article>
      </div>
    </section>

    <section id="faq" class="section alt">
      <h2>Preguntas frecuentes</h2>
      <details v-for="(item, i) in faq" :key="i" class="faq-item">
        <summary>{{ item.q }}</summary>
        <p>{{ item.a }}</p>
      </details>
    </section>

    <section class="cta-final">
      <h2>¿Listo para operar con certeza climática?</h2>
      <p>Piloto 15 días · sin tarjeta · soporte METGO 3D SpA</p>
      <div class="hero-actions">
        <router-link class="btn solid lg" :to="registroPath">Crear cuenta</router-link>
        <router-link class="btn ghost lg" :to="loginPath">Ya tengo acceso</router-link>
      </div>
    </section>

    <footer class="foot">
      <span>METGO 3D SpA · Santiago, Chile</span>
      <a href="mailto:contacto@metgo3d.com">contacto@metgo3d.com</a>
      <router-link v-if="isLoggedIn" to="/app">Ir a mis faenas</router-link>
    </footer>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { fetchPlanes, getToken } from '@/services/authApi'
import { useAuth } from '@/stores/auth'

const site = inject('site')
const auth = useAuth()
const loginPath = computed(() => '/login')
const registroPath = computed(() => '/registro')
const isLoggedIn = computed(() => Boolean(auth.state.token || getToken()))

const planesApi = ref([])

const FALLBACK = [
  {
    code: 'starter',
    nombre: 'Básico',
    precio_mensual_clp: 300_000,
    descripcion: '1 faena · hasta 2 grúas · Ahora + PDF · email',
    features: ['panel', 'ambiente', 'ahora', 'alertas'],
  },
  {
    code: 'pro',
    nombre: 'Pro',
    precio_mensual_clp: 500_000,
    recomendado: true,
    descripcion: 'Hasta 3 faenas · WhatsApp · umbrales · reporte mensual',
    features: ['dron', 'umbrales', 'reporte_mensual'],
  },
  {
    code: 'enterprise',
    nombre: 'Enterprise',
    precio_mensual_clp: 1_200_000,
    precio_etiqueta: 'desde',
    contacto: true,
    descripcion: 'Multi-faena · API · SLA 99.5% · AM 24/7 · ERP',
    features: ['multi_faena', 'api', 'sla'],
  },
]

const BULLETS = {
  starter: ['Vista Ahora + panel 72 h', '1 faena / 2 grúas', 'Alertas email', 'Informe PDF'],
  pro: ['Hasta 3 faenas / 5 grúas', 'WhatsApp + umbrales', 'Calibración dron', 'Reporte mensual ROI'],
  enterprise: ['Faenas ilimitadas + /ops', 'API + webhooks', 'SLA 99.5% + soporte 24/7', 'Integración ERP'],
}

function fmtClp(n) {
  if (n == null) return 'A convenir'
  return `$${Number(n).toLocaleString('es-CL')}`
}

const planesUi = computed(() => {
  const src = (planesApi.value || []).filter((p) =>
    ['starter', 'pro', 'enterprise'].includes(p.plan_code),
  )
  const list = src.length ? src : FALLBACK
  return list.map((p) => {
    const code = p.plan_code || p.code
    const desde = p.precio_etiqueta === 'desde' || code === 'enterprise'
    return {
      code,
      nombre: p.nombre || p.nombre_corto || code,
      precioLabel: fmtClp(p.precio_mensual_clp),
      desde,
      descripcion: p.descripcion || '',
      bullets: BULLETS[code] || (p.features || []).slice(0, 4),
      featured: Boolean(p.recomendado || code === 'pro'),
      cta: code === 'enterprise' ? 'Solicitar cotización' : 'Empezar',
    }
  })
})

const faq = [
  {
    q: '¿En qué se diferencia de Windy u Open-Meteo?',
    a: 'SPATI está calibrado para el punto GPS de su faena de izaje, con umbrales operativos, alertas a operadores e informe PDF de respaldo. No es meteorología genérica.',
  },
  {
    q: '¿Funciona en alta montaña?',
    a: 'Sí. Cubrimos faenas de altura en Chile. Sobre 3.000 msnm evaluamos con el plan Enterprise.',
  },
  {
    q: '¿El PDF sirve como respaldo?',
    a: 'El informe incluye coordenadas, serie 72 h, alertas y decisión registrada, con sello UTC. Pensado para fiscalización y mandantes.',
  },
  {
    q: '¿Cómo es el piloto?',
    a: '15 días sin costo ni tarjeta. Tras el piloto elige Básico, Pro o cotiza Enterprise.',
  },
]

function streakStyle(n) {
  const top = 8 + ((n * 7) % 80)
  const delay = (n * 0.35) % 3
  const dur = 2.2 + (n % 5) * 0.25
  return {
    top: `${top}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${dur}s`,
  }
}

onMounted(async () => {
  try {
    const data = await fetchPlanes('spati')
    planesApi.value = data.planes || []
  } catch {
    planesApi.value = []
  }
})
</script>

<style scoped>
.landing {
  --navy: #0f172a;
  --emer: #10b981;
  --blue: #3b82f6;
  --amber: #f59e0b;
  --red: #ef4444;
  --muted: #94a3b8;
  --line: #1e293b;
  min-height: 100vh;
  background: var(--spati-bg-atmosphere, radial-gradient(ellipse 80% 50% at 10% -10%, rgba(16, 185, 129, 0.18), transparent), radial-gradient(ellipse 60% 40% at 90% 10%, rgba(59, 130, 246, 0.12), transparent)), var(--navy);
  color: #e2e8f0;
  font-family: var(--font-sans, 'DM Sans', system-ui, sans-serif);
}
.top {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.85rem 1.25rem;
  background: rgba(15, 23, 42, 0.92);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(10px);
}
.brand {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  min-width: 5rem;
}
.brand-mark {
  font-weight: 900;
  letter-spacing: 0.06em;
  color: var(--emer);
  font-size: 1.05rem;
}
.brand-sub {
  font-size: 0.68rem;
  color: var(--muted);
}
.nav {
  display: none;
  gap: 1rem;
  margin-left: auto;
}
.nav a {
  color: var(--muted);
  text-decoration: none;
  font-size: 0.88rem;
  font-weight: 600;
}
.nav a:hover {
  color: #fff;
}
.top-cta {
  display: flex;
  gap: 0.5rem;
  margin-left: auto;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0.95rem;
  border-radius: 9px;
  font-weight: 700;
  font-size: 0.88rem;
  text-decoration: none;
  border: 1px solid transparent;
  cursor: pointer;
}
.btn.solid {
  background: var(--emer);
  color: var(--navy);
}
.btn.ghost {
  background: transparent;
  border-color: #334155;
  color: #e2e8f0;
}
.btn.lg {
  padding: 0.7rem 1.2rem;
  font-size: 0.95rem;
}

.hero {
  display: grid;
  gap: 2rem;
  padding: 2.5rem 1.25rem 3rem;
  max-width: 1100px;
  margin: 0 auto;
}
.eyebrow {
  color: var(--emer);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin: 0 0 0.75rem;
}
.hero h1 {
  margin: 0;
  font-size: clamp(2rem, 5vw, 3.2rem);
  font-weight: 900;
  line-height: 1.08;
  letter-spacing: -0.03em;
  color: #fff;
}
.hero h1 em {
  font-style: normal;
  color: var(--emer);
}
.lede {
  margin: 1rem 0 1.4rem;
  color: var(--muted);
  font-size: 1.05rem;
  line-height: 1.55;
  max-width: 34rem;
}
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}
.stats {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
  padding: 0;
  margin: 1.75rem 0 0;
}
.stats li {
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.7rem 0.55rem;
  text-align: center;
  background: rgba(30, 41, 59, 0.55);
}
.stats strong {
  display: block;
  color: var(--emer);
  font-size: 1.05rem;
}
.stats span {
  font-size: 0.7rem;
  color: var(--muted);
}

.hero-visual {
  display: flex;
  align-items: center;
  justify-content: center;
}
.wind-card {
  width: min(100%, 420px);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #334155;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
}
.wind-sky {
  position: relative;
  height: 220px;
  background: linear-gradient(160deg, #0b3d4a, #0f172a 55%, #1e293b);
  overflow: hidden;
}
.streak {
  position: absolute;
  left: -20%;
  width: 40%;
  height: 2px;
  border-radius: 2px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.75), transparent);
  animation: blow linear infinite;
  opacity: 0.55;
}
@keyframes blow {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(280%);
  }
}
.wind-readout {
  padding: 0.9rem 1rem 1.1rem;
  background: #111827;
  display: grid;
  gap: 0.25rem;
}
.lvl {
  width: fit-content;
  font-size: 0.68rem;
  font-weight: 800;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
}
.lvl.amarillo {
  background: var(--amber);
  color: #0f172a;
}
.wind-readout strong {
  font-size: 1.6rem;
  color: #fff;
}
.muted {
  color: var(--muted);
  font-size: 0.82rem;
}

.section {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2.5rem 1.25rem;
}
.section.alt {
  background: rgba(15, 23, 42, 0.55);
  max-width: none;
  padding-left: max(1.25rem, calc((100% - 1100px) / 2 + 1.25rem));
  padding-right: max(1.25rem, calc((100% - 1100px) / 2 + 1.25rem));
}
.section h2 {
  margin: 0;
  font-size: 1.55rem;
  color: #fff;
}
.section-sub {
  color: var(--muted);
  margin: 0.4rem 0 1.4rem;
}
.steps {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.75rem;
}
.steps li {
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.9rem 1rem;
  background: rgba(30, 41, 59, 0.4);
  counter-increment: step;
}
.steps li strong {
  color: var(--emer);
  margin-right: 0.4rem;
}

.umbral-grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}
.umbral {
  border-radius: 12px;
  padding: 1.1rem;
  text-align: center;
}
.umbral h3 {
  margin: 0 0 0.35rem;
  font-size: 1.25rem;
}
.umbral p {
  margin: 0;
  font-weight: 700;
}
.umbral.verde {
  background: rgba(16, 185, 129, 0.18);
  border: 1px solid #10b98166;
}
.umbral.amarillo {
  background: rgba(245, 158, 11, 0.18);
  border: 1px solid #f59e0b66;
}
.umbral.rojo {
  background: rgba(239, 68, 68, 0.18);
  border: 1px solid #ef444466;
}

.plans {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}
.plan {
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 1.25rem;
  background: rgba(30, 41, 59, 0.45);
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}
.plan.featured {
  border-color: var(--emer);
  box-shadow: 0 0 0 1px rgba(16, 185, 129, 0.35);
}
.plan-name {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}
.plan-price {
  margin: 0;
  font-size: 0.9rem;
  color: var(--muted);
}
.plan-price strong {
  font-size: 1.55rem;
  color: #fff;
}
.plan-desc {
  margin: 0;
  font-size: 0.88rem;
  color: var(--muted);
  line-height: 1.45;
  min-height: 2.6rem;
}
.plan ul {
  margin: 0.25rem 0 0.75rem;
  padding: 0 0 0 1rem;
  color: #cbd5e1;
  font-size: 0.88rem;
  flex: 1;
}
.plan .btn {
  width: 100%;
}

.faq-item {
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.85rem 1rem;
  margin-bottom: 0.55rem;
  background: rgba(30, 41, 59, 0.35);
}
.faq-item summary {
  cursor: pointer;
  font-weight: 700;
  color: #fff;
}
.faq-item p {
  margin: 0.55rem 0 0;
  color: var(--muted);
  line-height: 1.5;
  font-size: 0.92rem;
}

.cta-final {
  text-align: center;
  padding: 3rem 1.25rem;
  background: linear-gradient(180deg, transparent, rgba(16, 185, 129, 0.08));
}
.cta-final h2 {
  margin: 0 0 0.4rem;
  color: #fff;
}
.cta-final p {
  color: var(--muted);
  margin: 0 0 1.2rem;
}
.cta-final .hero-actions {
  justify-content: center;
}

.foot {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1.25rem;
  justify-content: space-between;
  padding: 1.25rem;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.8rem;
}
.foot a {
  color: var(--emer);
  text-decoration: none;
}

@media (min-width: 880px) {
  .nav {
    display: flex;
  }
  .top-cta {
    margin-left: 0;
  }
  .hero {
    grid-template-columns: 1.1fr 0.9fr;
    align-items: center;
    padding-top: 3.5rem;
  }
}
@media (max-width: 560px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
  }
  .top .nav {
    display: none;
  }
}
</style>
