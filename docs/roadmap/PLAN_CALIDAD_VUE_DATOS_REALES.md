# Plan de trabajo — Calidad Vue en todos los módulos + solo datos reales

> Actualizado: 2026-07-21 · Etapa B cerrada en código; F parcial.
> Ver también `docs/PROMPT_UNIFICACION_FORMATO_UI.md`.

## Principios

1. Referencia visual: SPA Vue Netlify.
2. Gráficos: ECharts (Vue) / Plotly + `plotly_layout` (Streamlit).
3. Cero datos sintéticos.
4. Históricos: OpenMeteo Archive → store; Agromet/DMC después.

## Estado por etapa

### A — Errores producción — HECHA
### B — Vue ECharts — HECHA
- [x] TimeSeries / HorizontalBar / WindRose / precipitación / heladas precip
- [x] `ComboMeteoChart.vue` → ECharts
- [x] AnalizadorNubosidad, PredictorNiebla, ComparacionModelos
- [x] PronosticoHeladaAvanzado, SparklineGrid, MlProjectionChart

### C — Sin emojis Streamlit — PARCIAL
- Strip masivo aplazado (corrompía sintaxis). Manual pendiente archivo a archivo.

### D — Sin sintéticos catálogo 8501–8513 — HECHA
- [x] 8502–8507 + 8509 (antes)
- [x] 8508 agricultura_precision, 8510 alertas, 8511 simple, 8512 unificado, 8513 mobile
- [x] `tests/test_ui_theme.py` cubre los 12 dashboards activos del catálogo

### E — Archive histórico — CÓDIGO LISTO + API
- [x] ETL Archive + sync `incluir_archive`
- [x] `historico_meteo(dias>92)` lee **solo store** (sin OpenMeteo en caliente)
- [x] `/api/meteo/{id}/historico` acepta hasta 3650 días (contrato lista intacto)
- [ ] Operativo: SQL Supabase + sync Archive en Render
- [ ] Agromet/DMC

### F — Limpieza — PARCIAL
- [x] 14 dashboards legacy → `backend/12_Respaldos_Archivos/archivos_obsoletos/frontend_dashboards_legacy/`
- [ ] Commit/push cuando el usuario lo pida

## Verificación última pasada
- `npm run build` (Vue) OK (2026-07-21)
- Catálogo 8502–8513 intacto en `frontend/dashboards/`
