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

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import metgo_paths

metgo_paths.setup_paths("05_api_rest")

from api_rest.services import generar_alertas, historico_meteo, nombre_a_slug, resumen_meteo
from meteo_dashboard_utils import filtrar_historico_hasta_hoy, hoy_chile

from mobile_config import MobileConfig

# Aplicar configuraciones móviles
MobileConfig.apply_mobile_optimizations()

# Header móvil optimizado
st.markdown("""
<div class="mobile-header">
    <h1>📱 METGO Mobile</h1>
    <h3>Sistema Meteorológico Agrícola</h3>
    <p>Optimizado para dispositivos móviles</p>
    <div style="margin-top: 0.5rem; padding: 0.25rem 0.75rem; background: rgba(255,255,255,0.2); border-radius: 15px; display: inline-block; font-size: 0.9rem;">
        🌡️ Tiempo Real | 🌾 Quillota
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar móvil colapsado
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    
    # Selector de estación
    estacion = st.selectbox(
        "🌍 Estación:",
        ["Quillota", "Los Nogales", "Hijuelas", "Limache", "Olmue"],
        key="estacion_mobile"
    )
    
    # Selector de vista
    vista = st.selectbox(
        "👁️ Vista:",
        ["Resumen", "Detallada", "Gráficos", "Alertas"],
        key="vista_mobile"
    )
    
    # Toggle de modo oscuro
    modo_oscuro = st.toggle("🌙 Modo Oscuro", value=False)

    modo_mobile = st.radio(
        "Fuente",
        ["API METGO", "Demo móvil"],
        index=0,
    )

if modo_mobile.startswith("API"):
    slug_m = nombre_a_slug(estacion)
    with st.spinner("Sincronizando…"):
        res_m = resumen_meteo(slug_m) or {}
        hist_m = filtrar_historico_hasta_hoy(historico_meteo(slug_m, 7) or [])
        alertas_m = generar_alertas(slug_m)
    datos = {
        "temperatura": float(res_m.get("temperatura") or 0),
        "humedad": float(res_m.get("humedad") or 0),
        "precipitacion": float(res_m.get("precipitacion") or 0),
        "viento": float(res_m.get("viento") or 0),
        "presion": float(res_m.get("presion") or 1013),
        "rendimiento": None,
        "calidad": None,
        "eficiencia": None,
        "alertas": [
            {"tipo": a.get("nivel", "info"), "mensaje": a.get("mensaje", "")}
            for a in alertas_m[:6]
        ],
        "hist": hist_m,
        "tipo_dato": res_m.get("tipo_dato"),
    }
    st.caption(f"{hoy_chile()} · {estacion} · {datos['tipo_dato']} · Vue 5173")
else:
    datos = None


if datos is None:
    st.warning("Sin datos — requiere API METGO (:8080).")
    st.stop()

# Métricas principales en grid móvil
if vista == "Resumen" or vista == "Detallada":
    st.markdown("### 📊 Condiciones Actuales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="mobile-metric">
            <div class="mobile-number">{datos['temperatura']}°C</div>
            <div class="mobile-label">🌡️ Temperatura</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="mobile-metric">
            <div class="mobile-number">{datos['humedad']}%</div>
            <div class="mobile-label">💧 Humedad</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="mobile-metric">
            <div class="mobile-number">{datos['viento']} km/h</div>
            <div class="mobile-label">💨 Viento</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="mobile-metric">
            <div class="mobile-number">{datos['precipitacion']} mm</div>
            <div class="mobile-label">🌧️ Lluvia</div>
        </div>
        """, unsafe_allow_html=True)

if vista == "Gráficos":
    hist = datos.get("hist") or []
    if hist:
        df_h = pd.DataFrame(hist)
        fig = go.Figure()
        if "temperatura" in df_h.columns or "temperatura_max" in df_h.columns:
            ycol = "temperatura_max" if "temperatura_max" in df_h.columns else "temperatura"
            fig.add_trace(
                go.Scatter(x=df_h.get("fecha"), y=df_h[ycol], mode="lines+markers", name="Temperatura")
            )
            fig.update_layout(**plotly_layout("Histórico temperatura", height=320))
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    else:
        st.info("Sin serie histórica — use Vue /meteo/historico o ejecute ETL Archive.")

st.caption("Vista móvil · datos API METGO · Vue http://127.0.0.1:5173")
