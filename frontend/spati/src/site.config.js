/**
 * METGO SPATI — Pronóstico de izaje en mineras de alta montaña (Chile).
 */
export default {
  sitio: 'mantos_blancos',
  productName: 'METGO',
  siteLabel: 'SPATI Izaje',
  tagline: 'Pronóstico 72 h · mineras alta montaña · alertas 0–3',
  region: 'Chile · 17 faenas de alta montaña',
  versionLabel: 'v0.2 · SPATI Alta Montaña',
  documentTitle: 'METGO SPATI — Izaje alta montaña',
  documentDescription:
    'Sistema de Pronóstico y Alerta Temprana para Izaje en mineras de altura: Quebrada Blanca, Collahuasi, Escondida, Los Bronces, Andina, El Teniente y más.',
  center: { lat: -24.25, lon: -69.05 },
  spatiDefaultSitio: 'escondida',
  api: {
    defaultPublicBase: 'https://metgo-api.onrender.com/api',
    localBase: 'http://127.0.0.1:8080/api',
  },
  theme: {
    primary: '#3b82f6',
    primaryHover: '#2563eb',
    accent: '#14b8a6',
    accentLight: '#5eead4',
  },
  modules: {
    meteo: true,
    precipitacion: false,
    lugares: false,
    aire: false,
    operaciones: true,
    spati: true,
  },
  storagePrefix: 'metgo_spati',
  copy: {
    headerTitle: 'SPATI · Alta montaña',
  },
  /** Seed UI; la lista canónica viene de GET /public/spati/sitios?alta_montana=1 */
  stations: [
    { slug: 'quebrada_blanca', nombre: 'Quebrada Blanca', region: 'Tarapacá', lat: -21.0, lon: -68.816667, altitud_msnm: 4400, z0: 0.25 },
    { slug: 'collahuasi', nombre: 'Collahuasi', region: 'Tarapacá', lat: -20.964167, lon: -68.661111, altitud_msnm: 4200, z0: 0.20 },
    { slug: 'cerro_colorado', nombre: 'Cerro Colorado', region: 'Tarapacá', lat: -20.059444, lon: -69.27, altitud_msnm: 2600, z0: 0.10 },
    { slug: 'el_abra', nombre: 'El Abra', region: 'Antofagasta', lat: -21.920556, lon: -68.832222, altitud_msnm: 4005, z0: 0.22 },
    { slug: 'chuquicamata', nombre: 'Chuquicamata', region: 'Antofagasta', lat: -22.290556, lon: -68.901944, altitud_msnm: 2860, z0: 0.35 },
    { slug: 'radomiro_tomic', nombre: 'Radomiro Tomic', region: 'Antofagasta', lat: -22.216667, lon: -68.9, altitud_msnm: 2950, z0: 0.15 },
    { slug: 'ministro_hales', nombre: 'Ministro Hales', region: 'Antofagasta', lat: -22.381667, lon: -68.912222, altitud_msnm: 2600, z0: 0.20 },
    { slug: 'spence', nombre: 'Spence', region: 'Antofagasta', lat: -22.795556, lon: -69.253333, altitud_msnm: 1725, z0: 0.05 },
    { slug: 'escondida', nombre: 'Escondida', region: 'Antofagasta', lat: -24.251667, lon: -69.054167, altitud_msnm: 3075, z0: 0.25 },
    { slug: 'el_penon', nombre: 'El Peñón', region: 'Antofagasta', lat: -24.410833, lon: -69.496111, altitud_msnm: 2200, z0: 0.15 },
    { slug: 'la_coipa', nombre: 'La Coipa', region: 'Atacama', lat: -26.699722, lon: -69.5, altitud_msnm: 4000, z0: 0.18 },
    { slug: 'maricunga', nombre: 'Maricunga', region: 'Atacama', lat: -27.533333, lon: -69.3, altitud_msnm: 4300, z0: 0.05 },
    { slug: 'candelaria', nombre: 'Candelaria', region: 'Atacama', lat: -27.509722, lon: -70.2875, altitud_msnm: 729, z0: 0.05 },
    { slug: 'los_pelambres', nombre: 'Los Pelambres', region: 'Coquimbo', lat: -31.716667, lon: -70.490556, altitud_msnm: 3600, z0: 0.30 },
    { slug: 'los_bronces', nombre: 'Los Bronces', region: 'Metropolitana', lat: -33.150278, lon: -70.287222, altitud_msnm: 3500, z0: 0.35 },
    { slug: 'andina', nombre: 'Andina', region: 'Valparaíso', lat: -33.061389, lon: -70.250278, altitud_msnm: 3950, z0: 0.40 },
    { slug: 'el_teniente', nombre: 'El Teniente', region: "O'Higgins", lat: -34.094167, lon: -70.350833, altitud_msnm: 2300, z0: 0.30 },
  ],
  umbralesSpati: {
    verde_max_kmh: 26,
    amarillo: [26, 29],
    naranja: [30, 34],
    rojo_min_kmh: 35,
    flag_critico_kmh: 36,
  },
}
