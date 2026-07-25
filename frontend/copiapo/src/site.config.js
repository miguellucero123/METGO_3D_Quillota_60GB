/**
 * METGO Copiapó (E7) — calidad del aire urbana.
 * Único archivo de identidad / módulos / estaciones seed.
 */
export default {
  sitio: 'copiapo',
  productName: 'METGO',
  siteLabel: 'Copiapó',
  tagline: 'Aire · ventilación faena Paipote · Atacama',
  region: 'Copiapó / Paipote / Tierra Amarilla',
  versionLabel: 'v0.2 · METGO Aire + Paipote',
  documentTitle: 'METGO Copiapó — Aire y faena Paipote',
  documentDescription:
    'ICAP, ventilación N/R/M para faena Paipote, soundings y calidad del aire en el valle de Copiapó.',
  center: { lat: -27.3668, lon: -70.3323 },
  api: {
    defaultPublicBase: 'https://metgo-api.onrender.com/api',
    localBase: 'http://127.0.0.1:8080/api',
  },
  theme: {
    primary: '#fbbf24',
    primaryHover: '#f59e0b',
    accent: '#fb923c',
    accentLight: '#fcd34d',
  },
  modules: {
    meteo: true,
    precipitacion: false,
    lugares: false,
    aire: true,
    operaciones: true,
  },
  storagePrefix: 'metgo_copiapo',
  copy: {
    headerTitle: 'Aire y operaciones Paipote',
  },
  stations: [
    {
      id: 1,
      slug: 'copiapo_centro',
      nombre: 'Copiapó Centro',
      lat: -27.3668,
      lon: -70.3323,
      descripcion: 'Casco urbano — referencia ciudad',
    },
    {
      id: 2,
      slug: 'paipote',
      nombre: 'Paipote (faena)',
      lat: -27.4064,
      lon: -70.2853,
      descripcion: 'Sector industrial / faena — ancla ventilación',
    },
    {
      id: 3,
      slug: 'tierra_amarilla',
      nombre: 'Tierra Amarilla',
      lat: -27.4667,
      lon: -70.2667,
      descripcion: 'Comuna sur — polvo y minería cercana',
    },
    {
      id: 4,
      slug: 'chamonate',
      nombre: 'Chamonate',
      lat: -27.261,
      lon: -70.447,
      descripcion: 'NO — aeropuerto / valle bajo (entrada de brisa)',
    },
    {
      id: 5,
      slug: 'la_chimba',
      nombre: 'La Chimba',
      lat: -27.33,
      lon: -70.31,
      descripcion: 'Sector norte de Copiapó',
    },
    {
      id: 6,
      slug: 'punta_del_cobre',
      nombre: 'Punta del Cobre',
      lat: -27.44,
      lon: -70.21,
      descripcion: 'SE — zona minera (fuentes fijas)',
    },
    {
      id: 7,
      slug: 'nantoco',
      nombre: 'Nantoco',
      lat: -27.56,
      lon: -70.24,
      descripcion: 'Sur del valle — Tierra Amarilla',
    },
  ],
}
