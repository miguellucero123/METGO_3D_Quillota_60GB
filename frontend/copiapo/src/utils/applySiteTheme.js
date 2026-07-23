/**
 * Aplica paleta del sitio a CSS variables (referencia E6).
 * En metgo-paine vive en src/utils/applySiteTheme.js
 */
export function applySiteTheme(site) {
  if (typeof document === 'undefined' || !site) return
  const root = document.documentElement
  const t = site.theme || {}
  const map = {
    '--color-primary': t.primary,
    '--color-primary-hover': t.primaryHover,
    '--color-accent': t.accent,
    '--color-accent-light': t.accentLight,
  }
  for (const [key, val] of Object.entries(map)) {
    if (val) root.style.setProperty(key, val)
  }
  if (t.primary) {
    root.style.setProperty('--color-primary-muted', hexToRgba(t.primary, 0.12))
    root.style.setProperty('--color-primary-subtle', hexToRgba(t.primary, 0.06))
    root.style.setProperty('--glow-primary', `0 0 15px ${hexToRgba(t.primary, 0.35)}`)
  }
  if (site.documentTitle) document.title = site.documentTitle
}

function hexToRgba(hex, alpha) {
  const h = String(hex).replace('#', '')
  if (h.length !== 6) return hex
  const r = parseInt(h.slice(0, 2), 16)
  const g = parseInt(h.slice(2, 4), 16)
  const b = parseInt(h.slice(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}
