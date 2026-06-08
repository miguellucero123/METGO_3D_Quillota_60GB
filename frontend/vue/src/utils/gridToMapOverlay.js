import { colorMapa, valorANormalizado } from '@/utils/mapColorScale'

/** Convierte color CSS (rgb/hsl/hex) a rgba con alpha. */
function cssColorToRgba(color, alpha) {
  const canvas = document.createElement('canvas')
  canvas.width = 1
  canvas.height = 1
  const ctx = canvas.getContext('2d')
  ctx.fillStyle = color
  ctx.fillRect(0, 0, 1, 1)
  const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data
  return `rgba(${r},${g},${b},${alpha})`
}

/**
 * Grilla IDW → imagen PNG semitransparente para Leaflet ImageOverlay.
 * Fila 0 = latitud norte (lat_max).
 */
export function grillaADataUrl(grilla, variable, alpha = 0.62) {
  if (!grilla?.valores?.length) return null
  const { lats, lons, valores } = grilla
  const nLat = lats.length
  const nLon = lons.length
  const canvas = document.createElement('canvas')
  canvas.width = Math.max(nLon, 2)
  canvas.height = Math.max(nLat, 2)
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  for (let i = 0; i < nLat; i++) {
    for (let j = 0; j < nLon; j++) {
      const val = valores[i]?.[j]
      if (val == null) continue
      const n = valorANormalizado(variable, val)
      ctx.fillStyle = cssColorToRgba(colorMapa(variable, n), alpha)
      ctx.fillRect(j, i, 1, 1)
    }
  }
  return canvas.toDataURL('image/png')
}

export function boundsLeaflet(grilla, ambito = 'regional') {
  const b = grilla?.bounds
  if (b) {
    return [
      [b.lat_min, b.lon_min],
      [b.lat_max, b.lon_max],
    ]
  }
  if (ambito === 'global') {
    return [
      [-60, -180],
      [60, 180],
    ]
  }
  const { lats, lons } = grilla || {}
  if (!lats?.length || !lons?.length) {
    return [
      [-33.15, -71.35],
      [-32.75, -71.05],
    ]
  }
  return [
    [Math.min(...lats), Math.min(...lons)],
    [Math.max(...lats), Math.max(...lons)],
  ]
}
