import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import metgo_paths

metgo_paths.setup_paths("05_api_rest")

from api_rest.services import comparativo_estaciones, comparativo_historico
from metgo.streamlit_theme import bootstrap_dashboard, PLOTLY_CONFIG, plotly_layout
from meteo_dashboard_utils import hoy_chile

# Configuración de la página optimizada para móviles
st.set_page_config(
    page_title="Análisis Comparativo - METGO",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="collapsed",
)

bootstrap_dashboard(
    "Análisis Comparativo",
    "Estaciones y variables del Valle de Aconcagua",
    module="comparativo",
)

# CSS personalizado para diseño móvil profesional
st.markdown("""
<style>
    /* Diseño móvil profesional para análisis comparativo */
    .comparativo-header {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .comparativo-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        overflow: hidden;
    }
    
    .comparativo-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #74b9ff, #0984e3, #6c5ce7, #a29bfe);
    }
    
    .comparativo-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .comparativo-label {
        font-size: 1rem;
        color: #7f8c8d;
        margin: 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .comparativo-change {
        font-size: 0.9rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .comparativo-positive {
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white;
    }
    
    .comparativo-negative {
        background: linear-gradient(135deg, #e17055, #d63031);
        color: white;
    }
    
    .comparativo-neutral {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
    }
    
    .chart-comparativo-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
    }
    
    .section-title-comparativo {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #74b9ff;
        display: inline-block;
    }
    
    .comparison-badge {
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.25rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .comparativo-header {
            padding: 1.5rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .comparativo-card {
            padding: 1.5rem;
            margin: 0.5rem 0;
        }
        
        .comparativo-number {
            font-size: 2rem;
        }
        
        .chart-comparativo-container {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="comparativo-header">
    <h1> Análisis Comparativo</h1>
    <h3>Sistema METGO - Comparación de 5 Años</h3>
    <p>Análisis comparativo detallado entre períodos, estaciones y métricas</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Panel de Comparación")
    
    # Selector de tipo de comparación
    tipo_comparacion = st.selectbox(
        "Tipo de Comparación:",
        ["Año vs Año", "Mes vs Mes", "Estación vs Estación", "Cultivo vs Cultivo", "Zona vs Zona"],
        key="tipo_comparacion"
    )
    
    # Selector de métricas a comparar (solo variables con serie real en API)
    metricas_comparar = st.multiselect(
        "Métricas a Comparar:",
        ["Temperatura", "Precipitación", "Humedad", "Viento", "Presión"],
        default=["Temperatura", "Humedad"],
        key="metricas_comparar"
    )
    
    # Selector de período base
    periodo_base = st.selectbox(
        "Período Base:",
        ["2020", "2021", "2022", "2023", "2024"],
        key="periodo_base"
    )

    modo_comparativo = st.radio(
        "Fuente de datos",
        ["API METGO (valle)"],
        index=0,
    )
    dias_hist_api = st.slider("Días histórico (API)", 7, 30, 14)

if modo_comparativo.startswith("API"):
    with st.spinner("Cargando comparativo del valle (OpenMeteo)…"):
        valle_cmp = comparativo_estaciones()
        hist_cmp = comparativo_historico(dias_hist_api)

    st.success(
        f"**API METGO** · {hoy_chile()} · {len(valle_cmp)} estaciones · "
        "Vue: http://127.0.0.1:5173/meteo/comparativo"
    )

    if valle_cmp:
        df_v = pd.DataFrame(valle_cmp)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Estaciones", len(df_v))
        if "temperatura_max" in df_v.columns:
            c2.metric("T° máx media", f"{df_v['temperatura_max'].mean():.1f}°C")
            c3.metric("T° mín media", f"{df_v['temperatura_min'].mean():.1f}°C")
        if "humedad" in df_v.columns:
            c4.metric("Humedad media", f"{df_v['humedad'].mean():.0f}%")

        fig_tmax = px.bar(
            df_v,
            x="estacion",
            y="temperatura_max",
            title="T° máxima hoy por estación",
            color="temperatura_max",
            color_continuous_scale="RdYlBu_r",
        )
        fig_tmax.update_layout(**plotly_layout(height=380, xaxis_tickangle=-25))
        st.plotly_chart(fig_tmax, use_container_width=True, config=PLOTLY_CONFIG)

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
                        "viento",
                    ]
                    if c in df_v.columns
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    if hist_cmp:
        df_h = pd.DataFrame(hist_cmp)
        if {"estacion", "fecha", "temperatura"}.issubset(df_h.columns):
            fig_hist = px.line(
                df_h,
                x="fecha",
                y="temperatura",
                color="estacion",
                title=f"Temperatura diaria · últimos {dias_hist_api} días",
                markers=True,
            )
            fig_hist.update_layout(**plotly_layout(height=420, xaxis_tickangle=-45))
            st.plotly_chart(fig_hist, use_container_width=True, config=PLOTLY_CONFIG)

    st.stop()

