# Plan de trabajo — Calidad Vue en todos los módulos + solo datos reales

> Actualizado: 2026-07-21 · Etapas B/C/D/F avanzadas; E pendiente operativo usuario.
> Ver también `docs/PROMPT_UNIFICACION_FORMATO_UI.md` y `docs/roadmap/CHECKLIST_ETAPA_E_SUPABASE_ARCHIVE.md`.

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

### C — Sin emojis Streamlit — HECHA (catálogo)
- [x] 292 líneas limpiadas en 11/12 dashboards activos (8505 ya sin emoji)
- [x] Guardarraíl: `tests/test_ui_theme.py::test_dashboards_activos_sin_emojis`
- Script seguro: `scratch/strip_emojis_catalog_safe.py` (no colapsar whitespace global)

### D — Sin sintéticos catálogo 8501–8513 — HECHA

### E — Archive histórico — CÓDIGO + CRON LISTOS
- [x] ETL Archive + sync `incluir_archive`
- [x] `historico_meteo(dias>92)` lee **solo store**
- [x] `/api/cron/sync?incluir_archive=true` + OpenAPI
- [x] Cron GitHub: 00/12 ligero; domingo 03 UTC + `workflow_dispatch` con Archive
- [ ] Operativo: ejecutar SQL Supabase (ver checklist Etapa E)
- [ ] Agromet/DMC

### F — Limpieza — HECHA (código)
- [x] Legacy `*_metgo` + launchers/auditores → `archivos_obsoletos/frontend_dashboards_legacy/`
- [ ] Commit/push cuando el usuario lo pida

## Verificación última pasada
- `python -m py_compile` dashboards catálogo OK
- `pytest tests/test_ui_theme.py` OK (sintéticos + plotly_white + emojis)
- `npm run build` (Vue) OK (sesión previa)
