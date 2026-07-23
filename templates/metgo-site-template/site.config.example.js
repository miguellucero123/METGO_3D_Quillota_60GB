/**
 * Ejemplo E6 — sitio plantilla ficticio "demo".
 * Copiar a src/site.config.js al crear un SPA desde metgo-paine.
 */
export default {
  sitio: 'demo',
  productName: 'METGO',
  siteLabel: 'Demo',
  tagline: 'Valle Demo · plantilla multi-sitio',
  region: 'Valle Demo (ficticio)',
  versionLabel: 'v0.1 · METGO Template',
  documentTitle: 'METGO Demo — plantilla multi-sitio',
  documentDescription: 'Sitio de prueba generado desde metgo-site-template (E6).',
  center: { lat: -33.32, lon: -71.42 },
  api: {
    defaultPublicBase: 'https://metgo-api.onrender.com/api',
    localBase: 'http://127.0.0.1:8080/api',
  },
  theme: {
    primary: '#a78bfa',
    primaryHover: '#8b5cf6',
    accent: '#c4b5fd',
    accentLight: '#ddd6fe',
  },
  modules: {
    meteo: true,
    precipitacion: true,
    lugares: true,
    aire: false,
    operaciones: false,
  },
  storagePrefix: 'metgo_demo',
  copy: {
    headerTitle: 'Sistema de monitoreo',
  },
  stations: [
    {
      id: 1,
      slug: 'demo_norte',
      nombre: 'Demo Norte',
      lat: -33.3,
      lon: -71.4,
      circuito: 'A',
      altitud: 200,
      descripcion: 'Punto norte del valle demo',
      dificultad: 'Baja',
      icono: 'MapPin',
    },
    {
      id: 2,
      slug: 'demo_sur',
      nombre: 'Demo Sur',
      lat: -33.34,
      lon: -71.44,
      circuito: 'B',
      altitud: 180,
      descripcion: 'Punto sur del valle demo',
      dificultad: 'Baja',
      icono: 'MapPin',
    },
  ],
}
