<template>
  <div class="landing">
    <a href="#inicio" class="skip-link">{{ t('app.skipContent') }}</a>

    <header class="top">
      <nav class="nav" aria-label="Principal">
        <a href="#inicio" class="brand">
          <span class="brand-icon" aria-hidden="true">
            <Leaf :size="17" />
          </span>
          <span class="brand-text">
            <span class="brand-name">METGO</span>
            <span class="brand-sub">QUILLOTA</span>
          </span>
        </a>
        <div class="nav-links">
          <router-link to="/planes">Planes</router-link>
          <router-link to="/nosotros">Nosotros</router-link>
          <router-link to="/contacto">Contacto</router-link>
        </div>
        <div class="nav-cta">
          <div class="lang-switch" role="group" :aria-label="t('lang.label')">
            <button type="button" :class="{ active: locale === 'es' }" @click="setLocale('es')">
              {{ t('lang.es') }}
            </button>
            <button type="button" :class="{ active: locale === 'en' }" @click="setLocale('en')">
              {{ t('lang.en') }}
            </button>
          </div>
          <template v-if="isLoggedIn">
            <router-link class="btn btn-primary" to="/app">{{ t('landing.goPanel') }}</router-link>
          </template>
          <template v-else>
            <router-link class="btn btn-ghost" to="/login">{{ t('landing.login') }}</router-link>
            <router-link class="btn btn-primary" :to="accessPath">{{ t('landing.requestAccess') }}</router-link>
          </template>
        </div>
      </nav>
    </header>

    <main>
      <section id="inicio" class="hero">
        <div class="wrap hero-grid">
          <div>
            <p class="eyebrow">{{ t('landing.eyebrow') }}</p>
            <h1>
              {{ t('landing.heroTitle') }}
            </h1>
            <p class="hero-sub">{{ t('landing.heroSub') }}</p>
            <div class="hero-actions">
              <router-link class="btn btn-primary btn-lg" to="/contacto">
                {{ t('landing.requestDemo') }}
              </router-link>
              <router-link class="btn btn-ghost btn-lg" to="/app">
                {{ t('landing.viewLivePanel') }}
              </router-link>
            </div>
            <div class="hero-meta">
              <div>
                <strong>3+</strong>
                {{ t('landing.metaFaenas') }}
              </div>
              <div>
                <strong>1.200+</strong>
                {{ t('landing.metaAlertas') }}
              </div>
              <div>
                <strong>4</strong>
                {{ t('landing.metaAnos') }}
              </div>
            </div>
          </div>

          <div class="card live-card">
            <div class="live-head">
              <span class="live-title">{{ t('landing.liveTitle') }}</span>
              <span class="live-dot">
                <span class="pulse" aria-hidden="true" />
                {{ meteoLoading ? t('landing.liveLoading') : t('landing.liveNow') }}
              </span>
            </div>
            <p class="live-location">{{ estacionNombre }}</p>
            <p class="live-sub">{{ t('landing.liveSubPanel') }}</p>

            <!-- Misma lógica visual que el Panel general -->
            <div class="panel-metrics">
              <div class="metric">
                <span class="metric-label">{{ t('landing.metricMean') }}</span>
                <strong>{{ formatTemp(meteo?.temperatura) }}</strong>
              </div>
              <div class="metric" :class="{ 'metric--alert': helada.nivel === 'high' }">
                <span class="metric-label">{{ t('landing.metricMin') }}</span>
                <strong>{{ formatTemp(meteo?.temperatura_min) }}</strong>
              </div>
              <div class="metric">
                <span class="metric-label">{{ t('landing.metricMax') }}</span>
                <strong>{{ formatTemp(meteo?.temperatura_max) }}</strong>
              </div>
            </div>

            <div class="insight-chip insight-chip--frost" :class="`insight-chip--${helada.nivel}`">
              <FrostBadge v-if="helada.nivel !== 'low'" size="sm" />
              <span><strong>{{ t('landing.frostLabel') }}:</strong> {{ helada.label }}</span>
            </div>

            <div v-if="helada.nivel === 'high' || helada.nivel === 'medium'" class="live-alert" role="status">
              <span class="dot2" aria-hidden="true" />
              <p>{{ accionHelada }}</p>
            </div>
            <p v-else-if="meteoError" class="live-fallback">{{ t('landing.liveFallback') }}</p>

            <router-link class="live-link" to="/login">{{ t('landing.seeInPanel') }} →</router-link>
          </div>
        </div>
      </section>

      <section class="innov wrap" aria-labelledby="innov-title">
        <h2 id="innov-title">{{ t('landing.innovTitle') }}</h2>
        <p class="innov-sub">{{ t('landing.innovSub') }}</p>
        <div class="innov-grid">
          <article>
            <h3>{{ t('landing.innov1Title') }}</h3>
            <p>{{ t('landing.innov1Body') }}</p>
            <a href="https://metgo-spati.pages.dev" target="_blank" rel="noopener">VENTORA →</a>
          </article>
          <article>
            <h3>{{ t('landing.innov2Title') }}</h3>
            <p>{{ t('landing.innov2Body') }}</p>
            <a href="https://metgo-copiapo.pages.dev" target="_blank" rel="noopener">Copiapó →</a>
          </article>
          <article>
            <h3>{{ t('landing.innov3Title') }}</h3>
            <p>{{ t('landing.innov3Body') }}</p>
            <router-link to="/planes">{{ t('landing.innovCta') }} →</router-link>
          </article>
        </div>
        <p class="innov-mail">
          Demo / cotización:
          <a href="mailto:miguel.lucero@metgo3d.com">miguel.lucero@metgo3d.com</a>
        </p>
      </section>

      <div class="stats">
        <div class="wrap stats-grid">
          <div>
            <div class="stat-num"><span>18+</span> h</div>
            <div class="stat-label">{{ t('landing.statFrost') }}</div>
          </div>
          <div>
            <div class="stat-num">±<span>0.6</span>°C</div>
            <div class="stat-label">{{ t('landing.statError') }}</div>
          </div>
          <div>
            <div class="stat-num"><span>&lt;5</span> min</div>
            <div class="stat-label">{{ t('landing.statLatency') }}</div>
          </div>
          <div>
            <div class="stat-num"><span>100</span>%</div>
            <div class="stat-label">{{ t('landing.statPdf') }}</div>
          </div>
        </div>
      </div>

      <section id="servicios">
        <div class="wrap">
          <div class="section-head">
            <p class="section-eyebrow">{{ t('landing.modulesEyebrow') }}</p>
            <h2>{{ t('landing.modulesTitle') }}</h2>
            <p class="section-desc">{{ t('landing.modulesDesc') }}</p>
          </div>
          <div class="feat-grid">
            <article v-for="f in features" :key="f.title" class="feat">
              <div class="feat-icon" aria-hidden="true">
                <component :is="f.icon" :size="18" />
              </div>
              <h3>{{ f.title }}</h3>
              <p>{{ f.body }}</p>
            </article>
          </div>
        </div>
      </section>

      <section id="funciona">
        <div class="wrap">
          <div class="section-head">
            <p class="section-eyebrow">{{ t('landing.howEyebrow') }}</p>
            <h2>{{ t('landing.howTitle') }}</h2>
            <p class="section-desc">{{ t('landing.howDesc') }}</p>
          </div>
          <div class="steps">
            <div v-for="(s, i) in steps" :key="s.title" class="step">
              <span class="step-num">{{ String(i + 1).padStart(2, '0') }}</span>
              <div>
                <h4>{{ s.title }}</h4>
                <p>{{ s.body }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="alertas">
        <div class="wrap">
          <div class="section-head">
            <p class="section-eyebrow">{{ t('landing.alertsEyebrow') }}</p>
            <h2>{{ t('landing.alertsTitle') }}</h2>
            <p class="section-desc">{{ t('landing.alertsDesc') }}</p>
          </div>
          <div class="alert-grid">
            <div class="card alert-tier alert-tier--ok">
              <strong>{{ t('landing.alertOk') }}</strong>
              <p>{{ t('landing.alertOkDesc') }}</p>
            </div>
            <div class="card alert-tier alert-tier--warn">
              <strong>{{ t('landing.alertWarn') }}</strong>
              <p>{{ t('landing.alertWarnDesc') }}</p>
            </div>
            <div class="card alert-tier alert-tier--bad">
              <strong>{{ t('landing.alertBad') }}</strong>
              <p>{{ t('landing.alertBadDesc') }}</p>
            </div>
          </div>
        </div>
      </section>

      <section id="faq">
        <div class="wrap">
          <div class="section-head">
            <p class="section-eyebrow">FAQ</p>
            <h2>{{ t('landing.faqTitle') }}</h2>
          </div>
          <div class="faq-list">
            <details v-for="item in faqs" :key="item.q" class="faq-item">
              <summary>{{ item.q }}</summary>
              <p>{{ item.a }}</p>
            </details>
          </div>
        </div>
      </section>

      <section id="cta">
        <div class="wrap">
          <div class="cta-band">
            <h2>{{ t('landing.ctaTitle') }}</h2>
            <p>{{ t('landing.ctaSub') }}</p>
            <div class="cta-actions">
              <router-link v-if="isLoggedIn" class="btn btn-primary btn-lg" to="/app">
                {{ t('landing.goPanel') }}
              </router-link>
              <template v-else>
                <router-link class="btn btn-primary btn-lg" to="/login">{{ t('landing.login') }}</router-link>
                <router-link class="btn btn-ghost btn-lg" :to="accessPath">
                  {{ t('landing.requestAccess') }}
                </router-link>
              </template>
              <a href="#servicios" class="btn btn-ghost btn-lg">{{ t('landing.seeModules') }}</a>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer class="foot">
      <div class="wrap foot-row">
        <div class="foot-brand">
          <span class="brand-icon brand-icon--sm" aria-hidden="true"><Leaf :size="12" /></span>
          {{ t('landing.footerBrand') }}
        </div>
        <div class="foot-links">
          <router-link to="/planes">Planes</router-link>
          <router-link to="/nosotros">Nosotros</router-link>
          <router-link to="/contacto">Contacto</router-link>
          <router-link to="/login">{{ t('landing.login') }}</router-link>
          <router-link v-if="isLoggedIn" to="/app">{{ t('landing.goPanel') }}</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Leaf,
  LogIn,
  LayoutDashboard,
  ThermometerSnowflake,
  Droplets,
  Wind,
  FileText,
} from 'lucide-vue-next'
import { setLocale } from '@/i18n'
import { useAuthStore } from '@/stores/auth'
import FrostBadge from '@/components/meteo/FrostBadge.vue'
import { riesgoHelada } from '@/utils/agroInsights'
import { fetchPublicMeteo } from '@/api/metgoApi'

