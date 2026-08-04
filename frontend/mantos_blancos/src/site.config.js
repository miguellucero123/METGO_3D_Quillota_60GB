/**
 * METGO Mantos Blancos (E8) — operaciones de faena minera.
 * Único archivo de identidad / módulos / puntos seed.
 */
export default {
  sitio: 'mantos_blancos',
  productName: 'METGO',
  siteLabel: 'Mantos Blancos',
  tagline: 'Atmósfera · ventilación faena · operaciones · Antofagasta',
  region: 'Antofagasta · faena minera',
  versionLabel: 'v0.2 · METGO Faena + Atmósfera',
  documentTitle: 'METGO Mantos Blancos — Faena y atmósfera',
  documentDescription:
    'Ventanas operacionales, ventilación N/R/M, ICAP, dispersión y modelación airshed en faena Mantos Blancos.',
  center: { lat: -23.43, lon: -70.06 },
  faena: {
    id: 'mantos_blancos',
    nombre: 'Mantos Blancos',
    estacionAncla: 'mb_rajo',
  },
  bounds: { west: -70.35, south: -23.55, east: -69.95, north: -23.30 },
  api: {
    defaultPublicBase: 'https://metgo-api.onrender.com/api',
    /** Solo si corre Flask local; el SPA usa Render salvo VITE_METGO_API. */
    localBase: 'http://127.0.0.1:8080/api',
  },
  theme: {
    primary: '#fb923c',
    primaryHover: '#f97316',
    accent: '#fdba74',
    accentLight: '#fed7aa',
  },
  modules: {
    meteo: true,
    precipitacion: false,
    lugares: false,
    aire: true,
    operaciones: true,
  },
  storagePrefix: 'metgo_mantos',
  copy: {
  headerTitle: 'Faena y atmósfera',
},
  stations: [
    {
      id: 1,
      slug: 'mb_rajo',
      nombre: 'Rajo',
      lat: -23.43,
      lon: -70.06,
      actividad: 'tronadura',
      descripcion: 'Rajo abierto — tronadura e izaje',
    },
    {
      id: 2,
      slug: 'mb_campamento',
      nombre: 'Campamento',
      lat: -23.42,
      lon: -70.05,
      actividad: 'transporte',
      descripcion: 'Campamento / logística',
    },
    {
      id: 3,
      slug: 'mb_chancado',
      nombre: 'Chancado',
      lat: -23.44,
      lon: -70.07,
      actividad: 'transporte',
      descripcion: 'Chancado — polvo en suspensión',
    },
    {
      id: 4,
      slug: 'mb_ruta_acceso',
      nombre: 'Ruta de acceso',
      lat: -23.5,
      lon: -70.2,
      actividad: 'transporte',
      descripcion: 'Ruta de acceso a Antofagasta',
    },
  ],
  /**
   * Espejo documentativo de umbrales (la fuente de verdad operativa es la API).
   * Override en producción: METGO_OP_UMBRALES_JSON en Render.
   */
  umbrales: {
    izaje: { racha: [11, 17], viento_sostenido: [10, 14] },
    tronadura: {
      viento_sostenido: [10, 14],
      racha: [12, 16],
      visibilidad: [5, 2],
      viento_min_dispersion: 1.5,
    },
    transporte: { visibilidad: [5, 1], precipitacion: [2, 8], racha: [16, 22] },
    exposicion_uv: { uv_index: [6, 10] },
    so2: { so2: [50, 125] },
  },
}
