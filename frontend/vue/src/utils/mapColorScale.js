/** Escala de color fija para mapas IDW (no min-max dinámico). */

const RANGOS = {
  temperatura: { min: 5, max: 32 },
  humedad: { min: 20, max: 100 },
  precipitacion: { min: 0, max: 25 },
  radiacion: { min: 0, max: 900 },
  nubosidad: { min: 0, max: 100 },
  viento_velocidad: { min: 0, max: 20 },
  presion: { min: 990, max: 1025 },
}

export function rangoMapa(variable) {
  return RANGOS[variable] || { min: 0, max: 100 }
}

export function valorANormalizado(variable, valor) {
  const { min, max } = rangoMapa(variable)
  if (valor == null || Number.isNaN(valor)) return 0
  return Math.max(0, Math.min(1, (Number(valor) - min) / (max - min || 1)))
}

export function colorMapa(variable, n) {
  const t = Math.max(0, Math.min(1, n))
  if (variable === 'temperatura') {
    const r = Math.round(30 + t * 200)
    const g = Math.round(80 + t * 60)
    const b = Math.round(200 - t * 170)
    return `rgb(${r}, ${g}, ${b})`
  }
  if (variable === 'humedad') {
    return `hsl(${210 - t * 120}, ${50 + t * 40}%, ${55 - t * 20}%)`
  }
  if (variable === 'precipitacion') {
    if (t < 0.02) return '#e5e7eb'
    return `hsl(220, ${40 + t * 60}%, ${45 - t * 15}%)`
  }
  if (variable === 'radiacion') {
    return `hsl(${45 + t * 25}, 90%, ${70 - t * 35}%)`
  }
  if (variable === 'nubosidad') {
    return `hsl(210, 15%, ${75 - t * 45}%)`
  }
  if (variable === 'viento_velocidad') {
    return `hsl(${200 + t * 80}, 75%, 50%)`
  }
  return `hsl(${t * 240}, 70%, 50%)`
}
