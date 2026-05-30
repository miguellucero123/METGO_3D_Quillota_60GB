<script setup>
import { usePreferencesStore } from '@/stores/preferences'
import { Settings } from 'lucide-vue-next'
import SectionCard from '@/components/ui/SectionCard.vue'

const prefs = usePreferencesStore()
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Preferencias</h2>
      <p class="page-subtitle">Unidades y apariencia · alias `/preferencias-clima`</p>
    </header>

    <SectionCard title="Unidades meteorológicas" subtitle="Aplica en panel y detalle de estación">
      <template #icon><Settings /></template>
      <fieldset class="field-group">
        <legend>Temperatura</legend>
        <label class="radio-row">
          <input
            type="radio"
            name="unit"
            value="C"
            :checked="prefs.tempUnit === 'C'"
            @change="prefs.setTempUnit('C')"
          />
          Celsius (°C)
        </label>
        <label class="radio-row">
          <input
            type="radio"
            name="unit"
            value="F"
            :checked="prefs.tempUnit === 'F'"
            @change="prefs.setTempUnit('F')"
          />
          Fahrenheit (°F)
        </label>
      </fieldset>
    </SectionCard>

    <SectionCard title="Tema visual" subtitle="Claro u oscuro">
      <fieldset class="field-group">
        <legend>Apariencia</legend>
        <label class="radio-row">
          <input
            type="radio"
            name="theme"
            value="light"
            :checked="prefs.theme === 'light'"
            @change="prefs.setTheme('light')"
          />
          Claro (verde METGO)
        </label>
        <label class="radio-row">
          <input
            type="radio"
            name="theme"
            value="dark"
            :checked="prefs.theme === 'dark'"
            @change="prefs.setTheme('dark')"
          />
          Oscuro
        </label>
      </fieldset>
    </SectionCard>
  </div>
</template>

<style scoped>
.field-group {
  border: none;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.field-group legend {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-muted);
  margin-bottom: 0.35rem;
}
.radio-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
}
</style>
