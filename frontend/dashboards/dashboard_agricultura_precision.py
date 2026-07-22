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

metgo_paths.setup_paths("02_agricola", "05_api_rest")

from api_rest.services import (
    comparativo_estaciones,
    historico_meteo,
    nombre_a_slug,
    reporte_agricola_avanzado,
)
from agricola_dashboard_utils import CULTIVO_A_SLUG, ESTACIONES_VALLE, cargar_contexto_agricola
from meteo_dashboard_utils import filtrar_historico_hasta_hoy, hoy_chile

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "Agricultura de Precisión",
    "Análisis de cultivos con datos históricos Quillota",
    module="precision",
    page_icon="M",
    initial_sidebar_state="collapsed",
)

# CSS complementario
st.markdown("""
<style>
    /* Diseño móvil profesional para agricultura */
    .precision-header {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .precision-card {
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
    
    .precision-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #27ae60, #2ecc71, #16a085, #1abc9c);
    }
    
    .precision-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .precision-label {
        font-size: 1rem;
        color: #7f8c8d;
        margin: 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .precision-change {
        font-size: 0.9rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .precision-positive {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        color: white;
    }
    
    .precision-negative {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
    }
    
    .precision-neutral {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
    }
    
    .chart-precision-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
    }
    
    .section-title-precision {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #27ae60;
        display: inline-block;
    }
    
    .zone-card {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .precision-header {
            padding: 1.5rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .precision-card {
            padding: 1.5rem;
            margin: 0.5rem 0;
        }
        
        .precision-number {
            font-size: 2rem;
        }
        
        .chart-precision-container {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="precision-header">
    <h1> Agricultura de Precisión</h1>
    <h3>Sistema METGO - Tecnología Avanzada</h3>
    <p>Monitoreo preciso, análisis de zonas y optimización inteligente de cultivos</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Panel de Control de Precisión")
    
    # Selector de cultivo
    cultivo_precision = st.selectbox(
        "Cultivo:",
        ["Palta", "Cítricos", "Vid", "Tomate", "Lechuga", "Todos los Cultivos"],
        key="cultivo_precision"
    )
    
    # Selector de zona
    zona_precision = st.selectbox(
        "Zona de Análisis:",
        ["Zona A - Norte", "Zona B - Centro", "Zona C - Sur", "Zona D - Este", "Zona E - Oeste", "Todas las Zonas"],
        key="zona_precision"
    )
    
    # Selector de tecnología
    tecnologia = st.selectbox(
        "Tecnología:",
        ["Sensores IoT", "Drones", "Satélites", "IA/ML", "Sistema Integrado"],
        key="tecnologia"
    )

    modo_precision = st.radio(
        "Fuente de datos",
        ["API METGO (valle)"],
        index=0,
    )

    if modo_precision.startswith("API"):
        est_p = st.selectbox("Estación", ESTACIONES_VALLE, key="est_api_p")
        cult_p = st.selectbox("Cultivo", list(CULTIVO_A_SLUG.keys()), key="cult_api_p")

if modo_precision.startswith("API"):
    slug_p = nombre_a_slug(est_p)

    with st.spinner("Cargando precisión agrícola (API)…"):
        ctx_p = cargar_contexto_agricola(est_p, cult_p)
        hist_p = filtrar_historico_hasta_hoy(historico_meteo(slug_p, 30) or [])
        valle_p = comparativo_estaciones()
        rep_p = reporte_agricola_avanzado(slug_p)

    st.success(f"**API METGO** · {est_p} · {hoy_chile()} · Vue http://127.0.0.1:5173/agricola")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("T° actual", f"{ctx_p['temperatura']:.1f}°C")
    c2.metric("Humedad", f"{ctx_p['humedad']:.0f}%")
    c3.metric("Riego sugerido", f"{ctx_p.get('riego', {}).get('mm_sugeridos_hoy', '—')} mm")
    c4.metric("Lluvia hoy", f"{ctx_p['precipitacion']:.1f} mm")

    if hist_p:
        df_h = pd.DataFrame(
            [
                {
                    "fecha": r["fecha"],
                    "humedad": r.get("humedad"),
                    "precipitacion": r.get("precipitacion"),
                    "temperatura": r.get("temperatura"),
                }
                for r in hist_p
            ]
        )
        fig_h = make_subplots(rows=2, cols=1, subplot_titles=("Humedad (%)", "Precipitación (mm)"))
        fig_h.add_trace(
            go.Scatter(x=df_h["fecha"], y=df_h["humedad"], name="Humedad"),
            row=1,
            col=1,
        )
        fig_h.add_trace(
            go.Bar(x=df_h["fecha"], y=df_h["precipitacion"], name="Lluvia"),
            row=2,
            col=1,
        )
        fig_h.update_layout(**plotly_layout(f"Histórico 30 días · {est_p}", height=420))
        st.plotly_chart(fig_h, use_container_width=True, config=PLOTLY_CONFIG)

    if valle_p:
        st.markdown("### Comparación por estación (hoy)")
        st.dataframe(
            pd.DataFrame(valle_p)[
                ["estacion", "temperatura_max", "temperatura_min", "humedad", "precipitacion"]
            ],
            use_container_width=True,
            hide_index=True,
        )

    if rep_p and not rep_p.get("error"):
        with st.expander("Reporte integral módulo 02", expanded=True):
            st.json(rep_p)
    elif rep_p:
        st.warning(rep_p.get("error", "Sin reporte avanzado"))

    for rec in ctx_p.get("recomendaciones_api") or []:
        st.info(f"**{rec.get('cultivo')}**: {rec.get('accion')} — {rec.get('motivo')}")

    st.stop()
