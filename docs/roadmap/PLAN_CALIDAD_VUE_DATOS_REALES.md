# Plan de trabajo — Calidad Vue en todos los módulos + solo datos reales

> Actualizado: 2026-07-21 · Continuación etapas C–F (paridad Plotly, proxies, stubs Agromet, QA puertos).
> Ver: `docs/PROMPT_UNIFICACION_FORMATO_UI.md` · `CHECKLIST_ETAPA_E_SUPABASE_ARCHIVE.md` · `CHECKLIST_ETAPA_F_PUERTOS.md`

## Principios

1. Referencia visual: SPA Vue Netlify.
2. Gráficos: ECharts (Vue) / Plotly + `plotly_layout` (Streamlit).
3. Cero datos sintéticos.
4. Históricos: OpenMeteo Archive → store; Agromet/DMC después.

## Estado por etapa

### A — Errores producción + precip Vue ECharts — HECHA
### B — SVG → ECharts (tema Ensemble) — HECHA

### C — Paridad visual Streamlit / Vue — HECHA (código catálogo)
- [x] Emojis eliminados en 8502–8513 + test CI
- [x] `plotly_layout` en charts que faltaban (8503, 8506, 8508, 8509, 8512)
- [x] 8513: `bootstrap_dashboard` + solo API (sin Demo)
- [x] Test: `test_plotly_charts_usan_plotly_layout`
- [ ] Smoke visual manual puerto a puerto (checklist F)

### D — Sin sintéticos — HECHA (código + CI reforzado)
- [x] 8506: eliminados `Rendimiento`/`Calidad` inventados; copy sin “datos generados”
- [x] 8503: sin cronograma sintético ni ton/ha inventadas; riesgos = heurística clima etiquetada
- [x] Regex CI ampliado (proxies + Demo móvil)
- [x] `pytest tests/test_ui_theme.py` (4 tests)

### E — Históricos oficiales — CÓDIGO LISTO / OPS PENDIENTE
- [x] ETL Archive + cron `incluir_archive` + SQL idempotente `meteo_pronostico.sql`
- [x] Stub Agromet/DMC: `backend/08_Gestion_Datos/scripts/fuentes_oficiales_chile.py`
- [ ] **Operativo:** ejecutar SQL en Supabase + primer sync Archive
- [ ] Registrar códigos Agromet/DMC y cablear ETL real

### F — Limpieza + verificación — HECHA (código) / QA manual pendiente
- [x] Legacy + `.backup` + notebooks → `archivos_obsoletos/frontend_dashboards_legacy/`
- [x] Checklist: `docs/roadmap/CHECKLIST_ETAPA_F_PUERTOS.md`
- [ ] Marcar checkboxes tras smoke local 8502–8513
- [ ] Commit/push cuando el usuario lo pida

## Verificación automática
```bash
pytest tests/test_ui_theme.py -q
python -m py_compile frontend/dashboards/dashboard_*.py
```
