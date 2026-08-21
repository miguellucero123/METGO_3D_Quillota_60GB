<script setup>
import { computed, ref, onMounted } from 'vue'
import { Leaf, Menu, X } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { setLocale } from '@/i18n'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { useSeo } from '@/composables/useSeo'
import LeadCaptureBar from '@/components/ui/LeadCaptureBar.vue'
import LeadMagnetModal from '@/components/ui/LeadMagnetModal.vue'

const props = defineProps({
  brandName: { type: String, default: 'METGO3D' },
  brandSub: { type: String, default: 'QUILLOTA' },
  brandIcon: { type: [Object, Function], required: true },
  accentColor: { type: String, default: '#00ffaa' },
  seoTitle: { type: String, default: 'METGO3D Quillota' },
  seoDescription: { type: String, default: 'Inteligencia climática construida para Chile' },
})

useSeo({ title: props.seoTitle, description: props.seoDescription })

const { t, locale } = useI18n()
const auth = useAuthStore()
const isLoggedIn = computed(() => auth.isAuthenticated)

const isMobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}
const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

const accessPath = '/registro'
</script>

<template>
  <div class="commercial-layout" :style="{ '--local-accent': accentColor }">
    <a href="#inicio" class="skip-link">{{ t('app.skipContent', 'Saltar al contenido principal') }}</a>

    <header class="top">
      <nav class="nav" aria-label="Principal">
        <router-link to="/" class="brand">
          <span class="brand-icon" aria-hidden="true">
            <component :is="brandIcon" :size="17" />
          </span>
          <span class="brand-text">
            <span class="brand-name">{{ brandName }}</span>
            <span class="brand-sub">{{ brandSub }}</span>
          </span>
        </router-link>

        <div class="nav-links desktop-only">
          <router-link to="/planes">Planes</router-link>
          <router-link to="/blog">Blog</router-link>
          <router-link to="/nosotros">Nosotros</router-link>
          <router-link to="/contacto">Contacto</router-link>
        </div>

        <div class="nav-cta desktop-only">
          <ThemeToggle />
          <div class="lang-switch" role="group" :aria-label="t('lang.label')">
            <button type="button" :class="{ active: locale === 'es' }" @click="setLocale('es')">
              {{ t('lang.es', 'ES') }}
            </button>
            <button type="button" :class="{ active: locale === 'en' }" @click="setLocale('en')">
              {{ t('lang.en', 'EN') }}
            </button>
          </div>
          <template v-if="isLoggedIn">
            <router-link class="btn btn-primary" to="/app">{{ t('landing.goPanel', 'Ir al panel') }}</router-link>
          </template>
          <template v-else>
            <router-link class="btn btn-ghost" to="/login">{{ t('landing.login', 'Ingresar') }}</router-link>
            <router-link class="btn btn-primary" :to="accessPath">{{ t('landing.requestAccess', 'Solicitar acceso') }}</router-link>
          </template>
        </div>

        <button class="mobile-menu-btn mobile-only" @click="toggleMobileMenu" aria-label="Abrir menú">
          <Menu :size="28" />
        </button>
      </nav>
    </header>

    <!-- Mobile Navigation Drawer -->
    <div class="mobile-drawer" :class="{ 'drawer-open': isMobileMenuOpen }">
      <div class="drawer-header">
        <span class="brand-name">{{ brandName }}</span>
        <button class="close-btn" @click="closeMobileMenu" aria-label="Cerrar menú">
          <X :size="28" />
        </button>
      </div>
      <div class="drawer-content">
        <router-link to="/planes" @click="closeMobileMenu">Planes</router-link>
        <router-link to="/blog" @click="closeMobileMenu">Blog</router-link>
        <router-link to="/nosotros" @click="closeMobileMenu">Nosotros</router-link>
        <router-link to="/contacto" @click="closeMobileMenu">Contacto</router-link>
        
        <div class="drawer-actions">
          <div style="display: flex; gap: 1rem; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;">
            <ThemeToggle />
            <div class="lang-switch" role="group">
              <button type="button" :class="{ active: locale === 'es' }" @click="setLocale('es')">ES</button>
              <button type="button" :class="{ active: locale === 'en' }" @click="setLocale('en')">EN</button>
            </div>
          </div>
          
          <template v-if="isLoggedIn">
            <router-link class="btn btn-primary btn-block" to="/app" @click="closeMobileMenu">{{ t('landing.goPanel', 'Ir al panel') }}</router-link>
          </template>
          <template v-else>
            <router-link class="btn btn-ghost btn-block" to="/login" style="margin-bottom: 1rem;" @click="closeMobileMenu">{{ t('landing.login', 'Ingresar') }}</router-link>
            <router-link class="btn btn-primary btn-block" :to="accessPath" @click="closeMobileMenu">{{ t('landing.requestAccess', 'Solicitar acceso') }}</router-link>
          </template>
        </div>
      </div>
    </div>
    <!-- Backdrop -->
    <div class="drawer-backdrop" :class="{ 'drawer-backdrop-open': isMobileMenuOpen }" @click="closeMobileMenu"></div>

    <main class="commercial-content">
      <slot></slot>
    </main>

    <LeadCaptureBar />
    <LeadMagnetModal />

    <footer class="foot">
      <div class="wrap foot-row">
        <div class="foot-brand">
          <span class="brand-icon brand-icon--sm" aria-hidden="true">
            <component :is="brandIcon" :size="12" />
          </span>
          {{ t('landing.footerBrand', '© METGO3D SpA.') }}
        </div>
        <div class="foot-links">
          <router-link to="/planes">Planes</router-link>
          <router-link to="/blog">Blog</router-link>
          <router-link to="/nosotros">Nosotros</router-link>
          <router-link to="/contacto">Contacto</router-link>
          <router-link to="/login">{{ t('landing.login', 'Ingresar') }}</router-link>
          <router-link v-if="isLoggedIn" to="/app">{{ t('landing.goPanel', 'Ir al panel') }}</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<style>
