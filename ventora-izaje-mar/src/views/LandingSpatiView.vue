<template>
  <div class="landing">
    <a href="#inicio" class="skip-link">{{ t('app.skipContent') }}</a>
    <header class="top">
      <a class="brand" href="#inicio">
        <span class="brand-mark">{{ site.brandName || 'VENTORA' }}</span>
        <span class="brand-sub">Operaciones Marítimas</span>
      </a>
      <nav class="nav" :aria-label="t('landing.navHow')">
        <a href="#como">{{ t('landing.navHow') }}</a>
        <a href="#alertas">{{ t('landing.navAlerts') }}</a>
        <a href="#solucion">{{ t('landing.navSolution') }}</a>
        <a href="#impacto">{{ t('landing.navImpact') }}</a>
        <a href="#precios">{{ t('landing.navPlans') }}</a>
        <a href="#faq">{{ t('landing.navFaq') }}</a>
      </nav>
      <div class="top-cta">
        <div class="lang-switch" role="group" :aria-label="t('lang.label')">
          <button type="button" :class="{ active: locale === 'es' }" @click="setLocale('es')">
            {{ t('lang.es') }}
          </button>
          <button type="button" :class="{ active: locale === 'en' }" @click="setLocale('en')">
            {{ t('lang.en') }}
          </button>
        </div>
        <router-link class="btn ghost" :to="loginPath">{{ t('landing.login') }}</router-link>
        <router-link class="btn solid" :to="registroPath">{{ t('landing.pilotCta') }}</router-link>
      </div>
    </header>

    <section id="inicio" class="hero">
      <div class="hero-copy">
        <p class="eyebrow">{{ t('landing.eyebrow') }}</p>
        <h1>
          {{ t('landing.heroTitle') }}<br />
          <em>{{ t('landing.heroTitleEm', { brand: site.brandName || 'VENTORA' }) }}</em>
        </h1>
        <p class="lede">{{ t('landing.lede') }}</p>
        <div class="hero-actions">
          <router-link class="btn solid lg" :to="registroPath">{{ t('landing.startPilot') }}</router-link>
          <a class="btn ghost lg" href="#precios">{{ t('landing.seePlans') }}</a>
        </div>
        <ul class="stats">
          <li><strong>72 h</strong><span>{{ t('landing.statHorizon') }}</span></li>
          <li><strong>18+ h</strong><span>{{ t('landing.statLead') }}</span></li>
          <li><strong>88–94%</strong><span>{{ t('landing.statAccuracy') }}</span></li>
          <li><strong>&lt;5 min</strong><span>{{ t('landing.statLatency') }}</span></li>
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
      <h2>{{ t('landing.howTitle') }}</h2>
      <p class="section-sub">{{ t('landing.howSub') }}</p>
      <ol class="steps">
        <li><strong>Configuración</strong> Defina su puerto, grúas STS y área de fondeo.</li>
        <li><strong>Pronóstico</strong> Modelo costero 72 h con actualización dinámica.</li>
        <li><strong>Alertas</strong> Notificaciones automáticas por umbrales de viento y oleaje.</li>
        <li><strong>Decisión</strong> Información precisa para amarrar naves o suspender izaje.</li>
        <li><strong>Informe</strong> PDF de respaldo al cierre del turno operativo.</li>
      </ol>
    </section>

    <section id="alertas" class="section alt">
      <h2>{{ t('landing.alertsTitle') }}</h2>
      <p class="section-sub">{{ t('landing.alertsSub') }}</p>
      <div class="umbral-grid">
        <article class="umbral verde"><h3>≥26 km/h</h3><p>{{ t('landing.caution') }}</p></article>
        <article class="umbral amarillo"><h3>≥31 km/h</h3><p>{{ t('landing.suspendRec') }}</p></article>
        <article class="umbral rojo"><h3>≥36 km/h</h3><p>{{ t('landing.suspendReq') }}</p></article>
      </div>
    </section>

    <section id="solucion" class="section">
      <h2>{{ t('landing.solutionTitle') }}</h2>
      <p class="section-sub">{{ t('landing.solutionSub') }}</p>
      <div class="pillars">
        <article class="pillar">
          <div class="pillar-icon software-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
          </div>
          <h3>{{ t('landing.pillarSoftware') }}</h3>
          <p>{{ t('landing.pillarSoftwareDesc') }}</p>
          <ul>
            <li>{{ t('landing.pillarSw1') }}</li>
            <li>{{ t('landing.pillarSw2') }}</li>
            <li>{{ t('landing.pillarSw3') }}</li>
          </ul>
        </article>
        <article class="pillar">
          <div class="pillar-icon hardware-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v6M12 18v4M4.93 4.93l4.24 4.24M14.83 14.83l4.24 4.24M2 12h6M18 12h4M4.93 19.07l4.24-4.24M14.83 9.17l4.24-4.24"/></svg>
          </div>
          <h3>{{ t('landing.pillarHardware') }}</h3>
          <p>{{ t('landing.pillarHardwareDesc') }}</p>
          <ul>
            <li>{{ t('landing.pillarHw1') }}</li>
            <li>{{ t('landing.pillarHw2') }}</li>
            <li>{{ t('landing.pillarHw3') }}</li>
          </ul>
        </article>
        <article class="pillar">
          <div class="pillar-icon services-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
          </div>
          <h3>{{ t('landing.pillarServices') }}</h3>
          <p>{{ t('landing.pillarServicesDesc') }}</p>
          <ul>
            <li>{{ t('landing.pillarSv1') }}</li>
            <li>{{ t('landing.pillarSv2') }}</li>
            <li>{{ t('landing.pillarSv3') }}</li>
          </ul>
        </article>
      </div>
      <div class="compliance-row">
        <span class="badge">DS 59</span>
        <span class="badge">DS 138</span>
        <span class="badge">WMO</span>
        <span class="badge">SHOA</span>
        <span class="badge">ISGOTT</span>
      </div>
    </section>

    <section id="impacto" class="section alt">
      <h2>{{ t('landing.impactTitle') }}</h2>
      <p class="section-sub">{{ t('landing.impactSub') }}</p>
      <div class="impact-grid">
        <article class="impact-card">
          <strong class="impact-number">480x</strong>
          <span class="impact-label">{{ t('landing.impactRoiAgro') }}</span>
          <p class="impact-detail">{{ t('landing.impactRoiAgroDetail') }}</p>
        </article>
        <article class="impact-card">
          <strong class="impact-number">135h</strong>
          <span class="impact-label">{{ t('landing.impactHoursMining') }}</span>
          <p class="impact-detail">{{ t('landing.impactHoursMiningDetail') }}</p>
        </article>
        <article class="impact-card">
          <strong class="impact-number">0</strong>
          <span class="impact-label">{{ t('landing.impactAccidents') }}</span>
          <p class="impact-detail">{{ t('landing.impactAccidentsDetail') }}</p>
        </article>
      </div>
    </section>

    <section id="precios" class="section">
      <h2>{{ t('landing.plansTitle') }}</h2>
      <p class="section-sub">{{ t('landing.plansSub') }}</p>
      <div class="plans">
        <article v-for="p in planesUi" :key="p.code" class="plan" :class="{ featured: p.featured }">
          <p class="plan-name">{{ p.nombre }}</p>
          <p v-if="p.precio" class="plan-price">{{ p.precio }}</p>
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
      <h2>{{ t('landing.faqTitle') }}</h2>
      <details v-for="(item, i) in faq" :key="i" class="faq-item">
        <summary>{{ item.q }}</summary>
        <p>{{ item.a }}</p>
      </details>
    </section>

    <section class="cta-final">
      <h2>{{ t('landing.ctaTitle') }}</h2>
      <p>{{ t('landing.ctaSub') }}</p>
      <div class="hero-actions">
        <router-link class="btn solid lg" :to="registroPath">{{ t('landing.createAccount') }}</router-link>
        <router-link class="btn ghost lg" :to="loginPath">{{ t('landing.haveAccess') }}</router-link>
      </div>
    </section>

    <footer class="foot">
      <span>METGO 3D SpA · Santiago, Chile</span>
      <span class="giro">Servicios de análisis meteorológico, inteligencia climática y desarrollo de plataformas tecnológicas para la gestión de riesgos ambientales y operacionales.</span>
      <a href="mailto:miguel.lucero@metgo3d.com">miguel.lucero@metgo3d.com</a>
      <router-link v-if="isLoggedIn" to="/app">{{ t('landing.goHub') }}</router-link>
    </footer>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchPlanes, getToken } from '@/services/authApi'
