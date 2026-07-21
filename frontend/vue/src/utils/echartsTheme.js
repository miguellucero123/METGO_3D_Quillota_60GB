// Tema ECharts METGO — mismo formato que el "Motor Predictivo Multi-Modelo (Ensemble)".
// Usar estos helpers en todo gráfico nuevo para mantener el formato unificado.

export const CHART_COLORS = {
  verde: '#00ffaa',
  celeste: '#38bdf8',
  azul: '#0284c7',
  ambar: '#f59e0b',
  rojo: '#ef4444',
  eje: '#374151',
  texto: '#9ca3af',
  grilla: '#1f2937',
}

export function tooltipOscuro(formatter) {
  return {
    trigger: 'axis',
    axisPointer: { type: 'cross', animation: false },
    backgroundColor: 'rgba(17, 24, 39, 0.9)',
    borderColor: 'rgba(0, 255, 170, 0.3)',
    textStyle: { color: '#f3f4f6' },
    ...(formatter ? { formatter } : {}),
  }
}

export function leyendaSuperior(items) {
  return { data: items, textStyle: { color: CHART_COLORS.texto }, top: 0 }
}

export function zoomSlider() {
  return [
    { type: 'inside', xAxisIndex: 0, filterMode: 'filter' },
    {
      type: 'slider',
      xAxisIndex: 0,
      height: 25,
      bottom: 5,
      borderColor: 'rgba(0, 255, 170, 0.2)',
      textStyle: { color: CHART_COLORS.texto },
    },
  ]
}

export function grillaBase() {
  return { top: '15%', left: '3%', right: '4%', bottom: '15%', containLabel: true }
}

export function ejeCategoria(labels) {
  return {
    type: 'category',
    data: labels,
    axisLine: { lineStyle: { color: CHART_COLORS.eje } },
    axisLabel: { color: CHART_COLORS.texto },
  }
}

export function ejeValor(name, color, extra = {}) {
  return {
    type: 'value',
    name,
    axisLine: { show: true, lineStyle: { color } },
    splitLine: { lineStyle: { color: CHART_COLORS.grilla, type: 'dashed' } },
    axisLabel: { color: CHART_COLORS.texto },
    ...extra,
  }
}

export function serieBarrasAzules(name, data, extra = {}) {
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
          { offset: 0, color: CHART_COLORS.celeste },
          { offset: 1, color: CHART_COLORS.azul },
        ],
      },
      borderRadius: [4, 4, 0, 0],
    },
    barMaxWidth: 30,
    ...extra,
  }
}

export function serieLineaVerde(name, data, extra = {}) {
  return {
    name,
    type: 'line',
    data,
    smooth: true,
    symbol: 'circle',
    symbolSize: 6,
    itemStyle: { color: CHART_COLORS.verde },
    lineStyle: { width: 3, shadowColor: 'rgba(0, 255, 170, 0.5)', shadowBlur: 10 },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(0, 255, 170, 0.25)' },
          { offset: 1, color: 'rgba(0, 255, 170, 0.0)' },
        ],
      },
    },
    ...extra,
  }
}