const ESTACION_LANDING = 'quillota'

const { t, locale } = useI18n()
const auth = useAuthStore()
const isLoggedIn = computed(() => auth.isAuthenticated)
const accessPath = '/registro'

const meteo = ref(null)
const meteoLoading = ref(true)
const meteoError = ref(false)

const estacionNombre = computed(
  () => meteo.value?.estacion || meteo.value?.nombre || t('landing.liveLocation'),
)
const helada = computed(() => riesgoHelada(meteo.value?.temperatura_min))

const accionHelada = computed(() => {
  if (helada.value.nivel === 'high') return t('landing.frostActionHigh')
  if (helada.value.nivel === 'medium') return t('landing.frostActionMed')
  return ''
})

function formatTemp(v) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return `${Number(v).toFixed(1)}°C`
}

onMounted(async () => {
  meteoLoading.value = true
  meteoError.value = false
  try {
    meteo.value = await fetchPublicMeteo(ESTACION_LANDING)
  } catch {
    meteoError.value = true
    // Fallback ilustrativo alineado a umbrales del panel (palto)
    meteo.value = {
      estacion: 'Quillota',
      temperatura: 8.5,
      temperatura_min: -0.5,
      temperatura_max: 14.2,
    }
  } finally {
    meteoLoading.value = false
  }
})

