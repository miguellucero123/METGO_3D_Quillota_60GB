/** Paleta semántica agrícola METGO 3D (consistente con mapas y barras). */

export function tempColor(valor) {
  if (valor == null || Number.isNaN(valor)) return '#9ca3af'
  if (valor < 0) return '#3b82f6'
  if (valor < 5) return '#60a5fa'
  if (valor < 15) return '#22d3ee'
  if (valor < 25) return '#f59e0b'
  if (valor < 32) return '#ef4444'
  return '#7c3aed'
}

export function humedadColor(valor) {
  if (valor == null) return '#9ca3af'
  if (valor < 40) return '#ef4444'
  if (valor < 55) return '#f59e0b'
  if (valor < 75) return '#22c55e'
  return '#3b82f6'
}

export function riegoColor(mm) {
  if (mm === 0) return '#F09595'
  if (mm < 3) return '#FAC775'
  return '#5DCAA5'
}

export function riesgoHelada(tMin) {
  if (tMin == null) {
    return { nivel: 'bajo', label: 'Sin dato', color: '#6b7280', bg: '#f3f4f6' }
  }
  if (tMin <= 0) return { nivel: 'critico', label: 'Helada severa', color: '#A32D2D', bg: '#FCEBEB' }
  if (tMin <= 3) return { nivel: 'alto', label: 'Riesgo alto', color: '#A32D2D', bg: '#FCEBEB' }
  if (tMin <= 7) return { nivel: 'moderado', label: 'Riesgo moderado', color: '#633806', bg: '#FAEEDA' }
  return { nivel: 'bajo', label: 'Sin riesgo', color: '#3B6D11', bg: '#EAF3DE' }
}

export const CULTIVOS_CATALOG = [
  { label: 'Palto', slug: 'palto', icono: 'leaf' },
  { label: 'Cítricos', slug: 'citricos', icono: 'citrus' },
  { label: 'Vid', slug: 'vid', icono: 'grape' },
  { label: 'Tomate', slug: 'tomate', icono: 'tomato' },
  { label: 'Lechuga', slug: 'lechuga', icono: 'salad' },
]

export const CULTIVOS_RIEGO_SLUGS = new Set([
  'palto',
  'citricos',
  'vid',
  'tomate',
  'lechuga',
  'hortalizas',
  'cereales',
])
