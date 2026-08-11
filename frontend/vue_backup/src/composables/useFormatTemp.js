import { computed } from 'vue'
import { usePreferencesStore } from '@/stores/preferences'
import { formatTemperatura as fmt } from '@/utils/formatTemperatura'

/** Preferencias de usuario + formateo de temperatura (P7). */
export function useFormatTemp() {
  const prefs = usePreferencesStore()
  const unit = computed(() => prefs.tempUnit)
  function formatTemperatura(celsius, digits = 1) {
    return fmt(celsius, unit.value, digits)
  }
  return { unit, formatTemperatura }
}