import { useAuth } from '@/stores/auth'
import { setLocale } from '@/i18n'

const { t, locale } = useI18n()
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
    descripcion: '1 terminal · pronóstico 72 h · alertas viento · informe PDF',
    features: ['panel', 'ambiente', 'ahora', 'alertas'],
  },
  {
    code: 'pro',
    nombre: 'Pro',
    recomendado: true,
    descripcion: 'Hasta 3 terminales · fondeo de naves · WhatsApp · oleaje',
    features: ['dron', 'umbrales', 'reporte_mensual'],
  },
  {
    code: 'enterprise',
    nombre: 'Enterprise',
    contacto: true,
    descripcion: 'Multi-puerto · SLA 99.9% · viento a +100m para grúas STS · API',
    features: ['multi_faena', 'api', 'sla'],
  },
]

const BULLETS = {
  starter: ['Panel Marítimo 72 h', '1 terminal', 'Alertas email', 'Informe PDF'],
  pro: ['Hasta 3 terminales', 'Pronóstico de oleaje y fondeo', 'Alertas por WhatsApp', 'Reporte mensual de métricas'],
  enterprise: ['Puertos ilimitados + Centro de Ops', 'Soporte 24/7 y SLA 99.9%', 'Perfil vertical para grúas STS', 'Integración ERP / API'],
}