const features = computed(() => [
  { icon: ThermometerSnowflake, title: t('landing.featFrostTitle'), body: t('landing.featFrostBody') },
  { icon: Droplets, title: t('landing.featEtTitle'), body: t('landing.featEtBody') },
  { icon: Wind, title: t('landing.featSprayTitle'), body: t('landing.featSprayBody') },
  { icon: FileText, title: t('landing.featPdfTitle'), body: t('landing.featPdfBody') },
])

const steps = computed(() => [
  { title: t('landing.step1Title'), body: t('landing.step1Body') },
  { title: t('landing.step2Title'), body: t('landing.step2Body') },
  { title: t('landing.step3Title'), body: t('landing.step3Body') },
  { title: t('landing.step4Title'), body: t('landing.step4Body') },
])

const faqs = computed(() => [
  { q: t('landing.faq1q'), a: t('landing.faq1a') },
  { q: t('landing.faq2q'), a: t('landing.faq2a') },
  { q: t('landing.faq3q'), a: t('landing.faq3a') },
])
</script>

<style scoped>
.landing {
  --bg: #080c14;
  --bg-glow: radial-gradient(ellipse 900px 500px at 15% -10%, rgba(0, 255, 170, 0.1), transparent 60%),
    radial-gradient(ellipse 700px 500px at 100% 20%, rgba(14, 165, 233, 0.06), transparent 55%);
  --surface: #121a2b;
  --surface-2: #0d1420;
  --border: rgba(255, 255, 255, 0.08);
  --border-accent: rgba(0, 255, 170, 0.28);
  --accent: #00ffaa;
  --accent-dim: rgba(0, 255, 170, 0.12);
  --text: #f4f7fa;
  --muted: #8fa0b3;
  --dim: #4c5a70;
  --amber: #f5b942;
  --red: #ef5b5b;
  --mono: ui-monospace, 'SF Mono', 'Cascadia Code', 'Segoe UI Mono', monospace;
  min-height: 100vh;
  background: var(--bg);
  background-image: var(--bg-glow);
  background-attachment: fixed;
  color: var(--text);
  font-family: 'DM Sans', system-ui, sans-serif;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
.landing a {
  color: inherit;
  text-decoration: none;
}
.wrap {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 28px;
}
.skip-link {
  position: absolute;
  left: -9999px;
  top: 0;
  z-index: 100;
  padding: 0.75rem 1rem;
  background: var(--accent);
  color: #04140e;
  font-weight: 700;
}
.skip-link:focus {
  left: 1rem;
  top: 1rem;
}
a:focus-visible,
button:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
  border-radius: 4px;
}

