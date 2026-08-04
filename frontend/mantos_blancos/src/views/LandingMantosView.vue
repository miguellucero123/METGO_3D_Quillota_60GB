<template>
  <div class="landing">
    <a href="#inicio" class="skip-link">{{ t('app.skipContent') }}</a>

    <header class="top">
      <nav class="nav" aria-label="Principal">
        <a href="#inicio" class="brand">
          <span class="brand-icon" aria-hidden="true"><HardHat :size="17" /></span>
          <span>
            <span class="brand-name">METGO</span>
            <span class="brand-sub">MANTOS BLANCOS</span>
          </span>
        </a>
        <div class="nav-links">
          <a href="#actividades">{{ t('landing.navActivities') }}</a>
          <a href="#funciona">{{ t('landing.navHow') }}</a>
          <a href="#alertas">{{ t('landing.navModules') }}</a>
          <a href="#faq">{{ t('landing.navFaq') }}</a>
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
          <router-link v-if="isLoggedIn" class="btn btn-primary" to="/app">{{ t('landing.goPanel') }}</router-link>
          <template v-else>
            <router-link class="btn btn-ghost" to="/login">{{ t('landing.login') }}</router-link>
            <router-link class="btn btn-primary" to="/registro">{{ t('landing.requestAccess') }}</router-link>
          </template>
        </div>
      </nav>
    </header>

    <main>
      <section id="inicio" class="hero">
        <div class="wrap hero-grid">
          <div>
            <p class="eyebrow">{{ t('landing.eyebrow') }}</p>
            <h1 v-html="heroTitleHtml" />
            <p class="hero-sub">{{ t('landing.heroSub') }}</p>
            <div class="hero-actions">
              <router-link v-if="isLoggedIn" class="btn btn-primary btn-lg" to="/app">
                {{ t('landing.goPanel') }}
              </router-link>
              <router-link v-else class="btn btn-primary btn-lg" to="/registro">
                {{ t('landing.requestAccess') }}
              </router-link>
              <a href="#funciona" class="btn btn-ghost btn-lg">{{ t('landing.navHow') }}</a>
            </div>
            <div class="hero-meta">
              <div><strong>4</strong>{{ t('landing.metaVars') }}</div>
              <div><strong>15 min</strong>{{ t('landing.metaFreq') }}</div>
              <div><strong>3</strong>{{ t('landing.metaActs') }}</div>
            </div>
          </div>

          <div class="card live-card">
            <div class="live-head">
              <span class="live-title">{{ t('landing.liveTitle') }}</span>
              <span class="live-dot">
                <span class="pulse" aria-hidden="true" />
                {{ opsLoading ? t('landing.liveLoading') : t('landing.liveNow') }}
              </span>
            </div>
            <p class="live-location">{{ t('landing.liveLocation') }}</p>
            <p class="live-sub">{{ liveSub }}</p>

            <div class="param-list">
              <div v-for="p in liveParams" :key="p.name" class="param">
                <span class="param-name">
                  <span class="param-dot" :class="p.dot" aria-hidden="true" />
                  {{ p.name }}
                </span>
                <span class="param-val">{{ p.value }}</span>
              </div>
            </div>

            <div v-if="liveAlertStrong || liveAlertRest" class="live-alert" role="status">
              <span class="dot2" aria-hidden="true" />
              <p>
                <strong v-if="liveAlertStrong">{{ liveAlertStrong }}</strong>
                {{ liveAlertRest }}
              </p>
            </div>
            <p v-else-if="opsError" class="live-fallback">{{ t('landing.liveFallback') }}</p>

            <router-link class="live-link" to="/login?redirect=/app">{{ t('landing.seeInPanel') }} →</router-link>
          </div>
        </div>
      </section>

      <section id="acceso" class="access-gate">
        <div class="wrap access-grid">
          <div>
            <p class="section-eyebrow">{{ t('landing.accessEyebrow') }}</p>
            <h2>{{ t('landing.accessTitle') }}</h2>
            <p class="section-desc">{{ t('landing.accessDesc') }}</p>
            <ul class="access-list">
              <li>{{ t('landing.accessBullet1') }}</li>
              <li>{{ t('landing.accessBullet2') }}</li>
              <li>{{ t('landing.accessBullet3') }}</li>
            </ul>
          </div>
          <div class="card access-card">
            <div class="access-card-brand">
              <span class="brand-icon" aria-hidden="true"><HardHat :size="20" /></span>
              <div>
                <strong>{{ site.productName }}</strong>
                <span>{{ t('login.subtitle') }}</span>
              </div>
            </div>
            <p class="access-region">{{ site.region }}</p>
            <div class="access-actions">
              <router-link v-if="isLoggedIn" class="btn btn-primary btn-lg btn-block" to="/app">
                <LayoutDashboard :size="18" aria-hidden="true" />
                {{ t('landing.goPanel') }}
              </router-link>
              <template v-else>
                <router-link class="btn btn-primary btn-lg btn-block" to="/login">
                  <LogIn :size="18" aria-hidden="true" />
                  {{ t('landing.login') }}
                </router-link>
                <p class="access-hint">{{ t('landing.accessHint') }}</p>
              </template>
            </div>
          </div>
        </div>
      </section>

      <div class="stats">
        <div class="wrap stats-grid">
          <div>
            <div class="stat-num"><span>18+</span> h</div>
            <div class="stat-label">{{ t('landing.statLead') }}</div>
          </div>
          <div>
            <div class="stat-num"><span>15</span> min</div>
            <div class="stat-label">{{ t('landing.statRes') }}</div>
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

      <section id="actividades">
        <div class="wrap">
          <div class="section-head">
            <p class="section-eyebrow">{{ t('landing.actEyebrow') }}</p>
            <h2>{{ t('landing.actTitle') }}</h2>
            <p class="section-desc">{{ t('landing.actDesc') }}</p>
          </div>
          <div class="act-grid">
            <article v-for="a in activities" :key="a.title" class="act">
              <div class="act-head">
                <h3>{{ a.title }}</h3>
                <span class="act-badge">{{ t('landing.actBadge') }}</span>
              </div>
              <div v-for="row in a.rows" :key="row.label" class="act-row">
                <span>{{ row.label }}</span>
                <b>{{ row.value }}</b>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section id="alertas">
        <div class="wrap">
          <div class="section-head">
            <p class="section-eyebrow">{{ t('landing.modulesEyebrow') }}</p>
            <h2>{{ t('landing.modulesTitle') }}</h2>
            <p class="section-desc">{{ t('landing.modulesDesc') }}</p>
          </div>
          <div class="feat-grid">
            <article v-for="m in modules" :key="m.title" class="feat">
              <div class="feat-icon" aria-hidden="true">
                <component :is="m.icon" :size="18" />
              </div>
              <h3>{{ m.title }}</h3>
              <p>{{ m.body }}</p>
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
              <router-link v-else class="btn btn-primary btn-lg" to="/registro">
                {{ t('landing.requestAccess') }}
              </router-link>
              <a href="#actividades" class="btn btn-ghost btn-lg">{{ t('landing.seeThresholds') }}</a>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer class="foot">
      <div class="wrap foot-row">
        <div class="foot-brand">
          <span class="brand-icon brand-icon--sm" aria-hidden="true"><HardHat :size="12" /></span>
          {{ t('landing.footerBrand') }}
        </div>
        <div class="foot-links">
          <a href="#actividades">{{ t('landing.navActivities') }}</a>
          <a href="#funciona">{{ t('landing.navHow') }}</a>
          <a href="#acceso">{{ t('landing.accessEyebrow') }}</a>
          <router-link to="/login">{{ t('landing.login') }}</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  HardHat,
  LogIn,
  LayoutDashboard,
  Wind,
  Eye,
  Sun,
  FileText,
} from 'lucide-vue-next'
import { setLocale } from '@/i18n'
import { getToken } from '@/services/authApi'
import { wakeApi, fetchVentanas } from '@/services/operacionesApi'

