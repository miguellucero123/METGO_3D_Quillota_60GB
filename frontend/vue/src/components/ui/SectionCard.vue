<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})
</script>

<template>
  <section class="section-card">
    <header class="section-card__head">
      <div class="section-card__title-row">
        <span v-if="$slots.icon" class="section-card__icon">
          <slot name="icon" />
        </span>
        <div>
          <h3 class="section-card__title">{{ title }}</h3>
          <p v-if="subtitle" class="section-card__subtitle">{{ subtitle }}</p>
        </div>
      </div>
      <div v-if="$slots.actions" class="section-card__actions">
        <slot name="actions" />
      </div>
    </header>
    <div class="section-card__content">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.section-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.section-card__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-primary-subtle);
}

.section-card__title-row {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
}

.section-card__icon {
  color: var(--color-primary);
  display: flex;
  padding-top: 0.1rem;
}

.section-card__icon :deep(svg) {
  width: 1.125rem;
  height: 1.125rem;
}

.section-card__title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text);
}

.section-card__subtitle {
  font-size: 0.8rem;
  color: var(--color-muted);
  margin-top: 0.15rem;
}

.section-card__content {
  padding: 1.25rem;
}
</style>
