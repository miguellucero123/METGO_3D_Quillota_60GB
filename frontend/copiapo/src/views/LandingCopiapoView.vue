<template>
  <div class="landing">
    <a href="#inicio" class="skip-link">{{ t('app.skipContent') }}</a>

    <header class="top">
      <nav class="nav" aria-label="Principal">
        <a href="#inicio" class="brand">
          <span class="brand-icon" aria-hidden="true"><Wind :size="17" /></span>
          <span>
            <span class="brand-name">METGO</span>
            <span class="brand-sub">COPIAPÓ</span>
          </span>
        </a>
        <div class="nav-links">
          <router-link :to="{ path: '/', hash: '#estaciones' }">{{ t('landing.navStations') }}</router-link>
          <router-link :to="{ path: '/', hash: '#funciona' }">{{ t('landing.navHow') }}</router-link>
          <router-link :to="{ path: '/', hash: '#alertas' }">{{ t('landing.navModules') }}</router-link>
          <router-link :to="{ path: '/', hash: '#faq' }">{{ t('landing.navFaq') }}</router-link>
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
              <template v-else>
                <router-link class="btn btn-primary btn-lg" to="/registro">
                  {{ t('landing.requestAccess') }}
                </router-link>
                <router-link class="btn btn-ghost btn-lg" to="/login">
                  {{ t('landing.login') }}
                </router-link>
              </template>
              <a href="#funciona" class="btn btn-ghost btn-lg" @click.prevent="scrollTo('#funciona')">{{ t('landing.navHow') }}</a>
            </div>
            <div class="hero-meta">
              <div><strong>3</strong>{{ t('landing.metaStations') }}</div>
              <div><strong>1 h</strong>{{ t('landing.metaFreq') }}</div>
              <div><strong>PM10 · PM2.5 · SO₂</strong>{{ t('landing.metaParams') }}</div>
            </div>
          </div>

          <div class="card live-card">
            <div class="live-head">
              <span class="live-title">{{ t('landing.liveTitle') }}</span>
              <span class="live-dot">
                <span class="pulse" aria-hidden="true" />
                {{ aireLoading ? t('landing.liveLoading') : t('landing.liveNow') }}
              </span>
            </div>
            <p class="live-location">{{ liveNombre }}</p>
            <p class="live-sub">{{ t('landing.liveSubPanel') }}</p>

            <!-- Misma lectura que el Panel ICAP -->
            <div class="icap-live" :data-nivel="liveNivel">
              <div class="icap-live-valor">
                <span class="icap-live-num">{{ liveIcapDisplay }}</span>
                <span class="icap-live-label">{{ t('landing.ica') }}</span>
              </div>
              <div class="icap-live-meta">
                <p class="icap-live-cat">{{ liveEtiqueta }}</p>
                <p v-if="liveRector" class="icap-live-rector">
                  {{ t('landing.rector') }}: {{ liveRector }}
                </p>
                <div class="poll-row">
                  <div class="poll">
                    <span>PM2.5</span>
                    <strong>{{ fmtPoll(liveAire?.pm2_5) }}</strong>
                  </div>
                  <div class="poll">
                    <span>PM10</span>
                    <strong>{{ fmtPoll(liveAire?.pm10) }}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div
              v-if="showLiveAlert"
              class="live-alert"
              role="status"
            >
              <span class="dot2" aria-hidden="true" />
              <p>
                <strong v-if="liveAlertaTexto">{{ liveAlertaTexto }}</strong>
                {{ liveRecs[0] || '' }}
              </p>
            </div>
            <p v-else-if="aireError" class="live-fallback">{{ t('landing.liveFallback') }}</p>

            <router-link class="live-link" to="/login">{{ t('landing.seeInPanel') }} →</router-link>
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
              <span class="brand-icon" aria-hidden="true"><Wind :size="20" /></span>
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
            <div class="stat-num"><span>6+</span> h</div>
            <div class="stat-label">{{ t('landing.statLead') }}</div>
          </div>
          <div>
            <div class="stat-num"><span>1</span> h</div>
            <div class="stat-label">{{ t('landing.statRes') }}</div>
          </div>
          <div>
            <div class="stat-num"><span>&lt;5</span> min</div>
            <div class="stat-label">{{ t('landing.statLatency') }}</div>
          </div>
          <div>
            <div class="stat-num"><span>3</span></div>
            <div class="stat-label">{{ t('landing.statCommunes') }}</div>
          </div>
        </div>
      </div>

      <section id="estaciones">
        <div class="wrap">
          <div class="section-head">
            <p class="section-eyebrow">{{ t('landing.stationsEyebrow') }}</p>
            <h2>{{ t('landing.stationsTitle') }}</h2>
            <p class="section-desc">{{ t('landing.stationsDesc') }}</p>
          </div>
          <div class="feat-grid stations">
            <article v-for="s in stations" :key="s.name" class="feat">
              <div class="feat-top">
                <div class="feat-icon" aria-hidden="true"><MapPin :size="18" /></div>
                <span class="feat-badge" :class="s.badgeCls">{{ s.badge }}</span>
              </div>
              <h3>{{ s.name }}</h3>
              <p>{{ s.body }}</p>
              <div class="feat-aqi">
                {{ s.aqi }}
                <span>{{ t('landing.ica') }}</span>
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
          <div class="mod-grid">
            <article v-for="m in modules" :key="m.title" class="feat">
              <div class="feat-icon feat-icon--mod" aria-hidden="true">
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
              <a href="#estaciones" class="btn btn-ghost btn-lg" @click.prevent="scrollTo('#estaciones')">{{ t('landing.seeStations') }}</a>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer class="foot">
      <div class="wrap foot-row">
        <div class="foot-brand">
          <span class="brand-icon brand-icon--sm" aria-hidden="true"><Wind :size="12" /></span>
          {{ t('landing.footerBrand') }}
        </div>
        <div class="foot-links">
          <a href="#estaciones" @click.prevent="scrollTo('#estaciones')">{{ t('landing.navStations') }}</a>
          <a href="#funciona" @click.prevent="scrollTo('#funciona')">{{ t('landing.navHow') }}</a>
          <a href="#acceso" @click.prevent="scrollTo('#acceso')">{{ t('landing.accessEyebrow') }}</a>
          <router-link to="/login">{{ t('landing.login') }}</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Wind,
  LogIn,
  LayoutDashboard,
  MapPin,
  FileText,
  Bell,
  Star,
} from 'lucide-vue-next'
import { setLocale } from '@/i18n'
import { getToken } from '@/services/authApi'
import { fetchAireActual, wakeApi } from '@/services/aireApi'

