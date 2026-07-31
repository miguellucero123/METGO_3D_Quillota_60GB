<template>
  <div class="page">
    <header class="page-head">
      <h1>{{ t('informes.title') }}</h1>
      <p>{{ t('informes.sub', { name: faenaMeta?.nombre || sitioId }) }}</p>
    </header>

    <section class="card">
      <h2>{{ t('informes.opTitle') }}</h2>
      <p class="hint">{{ t('informes.opHint') }}</p>
      <div class="actions">
        <a class="btn solid" :href="urlPdf" target="_blank" rel="noopener">{{ t('informes.pdf') }}</a>
        <a class="btn ghost" :href="urlHtml" target="_blank" rel="noopener">{{ t('informes.html') }}</a>
        <a class="btn ghost" :href="urlCsv" target="_blank" rel="noopener">{{ t('informes.csv') }}</a>
      </div>
    </section>

    <section class="card">
      <h2>{{ t('informes.monthlyTitle') }}</h2>
      <p v-if="!puedeMensual" class="hint">{{ t('informes.monthlyLocked') }}</p>
      <template v-else>
        <p class="hint">{{ t('informes.monthlyHint') }}</p>
        <div class="actions">
          <a class="btn solid" :href="urlMensual" target="_blank" rel="noopener">{{ t('informes.monthlyOpen') }}</a>
        </div>
      </template>
    </section>

    <section class="card muted">
      <h2>{{ t('informes.commercialTitle') }}</h2>
      <p class="hint">{{ t('informes.commercialHint') }}</p>
      <ul class="links">
        <li><a href="/docs-comercial/propuesta-comercial.html" @click.prevent="avisoPlantilla">{{ t('informes.proposal') }}</a></li>
        <li><a href="/docs-comercial/datasheet-tecnico.html" @click.prevent="avisoPlantilla">{{ t('informes.datasheet') }}</a></li>
      </ul>
      <p class="fine">{{ t('informes.fine') }}</p>
    </section>

    <p class="back">
      <router-link :to="{ name: 'faena-ahora', params: { faena: sitioId } }">{{ t('informes.back') }}</router-link>
    </p>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { urlInformeFaena, urlReporteMensual } from '@/services/spatiApi'
import { useAccess } from '@/stores/access'

const { t } = useI18n()
const site = inject('site')
const route = useRoute()
const access = useAccess()
const injectedFaena = inject('faena', null)
const injectedMeta = inject('faenaMeta', null)

const sitioId = computed(
  () =>
    (injectedFaena && injectedFaena.value) ||
    String(route.params.faena || site.spatiDefaultSitio || 'quebrada_blanca').toLowerCase(),
)
const faenaMeta = computed(
  () =>
    (injectedMeta && injectedMeta.value) ||
    (site.stations || []).find((s) => s.slug === sitioId.value) || { slug: sitioId.value },
)

const urlPdf = computed(() => urlInformeFaena(sitioId.value, 'pdf'))
const urlHtml = computed(() => urlInformeFaena(sitioId.value, 'html'))
const urlCsv = computed(() => urlInformeFaena(sitioId.value, 'csv'))
const urlMensual = computed(() => urlReporteMensual(sitioId.value))

const snap = computed(() => access.snapshot(sitioId.value))
const puedeMensual = computed(() => {
  const plan = String(snap.value?.plan_code || '').toLowerCase()
  return ['pro', 'enterprise'].includes(plan)
})

function avisoPlantilla() {
  window.alert(t('informes.fine'))
}
</script>

<style scoped>
.page {
  padding: 1.25rem;
  max-width: 720px;
  color: var(--color-text);
}
.page-head h1 {
  margin: 0 0 0.25rem;
  font-size: 1.35rem;
}
.page-head p {
  margin: 0;
  color: var(--color-muted);
  font-size: 0.9rem;
}
.card {
  margin-top: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.1rem 1.15rem;
  background: var(--color-surface, rgba(17, 24, 39, 0.6));
}
.card.muted {
  opacity: 0.92;
}
.card h2 {
  margin: 0 0 0.4rem;
  font-size: 1.05rem;
}
.hint {
  margin: 0 0 0.85rem;
  color: var(--color-muted);
  font-size: 0.88rem;
  line-height: 1.45;
}
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 0.9rem;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.88rem;
  text-decoration: none;
}
.btn.solid {
  background: #10b981;
  color: #0f172a;
}
.btn.ghost {
  border: 1px solid var(--color-border);
  color: var(--color-text);
}
.links {
  margin: 0;
  padding-left: 1.1rem;
  color: #5eead4;
}
.fine {
  margin: 0.75rem 0 0;
  font-size: 0.75rem;
  color: var(--color-muted);
}
.back {
  margin-top: 1.25rem;
}
.back a {
  color: #10b981;
  text-decoration: none;
  font-weight: 600;
}
</style>
