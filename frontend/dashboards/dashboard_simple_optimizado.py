import streamlit as st
from metgo.streamlit_theme import bootstrap_dashboard, PLOTLY_CONFIG, plotly_layout

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path

_DASH = Path(__file__).resolve().parent
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))

from metgo_dashboard_init import page_config_and_theme

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import metgo_paths

metgo_paths.setup_paths("05_api_rest")

from api_rest.services import nombre_a_slug, resumen_meteo
from meteo_dashboard_utils import hoy_chile

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "Dashboard Simple",
    "Vista resumida optimizada para móvil",
    module="simple",
    page_icon="M",
    initial_sidebar_state="collapsed",
)

# CSS complementario (cards locales)
st.markdown("""
<style>
    /* Diseño simple y limpio */
    .simple-header {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .simple-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: 1rem 0;
        border-left: 3px solid #74b9ff;
    }
    
    .simple-metric {
        text-align: center;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .simple-number {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
    }
    
    .simple-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    
    .simple-section {
        margin: 2rem 0;
        padding: 1rem 0;
    }
    
    .simple-button {
        background: #74b9ff;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
        cursor: pointer;
        transition: background 0.3s ease;
    }
    
    .simple-button:hover {
        background: #0984e3;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .simple-header {
            padding: 1rem 0.5rem;
        }
        
        .simple-card {
            padding: 1rem;
        }
        
        .simple-number {
            font-size: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="simple-header">
    <h1> Dashboard Simple</h1>
    <h3>Sistema METGO - Vista Simplificada</h3>
    <p>Información esencial y fácil de entender</p>
</div>
""", unsafe_allow_html=True)

# Sidebar simple
with st.sidebar:
    st.markdown("### Opciones")
    
    # Selector de estación
    estacion = st.selectbox(
        "Estación:",
        ["Quillota", "Los Nogales", "Hijuelas", "Limache", "Olmue"],
        key="estacion_simple"
    )
    
    # Selector de período
    periodo = st.selectbox(
        "Período:",
        ["Hoy", "Esta semana", "Este mes", "Últimos 3 meses"],
        key="periodo_simple"
    )
    modo_simple = st.radio(
        "Fuente",
        ["API METGO (OpenMeteo)"],
        index=0,
    )

if modo_simple.startswith("API"):
    slug_s = nombre_a_slug(estacion)
    with st.spinner("Cargando…"):
        res_s = resumen_meteo(slug_s)
    if not res_s:
        st.error("Sin datos. Levante la API en :8080.")
        st.stop()
    st.success(f"**{hoy_chile()}** · {estacion} · {res_s.get('tipo_dato', 'observado')}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("T°", f"{res_s.get('temperatura', 0):.1f}°C")
    c2.metric("Humedad", f"{res_s.get('humedad', 0):.0f}%")
    c3.metric("Lluvia", f"{res_s.get('precipitacion', 0):.1f} mm")
    c4.metric("Viento", f"{res_s.get('viento', 0):.1f} km/h")
    st.caption("Vue: http://127.0.0.1:5173 · Puerto 8511")
    st.stop()
