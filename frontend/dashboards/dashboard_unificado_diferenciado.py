import streamlit as st
from metgo.streamlit_theme import bootstrap_dashboard, PLOTLY_CONFIG, plotly_layout

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

from api_rest.services import (
    comparativo_estaciones,
    generar_alertas,
    historico_meteo,
    metricas_globales,
    nombre_a_slug,
    resumen_meteo,
)
from meteo_dashboard_utils import filtrar_historico_hasta_hoy, hoy_chile

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "Dashboard Unificado",
    "Hub diferenciado · acceso a módulos METGO",
    module="unificado",
    page_icon="🏠",
    initial_sidebar_state="collapsed",
)

# CSS complementario
st.markdown("""
<style>
    /* Diseño unificado */
    .unificado-header {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .unificado-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        overflow: hidden;
        transition: transform 0.3s ease;
    }
    
    .unificado-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #00b894, #00a085, #74b9ff, #0984e3);
    }
    
    .unificado-card:hover {
        transform: translateY(-3px);
    }
    
    .metric-unificado-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 0.5rem 0;
        text-align: center;
        border-left: 4px solid #00b894;
    }
    
    .metric-unificado-number {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-unificado-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin: 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .chart-unificado-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
    }
    
    .section-title-unificado {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #00b894;
        display: inline-block;
    }
    
    .integration-card {
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .unificado-header {
            padding: 1.5rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .unificado-card {
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .metric-unificado-card {
            padding: 1rem;
        }
        
        .chart-unificado-container {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="unificado-header">
    <h1>🏠 Dashboard Unificado</h1>
    <h3>Sistema METGO - Vista Integral</h3>
    <p>Integración completa de meteorología, agricultura y monitoreo en una sola vista</p>
    <div style="margin-top: 1rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 20px; display: inline-block;">
        🔄 Vista Integral - Todos los Sistemas Integrados
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Panel de Control Unificado")
    
    # Selector de vista
    vista_unificada = st.selectbox(
        "👁️ Vista:",
        ["Vista Completa", "Solo Meteorología", "Solo Agricultura", "Solo Monitoreo", "Vista Ejecutiva"],
        key="vista_unificada"
    )
    
    # Selector de estación
    estacion_unificada = st.selectbox(
        "🌍 Estación:",
        ["Quillota", "Los Nogales", "Hijuelas", "Limache", "Olmue", "Todas las Estaciones"],
        key="estacion_unificada"
    )
    
    # Selector de período
    periodo_unificada = st.selectbox(
        "📅 Período:",
        ["Tiempo Real", "Últimas 24 horas", "Últimos 7 días", "Últimos 30 días", "Últimos 3 meses"],
        key="periodo_unificada"
    )

    modo_unificado = st.radio(
        "Fuente",
        ["API METGO (valle)"],
        index=0,
    )

if modo_unificado.startswith("API"):
    st.success(f"**Hub METGO · API** · {hoy_chile()} · Vue http://127.0.0.1:5173")

    if estacion_unificada == "Todas las Estaciones":
        with st.spinner("Cargando valle…"):
            valle = comparativo_estaciones()
            mg = metricas_globales()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Estaciones", mg.get("estaciones_activas", len(valle)))
        c2.metric("T° máx media", mg.get("temperatura_media_max"))
        c3.metric("T° mín media", mg.get("temperatura_media_min"))
        c4.metric("Alertas", mg.get("alertas_activas", 0))
        if valle:
            df_v = pd.DataFrame(valle)
            st.dataframe(
                df_v[
                    [
                        c
                        for c in [
                            "estacion",
                            "temperatura",
                            "temperatura_max",
                            "temperatura_min",
                            "humedad",
                            "precipitacion",
                        ]
                        if c in df_v.columns
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
    else:
        slug_u = nombre_a_slug(estacion_unificada)
        with st.spinner(f"Cargando {estacion_unificada}…"):
            res_u = resumen_meteo(slug_u) or {}
            hist_u = filtrar_historico_hasta_hoy(historico_meteo(slug_u, 14) or [])
            alertas_u = generar_alertas(slug_u)
        st.caption(f"Tipo dato: **{res_u.get('tipo_dato', '—')}** · {res_u.get('fuente', 'METGO')}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("T°", f"{res_u.get('temperatura', 0):.1f}°C")
        c2.metric("Humedad", f"{res_u.get('humedad', 0):.0f}%")
        c3.metric("Lluvia", f"{res_u.get('precipitacion', 0):.1f} mm")
        c4.metric("Alertas", len(alertas_u))
        if hist_u:
            df_h = pd.DataFrame(hist_u)
            fig_u = go.Figure()
            fig_u.add_trace(
                go.Scatter(
                    x=df_h["fecha"],
                    y=df_h["temperatura_max"],
                    name="T° máx",
                    mode="lines+markers",
                )
            )
            fig_u.add_trace(
                go.Scatter(
                    x=df_h["fecha"],
                    y=df_h["temperatura_min"],
                    name="T° mín",
                    mode="lines+markers",
                )
            )
            fig_u.update_layout(height=360, title=f"Histórico 14 d · {estacion_unificada}")
            st.plotly_chart(fig_u, use_container_width=True, config=PLOTLY_CONFIG)
        for a in alertas_u[:5]:
            st.warning(f"**{a.get('nivel', 'info')}**: {a.get('mensaje', '')}")

    st.info("Módulos: /meteo · /agricola · /monitoreo · /ml en Vue (5173)")
    st.stop()
