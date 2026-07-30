<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, HardHat, Mountain } from 'lucide-vue-next'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { fetchMisFaenas, fetchMe, getToken, wakeApi } from '@/services/authApi'
import { useAuth } from '@/stores/auth'

const site = inject('site')
const router = useRouter()
const auth = useAuth()

const loading = ref(true)
const hub = ref(null)
const error = ref('')
const slugManual = ref('')
const query = ref('')

const catalog = computed(() => site.stations || [])

const visible = computed(() => {
  if (!hub.value) return []
  let list
  if (hub.value.catalogo_completo) list = catalog.value
  else {
    const slugs = new Set((hub.value.faenas || []).map((f) => f.slug))
    list = catalog.value.filter((s) => slugs.has(s.slug))
  }
  const q = query.value.trim().toLowerCase()
  if (!q) return list
  return list.filter(
    (f) =>
      f.nombre.toLowerCase().includes(q) ||
      f.slug.includes(q) ||
      String(f.region || '')
        .toLowerCase()
        .includes(q),
  )
})

const byRegion = computed(() => {
  const map = new Map()
  for (const f of visible.value) {
    const r = f.region || 'Chile'
    if (!map.has(r)) map.set(r, [])
    map.get(r).push(f)
  }
  return [...map.entries()]
})

const isLoggedIn = computed(() => Boolean(getToken()))
const isAdminCatalog = computed(() => Boolean(hub.value?.catalogo_completo))

onMounted(async () => {
  wakeApi().catch(() => {})
  if (!getToken()) {
    loading.value = false
    return
  }
  try {
    await auth.ensureValidSession()
    try {
      hub.value = await fetchMisFaenas()
    } catch {
      const me = await fetchMe()
      hub.value = me.hub || {
        catalogo_completo: ['admin', 'administrador'].includes(
          String(me.role || '').toLowerCase(),
        ),
        faenas: me.faena ? [{ slug: me.faena }] : me.faenas || [],
      }
    }
    if (!hub.value.catalogo_completo && (hub.value.faenas || []).length === 1) {
      await router.replace(`/f/${hub.value.faenas[0].slug}/`)
      return
    }
  } catch (e) {
    error.value = e.message || 'No se pudo cargar acceso'
  } finally {
    loading.value = false
  }
})

function irA(slug) {
  const s = String(slug || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '_')
  if (!s) return
  router.push(isLoggedIn.value ? `/f/${s}/` : `/f/${s}/login`)
}
</script>

