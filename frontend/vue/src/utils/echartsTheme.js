/** Tema ECharts METGO — colores desde tokens CSS (site-aware). */

function cssVar(name, fallback) {
  if (typeof document === 'undefined') return fallback
  try {
    const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
    return v || fallback
  } catch {
    return fallback
  }
}

function hexToRgba(hex, alpha) {
  const h = (hex || '').replace('#', '')
  if (h.length !== 6) return `rgba(0, 255, 170, ${alpha})`
  const r = parseInt(h.slice(0, 2), 16)
  const g = parseInt(h.slice(2, 4), 16)
  const b = parseInt(h.slice(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

/** Snapshot de tokens (llamar desde computed de charts para reactividad al tema). */
export function resolveChartColors() {
  const primary = cssVar('--color-primary', '#00ffaa')
  const accent = cssVar('--color-accent', '#0ea5e9')
  const accentLight = cssVar('--color-accent-light', '#38bdf8')
  return {
    verde: primary,
    primary,
    celeste: accentLight,
    azul: accent,
    ambar: cssVar('--color-warning', '#f59e0b'),
    rojo: cssVar('--color-danger', '#ef4444'),
    eje: cssVar('--color-border', '#374151'),
    texto: cssVar('--color-text-secondary', '#9ca3af'),
    grilla: cssVar('--color-surface-elevated', '#1f2937'),
    primaryRgba: (a) => hexToRgba(primary, a),
  }
}

/** Compat: objeto estático con defaults Quillota (se actualiza al llamar refreshChartColors). */
export const CHART_COLORS = resolveChartColors()

export function refreshChartColors() {
  Object.assign(CHART_COLORS, resolveChartColors())
  return CHART_COLORS
}

export function tooltipOscuro(formatter) {
  const c = resolveChartColors()
  return {
    trigger: 'axis',
    axisPointer: { type: 'cross', animation: false },
    backgroundColor: 'rgba(17, 24, 39, 0.9)',
    borderColor: c.primaryRgba(0.3),
    textStyle: { color: '#f3f4f6' },
    ...(formatter ? { formatter } : {}),
  }
}

export function leyendaSuperior(items) {
  const c = resolveChartColors()
  return {
    data: items,
    textStyle: { color: c.texto },
    top: 0,
    selectedMode: true,
  }
}

export function zoomSlider() {
  const c = resolveChartColors()
  return [
    { type: 'inside', xAxisIndex: 0, filterMode: 'filter' },
    {
      type: 'slider',
      xAxisIndex: 0,
      height: 25,
      bottom: 5,
      borderColor: c.primaryRgba(0.2),
      textStyle: { color: c.texto },
    },
  ]
}

export function grillaBase() {
  return { top: '15%', left: '3%', right: '4%', bottom: '15%', containLabel: true }
}

export function ejeCategoria(labels) {
  const c = resolveChartColors()
  return {
    type: 'category',
    data: labels,
    axisLine: { lineStyle: { color: c.eje } },
    axisLabel: { color: c.texto },
  }
}

export function ejeValor(name, color, extra = {}) {
  const c = resolveChartColors()
  return {
    type: 'value',
    name,
    axisLine: { show: true, lineStyle: { color: color || c.primary } },
    splitLine: { lineStyle: { color: c.grilla, type: 'dashed' } },
    axisLabel: { color: c.texto },
    ...extra,
  }
}

export function serieBarrasAzules(name, data, extra = {}) {
  const c = resolveChartColors()
  return {
    name,
    type: 'bar',
    data,
    itemStyle: {
      color: {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [
          { offset: 0, color: c.celeste },
          { offset: 1, color: c.azul },
        ],
      },
      borderRadius: [4, 4, 0, 0],
    },
    barMaxWidth: 30,
    ...extra,
  }
}

export function serieLineaVerde(name, data, extra = {}) {
  const c = resolveChartColors()
  return {
    name,
    type: 'line',
    data,
    smooth: true,
    symbol: 'circle',
    symbolSize: 6,
    itemStyle: { color: c.primary },
    lineStyle: { width: 3, shadowColor: c.primaryRgba(0.5), shadowBlur: 10 },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [
          { offset: 0, color: c.primaryRgba(0.25) },
          { offset: 1, color: c.primaryRgba(0) },
        ],
      },
    },
    ...extra,
  }
}
