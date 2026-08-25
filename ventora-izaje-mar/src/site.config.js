/**
 * METGO VENTORA — Pronóstico de izaje en mineras de alta montaña (Chile).
 * Código interno / API: sitio=spati (sin cambiar contratos).
 */
export default {
  sitio: 'spati',
  productName: 'METGO',
  /** Marca comercial visible (antes SPATI) */
  brandName: 'VENTORA',
  siteLabel: 'VENTORA · Izaje',
  tagline: 'Pronóstico 72 h · puertos y terminales marítimos · alertas 0–3',
  region: 'Chile · Terminales marítimos',
  versionLabel: 'v0.5.0 · VENTORA Izaje Mar',
  documentTitle: 'VENTORA Izaje Mar',
  documentDescription:
    'VENTORA: inteligencia de viento y oleaje para izaje en puertos. Acceso por terminal contratado.',
  center: { lat: -20.21, lon: -70.15 },
  spatiDefaultSitio: 'puerto_iquique',
  api: {
    defaultPublicBase: 'https://metgo-api.onrender.com/api',
    localBase: 'http://127.0.0.1:8080/api',
  },
  theme: {
    primary: '#10b981',
    primaryHover: '#059669',
    accent: '#34d399',
    accentLight: '#6ee7b7',
  },
  modules: {
    meteo: true,
    precipitacion: false,
    lugares: false,
    aire: false,
    operaciones: true,
    spati: true,
  },
  storagePrefix: 'ventora_mar',
  copy: {
    headerTitle: 'VENTORA · Izaje Mar',
  },
  /** Seed UI; la lista canónica viene de GET /public/spati/sitios?alta_montana=1 */
  stations: [
    { slug: 'puerto_iquique', nombre: 'Puerto de Iquique', region: 'Tarapacá', lat: -20.208, lon: -70.157, altitud_msnm: 5, z0: 0.05 },
  ],
  umbralesSpati: {
    verde_max_kmh: 26,
    amarillo: [26, 29],
    naranja: [30, 34],
    rojo_min_kmh: 35,
    flag_critico_kmh: 36,
  },
}