const LIVE_SLUG = 'mb_rajo'

const site = inject('site')
const { t, locale } = useI18n()
const isLoggedIn = computed(() => Boolean(getToken()))
const heroTitleHtml = computed(() => t('landing.heroTitleHtml'))

const opsLoading = ref(true)
const opsError = ref(false)
const horaActual = ref(null)

function msToKmh(v) {
  if (v == null || Number.isNaN(Number(v))) return null
  return Number(v) * 3.6
}

function nivelDot(nivel) {
  if (nivel === 'rojo') return 'd-bad'
  if (nivel === 'amarillo') return 'd-warn'
  if (nivel === 'verde') return 'd-ok'
  return 'd-ok'
}

function peorNivel(...niveles) {
  const rank = { rojo: 3, amarillo: 2, verde: 1 }
  let best = 'verde'
  for (const n of niveles) {
    if ((rank[n] || 0) > (rank[best] || 0)) best = n
  }
  return best
}

const liveSub = computed(() => {
  if (horaActual.value?.fecha_hora) {
    const hh = String(horaActual.value.fecha_hora).slice(11, 16)
    return t('landing.liveSubPanel', { hora: hh || '—' })
  }
  return t('landing.liveSub')
})

const liveParams = computed(() => {
  const h = horaActual.value
  if (!h) {
    return [
      { name: t('landing.pWind'), value: '—', dot: 'd-ok' },
      { name: t('landing.pVis'), value: '—', dot: 'd-ok' },
      { name: t('landing.pTemp'), value: '—', dot: 'd-ok' },
      { name: t('landing.pUv'), value: '—', dot: 'd-ok' },
    ]
  }
  const acts = h.actividades || {}
  const windKmh = msToKmh(h.viento_sostenido)
  const windNivel = peorNivel(acts.tronadura?.nivel, acts.izaje?.nivel)
  const visNivel = peorNivel(acts.transporte?.nivel, acts.tronadura?.nivel)
  const uvNivel = acts.exposicion_uv?.nivel || 'verde'
  const temp = h.temperatura
  let tempDot = 'd-ok'
  if (temp != null && temp >= 38) tempDot = 'd-bad'
  else if (temp != null && temp >= 32) tempDot = 'd-warn'

  return [
    {
      name: t('landing.pWind'),
      value: windKmh == null ? '—' : `${windKmh.toFixed(0)} km/h`,
      dot: nivelDot(windNivel),
    },
    {
      name: t('landing.pVis'),
      value: h.visibilidad == null ? '—' : `${Number(h.visibilidad).toFixed(1)} km`,
      dot: nivelDot(visNivel),
    },
    {
      name: t('landing.pTemp'),
      value: temp == null ? '—' : `${Number(temp).toFixed(0)}°C`,
      dot: tempDot,
    },
    {
      name: t('landing.pUv'),
      value: h.uv_index == null ? '—' : t('landing.uvIndex', { n: Number(h.uv_index).toFixed(0) }),
      dot: nivelDot(uvNivel),
    },
  ]
})

