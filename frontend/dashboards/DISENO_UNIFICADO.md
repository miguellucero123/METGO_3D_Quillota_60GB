# Diseño unificado METGO 3D — Dashboards Streamlit

## Fuente de verdad

| Capa | Archivo |
|------|---------|
| Vue (Netlify) | `frontend/vue/src/assets/main.css` |
| Streamlit | `metgo/streamlit_theme.py` |
| Bootstrap dashboards | `frontend/dashboards/metgo_dashboard_init.py` |

Paleta: verde `#3d6b52` + azul cielo `#5b9bd5` · DM Sans.

## Inicialización estándar

```python
import sys
from pathlib import Path
_DASH = Path(__file__).resolve().parent
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))

from metgo_dashboard_init import page_config_and_theme

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "Título",
    "Subtítulo",
    module="meteo",  # meteo | agricola | ml | global | ...
)
```

## Puertos locales (8502–8513)

| Puerto | Script |
|--------|--------|
| 8502 | `dashboard_meteorologico_metgo.py` |
| 8503 | `dashboard_agricola_inteligente.py` |
| 8504 | `dashboard_monitoreo_tiempo_real.py` |
| 8505 | `dashboard_ia_ml_avanzado.py` |
| 8506 | `dashboard_visualizaciones_avanzadas.py` |
| 8507 | `dashboard_global_metricas.py` |
| 8508 | `dashboard_agricultura_precision.py` |
| 8509 | `dashboard_analisis_comparativo.py` |
| 8510 | `dashboard_alertas_automaticas.py` |
| 8511 | `dashboard_simple_optimizado.py` |
| 8512 | `dashboard_unificado_diferenciado.py` / `dashboard_sistema_unificado.py` |
| 8513 | `dashboard_metgo_3d.py` |

Hub navegación: `dashboard_sistema_unificado.py`

## HTML estático

Movido a `legacy_static/`. **No abrir en producción.**

Reemplazos dinámicos: `dashboard_metgo_3d.py`, `dashboard_global_html.py`, `dashboard_html_completo.py`, `dashboard_sistema_unificado.py`.

## Ilustraciones meteo (Streamlit)

```python
from metgo.streamlit_theme import weather_scene_html, classify_weather_from_row, frost_badge_html

st.markdown(weather_scene_html("lluvioso"), unsafe_allow_html=True)
st.markdown(frost_badge_html("Riesgo helada"), unsafe_allow_html=True)
```

Fase: **2.x** · **DT-x** UI