.top {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(8, 12, 20, 0.82);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
}
.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 28px;
  max-width: 1120px;
  margin: 0 auto;
  gap: 1rem;
}
.brand {
  display: flex;
  align-items: center;
  gap: 11px;
}
.brand-icon {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background: linear-gradient(145deg, #2ef2b8, #0fae7d);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #04140e;
  box-shadow: 0 4px 16px rgba(0, 255, 170, 0.35);
  flex-shrink: 0;
}
.brand-icon--sm {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  box-shadow: none;
}
.brand-name {
  display: block;
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 0.3px;
}
.brand-sub {
  display: block;
  font-size: 10px;
  color: var(--dim);
  font-family: var(--mono);
  letter-spacing: 1px;
  margin-top: 1px;
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 30px;
}
.nav-links a {
  font-size: 13.5px;
  color: var(--muted);
  transition: color 0.15s;
}
.nav-links a:hover {
  color: var(--text);
}
.nav-cta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.lang-switch {
  display: flex;
  gap: 4px;
  margin-right: 4px;
}
.lang-switch button {
  border: 1px solid var(--border);
  background: transparent;
  color: var(--muted);
  border-radius: 6px;
  padding: 0.2rem 0.45rem;
  font-size: 0.72rem;
  font-weight: 700;
  cursor: pointer;
}
.lang-switch button.active {
  border-color: var(--border-accent);
  color: var(--accent);
  background: var(--accent-dim);
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  font-size: 13.5px;
  font-weight: 600;
  padding: 9px 18px;
  border-radius: 9px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s, background 0.15s;
  white-space: nowrap;
}
.btn-primary {
  background: var(--accent);
  color: #04140e;
}
.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(0, 255, 170, 0.3);
}
.btn-ghost {
  border-color: var(--border);
  color: var(--text);
  background: transparent;
}
.btn-ghost:hover {
  border-color: var(--border-accent);
  background: var(--accent-dim);
}
.btn-lg {
  padding: 13px 24px;
  font-size: 14.5px;
  border-radius: 11px;
}
.btn-block {
  width: 100%;
}
@media (max-width: 900px) {
  .nav-links {
    display: none;
  }
}

