<template>
  <header class="metgo-header">
    <div class="header-left">
      <button
        type="button"
        class="nav-toggle"
        :aria-expanded="navOpen ? 'true' : 'false'"
        aria-controls="metgo-sidebar"
        :aria-label="t('app.menuToggle')"
        @click="toggleNav"
      >
        <Menu :size="20" aria-hidden="true" />
      </button>
      <div class="header-brand">
        <span class="brand-mark">{{ site.productName }}</span>
        <span class="brand-site">{{ site.siteLabel }}</span>
      </div>
    </div>
    <p class="header-tagline">{{ t('app.subtitle') }}</p>
    <div class="header-actions">
      <ThemeToggle />
      <div class="lang-switch" role="group" :aria-label="t('lang.label')">
        <button type="button" :class="{ active: locale === 'es' }" @click="setLocale('es')">
          {{ t('lang.es') }}
        </button>
        <button type="button" :class="{ active: locale === 'en' }" @click="setLocale('en')">
          {{ t('lang.en') }}
        </button>
      </div>
      <span v-if="auth.state.user" class="header-user" :title="auth.state.user.role">
        {{ auth.state.user.username }}
      </span>
      <button type="button" class="header-logout" @click="onLogout">{{ t('app.logout') }}</button>
      <span class="header-version">{{ site.versionLabel }}</span>
    </div>
  </header>
</template>

<script setup>
import { inject } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Menu } from 'lucide-vue-next'
import { useAuth } from '@/stores/auth'
import { setLocale } from '@/i18n'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'

const site = inject('site')
const navOpen = inject('navOpen', null)
const toggleNav = inject('toggleNav', () => {})
const auth = useAuth()
const router = useRouter()
const { t, locale } = useI18n()

function onLogout() {
  auth.logout()
  router.push({ name: 'landing' })
}
</script>

<style scoped>
.metgo-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem 1.25rem;
  padding: 0.85rem 1.25rem;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}
.header-left {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}
.nav-toggle {
  display: none;
  align-items: center;
  justify-content: center;
  width: 2.4rem;
  height: 2.4rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-text);
  cursor: pointer;
}
.nav-toggle:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
@media (max-width: 900px) {
  .nav-toggle {
    display: inline-flex;
  }
}
.header-brand {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}
.brand-mark {
  font-weight: 700;
  font-size: 1.15rem;
  letter-spacing: 0.04em;
  color: var(--color-primary);
}
.brand-site {
  font-weight: 600;
  color: var(--color-text);
}
.header-tagline {
  flex: 1;
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}
.lang-switch {
  display: inline-flex;
  gap: 0.2rem;
}
.lang-switch button {
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-muted);
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.45rem;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
}
.lang-switch button.active {
  color: var(--color-primary);
  border-color: var(--color-primary);
}
.header-user {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}
.header-logout {
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
  padding: 0.25rem 0.55rem;
  font-size: 0.75rem;
  cursor: pointer;
}
.header-logout:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
}
.header-version {
  font-size: 0.75rem;
  color: var(--color-muted);
}
</style>
