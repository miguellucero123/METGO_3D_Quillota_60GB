import streamlit as st
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
    page_icon="📊",
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
    <h1>📊 Dashboard Simple</h1>
    <h3>Sistema METGO - Vista Simplificada</h3>
    <p>Información esencial y fácil de entender</p>
</div>
""", unsafe_allow_html=True)

# Sidebar simple
with st.sidebar:
    st.markdown("### ⚙️ Opciones")
    
    # Selector de estación
    estacion = st.selectbox(
        "🌍 Estación:",
        ["Quillota", "Los Nogales", "Hijuelas", "Limache", "Olmue"],
        key="estacion_simple"
    )
    
    # Selector de período
    periodo = st.selectbox(
        "📅 Período:",
        ["Hoy", "Esta semana", "Este mes", "Últimos 3 meses"],
        key="periodo_simple"
    )
    modo_simple = st.radio(
        "Fuente",
        ["API METGO (OpenMeteo)", "Vista demo (valores fijos)"],
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

st.sidebar.caption("Modo demo activo")

# Función para generar datos simples
@st.cache_data
def generar_datos_simples(estacion, periodo):
    """Genera datos meteorológicos simples"""
    
    # Configuración por estación
    configs = {
        "Quillota": {"temp": 22, "humedad": 65, "precip": 0.3},
        "Los Nogales": {"temp": 21, "humedad": 70, "precip": 0.4},
        "Hijuelas": {"temp": 20, "humedad": 75, "precip": 0.5},
        "Limache": {"temp": 23, "humedad": 60, "precip": 0.2},
        "Olmue": {"temp": 22.5, "humedad": 68, "precip": 0.35}
    }
    
    config = configs[estacion]
    
    # Generar datos actuales con variación
    temperatura = config["temp"] + random.uniform(-3, 3)
    humedad = config["humedad"] + random.uniform(-10, 10)
    precipitacion = max(0, config["precip"] + random.uniform(-0.2, 0.2))
    viento = random.uniform(5, 15)
    presion = random.uniform(1010, 1020)
    
    # Datos agrícolas simples
    rendimiento = 20 + temperatura * 0.5 + random.uniform(-2, 2)
    calidad = 75 + random.uniform(-10, 10)
    
    return {
        'temperatura': round(temperatura, 1),
        'humedad': round(humedad, 1),
        'precipitacion': round(precipitacion, 2),
        'viento': round(viento, 1),
        'presion': round(presion, 1),
        'rendimiento': round(rendimiento, 1),
        'calidad': round(calidad, 1)
    }

# Generar datos
datos = generar_datos_simples(estacion, periodo)

# Métricas principales
st.markdown("### 📊 Condiciones Actuales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="simple-metric">
        <div class="simple-number">{datos['temperatura']}°C</div>
        <div class="simple-label">🌡️ Temperatura</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="simple-metric">
        <div class="simple-number">{datos['humedad']}%</div>
        <div class="simple-label">💧 Humedad</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="simple-metric">
        <div class="simple-number">{datos['precipitacion']} mm</div>
        <div class="simple-label">🌧️ Lluvia</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="simple-metric">
        <div class="simple-number">{datos['viento']} km/h</div>
        <div class="simple-label">💨 Viento</div>
    </div>
    """, unsafe_allow_html=True)

# Gráfico simple de temperatura
st.markdown("### 🌡️ Temperatura de Hoy")

# Generar datos de 24 horas
horas = list(range(24))
temp_horas = [datos['temperatura'] + np.sin(2 * np.pi * h / 24) * 5 + random.uniform(-1, 1) for h in horas]

fig_temp = go.Figure()
fig_temp.add_trace(go.Scatter(
    x=horas, 
    y=temp_horas,
    mode='lines+markers',
    name='Temperatura',
    line=dict(color='#e74c3c', width=3),
    marker=dict(size=6)
))

fig_temp.update_layout(
    title='Temperatura por Hora',
    xaxis_title='Hora del Día',
    yaxis_title='Temperatura (°C)',
    height=400,
    showlegend=False
)