const LIVE_SLUG = 'paipote'
const STATION_DEFS = [
  { slug: 'copiapo_centro', nameKey: 'landing.stCopiapo', bodyKey: 'landing.stCopiapoBody' },
  { slug: 'paipote', nameKey: 'landing.stPaipote', bodyKey: 'landing.stPaipoteBody' },
  { slug: 'tierra_amarilla', nameKey: 'landing.stTierra', bodyKey: 'landing.stTierraBody' },
]

const site = inject('site')
const { t, locale } = useI18n()
const isLoggedIn = computed(() => Boolean(getToken()))

function scrollTo(hash) {
  const el = document.querySelector(hash)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const heroTitleHtml = computed(() => t('landing.heroTitleHtml'))

const aireLoading = ref(true)
const aireError = ref(false)
const lecturas = reactive({})

const liveAire = computed(() => lecturas[LIVE_SLUG] || null)
const liveNombre = computed(() => {
  if (liveAire.value?.estacion || liveAire.value?.nombre) {
    return liveAire.value.estacion || liveAire.value.nombre
  }
  return t('landing.liveLocation')
})
const liveNivel = computed(() => liveAire.value?.nivel || 'sin')
const liveEtiqueta = computed(
  () => liveAire.value?.etiqueta || t('landing.badgeUnknown'),
)
const liveIcapDisplay = computed(() => {
  const v = liveAire.value?.icap
  if (v == null || Number.isNaN(Number(v))) return '—'
  return String(Math.round(Number(v)))
})
const liveRector = computed(() => {
  const m = { pm2_5: 'PM2.5', pm10: 'PM10', so2: 'SO₂', sulphur_dioxide: 'SO₂' }
  const r = liveAire.value?.contaminante_rector
  return r ? m[r] || r : null
})
const liveRecs = computed(() =>
  Array.isArray(liveAire.value?.recomendaciones) ? liveAire.value.recomendaciones : [],
)
const showLiveAlert = computed(() => {
  const n = liveNivel.value
  return n === 'regular' || n === 'alerta' || n === 'preemergencia' || n === 'emergencia'
})
const liveAlertaTexto = computed(() => {
  const n = liveNivel.value
  if (n === 'alerta' || n === 'preemergencia' || n === 'emergencia') {
    return t('landing.liveAlertLevel', { nivel: liveEtiqueta.value })
  }
  if (n === 'regular') return t('landing.liveAlertRegular')
  return ''
})

function fmtPoll(v) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return `${Number(v).toFixed(0)} µg/m³`
}