<template>
  <div class="hub">
    <div class="hub-bg" aria-hidden="true" />

    <header class="hub-top">
      <div class="hub-brand-mark">
        <HardHat :size="22" aria-hidden="true" />
        <span>{{ site.productName }}</span>
        <em>{{ site.siteLabel }}</em>
      </div>
      <div class="hub-top-actions">
        <ThemeToggle />
        <span class="hub-ver">{{ site.versionLabel }}</span>
      </div>
    </header>

    <main class="hub-main">
      <section class="hub-hero">
        <p class="eyebrow"><Mountain :size="14" aria-hidden="true" /> Alta montaña · Chile</p>
        <h1>
          <span class="h-brand">{{ site.productName }}</span>
          <span class="h-product">SPATI</span>
        </h1>
        <p class="lede">
          Acceso por faena contratada. Cada minera tiene su enlace, reglas y
          suscripción.
        </p>
      </section>

      <!-- Público -->
      <section v-if="!isLoggedIn" class="hub-panel">
        <h2>Ingresar a su faena</h2>
        <p class="panel-copy">
          Use el enlace que le envió su operador, o escriba el código (por ejemplo
          <code>quebrada_blanca</code>).
        </p>
        <form class="gate-form" @submit.prevent="irA(slugManual)">
          <label for="faena-slug">Código de faena</label>
          <div class="gate-row">
            <input
              id="faena-slug"
              v-model="slugManual"
              type="text"
              placeholder="quebrada_blanca"
              autocomplete="off"
              spellcheck="false"
              required
            />
            <button type="submit">
              Continuar
              <ArrowRight :size="18" aria-hidden="true" />
            </button>
          </div>
        </form>
        <p class="fine">
          El catálogo completo de mineras no se publica aquí. Enterprise o admin
          lo ven tras iniciar sesión.
        </p>
      </section>

      <!-- Autenticado -->
      <template v-else>
        <p v-if="loading" class="state">Cargando sus faenas…</p>
        <p v-else-if="error" class="state err" role="alert">{{ error }}</p>

        <section v-else-if="visible.length || isAdminCatalog" class="hub-panel hub-panel--list">
          <div class="list-head">
            <h2>{{ isAdminCatalog ? 'Administración · faenas' : 'Sus faenas' }}</h2>
            <div class="list-head-actions">
              <router-link
                v-if="isAdminCatalog || (hub?.faenas || []).length > 1 || hub?.multi_faena"
                class="ops-link"
                to="/ops"
                >Board ops M10</router-link
              >
              <input
                v-model="query"
                type="search"
                class="search"
                placeholder="Buscar por nombre o región…"
                aria-label="Buscar faena"
              />
            </div>
          </div>

          <div v-if="!visible.length" class="state">Sin resultados para “{{ query }}”.</div>

          <div v-for="[region, items] in byRegion" :key="region" class="region">
            <h3>{{ region }}</h3>
            <ul>
              <li v-for="f in items" :key="f.slug">
                <button type="button" class="faena-row" @click="irA(f.slug)">
                  <span class="faena-text">
                    <strong>{{ f.nombre }}</strong>
                    <span>{{ f.altitud_msnm }} m · {{ f.slug }}</span>
                  </span>
                  <ArrowRight :size="18" aria-hidden="true" />
                </button>
              </li>
            </ul>
          </div>
        </section>

        <p v-else class="state">
          No hay faenas asociadas a esta cuenta. Use el enlace de registro de su
          minera.
        </p>
      </template>
    </main>
  </div>
</template>

<style scoped>
.hub {
  --hub-display: 'Syne', 'DM Sans', system-ui, sans-serif;
  position: relative;
  min-height: 100vh;
  color: var(--color-text);
  overflow-x: hidden;
  isolation: isolate;
}

.hub-bg {
  position: absolute;
  inset: 0;
  z-index: -1;
  background:
    radial-gradient(ellipse 80% 50% at 15% 10%, rgba(59, 130, 246, 0.22), transparent 55%),
    radial-gradient(ellipse 60% 40% at 90% 80%, rgba(20, 184, 166, 0.12), transparent 50%),
    linear-gradient(165deg, #070b14 0%, #0b1120 45%, #0f172a 100%);
}
.hub-bg::after {
  content: '';
  position: absolute;
  inset: auto 0 0;
  height: 36%;
  background: linear-gradient(
    to top,
    rgba(15, 23, 42, 0.95),
    transparent
  );
  opacity: 0.9;
  pointer-events: none;
}

.hub-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  max-width: 720px;
  margin: 0 auto;
}
.hub-brand-mark {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}
.hub-brand-mark em {
  font-style: normal;
  font-weight: 500;
  color: var(--color-text-secondary);
}
.hub-top-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.hub-ver {
  font-size: 0.7rem;
  color: var(--color-muted);
}

.hub-main {
  max-width: 480px;
  margin: 0 auto;
  padding: 1.5rem 1.5rem 3rem;
  animation: rise 0.55s ease both;
}
@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

