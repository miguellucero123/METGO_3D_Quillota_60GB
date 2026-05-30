/**
 * Formatea temperatura según preferencia de unidad (Portafolio 7 — °C/°F).
 * @param {number|null|undefined} celsius
 * @param {'C'|'F'} unit
 */
export function celsiusToFahrenheit(c) {
  return (Number(c) * 9) / 5 + 32
}

export function formatTemperatura(celsius, unit = 'C', digits = 1) {
  if (celsius == null || Number.isNaN(Number(celsius))) return '—'
  if (unit === 'F') {
    return `${celsiusToFahrenheit(celsius).toFixed(digits)}°F`
  }
  return `${Number(celsius).toFixed(digits)}°C`
}
