# Checklist Etapa F — verificación puerto a puerto (Streamlit local)

> Tras `streamlit run` vía launcher METGO. UI de referencia: https://metgo3d.netlify.app

| Puerto | Script | Tema oscuro | Sin emoji | Sin sintéticos | plotly_layout | Notas |
|--------|--------|:-----------:|:---------:|:--------------:|:-------------:|-------|
| 8501 | `streamlit_app.py` | ☐ | ☐ | ☐ | ☐ | Portal; no mover sin actualizar Streamlit Cloud |
| 8502 | `dashboard_meteorologico_profesional.py` | ✅* | ✅* | ✅* | ✅* | *smoke estático 2026-07-22 |
| 8503 | `dashboard_agricola_inteligente.py` | ✅* | ✅* | ✅* | ✅* | Heurística plagas etiquetada |
| 8504 | `dashboard_monitoreo_tiempo_real.py` | ✅* | ✅* | ✅* | ✅* | |
| 8505 | `dashboard_ia_ml_avanzado.py` | ✅* | ✅* | ✅* | ✅* | |
| 8506 | `dashboard_visualizaciones_avanzadas.py` | ✅* | ✅* | ✅* | ✅* | Solo meteo real |
| 8507 | `dashboard_global_metricas.py` | ✅* | ✅* | ✅* | ✅* | |
| 8508 | `dashboard_agricultura_precision.py` | ✅* | ✅* | ✅* | ✅* | |
| 8509 | `dashboard_analisis_comparativo.py` | ✅* | ✅* | ✅* | ✅* | |
| 8510 | `dashboard_alertas_automaticas.py` | ✅* | ✅* | ✅* | ✅* | |
| 8511 | `dashboard_simple_optimizado.py` | ✅* | ✅* | ✅* | ✅* | |
| 8512 | `dashboard_unificado_diferenciado.py` | ✅* | ✅* | ✅* | ✅* | |
| 8513 | `dashboard_mobile_optimizado.py` | ✅* | ✅* | ✅* | ✅* | Solo API |

\* = `scratch/smoke_etapa_f_puertos.py` + `pytest tests/test_ui_theme.py` (no sustituye abrir Streamlit en navegador).

## Automatizado (CI local)

```bash
pytest tests/test_ui_theme.py -q
```

Legacy: `backend/12_Respaldos_Archivos/archivos_obsoletos/frontend_dashboards_legacy/`