const liveAlertStrong = computed(() => {
  const h = horaActual.value
  if (!h) return ''
  const global = h.nivel_global
  if (global === 'rojo') return t('landing.alertBlock')
  if (global === 'amarillo') return t('landing.alertCaution')
  const uv = Number(h.uv_index)
  if (uv >= 11) return t('landing.alertUvExtreme')
  if (uv >= 8) return t('landing.alertUvHigh')
  return ''
})

const liveAlertRest = computed(() => {
  const h = horaActual.value
  if (!h) return ''
  const factores = []
  const acts = h.actividades || {}
  for (const key of ['tronadura', 'izaje', 'transporte', 'exposicion_uv']) {
    const f = acts[key]?.factores
    if (Array.isArray(f)) factores.push(...f)
  }
  if (factores.length) return factores[0]
  if (liveAlertStrong.value) return t('landing.alertDefaultRest')
  return ''
})

const activities = computed(() => [
  {
    title: t('landing.actBlast'),
    rows: [
      { label: t('landing.rowWindMax'), value: '≤ 20 km/h' },
      { label: t('landing.rowVisMin'), value: '≥ 2 km' },
      { label: t('landing.rowPrecip'), value: '0 mm/h' },
    ],
  },
  {
    title: t('landing.actLift'),
    rows: [
      { label: t('landing.rowWindSus'), value: '≤ 26 km/h' },
      { label: t('landing.rowGust'), value: '≤ 35 km/h' },
      { label: t('landing.rowVisMin'), value: '≥ 1 km' },
    ],
  },
  {
    title: t('landing.actHaul'),
    rows: [
      { label: t('landing.rowVisMin'), value: '≥ 500 m' },
      { label: t('landing.rowUv'), value: t('landing.uvLeq', { n: 10 }) },
      { label: t('landing.rowTempMax'), value: '≤ 38°C' },
    ],
  },
])

