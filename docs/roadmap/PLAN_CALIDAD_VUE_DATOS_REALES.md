# Plan de trabajo — Calidad Vue en todos los módulos + solo datos reales

> Actualizado: 2026-07-22 · Etapas A–F en código; E operativo verificado (Supabase + sync corto).
> Ver: `CHECKLIST_ETAPA_E_SUPABASE_ARCHIVE.md` · `CHECKLIST_ETAPA_F_PUERTOS.md`

## Principios

1. Referencia visual: SPA Vue Netlify.
2. Gráficos: ECharts (Vue) / Plotly + `plotly_layout` (Streamlit).
3. Cero datos sintéticos.
4. Históricos: OpenMeteo Archive → store; Agromet/DMC después.

## Estado por etapa

### A — Errores producción + precip Vue ECharts — HECHA
### B — SVG → ECharts (tema Ensemble) — HECHA

### C — Paridad visual Streamlit / Vue — HECHA
- [x] Emojis + `plotly_layout` + 8513 solo API
- [x] BOM UTF-8 eliminado en dashboards; test CI anti-BOM
- [x] Smoke estático F: `scratch/smoke_etapa_f_puertos.py` → 12/12 OK

### D — Sin sintéticos — HECHA
- [x] Proxies 8503/8506 eliminados + `pytest tests/test_ui_theme.py` (5 tests)

### E — Históricos oficiales — OPERATIVO AVANZADO
- [x] SQL tablas OK (permisos): `meteo_registros` / `meteo_pronostico` / `meteo_series`
- [x] Sync corto: histórico 7d + pronóstico 7d en Supabase
- [x] **Archive 1 año** (2026-07-22): 366 días × 5 estaciones = **1830** filas `openmeteo_archive`
- [x] Stub Agromet/DMC + exposición en `fuentes_datos()` (`oficiales_chile`)
- [x] Cron ETL operativo (cron-job.org + wake; ver `OPS_CRON_ETL.md`)
- [x] SQL `ml_registry` en repo (`supabase_db/ml_registry.sql` + migración); tabla creada en Supabase
- [x] `ml_registry` poblada (1 fila, 43/43 servibles) — verificado 2026-07-22
- [x] **Archive 5 años** (2026-07-22 local): 1827 días × 5 estaciones = **9135** registros; `errores: []`
- [x] Lectura históricos largos: paginación Supabase (>1000) + Vue ventanas 90/365/5 años
- [x] Export CSV/JSON en `/meteo/historico` + test `test_historico_fechas.py`
- [x] Badge `tipo_dato` observado/pronóstico (`TipoDatoBadge`) en Panel y Meteorología
- [x] Pronóstico Vue: tabla + gráfico con `seriePronosticoPorDia` (misma serie)
- [x] Mapa valle: coords desde store/API + `DEFAULT_COORDS` alineados
- [x] §5.5 agrícola: timeline ops + económico Vue/8503 + export reporte 02 JSON
- [ ] Códigos Agromet/DMC reales *(diferido: requiere registro oficial; stub en `fuentes_oficiales_chile.py`)*

### F — Limpieza + verificación — HECHA (automático) / smoke visual opcional
- [x] Legacy + backups + notebooks movidos
- [x] Smoke estático 8502–8513 OK
- [ ] Smoke visual Streamlit (opcional, checklist F)
- [ ] Commit/push cuando el usuario lo pida

## Verificación
```bash
pytest tests/test_ui_theme.py -q
python scratch/smoke_etapa_f_puertos.py
python scratch/verificar_supabase_tablas.py
```
