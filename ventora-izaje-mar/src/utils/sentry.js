/**
 * Sentry opcional (E10). Ver frontend/vue/src/utils/sentry.js
 */
export async function initSentry(app, router, siteLabel = 'metgo') {
  const dsn = import.meta.env.VITE_SENTRY_DSN
  if (!dsn) return false
  try {
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
    console.warn('[sentry] npm i @sentry/vue si usa VITE_SENTRY_DSN', e)
    return false
  }
}