.hub-hero {
  margin-bottom: 1.75rem;
}
.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin: 0 0 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-primary);
}
.hub-hero h1 {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  line-height: 0.95;
}
.h-brand {
  font-family: var(--hub-display);
  font-size: clamp(2.6rem, 10vw, 3.4rem);
  font-weight: 800;
  letter-spacing: -0.03em;
}
.h-product {
  font-family: var(--hub-display);
  font-size: clamp(1.85rem, 7vw, 2.35rem);
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: 0.12em;
}
.lede {
  margin: 1rem 0 0;
  color: var(--color-text-secondary);
  font-size: 1rem;
  max-width: 28rem;
  line-height: 1.45;
}

.hub-panel {
  padding: 1.35rem 1.25rem;
  border: 1px solid color-mix(in srgb, var(--color-border) 80%, transparent);
  border-radius: 14px;
  background: color-mix(in srgb, var(--color-surface) 88%, transparent);
  backdrop-filter: blur(10px);
  animation: rise 0.65s 0.08s ease both;
}
.hub-panel h2 {
  margin: 0 0 0.5rem;
  font-size: 1.05rem;
  font-weight: 650;
}
.panel-copy {
  margin: 0 0 1rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}
.panel-copy code {
  font-size: 0.8rem;
  color: var(--color-primary);
}

.gate-form label {
  display: block;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-muted);
  margin-bottom: 0.4rem;
}
.gate-row {
  display: flex;
  gap: 0.5rem;
}
.gate-row input,
.search {
  flex: 1;
  min-width: 0;
  padding: 0.7rem 0.85rem;
  border-radius: 10px;
  border: 1px solid var(--color-border);
  background: #080c16;
  color: var(--color-text);
  font: inherit;
}
.gate-row input:focus,
.search:focus {
  outline: 2px solid color-mix(in srgb, var(--color-primary) 55%, transparent);
  outline-offset: 1px;
}
.gate-row button {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  flex-shrink: 0;
  border: none;
  border-radius: 10px;
  padding: 0.7rem 1rem;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  background: var(--color-primary);
  color: #04101f;
  transition: transform 0.15s ease, filter 0.15s ease;
}
.gate-row button:hover {
  filter: brightness(1.08);
  transform: translateY(-1px);
}
.fine {
  margin: 1rem 0 0;
  font-size: 0.78rem;
  color: var(--color-muted);
  line-height: 1.4;
}

.list-head {
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.list-head-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  align-items: center;
}
.ops-link {
  flex-shrink: 0;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-primary);
  text-decoration: none;
  border: 1px solid var(--color-border);
  padding: 0.4rem 0.7rem;
  border-radius: 6px;
}
.ops-link:hover {
  background: var(--color-primary-subtle, #1e293b44);
}
.search {
  width: 100%;
  flex: 1;
  min-width: 12rem;
}

.region {
  margin-top: 1rem;
}
.region h3 {
  margin: 0 0 0.45rem;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-muted);
}
.region ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.4rem;
}
.faena-row {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  text-align: left;
  padding: 0.75rem 0.85rem;
  border-radius: 10px;
  border: 1px solid transparent;
  background: rgba(8, 12, 22, 0.65);
  color: inherit;
  cursor: pointer;
  font: inherit;
  transition: border-color 0.15s ease, background 0.15s ease;
}
.faena-row:hover {
  border-color: color-mix(in srgb, var(--color-primary) 45%, transparent);
  background: rgba(59, 130, 246, 0.08);
}
.faena-text {
  display: grid;
  gap: 0.15rem;
  min-width: 0;
}
.faena-text strong {
  font-weight: 650;
}
.faena-text span {
  font-size: 0.78rem;
  color: var(--color-muted);
}
.faena-row :deep(svg) {
  flex-shrink: 0;
  color: var(--color-primary);
  opacity: 0.85;
}

.state {
  margin-top: 1rem;
  color: var(--color-text-secondary);
  font-size: 0.95rem;
}
.state.err {
  color: var(--color-danger);
}

@media (max-width: 520px) {
  .gate-row {
    flex-direction: column;
  }
  .gate-row button {
    justify-content: center;
  }
}
</style>
