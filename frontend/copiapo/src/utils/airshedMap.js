/**
 * Helpers mapa airshed Copiapó (viento + plumas simplificadas).
 */

/** Rumbo cardenal desde grados meteorológicos (FROM). */
export function rumboCardinal(deg) {
  if (deg == null || Number.isNaN(Number(deg))) return '—'
  const d = ((Number(deg) % 360) + 360) % 360
  const dirs = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']
  return dirs[Math.round(d / 45) % 8]
}

export function textoViento(velocidad, direccion) {
  if (velocidad == null || Number.isNaN(Number(velocidad))) return null
  const rumbo = rumboCardinal(direccion)
  return `${rumbo} ${Number(velocidad).toFixed(1)} m/s`
}

/** Largo flecha SVG (px): 1 px por 0.5 m/s, clamp 10–40. */
export function largoFlechaViento(ms) {
  const v = Number(ms)
  if (!Number.isFinite(v) || v <= 0) return 0
  return Math.min(40, Math.max(10, v / 0.5))
}

/**
 * Rotación CSS de flecha: convención meteo FROM → punta hacia donde sopla (+180).
 */
export function rotacionFlechaHacia(degFrom) {
  const d = Number(degFrom)
  if (!Number.isFinite(d)) return 0
  return (d + 180) % 360
}

function destPoint(lon, lat, bearingDeg, distKm) {
  const R = 6371
  const brng = (bearingDeg * Math.PI) / 180
  const lat1 = (lat * Math.PI) / 180
  const lon1 = (lon * Math.PI) / 180
  const lat2 = Math.asin(
    Math.sin(lat1) * Math.cos(distKm / R) +
      Math.cos(lat1) * Math.sin(distKm / R) * Math.cos(brng)
  )
  const lon2 =
    lon1 +
    Math.atan2(
      Math.sin(brng) * Math.sin(distKm / R) * Math.cos(lat1),
      Math.cos(distKm / R) - Math.sin(lat1) * Math.sin(lat2)
    )
  return [(lon2 * 180) / Math.PI, (lat2 * 180) / Math.PI]
}

/**
 * Pluma simplificada downwind (triángulo) a partir de dirección FROM y velocidad.
 * lengthKm escala con viento e índice de dispersión (más bajo = pluma más corta/ancha).
 */
export function plumeFeature(punto) {
  const { lon, lat, viento_direccion: dir, viento_velocidad: vel, valor, color } = punto
  if (dir == null || Number.isNaN(Number(dir))) return null
  const downwind = (Number(dir) + 180) % 360
  const v = Number(vel) || 1
  const idx = valor != null ? Number(valor) : 50
  // Dispersión baja → pluma más corta (contaminante queda cerca)
  const lengthKm = Math.min(8, Math.max(1.2, (v * 0.6) * (idx / 50)))
  const halfSpread = Math.min(35, Math.max(12, 40 - idx / 4))
  const tip = destPoint(lon, lat, downwind, lengthKm)
  const left = destPoint(lon, lat, downwind - halfSpread, lengthKm * 0.85)
  const right = destPoint(lon, lat, downwind + halfSpread, lengthKm * 0.85)
  return {
    type: 'Feature',
    properties: {
      slug: punto.slug,
      color: color || '#fbbf24',
      nombre: punto.nombre,
    },
    geometry: {
      type: 'Polygon',
      coordinates: [[[lon, lat], left, tip, right, [lon, lat]]],
    },
  }
}

export function plumesGeoJSON(puntos) {
  const features = (puntos || []).map(plumeFeature).filter(Boolean)
  return { type: 'FeatureCollection', features }
}

export const BOUNDS_COPIAPO = {
  west: -70.45,
  south: -27.6,
  east: -70.2,
  north: -27.25,
}

export const MAP_STYLE_DARK = {
  version: 8,
  name: 'metgo-copiapo-dark',
  glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
  sources: {
    hillshade: {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Hillshade/MapServer/tile/{z}/{y}/{x}',
      ],
      tileSize: 256,
      attribution: 'Esri',
    },
    carto: {
      type: 'raster',
      tiles: ['https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '© CARTO © OpenStreetMap',
    },
  },
  layers: [
    {
      id: 'hillshade',
      type: 'raster',
      source: 'hillshade',
      paint: { 'raster-opacity': 0.55 },
    },
    {
      id: 'carto-dark',
      type: 'raster',
      source: 'carto',
      paint: { 'raster-opacity': 0.88 },
    },
  ],
}

/** Estilo satelital + relieve (fondo geográfico valle Copiapó / Paipote). */
export const MAP_STYLE_SATELLITE = {
  version: 8,
  name: 'metgo-copiapo-sat',
  glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
  sources: {
    sat: {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      ],
      tileSize: 256,
      maxzoom: 19,
      attribution: 'Esri World Imagery',
    },
    hillshade: {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Hillshade/MapServer/tile/{z}/{y}/{x}',
      ],
      tileSize: 256,
      attribution: 'Esri',
    },
    labels: {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
      ],
      tileSize: 256,
      attribution: 'Esri',
    },
  },
  layers: [
    { id: 'sat', type: 'raster', source: 'sat', paint: { 'raster-opacity': 1 } },
    {
      id: 'hillshade',
      type: 'raster',
      source: 'hillshade',
      paint: { 'raster-opacity': 0.28 },
    },
    {
      id: 'labels',
      type: 'raster',
      source: 'labels',
      paint: { 'raster-opacity': 0.85 },
    },
  ],
}

/** Vectores de viento → LineString (punta = dirección hacia donde sopla). */
export function windVectorsToGeoJSON(vectors) {
  const features = (vectors || [])
    .map((v) => {
      if (v.lon == null || v.lat == null) return null
      const speed = Number(v.speed_ms) || 1
      const bearing = Number(v.dir_to ?? ((Number(v.dir_from) + 180) % 360))
      if (!Number.isFinite(bearing)) return null
      const tip = destPoint(v.lon, v.lat, bearing, Math.min(2.2, Math.max(0.35, speed * 0.28)))
      return {
        type: 'Feature',
        properties: { speed, dir_to: bearing },
        geometry: {
          type: 'LineString',
          coordinates: [
            [v.lon, v.lat],
            tip,
          ],
        },
      }
    })
    .filter(Boolean)
  return { type: 'FeatureCollection', features }
}

/** Fuentes de emisión → puntos. */
export function fuentesToGeoJSON(fuentes) {
  const features = (fuentes || [])
    .filter((f) => f.lon != null && f.lat != null)
    .map((f) => ({
      type: 'Feature',
      properties: {
        id: f.id,
        nombre: f.nombre || f.id,
        tipo: f.tipo || 'fuente',
        q: f.q,
      },
      geometry: { type: 'Point', coordinates: [f.lon, f.lat] },
    }))
  return { type: 'FeatureCollection', features }
}