.hero {
  padding: 76px 0 64px;
}
.hero-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 56px;
  align-items: center;
}
@media (max-width: 900px) {
  .hero-grid {
    grid-template-columns: 1fr;
  }
}
.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.8px;
  text-transform: uppercase;
  color: var(--accent);
  font-family: var(--mono);
  margin-bottom: 22px;
}
.eyebrow::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 8px var(--accent);
}
h1 {
  font-size: clamp(2rem, 4vw, 2.85rem);
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: -0.5px;
  margin-bottom: 20px;
}
h1 em {
  color: var(--accent);
  font-style: normal;
}
.hero-sub {
  font-size: 16px;
  color: var(--muted);
  line-height: 1.75;
  max-width: 480px;
  margin-bottom: 34px;
}
.hero-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}
.hero-meta {
  display: flex;
  gap: 26px;
  flex-wrap: wrap;
}
.hero-meta div {
  font-size: 12px;
  color: var(--dim);
}
.hero-meta strong {
  display: block;
  color: var(--text);
  font-size: 13.5px;
  font-weight: 700;
  margin-bottom: 2px;
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 22px;
}
.live-card {
  border-color: var(--border-accent);
  position: relative;
  overflow: hidden;
}
.live-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 100% 0%, rgba(0, 255, 170, 0.08), transparent 60%);
  pointer-events: none;
}
.live-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  position: relative;
}
.live-title {
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 1.4px;
  text-transform: uppercase;
  color: var(--accent);
  font-family: var(--mono);
}
.live-dot {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  color: var(--dim);
  font-family: var(--mono);
}
.pulse {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(0, 255, 170, 0.5);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(0, 255, 170, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(0, 255, 170, 0);
  }
}
.live-location {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 2px;
}
.live-sub {
  font-size: 11.5px;
  color: var(--dim);
  margin-bottom: 18px;
}
.panel-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 14px;
}
.metric {
  border-radius: 8px;
  padding: 10px 8px;
  background: var(--surface-2);
  text-align: center;
  border-top: 2px solid transparent;
}
.metric-label {
  display: block;
  font-size: 9px;
  color: var(--dim);
  font-family: var(--mono);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.metric strong {
  font-size: 15px;
  font-family: var(--mono);
  font-weight: 800;
  color: var(--text, #f2f5f3);
}
.metric--alert {
  border-top-color: var(--red);
}
.metric--alert strong {
  color: var(--red);
}
.insight-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  width: 100%;
  box-sizing: border-box;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  font-size: 12.5px;
  line-height: 1.35;
  margin-bottom: 12px;
  border: 1px solid transparent;
}
.insight-chip--frost {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}
.insight-chip--low {
  background: rgba(0, 255, 170, 0.08);
  border-color: rgba(0, 255, 170, 0.22);
  color: #b8f5de;
}
.insight-chip--medium {
  background: rgba(245, 185, 66, 0.1);
  border-color: rgba(245, 185, 66, 0.28);
  color: #e8d7ae;
}
.insight-chip--high {
  background: rgba(255, 90, 90, 0.1);
  border-color: rgba(255, 90, 90, 0.3);
  color: #f5c4c4;
}
.insight-chip--unknown {
  background: var(--surface-2);
  border-color: rgba(255, 255, 255, 0.08);
  color: var(--dim);
}
.live-alert {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  background: rgba(245, 185, 66, 0.08);
  border: 1px solid rgba(245, 185, 66, 0.25);
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 12px;
}
.live-alert .dot2 {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--amber);
  margin-top: 5px;
  flex-shrink: 0;
}
.live-alert p {
  margin: 0;
  font-size: 12.5px;
  color: #e8d7ae;
  line-height: 1.5;
}
.live-fallback {
  font-size: 11.5px;
  color: var(--dim);
  margin: 0 0 12px;
}
.live-link {
  display: inline-block;
  font-size: 12px;
  font-family: var(--mono);
  color: var(--accent);
  text-decoration: none;
}
.live-link:hover {
  text-decoration: underline;
}

.access-gate {
  padding: 24px 0 72px;
}
.access-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 40px;
  align-items: center;
}
@media (max-width: 900px) {
  .access-grid {
    grid-template-columns: 1fr;
  }
}
.access-list {
  margin: 18px 0 0;
  padding-left: 1.1rem;
  color: var(--muted);
  font-size: 13.5px;
  line-height: 1.7;
}
.access-card {
  border-color: var(--border-accent);
}
.access-card-brand {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 10px;
}
.access-card-brand strong {
  display: block;
  font-size: 1.1rem;
}
.access-card-brand span:last-child {
  display: block;
  font-size: 12.5px;
  color: var(--muted);
}
.access-region {
  font-size: 12px;
  color: var(--dim);
  margin-bottom: 18px;
}
.access-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.access-hint {
  font-size: 12px;
  color: var(--dim);
  text-align: center;
  margin-top: 4px;
}

