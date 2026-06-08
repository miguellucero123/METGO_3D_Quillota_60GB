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

# Función para generar datos móviles optimizados
@st.cache_data
def generar_datos_mobile(estacion, vista):
    """Genera datos optimizados para móviles"""
    
    # Configuración por estación
    configs = {
        "Quillota": {"temp": 22, "humedad": 65, "precip": 0.3, "viento": 8},
        "Los Nogales": {"temp": 21, "humedad": 70, "precip": 0.4, "viento": 6},
        "Hijuelas": {"temp": 20, "humedad": 75, "precip": 0.5, "viento": 7},
        "Limache": {"temp": 23, "humedad": 60, "precip": 0.2, "viento": 9},
        "Olmue": {"temp": 22.5, "humedad": 68, "precip": 0.35, "viento": 8}
    }
    
    config = configs[estacion]
    
    # Datos actuales con variación realista
    temperatura = config["temp"] + random.uniform(-2, 2)
    humedad = config["humedad"] + random.uniform(-8, 8)
    precipitacion = max(0, config["precip"] + random.uniform(-0.1, 0.1))
    viento = max(0, config["viento"] + random.uniform(-2, 2))
    presion = 1013 + random.uniform(-5, 5)
    
    # Datos agrícolas
    rendimiento = 20 + temperatura * 0.3 + random.uniform(-1, 1)
    calidad = 75 + random.uniform(-5, 5)
    eficiencia = 80 + random.uniform(-5, 5)
    
    # Alertas
    alertas = []
    if temperatura > 30:
        alertas.append({"tipo": "warning", "mensaje": "Temperatura alta"})
    if humedad < 50:
        alertas.append({"tipo": "info", "mensaje": "Humedad baja"})
    if viento > 15:
        alertas.append({"tipo": "warning", "mensaje": "Vientos fuertes"})
    
    return {
        'temperatura': round(temperatura, 1),
        'humedad': round(humedad, 1),
        'precipitacion': round(precipitacion, 2),
        'viento': round(viento, 1),
        'presion': round(presion, 1),
        'rendimiento': round(rendimiento, 1),
        'calidad': round(calidad, 1),
        'eficiencia': round(eficiencia, 1),
        'alertas': alertas
    }

if datos is None:
    datos = generar_datos_mobile(estacion, vista)
    datos["hist"] = []

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

# Gráfico móvil optimizado
if vista == "Gráficos" or vista == "Detallada":
    st.markdown("### 📈 Análisis Visual")

    hist_plot = datos.get("hist") or []
    if hist_plot:
        fechas = [r.get("fecha") for r in hist_plot]
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("T° máx / mín (OpenMeteo)", "Humedad %"),
            vertical_spacing=0.12,
        )
        fig.add_trace(
            go.Scatter(
                x=fechas,
                y=[r.get("temperatura_max") for r in hist_plot],
                name="T° máx",
                line=dict(color="#e74c3c", width=2),
                mode="lines+markers",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=fechas,
                y=[r.get("temperatura_min") for r in hist_plot],
                name="T° mín",
                line=dict(color="#3498db", width=2),
                mode="lines+markers",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=fechas,
                y=[r.get("humedad") for r in hist_plot],
                name="Humedad",
                line=dict(color="#27ae60", width=2),
                mode="lines+markers",
            ),
            row=2,
            col=1,
        )
        fig.update_layout(height=420, showlegend=True, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        horas = list(range(24))
        temp_horas = [
            datos["temperatura"] + np.sin(2 * np.pi * h / 24) * 4 + random.uniform(-1, 1)
            for h in horas
        ]
        humedad_horas = [
            datos["humedad"] + np.cos(2 * np.pi * h / 24) * 10 + random.uniform(-2, 2)
            for h in horas
        ]
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("Temperatura (demo)", "Humedad (demo)"),
            vertical_spacing=0.1,
        )
        fig.add_trace(go.Scatter(x=horas, y=temp_horas, line=dict(color="#e74c3c")), row=1, col=1)
        fig.add_trace(go.Scatter(x=horas, y=humedad_horas, line=dict(color="#3498db")), row=2, col=1)
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# Alertas móviles
if vista == "Alertas" or vista == "Detallada":
    st.markdown("### 🚨 Alertas y Recomendaciones")
    
    if datos["alertas"]:
        for alerta in datos["alertas"]:
            tipo_a = str(alerta.get("tipo", "")).lower()
            if tipo_a in ("warning", "critical"):
                st.markdown(f"""
                <div class="mobile-alert warning">
                    ⚠️ <strong>Advertencia:</strong> {alerta['mensaje']}
                </div>
                """, unsafe_allow_html=True)
            elif tipo_a == "info":
                st.markdown(f"""
                <div class="mobile-alert info">
                    ℹ️ <strong>Información:</strong> {alerta['mensaje']}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="mobile-alert success">
            ✅ <strong>Todo Normal:</strong> No hay alertas activas
        </div>
        """, unsafe_allow_html=True)

