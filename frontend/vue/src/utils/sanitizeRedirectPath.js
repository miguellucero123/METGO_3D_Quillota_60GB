/**
 * Limita redirect post-login a rutas internas de la SPA (Portafolio 7 — seguridad).
 * @param {unknown} raw
 * @param {string} [fallback='/']
 */
export function sanitizeRedirectPath(raw, fallback = '/') {
  if (typeof raw !== 'string' || !raw.startsWith('/') || raw.startsWith('//')) {
    return fallback
  }
  if (raw.includes('://') || raw.includes('\\')) {
    return fallback
  }
  return raw.split('?')[0] || fallback
}