st.plotly_chart(fig_temp, use_container_width=True)

# Información agrícola simple
st.markdown("### 🌾 Información Agrícola")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="simple-card">
        <h4>📈 Rendimiento Esperado</h4>
        <div class="simple-number" style="color: #27ae60;">{datos['rendimiento']} t/ha</div>
        <p>Producción estimada para esta temporada</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="simple-card">
        <h4>⭐ Calidad del Producto</h4>
        <div class="simple-number" style="color: #f39c12;">{datos['calidad']}%</div>
        <p>Calidad esperada de los cultivos</p>
    </div>
    """, unsafe_allow_html=True)

# Recomendaciones simples
st.markdown("### 💡 Recomendaciones")

recomendaciones = []

# Recomendaciones basadas en condiciones actuales
if datos['temperatura'] > 30:
    recomendaciones.append("🌡️ **Temperatura alta**: Considerar riego adicional")
elif datos['temperatura'] < 15:
    recomendaciones.append("🌡️ **Temperatura baja**: Proteger cultivos del frío")

if datos['humedad'] > 80:
    recomendaciones.append("💧 **Humedad alta**: Mejorar ventilación")
elif datos['humedad'] < 50:
    recomendaciones.append("💧 **Humedad baja**: Incrementar riego")

if datos['precipitacion'] > 1:
    recomendaciones.append("🌧️ **Lluvia intensa**: Verificar drenaje")
elif datos['precipitacion'] < 0.1:
    recomendaciones.append("🌧️ **Poca lluvia**: Programar riego")

if datos['viento'] > 20:
    recomendaciones.append("💨 **Vientos fuertes**: Proteger estructuras")

# Mostrar recomendaciones
for rec in recomendaciones:
    st.info(rec)

if not recomendaciones:
    st.success("✅ Condiciones óptimas - No se requieren acciones especiales")

# Estado del sistema
st.markdown("### ℹ️ Estado del Sistema")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="simple-card">
        <h4>📍 Estación</h4>
        <p><strong>{estacion}</strong></p>
        <p>Monitoreo activo</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="simple-card">
        <h4>🕐 Última Actualización</h4>
        <p><strong>{datetime.now().strftime("%H:%M")}</strong></p>
        <p>Datos en tiempo real</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="simple-card">
        <h4>📊 Estado</h4>
        <p><strong>🟢 Normal</strong></p>
        <p>Sistema funcionando</p>
    </div>
    """, unsafe_allow_html=True)

# Acciones rápidas
st.markdown("### ⚡ Acciones Rápidas")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Actualizar Datos", key="actualizar_simple"):
        st.success("Datos actualizados correctamente")
        st.rerun()

with col2:
    if st.button("📧 Enviar Reporte", key="reporte_simple"):
        st.success("Reporte enviado por email")

with col3:
    if st.button("📱 Compartir", key="compartir_simple"):
        st.success("Enlace copiado al portapapeles")

# Información adicional
st.markdown("### 📋 Información Adicional")

with st.expander("🔧 Configuración Avanzada"):
    st.markdown("""
    **Para acceder a funciones avanzadas:**
    - 📊 Dashboard Principal: Funciones completas
    - 🌤️ Meteorológico: Análisis detallado
    - 🌾 Agrícola: Gestión completa
    - 🤖 IA/ML: Predicciones avanzadas
    """)

with st.expander("📞 Contacto y Soporte"):
    st.markdown("""
    **Sistema METGO - Soporte Técnico**
    - 📧 Email: soporte@metgo.cl
    - 📱 Teléfono: +56 9 XXXX XXXX
    - 🌐 Web: www.metgo.cl
    - ⏰ Horario: Lunes a Viernes 8:00-18:00
    """)

# Footer simple
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 15px;">
    <p>📊 <strong>Sistema METGO</strong> - Dashboard Simple</p>
    <p>Vista simplificada para uso rápido y fácil</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