/* CSS Variables for standardizing landing pages */
.commercial-layout {
  --bg-color: #080c14;
  --surface-color: #121a2b;
  --surface-2-color: #0d1420;
  --text-color: #f4f7fa;
  --muted-color: #8fa0b3;
  --dim-color: #4c5a70;
  --border-color: rgba(255, 255, 255, 0.08);
  
  --accent: var(--local-accent, #00ffaa);
  --border-accent: color-mix(in srgb, var(--accent) 28%, transparent);
  --accent-dim: color-mix(in srgb, var(--accent) 12%, transparent);
  
  --bg-glow: radial-gradient(ellipse 900px 500px at 15% -10%, color-mix(in srgb, var(--local-accent) 10%, transparent), transparent 60%),
    radial-gradient(ellipse 700px 500px at 100% 20%, rgba(14, 165, 233, 0.06), transparent 55%);
  --mono: ui-monospace, 'SF Mono', 'Cascadia Code', 'Segoe UI Mono', monospace;

  min-height: 100vh;
  background: var(--bg-color);
  background-image: var(--bg-glow);
  background-attachment: fixed;
  color: var(--text-color);
  font-family: 'DM Sans', system-ui, sans-serif;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  transition: background-color 0.3s, color 0.3s;
  display: flex;
  flex-direction: column;
}

[data-theme="light"] .commercial-layout {
  --bg-color: #f8fafc;
  --surface-color: #ffffff;
  --surface-2-color: #f1f5f9;
  --text-color: #0f172a;
  --muted-color: #64748b;
  --dim-color: #94a3b8;
  --border-color: rgba(0, 0, 0, 0.08);
  
  --border-accent: color-mix(in srgb, var(--accent) 40%, transparent);
  --accent-dim: color-mix(in srgb, var(--accent) 20%, transparent);
  
  --bg-glow: radial-gradient(ellipse 900px 500px at 15% -10%, color-mix(in srgb, var(--local-accent) 15%, transparent), transparent 60%),
    radial-gradient(ellipse 700px 500px at 100% 20%, rgba(14, 165, 233, 0.1), transparent 55%);
}

.commercial-layout a {
  color: inherit;
  text-decoration: none;
}
.commercial-layout .wrap {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 28px;
}

/* Accessibility */
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

/* Header */
.top {
  position: sticky;
  top: 0;
  z-index: 50;
  background: color-mix(in srgb, var(--bg-color) 82%, transparent);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
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
  background: var(--accent); /* fallback */
  background: linear-gradient(145deg, color-mix(in srgb, var(--accent) 80%, white), var(--accent));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #04140e;
  box-shadow: 0 4px 16px color-mix(in srgb, var(--accent) 35%, transparent);
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
  color: var(--dim-color);
  font-family: var(--mono);
  letter-spacing: 1px;
  margin-top: 1px;
}

/* Nav Links */
.nav-links {
  display: flex;
  align-items: center;
  gap: 30px;
}
.nav-links a {
  font-size: 13.5px;
  color: var(--muted-color);
  transition: color 0.15s;
  font-weight: 500;
}
.nav-links a:hover,
.nav-links a.router-link-active {
  color: var(--text-color);
}

/* Buttons */
.nav-cta {
  display: flex;
  align-items: center;
  gap: 10px;
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
.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px color-mix(in srgb, var(--accent) 30%, transparent);
}
.btn-ghost {
  border-color: var(--border-color);
  color: var(--text-color);
  background: transparent;
}
.btn-ghost:hover {
  border-color: var(--border-accent);
  background: var(--accent-dim);
}
.btn-block {
  width: 100%;
}

/* Lang Switch */
.lang-switch {
  display: flex;
  gap: 4px;
  margin-right: 4px;
}
.lang-switch button {
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--muted-color);
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

/* Mobile responsive utils */
.mobile-only {
  display: none;
}
.mobile-menu-btn {
  background: transparent;
  border: none;
  color: var(--text-color);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
}

@media (max-width: 900px) {
  .desktop-only {
    display: none !important;
  }
  .mobile-only {
    display: block;
  }
}

/* Drawer Component */
.mobile-drawer {
  position: fixed;
  top: 0;
  right: -100%;
  width: 280px;
  height: 100vh;
  background: var(--surface-color);
  z-index: 200;
  transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.2);
  border-left: 1px solid var(--border-color);
}
.mobile-drawer.drawer-open {
  right: 0;
}
.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}
.drawer-header .brand-name {
  font-size: 1.1rem;
}
.close-btn {
  background: transparent;
  border: none;
  color: var(--muted-color);
  cursor: pointer;
}
.drawer-content {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  flex-grow: 1;
}
.drawer-content a {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color);
}
.drawer-actions {
  margin-top: auto;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}
.drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 150;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s;
}
.drawer-backdrop-open {
  opacity: 1;
  pointer-events: auto;
}

/* Main Content Wrapper */
.commercial-content {
  flex-grow: 1;
}

/* Footer */
.foot {
  margin-top: auto;
  border-top: 1px solid var(--border-color);
  background: var(--surface-color);
  padding: 32px 0;
  font-size: 13px;
  color: var(--dim-color);
}
.foot-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 20px;
}
.foot-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--mono);
}
.foot-links {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}
.foot-links a {
  transition: color 0.15s;
}
.foot-links a:hover {
  color: var(--accent);
}
</style>
