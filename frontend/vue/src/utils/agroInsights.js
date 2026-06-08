/** Indicadores derivados para vistas agrícolas y resumen. */

const UMBRALES_HELADA = {
  palto: { critico: 0, alto: 2, moderado: 5 },
  vid: { critico: -1, alto: 1, moderado: 4 },
  citricos: { critico: 0, alto: 2.5, moderado: 5 },
  tomate: { critico: 2, alto: 4, moderado: 6 },
  lechuga: { critico: 3, alto: 5, moderado: 7 },
}

export function riesgoHelada(tempMin) {
  return riesgoHeladaPorCultivo(tempMin, 'palto')
}

export function riesgoHeladaPorCultivo(tempMin, cultivo = 'palto') {
  if (tempMin == null) return { nivel: 'unknown', label: 'Sin dato', severidad: 'bajo' }
  const umb = UMBRALES_HELADA[cultivo] || UMBRALES_HELADA.palto
  if (tempMin <= umb.critico) {
    return { nivel: 'high', label: 'Riesgo crítico de helada', severidad: 'critico' }
  }
  if (tempMin <= umb.alto) {
    return { nivel: 'high', label: 'Riesgo alto de helada', severidad: 'alto' }
  }
  if (tempMin <= umb.moderado) {
    return { nivel: 'medium', label: 'Riesgo moderado de helada', severidad: 'moderado' }
  }
  return { nivel: 'low', label: 'Sin riesgo de helada', severidad: 'bajo' }
}

export function riesgoEncharcamiento(precip24h, cultivo = 'palto') {
  const umb = { palto: 25, vid: 20, citricos: 22, tomate: 18, lechuga: 15 }
  const u = umb[cultivo] ?? 25
  if (precip24h >= u) return { nivel: 'high', label: 'Riesgo encharcamiento' }
  if (precip24h >= u * 0.6) return { nivel: 'medium', label: 'Vigilar drenaje' }
  return { nivel: 'low', label: 'Sin riesgo' }
}

export function intensidadLluvia(mm) {
  if (mm < 0.1) return 'sin_lluvia'
  if (mm < 2) return 'ligera'
  if (mm < 10) return 'moderada'
  if (mm < 25) return 'fuerte'
  return 'extrema'
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
