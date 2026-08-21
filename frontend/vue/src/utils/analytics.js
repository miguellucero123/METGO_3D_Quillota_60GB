/**
 * analytics.js — Módulo central de tracking para METGO3D
 *
 * Abstracción sobre Google Analytics 4 (gtag) y LinkedIn Insight Tag.
 * IDs se configuran vía VITE_GA4_ID y VITE_LINKEDIN_PARTNER_ID en .env
 *
 * Uso:
 *   import { trackEvent, trackPageView } from '@/utils/analytics'
 *   trackEvent('checkout_start', { plan: 'faena', value: 299 })
 */

const GA4_ID = import.meta.env.VITE_GA4_ID || ''
const LI_PARTNER_ID = import.meta.env.VITE_LINKEDIN_PARTNER_ID || ''

let initialized = false

/**
 * Inyecta scripts de GA4 y LinkedIn Insight Tag en el <head>.
 * Llamar una sola vez desde main.js o router.
 */
export function initAnalytics() {
  if (initialized || typeof window === 'undefined') return
  initialized = true

  // — Google Analytics 4 —
  if (GA4_ID) {
    const script = document.createElement('script')
    script.async = true
    script.src = `https://www.googletagmanager.com/gtag/js?id=${GA4_ID}`
    document.head.appendChild(script)

    window.dataLayer = window.dataLayer || []
    window.gtag = function () {
      window.dataLayer.push(arguments)
    }
    window.gtag('js', new Date())
    window.gtag('config', GA4_ID, {
      send_page_view: false, // controlamos manualmente desde el router
    })
  }

  // — LinkedIn Insight Tag —
  if (LI_PARTNER_ID) {
    window._linkedin_data_partner_ids = window._linkedin_data_partner_ids || []
    window._linkedin_data_partner_ids.push(LI_PARTNER_ID)

    const liScript = document.createElement('script')
    liScript.async = true
    liScript.src = 'https://snap.licdn.com/li.lms-analytics/insight.min.js'
    document.head.appendChild(liScript)
  }
}

/**
 * Registrar una vista de página (SPA navigation).
 * @param {string} path — ruta actual, ej: '/planes'
 * @param {string} title — título de la página
 */
export function trackPageView(path, title) {
  if (typeof window === 'undefined') return

  // GA4
  if (window.gtag && GA4_ID) {
    window.gtag('event', 'page_view', {
      page_path: path,
      page_title: title,
    })
  }
}

/**
 * Registrar un evento de conversión o interacción.
 * @param {string} eventName — nombre del evento (snake_case)
 * @param {Object} params — parámetros adicionales
 *
 * Eventos estándar de METGO3D:
 *   - lead_form_submit     → formulario de contacto enviado
 *   - pricing_view         → visitó página de planes
 *   - checkout_start       → inició checkout PayPal/Stripe
 *   - signup_complete      → registro completado
 *   - lead_magnet_submit   → email capturado por lead magnet
 *   - plan_toggle          → cambió toggle anual/mensual
 */
export function trackEvent(eventName, params = {}) {
  if (typeof window === 'undefined') return

  // GA4
  if (window.gtag) {
    window.gtag('event', eventName, params)
  }

  // LinkedIn conversion (solo para eventos de alto valor)
  const liConversionEvents = ['lead_form_submit', 'checkout_start', 'signup_complete']
  if (window.lintrk && liConversionEvents.includes(eventName)) {
    // LinkedIn requiere un conversion_id configurado en Campaign Manager;
    // por ahora registramos como evento genérico.
    window.lintrk('track', { conversion_id: params.li_conversion_id || '' })
  }
}
