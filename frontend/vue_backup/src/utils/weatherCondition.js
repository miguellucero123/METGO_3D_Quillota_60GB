/**
 * Clasificación visual del tiempo (alineada con WeatherScene).
 * @param {{ precipitacion?: number, humedad?: number, temperatura_min?: number, nubosidad?: number }} d
 */
export function classifyWeather(d = {}) {
  const tmin = Number(d.temperatura_min ?? d.temperatura ?? 15)
  const precip = Number(d.precipitacion ?? 0)
  const hum = Number(d.humedad ?? 60)
  const nub = Number(d.nubosidad ?? Math.max(0, Math.min(100, 100 - hum + precip * 8)))

  if (tmin <= 2) return 'helada'
  if (precip >= 2) return 'lluvioso'
  if (nub >= 70 || hum >= 88) return 'nublado'
  if (nub >= 35 || hum >= 68 || precip >= 0.3) return 'parcial'
  return 'soleado'
}

export const WEATHER_LABELS = {
  soleado: 'Soleado',
  parcial: 'Parcialmente nublado',
  nublado: 'Nublado',
  lluvioso: 'Lluvioso',
  helada: 'Riesgo de heladas',
}