# Información agrícola móvil
if vista == "Detallada" and datos.get("rendimiento") is not None:
    st.markdown("### 🌾 Información Agrícola (demo)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="mobile-card">
            <h4>📈 Rendimiento</h4>
            <div class="mobile-number" style="color: #27ae60;">{datos['rendimiento']} t/ha</div>
            <p style="font-size: 0.9rem; color: #7f8c8d;">Producción estimada</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="mobile-card">
            <h4>⭐ Calidad</h4>
            <div class="mobile-number" style="color: #f39c12;">{datos['calidad']}%</div>
            <p style="font-size: 0.9rem; color: #7f8c8d;">Calidad del producto</p>
        </div>
        """, unsafe_allow_html=True)
elif vista == "Detallada":
    st.caption("Riego y cultivos: use Vue → /agricola")

# Acciones rápidas móviles
st.markdown("### ⚡ Acciones Rápidas")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Actualizar", key="actualizar_mobile", help="Actualizar datos"):
        st.success("Datos actualizados")
        st.rerun()

with col2:
    if st.button("📧 Reporte", key="reporte_mobile", help="Enviar reporte"):
        st.success("Reporte enviado")

# Navegación móvil
st.markdown("### 🧭 Navegación Rápida")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Principal", key="nav_principal"):
        st.info("Ir al Dashboard Principal")

with col2:
    if st.button("🌤️ Meteorológico", key="nav_meteo"):
        st.info("Ir al Dashboard Meteorológico")

with col3:
    if st.button("🌾 Agrícola", key="nav_agri"):
        st.info("Ir al Dashboard Agrícola")

# Información del sistema móvil
st.markdown("### ℹ️ Información del Sistema")

st.markdown(f"""
<div class="mobile-card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h4>📍 Estación</h4>
            <p><strong>{estacion}</strong></p>
        </div>
        <div>
            <h4>🕐 Actualización</h4>
            <p><strong>{datetime.now().strftime("%H:%M")}</strong></p>
        </div>
    </div>
    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e9ecef;">
        <div style="display: flex; justify-content: space-between;">
            <span>📊 Estado:</span>
            <span style="color: #27ae60; font-weight: bold;">🟢 Normal</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>📱 Optimizado:</span>
            <span style="color: #3498db; font-weight: bold;">✅ Móvil</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Navegación inferior móvil
st.markdown("""
<div class="mobile-nav">
    <a href="http://192.168.1.7:8501" class="mobile-nav-item">
        <div>🏠</div>
        <div>Principal</div>
    </a>
    <a href="http://192.168.1.7:8502" class="mobile-nav-item">
        <div>🌤️</div>
        <div>Meteo</div>
    </a>
    <a href="http://192.168.1.7:8503" class="mobile-nav-item">
        <div>🌾</div>
        <div>Agrícola</div>
    </a>
    <a href="http://192.168.1.7:8505" class="mobile-nav-item">
        <div>🤖</div>
        <div>IA/ML</div>
    </a>
    <a href="http://192.168.1.7:8511" class="mobile-nav-item active">
        <div>📱</div>
        <div>Móvil</div>
    </a>
</div>
""", unsafe_allow_html=True)

# Footer móvil
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 15px; font-size: 0.9rem;">
    <p><strong>📱 Sistema METGO Mobile</strong></p>
    <p>Optimizado para dispositivos móviles</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
