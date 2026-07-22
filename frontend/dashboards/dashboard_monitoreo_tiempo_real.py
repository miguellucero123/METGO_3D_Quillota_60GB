import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
import time
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import metgo_paths

metgo_paths.setup_paths("05_api_rest", "07_monitoreo")

from api_rest.services import comparativo_estaciones, generar_alertas as alertas_meteo_api
from metgo.streamlit_theme import bootstrap_dashboard, PLOTLY_CONFIG, plotly_layout
from meteo_dashboard_utils import hoy_chile

# Configuración de la página
st.set_page_config(
    page_title="Monitoreo en Tiempo Real - METGO",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

bootstrap_dashboard(
    "Monitoreo en Tiempo Real",
    "Supervisión continua de sensores y alertas",
    module="monitoreo",
)

# Sidebar para controles
st.sidebar.markdown("### 🎛️ Panel de Control")

# Configuración de sensores
sensores_config = {
    "Sensores Meteorológicos": {
        "Temperatura": {"unidad": "°C", "rango": (-5, 40), "critico": (35, 40)},
        "Humedad": {"unidad": "%", "rango": (0, 100), "critico": (90, 100)},
        "Presión": {"unidad": "hPa", "rango": (950, 1050), "critico": (950, 970)},
        "Viento": {"unidad": "km/h", "rango": (0, 100), "critico": (60, 100)},
        "Precipitación": {"unidad": "mm/h", "rango": (0, 50), "critico": (30, 50)},
        "Radiación": {"unidad": "W/m²", "rango": (0, 1200), "critico": (1000, 1200)}
    },
    "Sensores Agrícolas": {
        "Humedad del Suelo": {"unidad": "%", "rango": (0, 100), "critico": (90, 100)},
        "Temperatura del Suelo": {"unidad": "°C", "rango": (-10, 50), "critico": (40, 50)},
        "pH del Suelo": {"unidad": "pH", "rango": (3, 10), "critico": (8, 10)},
        "Conductividad": {"unidad": "mS/cm", "rango": (0, 10), "critico": (8, 10)},
        "Nivel de Agua": {"unidad": "cm", "rango": (0, 200), "critico": (180, 200)}
    },
    "Sensores IoT": {
        "Calidad del Aire": {"unidad": "AQI", "rango": (0, 500), "critico": (300, 500)},
        "Ruido": {"unidad": "dB", "rango": (0, 120), "critico": (100, 120)},
        "Movimiento": {"unidad": "Detectado", "rango": (0, 1), "critico": (1, 1)},
        "Puerta": {"unidad": "Abierta", "rango": (0, 1), "critico": (1, 1)}
    }
}

categoria_sensor = st.sidebar.selectbox("📡 Categoría de Sensores:", list(sensores_config.keys()))
modo_datos = st.sidebar.radio(
    "Fuente",
    ["Estaciones METGO (API)"],
    index=0,
    help="API usa resumen OpenMeteo del valle; simulación para demo IoT.",
)
actualizacion_automatica = st.sidebar.checkbox("🔄 Actualización Automática", value=True)
intervalo_actualizacion = st.sidebar.slider("⏱️ Intervalo (segundos):", 1, 60, 5)

if modo_datos.startswith("Estaciones"):
    try:
        resumen = comparativo_estaciones()
        alertas_api = alertas_meteo_api()
        st.success(f"🌐 **{hoy_chile()}** · {len(resumen)} estaciones · {len(alertas_api)} alertas activas")
        if resumen:
            st.dataframe(
                pd.DataFrame(resumen)[
                    ["estacion", "temperatura", "temperatura_max", "temperatura_min", "viento", "precipitacion"]
                ],
                use_container_width=True,
                hide_index=True,
            )
        if alertas_api:
            for a in alertas_api[:8]:
                nivel = a.get("nivel", "info")
                st.warning(f"**{nivel}** · {a.get('mensaje', '')}")
        st.caption("Monitoreo operativo en Vue: http://127.0.0.1:5173/monitoreo")
    except Exception as e:
        st.error(f"No se pudo conectar a la API METGO (:8080): {e}")
    st.stop()

st.caption(
    f"Sistema METGO — Monitoreo · datos reales API · "
)
