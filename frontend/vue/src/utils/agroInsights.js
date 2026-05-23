/** Indicadores derivados para vistas agrícolas y resumen. */

export function riesgoHelada(tempMin) {
  if (tempMin == null) return { nivel: 'unknown', label: 'Sin dato' }
  if (tempMin <= 2) return { nivel: 'high', label: 'Riesgo alto de helada' }
  if (tempMin <= 5) return { nivel: 'medium', label: 'Riesgo moderado de helada' }
  return { nivel: 'low', label: 'Sin riesgo de helada' }
}

export function necesidadRiego(humedad, precipitacion) {
  if (humedad == null) return { nivel: 'unknown', label: 'Sin dato' }
  if (precipitacion >= 5) return { nivel: 'low', label: 'Suspender riego (lluvia esperada)' }
  if (humedad < 45) return { nivel: 'high', label: 'Riego recomendado' }
  if (humedad < 60) return { nivel: 'medium', label: 'Monitorear humedad' }
  return { nivel: 'low', label: 'Humedad adecuada' }
}

export function condicionViento(viento) {
  if (viento == null) return { nivel: 'unknown', label: 'Sin dato' }
  if (viento >= 40) return { nivel: 'high', label: 'Viento fuerte — cautela en aplicaciones' }
  if (viento >= 25) return { nivel: 'medium', label: 'Viento moderado' }
  return { nivel: 'low', label: 'Condiciones de viento favorables' }
}

export const CULTIVOS_QUILLOTA = [
  { nombre: 'Palta', area: 'Alta', estacion: 'Cosecha / floración' },
  { nombre: 'Cítricos', area: 'Alta', estacion: 'Crecimiento / cosecha' },
  { nombre: 'Vid', area: 'Media', estacion: 'Poda / brotación' },
  { nombre: 'Hortalizas', area: 'Media', estacion: 'Siembra continua' },
  { nombre: 'Frutales de hueso', area: 'Media', estacion: 'Floración' },
]

export function acumuladoPrecipitacion(pronostico) {
  if (!pronostico?.length) return 0
  return pronostico.reduce((s, d) => s + (Number(d.precipitacion) || 0), 0)
}
