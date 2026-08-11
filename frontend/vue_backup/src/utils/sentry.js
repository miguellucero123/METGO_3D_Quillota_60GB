/**
 * Sentry opcional (E10).
 * Sin VITE_SENTRY_DSN: no-op.
 * Con DSN: requiere `npm i @sentry/vue` (no es dependencia dura del build).
 * La carga usa Function para que Vite/Rollup no resuelva el módulo en build.
 */
export async function initSentry(app, router, siteLabel = 'metgo') {
  const dsn = import.meta.env.VITE_SENTRY_DSN
  if (!dsn) return false
  try {
    // Evita resolución estática de Rollup cuando el paquete no está instalado
    const loader = new Function('m', 'return import(m)')
    const Sentry = await loader('@sentry/vue')
    Sentry.init({
      app,
      dsn,
      integrations: [Sentry.browserTracingIntegration({ router })],
      tracesSampleRate: 0.05,
      environment: import.meta.env.MODE,
      tags: { sitio: siteLabel },
    })
    return true
  } catch (e) {
    console.warn(
      '[sentry] DSN definido pero @sentry/vue no disponible. Ejecute: npm i @sentry/vue',
      e
    )
    return false
  }
}
