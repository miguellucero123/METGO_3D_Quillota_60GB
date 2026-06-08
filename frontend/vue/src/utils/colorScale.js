/** Paletas de color meteorológicas — precipitación, helada, PoP. */

export function precipColor(valor) {
  if (valor == null || valor < 0.1) return '#d1d5db'
  if (valor < 2) return '#bfdbfe'
  if (valor < 10) return '#60a5fa'
  if (valor < 25) return '#1e40af'
  if (valor < 40) return '#7c3aed'
  return '#991b1b'
}

export function intensidadColor(valor) {
  if (valor < 0.5) return '#86efac'
  if (valor < 1.5) return '#3b82f6'
  if (valor < 3) return '#f59e0b'
  if (valor < 5) return '#ef4444'
  return '#991b1b'
}

export function popColor(valor) {
  if (!valor) return '#d1d5db'
  if (valor < 25) return '#93c5fd'
  if (valor < 50) return '#3b82f6'
  if (valor < 75) return '#1d4ed8'
  return '#1e3a8a'
}

export function severidadAlertaColor(nivel) {
  const colores = {
    verde: '#22c55e',
    amarillo: '#eab308',
    naranja: '#f97316',
    rojo: '#ef4444',
    morado: '#a855f7',
    critico: '#7c3aed',
    alto: '#ef4444',
    moderado: '#f97316',
    bajo: '#22c55e',
  }
  return colores[nivel] || '#6b7280'
}

export function etiquetaIntensidad(mm) {
  if (mm < 0.1) return 'Sin lluvia'
  if (mm < 2) return 'Ligera'
  if (mm < 10) return 'Moderada'
  if (mm < 25) return 'Fuerte'
  return 'Extrema'
}
