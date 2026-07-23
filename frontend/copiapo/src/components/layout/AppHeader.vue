<template>
  <header class="metgo-header">
    <div class="header-brand">
      <span class="brand-mark">{{ site.productName }}</span>
      <span class="brand-site">{{ site.siteLabel }}</span>
    </div>
    <p class="header-tagline">{{ site.copy?.headerTitle || site.tagline }}</p>
    <span class="header-version">{{ site.versionLabel }}</span>
  </header>
</template>

<script setup>
import { inject } from 'vue'
const site = inject('site')
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
.header-version {
  font-size: 0.75rem;
  color: var(--color-muted);
}
</style>