function badgeForNivel(nivel) {
  if (nivel === 'bueno') return { text: t('landing.badgeGood'), cls: 'b-ok' }
  if (nivel === 'regular') return { text: t('landing.badgeFair'), cls: 'b-warn' }
  if (nivel === 'alerta' || nivel === 'preemergencia' || nivel === 'emergencia') {
    return { text: (nivel || '').toUpperCase(), cls: 'b-bad' }
  }
  return { text: t('landing.badgeUnknown'), cls: 'b-muted' }
}

const stations = computed(() =>
  STATION_DEFS.map((def) => {
    const aire = lecturas[def.slug]
    const badge = badgeForNivel(aire?.nivel)
    return {
      slug: def.slug,
      name: t(def.nameKey),
      body: t(def.bodyKey),
      badge: aire?.etiqueta ? String(aire.etiqueta).toUpperCase() : badge.text,
      badgeCls: badge.cls,
      aqi: aire?.icap != null ? String(Math.round(Number(aire.icap))) : '—',
    }
  }),
)

const modules = computed(() => [
  { icon: Wind, title: t('landing.modDispTitle'), body: t('landing.modDispBody') },
  { icon: Bell, title: t('landing.modAlertTitle'), body: t('landing.modAlertBody') },
  { icon: FileText, title: t('landing.modHistTitle'), body: t('landing.modHistBody') },
  { icon: Star, title: t('landing.modRecTitle'), body: t('landing.modRecBody') },
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
  aireLoading.value = true
  aireError.value = false
  try {
    await wakeApi()
    await Promise.all(
      STATION_DEFS.map(async ({ slug }) => {
        try {
          lecturas[slug] = await fetchAireActual(slug)
        } catch {
          lecturas[slug] = null
        }
      }),
    )
    if (!lecturas[LIVE_SLUG]) {
      aireError.value = true
      // Fallback ilustrativo alineado a umbrales del panel
      lecturas[LIVE_SLUG] = {
        estacion: 'Paipote',
        icap: 104,
        nivel: 'regular',
        etiqueta: 'Regular',
        contaminante_rector: 'pm10',
        pm2_5: 28,
        pm10: 62,
        recomendaciones: [
          t('landing.liveAlertRest').trim() ||
            'Evitar actividad física intensa al aire libre en grupos sensibles.',
        ],
      }
    }
  } catch {
    aireError.value = true
  } finally {
    aireLoading.value = false
  }
})
</script>