const planesUi = computed(() => {
  const src = (planesApi.value || []).filter((p) =>
    ['starter', 'pro', 'enterprise'].includes(p.plan_code),
  )
  const list = src.length ? src : FALLBACK
  return list.map((p) => {
    const code = p.plan_code || p.code
      return {
      code,
      nombre: p.nombre || p.nombre_corto || code,
      precio: precioLinea(p),
      descripcion: p.descripcion || '',
      bullets: BULLETS[code] || (p.features || []).slice(0, 4),
      featured: Boolean(p.recomendado || code === 'pro'),
      cta: code === 'enterprise' ? 'Solicitar cotización' : 'Empezar',
    }
  })
})

function precioLinea(p) {
  const usd = p.precio_mensual_usd
  if (usd == null) return ''
  const tag = p.precio_etiqueta === 'desde' ? 'Desde ' : ''
  if (Number(usd) === 0) return 'Piloto sin costo'
  return `${tag}USD ${Number(usd).toLocaleString('en-US')}/mes`
}

const faq = [
  {
    q: '¿En qué se diferencia de aplicaciones genéricas de clima?',
    a: 'VENTORA Izaje Mar está calibrado para el contexto marítimo-portuario, incluyendo altura de grúas STS, oleaje y límites de fondeo, en lugar de ser meteorología genérica.',
  },
  {
    q: '¿Incluye predicción de oleaje y mareas?',
    a: 'El oleaje (altura y período) usa datos reales de modelos meteorológicos (Open-Meteo Marine, ensamble ECMWF/ICON/GFS para viento). El estado de marea se calcula con una aproximación astronómica de referencia mientras se integra una fuente en tiempo real; se muestra siempre etiquetado en la API para que el operador sepa qué dato es cuál.',
  },
  {
    q: '¿El PDF sirve como respaldo?',
    a: 'El informe registra las ráfagas y el umbral exacto que forzó una suspensión de maniobra de atraque o izaje, con marca de tiempo UTC como evidencia.',
  },
  {
    q: '¿Tienen un periodo de prueba?',
    a: 'Sí, contamos con un plan piloto para un puerto sin costo durante 15 días, permitiendo evaluar el retorno de la plataforma.',
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
  --emer: #0ea5e9; /* Cambiado de verde a Ocean Cyan para Ventora */
  --blue: #3b82f6;
  --amber: #f59e0b;
  --red: #ef4444;
  --muted: #94a3b8;
  --line: #1e293b;
  min-height: 100vh;
  background: var(--spati-bg-atmosphere, radial-gradient(ellipse 80% 50% at 10% -10%, rgba(14, 165, 233, 0.18), transparent), radial-gradient(ellipse 60% 40% at 90% 10%, rgba(59, 130, 246, 0.12), transparent)), var(--navy);
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
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.lang-switch {
  display: inline-flex;
  gap: 0.25rem;
  margin-right: 0.25rem;
}
.lang-switch button {
  border: 1px solid #334155;
  background: transparent;
  color: #94a3b8;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.45rem;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
}
.lang-switch button.active {
  color: var(--emer);
  border-color: var(--emer);
  background: rgba(16, 185, 129, 0.12);
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
  background: rgba(14, 165, 233, 0.18);
  border: 1px solid #0ea5e966;
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
  box-shadow: 0 0 0 1px rgba(14, 165, 233, 0.35);
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
  font-size: 1.45rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #e2e8f0;
}
.plan.featured .plan-price {
  color: var(--emer);
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
  background: linear-gradient(180deg, transparent, rgba(14, 165, 233, 0.08));
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
.foot .giro {
  flex: 1 1 100%;
  max-width: 52rem;
  line-height: 1.45;
  font-size: 0.75rem;
  opacity: 0.9;
}
.foot a {
  color: var(--emer);
  text-decoration: none;
}

/* ===== PILARES (Solución Integral) ===== */
.pillars {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  margin-top: 0.5rem;
}
.pillar {
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 1.35rem;
  background: rgba(30, 41, 59, 0.45);
  transition: border-color 0.3s, box-shadow 0.3s;
}
.pillar:hover {
  border-color: var(--emer);
  box-shadow: 0 0 20px rgba(14, 165, 233, 0.15);
}
.pillar-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}
.software-icon {
  background: rgba(14, 165, 233, 0.15);
  color: var(--emer);
}
.hardware-icon {
  background: rgba(245, 158, 11, 0.15);
  color: var(--amber);
}
.services-icon {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}
.pillar h3 {
  margin: 0 0 0.4rem;
  font-size: 1.05rem;
  color: #fff;
}
.pillar > p {
  margin: 0 0 0.65rem;
  color: var(--muted);
  font-size: 0.88rem;
  line-height: 1.45;
}
.pillar ul {
  margin: 0;
  padding: 0 0 0 1rem;
  color: #cbd5e1;
  font-size: 0.85rem;
}
.pillar ul li {
  margin-bottom: 0.25rem;
}

/* ===== COMPLIANCE BADGES ===== */
.compliance-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1.5rem;
}
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  background: rgba(14, 165, 233, 0.12);
  color: var(--emer);
  border: 1px solid rgba(14, 165, 233, 0.25);
}

/* ===== IMPACT GRID ===== */
.impact-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
.impact-card {
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 1.35rem;
  text-align: center;
  background: rgba(30, 41, 59, 0.45);
  transition: transform 0.3s, box-shadow 0.3s;
}
.impact-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
}
.impact-number {
  display: block;
  font-size: 2.2rem;
  font-weight: 900;
  letter-spacing: -0.04em;
  background: linear-gradient(135deg, var(--emer), var(--blue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.impact-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 700;
  color: #e2e8f0;
  margin: 0.3rem 0 0.5rem;
}
.impact-detail {
  margin: 0;
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.45;
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
