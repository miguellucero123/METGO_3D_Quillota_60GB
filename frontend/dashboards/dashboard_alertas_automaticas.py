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

from api_rest.services import generar_alertas as alertas_meteo_api
from metgo.streamlit_theme import bootstrap_dashboard, frost_badge_html, PLOTLY_CONFIG
from meteo_dashboard_utils import hoy_chile

# Configuración de la página optimizada para móviles
st.set_page_config(
    page_title="Sistema de Alertas Automáticas - METGO",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="collapsed",
)

bootstrap_dashboard(
    "Sistema de Alertas Automáticas",
    "Umbrales, heladas y notificaciones operativas",
    module="alertas",
)

# CSS personalizado para diseño móvil profesional
st.markdown("""
<style>
    /* Diseño móvil profesional para alertas */
    .alertas-header {
        background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .alerta-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid;
        position: relative;
        overflow: hidden;
    }
    
    .alerta-critica {
        border-left-color: #e74c3c;
        background: linear-gradient(135deg, #fff5f5 0%, #ffeaea 100%);
    }
    
    .alerta-advertencia {
        border-left-color: #f39c12;
        background: linear-gradient(135deg, #fffbf0 0%, #fff7e6 100%);
    }
    
    .alerta-info {
        border-left-color: #3498db;
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
    }
    
    .alerta-success {
        border-left-color: #27ae60;
        background: linear-gradient(135deg, #f0fff4 0%, #e6ffe6 100%);
    }
    
    .alerta-titulo {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .alerta-mensaje {
        color: #7f8c8d;
        margin: 0.5rem 0;
        line-height: 1.5;
    }
    
    .alerta-timestamp {
        color: #95a5a6;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .alerta-accion {
        background: #2c3e50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        margin-top: 1rem;
        display: inline-block;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .alerta-accion:hover {
        background: #34495e;
        transform: translateY(-2px);
    }
    
    .metric-alerta-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .metric-alerta-number {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
    }
    
    .metric-alerta-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    
    .chart-alertas-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
    }
    
    .section-title-alertas {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #e17055;
        display: inline-block;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .alertas-header {
            padding: 1.5rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .alerta-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .metric-alerta-card {
            padding: 1rem;
        }
        
        .chart-alertas-container {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="alertas-header">
    <h1> Sistema de Alertas Automáticas</h1>
    <h3>Sistema METGO - Monitoreo Inteligente</h3>
    <p>Detección automática de anomalías, alertas inteligentes y respuesta inmediata</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Panel de Control de Alertas")
    
    # Selector de tipo de alerta
    tipo_alerta = st.selectbox(
        "Tipo de Alerta:",
        ["Todas", "Críticas", "Advertencias", "Informativas", "Exitosas"],
        key="tipo_alerta"
    )
    
    # Selector de sistema
    sistema_alerta = st.selectbox(
        "Sistema:",
        ["Meteorológico", "Agrícola", "IoT", "Calidad", "Económico", "Todos"],
        key="sistema_alerta"
    )
    
    # Selector de período
    periodo_alerta = st.selectbox(
        "Período:",
        ["Última hora", "Últimas 24 horas", "Última semana", "Último mes"],
        key="periodo_alerta"
    )

    modo_alertas = st.radio(
        "Fuente",
        ["Alertas METGO (API)"],
        index=0,
    )

_NIVEL_UI = {
    "critical": ("", "alerta-critica", "Críticas"),
    "warning": ("", "alerta-advertencia", "Advertencias"),
    "info": ("", "alerta-info", "Informativas"),
    "success": ("", "alerta-success", "Exitosas"),
}


def _tipo_ui(nivel: str) -> str:
    return _NIVEL_UI.get(str(nivel or "info").lower(), _NIVEL_UI["info"])[2]


if modo_alertas.startswith("Alertas METGO"):
    try:
        alertas_api = alertas_meteo_api()
    except Exception as e:
        st.error(f"No se pudo conectar a la API METGO (:8080): {e}")
        st.stop()

    st.success(
        f"**{hoy_chile()}** · {len(alertas_api)} alertas activas · "
        "Config en Vue: http://127.0.0.1:5173/alertas/config"
    )

    filtradas = alertas_api
    if tipo_alerta != "Todas":
        filtradas = [a for a in filtradas if _tipo_ui(a.get("nivel")) == tipo_alerta]

    if not filtradas:
        st.info("Sin alertas para el filtro seleccionado.")
    else:
        for a in filtradas:
            icono, css_cls, _ = _NIVEL_UI.get(
                str(a.get("nivel", "info")).lower(), _NIVEL_UI["info"]
            )
            est = a.get("estacion") or a.get("estacion_id") or "Valle"
            st.markdown(
                f"""
                <div class="alerta-card {css_cls}">
                    <div class="alerta-titulo">{icono} {a.get('tipo', 'Alerta')} · {est}</div>
                    <div class="alerta-mensaje">{a.get('mensaje', '')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        df_al = pd.DataFrame(
            [
                {
                    "nivel": a.get("nivel"),
                    "tipo": a.get("tipo"),
                    "estacion": a.get("estacion") or a.get("estacion_id"),
                    "mensaje": a.get("mensaje"),
                }
                for a in filtradas
            ]
        )
        st.dataframe(df_al, use_container_width=True, hide_index=True)

    st.stop()
