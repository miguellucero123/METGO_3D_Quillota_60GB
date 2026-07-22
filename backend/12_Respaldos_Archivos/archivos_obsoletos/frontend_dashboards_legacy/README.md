# Dashboards Streamlit legacy (fuera del catálogo 8501–8513)

Movidos desde `frontend/dashboards/` (2026-07-21).

## Activos (no mover)

Puertos del catálogo (`MODULOS_SISTEMA` en `catalog.py`) + utils:

- 8502–8513: `dashboard_*.py` listados en el catálogo
- `metgo_dashboard_init.py`, `meteo_dashboard_utils.py`, `agricola_dashboard_utils.py`, `ml_dashboard_utils.py`

## Contenido de esta carpeta

- Variantes `*_metgo.py` / HTML / unificados antiguos
- Launchers, auditores y correctores Plotly one-shot
- Auth/login demos no cableados al catálogo Vue

No lanzar desde el launcher METGO ni referenciar en Netlify.