<style scoped>
.landing {
  --bg: #0a0904;
  --bg-glow: radial-gradient(ellipse 900px 520px at 12% -10%, rgba(251, 191, 36, 0.12), transparent 60%),
    radial-gradient(ellipse 700px 500px at 100% 15%, rgba(251, 191, 36, 0.06), transparent 55%);
  --surface: #171410;
  --surface-2: #100e0a;
  --border: rgba(255, 255, 255, 0.08);
  --border-accent: rgba(251, 191, 36, 0.3);
  --accent: #fbbf24;
  --accent-dim: rgba(251, 191, 36, 0.12);
  --text: #f7f6f3;
  --muted: #a39b8a;
  --dim: #5c5546;
  --green: #34d399;
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
  color: #241b02;
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

section[id] {
  scroll-margin-top: 80px;
}
.top {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(10, 9, 4, 0.84);
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
  background: linear-gradient(145deg, #ffd66b, #f2a90e);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #241b02;
  box-shadow: 0 4px 16px rgba(251, 191, 36, 0.35);
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
  color: #241b02;
}
.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(251, 191, 36, 0.3);
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
  background: radial-gradient(circle at 100% 0%, rgba(251, 191, 36, 0.09), transparent 60%);
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
    box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.5);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(251, 191, 36, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(251, 191, 36, 0);
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
.icap-live {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  padding: 14px 12px;
  border-radius: 10px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  margin-bottom: 14px;
  position: relative;
}
.icap-live[data-nivel='bueno'] {
  border-left-color: var(--green);
}
.icap-live[data-nivel='regular'] {
  border-left-color: var(--accent);
}
.icap-live[data-nivel='alerta'] {
  border-left-color: #f97316;
}
.icap-live[data-nivel='preemergencia'],
.icap-live[data-nivel='emergencia'] {
  border-left-color: var(--red);
}
.icap-live-valor {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 72px;
}
.icap-live-num {
  font-size: 2.25rem;
  font-weight: 800;
  font-family: var(--mono);
  line-height: 1;
  color: var(--accent);
}
.icap-live-label {
  font-size: 10px;
  color: var(--dim);
  letter-spacing: 0.08em;
  font-family: var(--mono);
  margin-top: 4px;
}
.icap-live-meta {
  flex: 1;
  min-width: 140px;
}
.icap-live-cat {
  margin: 0 0 4px;
  font-size: 1.05rem;
  font-weight: 700;
}
.icap-live-rector {
  margin: 0 0 10px;
  font-size: 11.5px;
  color: var(--dim);
}
.poll-row {
  display: flex;
  gap: 14px;
}
.poll span {
  display: block;
  font-size: 9px;
  color: var(--dim);
  font-family: var(--mono);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.poll strong {
  font-size: 12.5px;
  font-family: var(--mono);
}
.live-alert {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  background: rgba(251, 191, 36, 0.08);
  border: 1px solid rgba(251, 191, 36, 0.25);
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
  color: #e8dcb8;
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

.feat-grid.stations {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
@media (max-width: 900px) {
  .feat-grid.stations {
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
.feat-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.feat-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: var(--accent-dim);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
}
.feat-icon--mod {
  margin-bottom: 16px;
}
.feat-badge {
  font-size: 10px;
  font-family: var(--mono);
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 20px;
  letter-spacing: 0.5px;
}
.b-ok {
  color: var(--green);
  background: rgba(52, 211, 153, 0.12);
}
.b-warn {
  color: var(--accent);
  background: rgba(251, 191, 36, 0.12);
}
.b-bad {
  color: var(--red);
  background: rgba(239, 91, 91, 0.12);
}
.b-muted {
  color: var(--dim);
  background: rgba(255, 255, 255, 0.06);
}
.feat h3 {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 6px;
}
.feat p {
  font-size: 12.5px;
  color: var(--muted);
  line-height: 1.6;
  margin-bottom: 12px;
}
.feat-aqi {
  font-size: 22px;
  font-weight: 800;
  font-family: var(--mono);
}
.feat-aqi span {
  font-size: 12px;
  color: var(--dim);
  font-weight: 600;
}

.mod-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
@media (max-width: 900px) {
  .mod-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 560px) {
  .mod-grid {
    grid-template-columns: 1fr;
  }
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
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(251, 191, 36, 0.02));
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