const modules = computed(() => [
  { icon: Wind, title: t('landing.modWindTitle'), body: t('landing.modWindBody') },
  { icon: Eye, title: t('landing.modVisTitle'), body: t('landing.modVisBody') },
  { icon: Sun, title: t('landing.modUvTitle'), body: t('landing.modUvBody') },
  { icon: FileText, title: t('landing.modPdfTitle'), body: t('landing.modPdfBody') },
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

onMounted(async () => {
  opsLoading.value = true
  opsError.value = false
  try {
    await wakeApi()
    const series = await fetchVentanas(LIVE_SLUG, 24)
    const list = Array.isArray(series) ? series : series?.horas || []
    const now = Date.now()
    let pick = list[0] || null
    for (const row of list) {
      const ts = Date.parse(row.fecha_hora)
      if (!Number.isNaN(ts) && ts <= now) pick = row
    }
    if (!pick) {
      opsError.value = true
      horaActual.value = {
        fecha_hora: new Date().toISOString(),
        nivel_global: 'amarillo',
        viento_sostenido: 4.4,
        visibilidad: 1.2,
        temperatura: 27,
        uv_index: 11,
        actividades: {
          tronadura: { nivel: 'verde', factores: [] },
          izaje: { nivel: 'verde', factores: [] },
          transporte: { nivel: 'amarillo', factores: [] },
          exposicion_uv: {
            nivel: 'rojo',
            factores: [t('landing.alertDefaultRest')],
          },
        },
      }
    } else {
      horaActual.value = pick
    }
  } catch {
    opsError.value = true
    horaActual.value = {
      fecha_hora: new Date().toISOString(),
      nivel_global: 'amarillo',
      viento_sostenido: 4.4,
      visibilidad: 1.2,
      temperatura: 27,
      uv_index: 11,
      actividades: {
        tronadura: { nivel: 'verde', factores: [] },
        izaje: { nivel: 'verde', factores: [] },
        transporte: { nivel: 'amarillo', factores: [] },
        exposicion_uv: {
          nivel: 'rojo',
          factores: [t('landing.alertDefaultRest')],
        },
      },
    }
  } finally {
    opsLoading.value = false
  }
})
</script>

<style scoped>
.landing {
  --bg: #0a0704;
  --bg-glow: radial-gradient(ellipse 900px 520px at 12% -10%, rgba(249, 115, 22, 0.13), transparent 60%),
    radial-gradient(ellipse 700px 500px at 100% 15%, rgba(249, 115, 22, 0.06), transparent 55%);
  --surface: #181209;
  --surface-2: #110c06;
  --border: rgba(255, 255, 255, 0.08);
  --border-accent: rgba(249, 115, 22, 0.3);
  --accent: #f97316;
  --accent-dim: rgba(249, 115, 22, 0.13);
  --text: #f8f6f2;
  --muted: #a89a86;
  --dim: #605140;
  --green: #34d399;
  --amber: #fbbf24;
  --red: #ef5b5b;
  --mono: ui-monospace, 'SF Mono', 'Cascadia Code', monospace;
  min-height: 100vh;
  background: var(--bg);
  background-image: var(--bg-glow);
  background-attachment: fixed;
  color: var(--text);
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
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
  z-index: 100;
  padding: 0.75rem 1rem;
  background: var(--accent);
  color: #2a1502;
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
  background: rgba(10, 7, 4, 0.85);
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
  background: linear-gradient(145deg, #ffab5c, #e8650a);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2a1502;
  box-shadow: 0 4px 16px rgba(249, 115, 22, 0.35);
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
  gap: 30px;
}
.nav-links a {
  font-size: 13.5px;
  color: var(--muted);
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
  color: #2a1502;
}
.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(249, 115, 22, 0.32);
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
@media (max-width: 860px) {
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
  font-size: clamp(2rem, 4vw, 2.75rem);
  font-weight: 800;
  line-height: 1.14;
  letter-spacing: -0.5px;
  margin-bottom: 20px;
}
h1 :deep(em) {
  color: var(--accent);
  font-style: normal;
}
.hero-sub {
  font-size: 16px;
  color: var(--muted);
  line-height: 1.75;
  max-width: 490px;
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
  background: radial-gradient(circle at 100% 0%, rgba(249, 115, 22, 0.1), transparent 60%);
  pointer-events: none;
}
.live-head {
  display: flex;
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
    box-shadow: 0 0 0 0 rgba(249, 115, 22, 0.5);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(249, 115, 22, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(249, 115, 22, 0);
  }
}
.live-location {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 2px;
  position: relative;
}
.live-sub {
  font-size: 11.5px;
  color: var(--dim);
  margin-bottom: 18px;
  position: relative;
}
.param-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  position: relative;
}
.param {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--surface-2);
  border-radius: 9px;
  padding: 10px 12px;
}
.param-name {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 12.5px;
  font-weight: 600;
}
.param-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.d-ok {
  background: var(--green);
}
.d-warn {
  background: var(--amber);
}
.d-bad {
  background: var(--red);
}
.param-val {
  font-size: 12.5px;
  font-family: var(--mono);
  font-weight: 700;
  color: var(--muted);
}
.live-alert {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  background: rgba(249, 115, 22, 0.09);
  border: 1px solid rgba(249, 115, 22, 0.26);
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 12px;
  position: relative;
}
.live-alert .dot2 {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent);
  margin-top: 5px;
  flex-shrink: 0;
}
.live-alert p {
  margin: 0;
  font-size: 12.5px;
  color: #ecd9c4;
  line-height: 1.5;
}
.live-alert strong {
  color: var(--accent);
}
.live-fallback {
  font-size: 11.5px;
  color: var(--dim);
  margin: 0 0 12px;
  position: relative;
}
.live-link {
  display: inline-block;
  position: relative;
  font-size: 12px;
  font-family: var(--mono);
  color: var(--accent);
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

.act-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
@media (max-width: 820px) {
  .act-grid {
    grid-template-columns: 1fr;
  }
}
.act {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 22px;
}
.act-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.act h3 {
  font-size: 14.5px;
  font-weight: 700;
  margin: 0;
}
.act-badge {
  font-size: 9.5px;
  font-family: var(--mono);
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 20px;
  letter-spacing: 0.5px;
  color: var(--accent);
  background: var(--accent-dim);
}
.act-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--muted);
  padding: 7px 0;
  border-top: 1px solid var(--border);
}
.act-row:first-of-type {
  border-top: none;
}
.act-row b {
  color: var(--text);
  font-family: var(--mono);
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
  margin: 0;
}

.steps {
  display: flex;
  flex-direction: column;
}
.step {
  display: grid;
  grid-template-columns: 56px 1fr;
  gap: 20px;
  padding: 22px 4px;
  border-bottom: 1px solid var(--border);
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
  margin: 0;
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
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.11), rgba(249, 115, 22, 0.02));
  border: 1px solid var(--border-accent);
  border-radius: 20px;
  padding: 52px 40px;
  text-align: center;
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