.innov {
  padding: 3.5rem 0 1rem;
}
.innov h2 {
  margin: 0 0 0.5rem;
  font-size: clamp(1.35rem, 2.5vw, 1.75rem);
}
.innov-sub {
  margin: 0 0 1.5rem;
  color: var(--text-secondary, #94a3b8);
  max-width: 40rem;
}
.innov-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
@media (max-width: 800px) {
  .innov-grid {
    grid-template-columns: 1fr;
  }
}
.innov-grid article {
  padding: 1.15rem 1.25rem;
  border: 1px solid var(--border-color, #1e293b);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.45);
}
.innov-grid h3 {
  margin: 0 0 0.4rem;
  font-size: 1.05rem;
}
.innov-grid p {
  margin: 0 0 0.75rem;
  color: var(--text-secondary, #94a3b8);
  font-size: 0.92rem;
  line-height: 1.45;
}
.innov-grid a {
  color: var(--accent-primary, #10b981);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
}
.innov-mail {
  margin: 1.5rem 0 0;
  font-size: 0.95rem;
}
.innov-mail a {
  color: var(--accent-primary, #10b981);
}
.stats {
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  padding: 34px 0;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
@media (max-width: 700px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
.stat-num {
  font-size: 26px;
  font-weight: 800;
  font-family: var(--mono);
  color: var(--text);
  margin-bottom: 4px;
}
.stat-num span {
  color: var(--accent);
}
.stat-label {
  font-size: 12px;
  color: var(--muted);
}

section {
  padding: 84px 0;
}
.section-head {
  max-width: 560px;
  margin-bottom: 44px;
}
.section-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.6px;
  text-transform: uppercase;
  color: var(--accent);
  font-family: var(--mono);
  margin-bottom: 12px;
}
h2 {
  font-size: clamp(1.5rem, 3vw, 1.9rem);
  font-weight: 800;
  letter-spacing: -0.4px;
  margin-bottom: 12px;
}
.section-desc {
  font-size: 14.5px;
  color: var(--muted);
  line-height: 1.7;
}

.feat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
@media (max-width: 900px) {
  .feat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 560px) {
  .feat-grid {
    grid-template-columns: 1fr;
  }
}
.feat {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 24px 20px;
  transition: border-color 0.2s, transform 0.2s;
}
.feat:hover {
  border-color: var(--border-accent);
  transform: translateY(-3px);
}
.feat-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: var(--accent-dim);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  color: var(--accent);
}
.feat h3 {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 8px;
}
.feat p {
  font-size: 12.5px;
  color: var(--muted);
  line-height: 1.6;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.step {
  display: grid;
  grid-template-columns: 56px 1fr;
  gap: 20px;
  padding: 22px 4px;
  border-bottom: 1px solid var(--border);
  align-items: flex-start;
}
.step:last-child {
  border-bottom: none;
}
.step-num {
  font-size: 22px;
  font-weight: 800;
  font-family: var(--mono);
  color: var(--border-accent);
}
.step h4 {
  font-size: 15.5px;
  font-weight: 700;
  margin-bottom: 5px;
}
.step p {
  font-size: 13px;
  color: var(--muted);
  max-width: 520px;
  line-height: 1.6;
}

.alert-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
@media (max-width: 800px) {
  .alert-grid {
    grid-template-columns: 1fr;
  }
}
.alert-tier strong {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
}
.alert-tier p {
  font-size: 13px;
  color: var(--muted);
  line-height: 1.55;
}
.alert-tier--ok {
  border-top: 3px solid var(--accent);
}
.alert-tier--warn {
  border-top: 3px solid var(--amber);
}
.alert-tier--bad {
  border-top: 3px solid var(--red);
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 720px;
}
.faq-item {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 18px;
}
.faq-item summary {
  cursor: pointer;
  font-weight: 700;
  font-size: 14px;
}
.faq-item p {
  margin-top: 10px;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.6;
}

.cta-band {
  background: linear-gradient(135deg, rgba(0, 255, 170, 0.1), rgba(0, 255, 170, 0.02));
  border: 1px solid var(--border-accent);
  border-radius: 20px;
  padding: 52px 40px;
  text-align: center;
}
.cta-band h2 {
  margin-bottom: 10px;
}
.cta-band p {
  color: var(--muted);
  font-size: 14.5px;
  margin-bottom: 26px;
}
.cta-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.foot {
  border-top: 1px solid var(--border);
  padding: 36px 0;
}
.foot-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}
.foot-brand {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 13px;
  color: var(--dim);
}
.foot-links {
  display: flex;
  gap: 22px;
  flex-wrap: wrap;
}
.foot-links a {
  font-size: 12.5px;
  color: var(--dim);
}
.foot-links a:hover {
  color: var(--muted);
}
</style>
