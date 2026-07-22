/**
 * Composable del tema ECharts METGO (estilo Ensemble).
 * Reexporta helpers de echartsTheme.js para uso en componentes.
 */
export {
  CHART_COLORS,
  tooltipOscuro,
  leyendaSuperior,
  zoomSlider,
  grillaBase,
  ejeCategoria,
  ejeValor,
  serieBarrasAzules,
  serieLineaVerde,
} from '@/utils/echartsTheme'

export function useEchartsTheme() {
  return {
    backgroundColor: 'transparent',
    textStyle: { color: '#9ca3af', fontFamily: 'DM Sans, sans-serif' },
  }
}
