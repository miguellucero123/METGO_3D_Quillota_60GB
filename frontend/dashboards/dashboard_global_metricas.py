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

from api_rest.services import metricas_globales
from metgo.streamlit_theme import bootstrap_dashboard, PLOTLY_CONFIG, plotly_layout
from meteo_dashboard_utils import hoy_chile

# Configuración de la página optimizada para móviles
st.set_page_config(
    page_title="Dashboard Global de Métricas - METGO",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

bootstrap_dashboard(
    "Dashboard Global de Métricas",
    "KPIs integrados del ecosistema METGO 3D",
    module="global",
)

# CSS personalizado para diseño móvil profesional
st.markdown("""
<style>
    /* Diseño móvil profesional */
    .global-header {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .metric-global-card {
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
    
    .metric-global-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #00b894, #00a085, #74b9ff, #0984e3);
    }
    
    .kpi-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .kpi-label {
        font-size: 1rem;
        color: #7f8c8d;
        margin: 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .kpi-change {
        font-size: 0.9rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .kpi-positive {
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white;
    }
    
    .kpi-negative {
        background: linear-gradient(135deg, #e17055, #d63031);
        color: white;
    }
    
    .kpi-neutral {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
    }
    
    .chart-container-global {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #00b894;
        display: inline-block;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .global-header {
            padding: 1.5rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .metric-global-card {
            padding: 1.5rem;
            margin: 0.5rem 0;
        }
        
        .kpi-number {
            font-size: 2rem;
        }
        
        .chart-container-global {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="global-header">
    <h1>📈 Dashboard Global de Métricas</h1>
    <h3>Sistema METGO - Análisis Integral 5 Años</h3>
    <p>Métricas globales, tendencias históricas y análisis comparativo completo</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Panel de Control Global")
    
    # Selector de período
    periodo_global = st.selectbox(
        "📅 Período de Análisis:",
        ["Últimos 5 años", "Últimos 3 años", "Últimos 2 años", "Último año", "Últimos 6 meses"],
        key="periodo_global"
    )
    
    # Selector de tipo de métrica
    tipo_metrica = st.selectbox(
        "📊 Tipo de Métrica:",
        ["Meteorológicas", "Agrícolas", "Económicas", "Ambientales", "Todas"],
        key="tipo_metrica"
    )
    
    # Selector de granularidad
    granularidad = st.selectbox(
        "⏱️ Granularidad:",
        ["Diaria", "Semanal", "Mensual", "Anual"],
        key="granularidad"
    )

# Función para generar datos globales de 5 años
@st.cache_data
def generar_datos_globales_5_anos(periodo, granularidad):
    """Genera datos globales simulados de 5 años"""
    
    # Mapeo de períodos
    periodos_map = {
        "Últimos 5 años": 5,
        "Últimos 3 años": 3,
        "Últimos 2 años": 2,
        "Último año": 1,
        "Últimos 6 meses": 0.5
    }
    
    anos = periodos_map[periodo]
    inicio = datetime.now() - timedelta(days=anos*365)
    
    # Configurar frecuencia según granularidad
    freq_map = {
        "Diaria": "D",
        "Semanal": "W",
        "Mensual": "M",
        "Anual": "Y"
    }
    
    freq = freq_map[granularidad]
    fechas = pd.date_range(start=inicio, end=datetime.now(), freq=freq)
    
    # Generar datos globales
    datos = []
    
    for fecha in fechas:
        # Tendencias de crecimiento simuladas
        anos_transcurridos = (fecha - inicio).days / 365
        
        # Datos meteorológicos globales
        temp_base = 18.5 + anos_transcurridos * 0.1  # Tendencia de calentamiento
        temp_estacional = np.sin(2 * np.pi * fecha.month / 12) * 5
        temperatura = temp_base + temp_estacional + np.random.normal(0, 3)
        
        precipitacion_base = 0.3 - anos_transcurridos * 0.01  # Tendencia de sequía
        precipitacion = max(0, precipitacion_base + np.random.exponential(1))
        
        humedad_base = 65 + np.sin(2 * np.pi * fecha.month / 12) * 10
        humedad = max(10, min(100, humedad_base + np.random.normal(0, 8)))
        
        # Datos agrícolas globales
        rendimiento_base = 20 + anos_transcurridos * 1.5  # Mejora tecnológica
        rendimiento = rendimiento_base + temperatura * 0.3 + humedad * 0.1 + np.random.normal(0, 2)
        
        calidad_base = 75 + anos_transcurridos * 2  # Mejora en calidad
        calidad = min(100, max(0, calidad_base + np.random.normal(0, 5)))
        
        # Datos económicos globales
        precio_base = 1000 + anos_transcurridos * 50  # Inflación
        precio = precio_base + np.random.normal(0, 100)
        
        ingreso_total = rendimiento * precio / 1000  # En miles de pesos
        
        # Datos ambientales
        co2_base = 400 + anos_transcurridos * 2  # Aumento CO2
        co2 = co2_base + np.random.normal(0, 10)
        
        biodiversidad_base = 85 - anos_transcurridos * 1  # Pérdida biodiversidad
        biodiversidad = max(0, min(100, biodiversidad_base + np.random.normal(0, 3)))
        
        # Métricas de eficiencia
        eficiencia_riego = 70 + anos_transcurridos * 3 + np.random.normal(0, 5)
        eficiencia_riego = max(0, min(100, eficiencia_riego))
        
        uso_sustentable = 60 + anos_transcurridos * 4 + np.random.normal(0, 6)
        uso_sustentable = max(0, min(100, uso_sustentable))
        
        datos.append({
            'Fecha': fecha,
            'Año': fecha.year,
            'Mes': fecha.month,
            'Trimestre': (fecha.month - 1) // 3 + 1,
            'Temperatura': round(temperatura, 1),
            'Precipitacion': round(precipitacion, 2),
            'Humedad': round(humedad, 1),
            'Rendimiento': round(rendimiento, 1),
            'Calidad': round(calidad, 1),
            'Precio': round(precio, 0),
            'Ingreso_Total': round(ingreso_total, 0),
            'CO2': round(co2, 1),
            'Biodiversidad': round(biodiversidad, 1),
            'Eficiencia_Riego': round(eficiencia_riego, 1),
            'Uso_Sustentable': round(uso_sustentable, 1),
            'Años_Transcurridos': round(anos_transcurridos, 1)
        })
    
    return pd.DataFrame(datos)

# KPIs en vivo (API) — mismo contrato que Vue /metricas
try:
    mg = metricas_globales()
    if mg.get("estaciones_activas", 0) > 0:
        st.markdown("### 🌍 Valle de Aconcagua · datos en vivo")
        st.caption(f"Día de referencia **{mg.get('referencia_fecha', hoy_chile())}** · Vue http://127.0.0.1:5173/metricas")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Estaciones", mg["estaciones_activas"])
        c2.metric("T° máx media", f"{mg.get('temperatura_media_max')}°C")
        c3.metric("T° mín media", f"{mg.get('temperatura_media_min')}°C")
        c4.metric("Precip. total", f"{mg.get('precipitacion_total')} mm")
        c5.metric("Viento máx", f"{mg.get('viento_max')} km/h")
        c6.metric("Alertas", mg.get("alertas_activas", 0))
        if mg.get("detalle_estaciones"):
            st.dataframe(
                pd.DataFrame(mg["detalle_estaciones"])[
                    [
                        "estacion",
                        "temperatura_max",
                        "temperatura_min",
                        "precipitacion",
                        "viento",
                        "humedad",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
except Exception as e:
    st.warning(f"API METGO no disponible para KPIs en vivo: {e}")

# Generar datos (series largas ilustrativas / ETL CSV)
with st.spinner("📈 Generando series históricas extendidas…"):
    df_global = generar_datos_globales_5_anos(periodo_global, granularidad)

st.info(
    "Las gráficas de tendencia multi-año siguen siendo **series ilustrativas** "
    "hasta integrar el CSV histórico vía ETL. Los KPIs del valle arriba son **OpenMeteo/API**."
)

# KPIs principales con diseño profesional
st.markdown("### 🎯 Indicadores históricos extendidos (ilustrativo)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    temp_actual = df_global['Temperatura'].iloc[-1]
    temp_anterior = df_global['Temperatura'].iloc[-2] if len(df_global) > 1 else temp_actual
    cambio_temp = temp_actual - temp_anterior
    
    st.markdown(f"""
    <div class="metric-global-card">
        <div class="kpi-label">🌡️ Temperatura Global</div>
        <div class="kpi-number">{temp_actual:.1f}°C</div>
        <div class="kpi-change {'kpi-positive' if cambio_temp > 0 else 'kpi-negative' if cambio_temp < 0 else 'kpi-neutral'}">
            {cambio_temp:+.1f}°C vs anterior
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    rendimiento_actual = df_global['Rendimiento'].iloc[-1]
    rendimiento_anterior = df_global['Rendimiento'].iloc[-2] if len(df_global) > 1 else rendimiento_actual
    cambio_rendimiento = rendimiento_actual - rendimiento_anterior
    
    st.markdown(f"""
    <div class="metric-global-card">
        <div class="kpi-label">🌾 Rendimiento Global</div>
        <div class="kpi-number">{rendimiento_actual:.1f} t/ha</div>
        <div class="kpi-change {'kpi-positive' if cambio_rendimiento > 0 else 'kpi-negative' if cambio_rendimiento < 0 else 'kpi-neutral'}">
            {cambio_rendimiento:+.1f} t/ha vs anterior
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    ingreso_actual = df_global['Ingreso_Total'].iloc[-1]
    ingreso_anterior = df_global['Ingreso_Total'].iloc[-2] if len(df_global) > 1 else ingreso_actual
    cambio_ingreso = ingreso_actual - ingreso_anterior
    
    st.markdown(f"""
    <div class="metric-global-card">
        <div class="kpi-label">💰 Ingreso Total</div>
        <div class="kpi-number">${ingreso_actual:,.0f}K</div>
        <div class="kpi-change {'kpi-positive' if cambio_ingreso > 0 else 'kpi-negative' if cambio_ingreso < 0 else 'kpi-neutral'}">
            ${cambio_ingreso:+,.0f}K vs anterior
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    eficiencia_actual = df_global['Eficiencia_Riego'].iloc[-1]
    eficiencia_anterior = df_global['Eficiencia_Riego'].iloc[-2] if len(df_global) > 1 else eficiencia_actual
    cambio_eficiencia = eficiencia_actual - eficiencia_anterior
    
    st.markdown(f"""
    <div class="metric-global-card">
        <div class="kpi-label">💧 Eficiencia Riego</div>
        <div class="kpi-number">{eficiencia_actual:.1f}%</div>
        <div class="kpi-change {'kpi-positive' if cambio_eficiencia > 0 else 'kpi-negative' if cambio_eficiencia < 0 else 'kpi-neutral'}">
            {cambio_eficiencia:+.1f}% vs anterior
        </div>
    </div>
    """, unsafe_allow_html=True)

# Tendencias históricas
st.markdown('<h2 class="section-title">📈 Tendencias Históricas</h2>', unsafe_allow_html=True)

# Gráfico de tendencias principales
fig_tendencias = make_subplots(
    rows=2, cols=2,
    subplot_titles=('🌡️ Evolución de Temperatura', '🌾 Rendimiento Agrícola', 
                   '💰 Ingresos Totales', '💧 Eficiencia de Riego'),
    vertical_spacing=0.1,
    horizontal_spacing=0.1
)

# Temperatura
fig_tendencias.add_trace(
    go.Scatter(x=df_global['Fecha'], y=df_global['Temperatura'], 
              name='Temperatura', line=dict(color='#e74c3c', width=3)),
    row=1, col=1
)

# Rendimiento
fig_tendencias.add_trace(
    go.Scatter(x=df_global['Fecha'], y=df_global['Rendimiento'], 
              name='Rendimiento', line=dict(color='#27ae60', width=3)),
    row=1, col=2
)

# Ingresos
fig_tendencias.add_trace(
    go.Scatter(x=df_global['Fecha'], y=df_global['Ingreso_Total'], 
              name='Ingresos', line=dict(color='#f39c12', width=3)),
    row=2, col=1
)

# Eficiencia
fig_tendencias.add_trace(
    go.Scatter(x=df_global['Fecha'], y=df_global['Eficiencia_Riego'], 
              name='Eficiencia', line=dict(color='#3498db', width=3)),
    row=2, col=2
)

fig_tendencias.update_layout(height=600, showlegend=False, 
                           title_text="📊 Tendencias Globales - Análisis de 5 Años")
fig_tendencias.update_xaxes(title_text="Fecha")
fig_tendencias.update_yaxes(title_text="Temperatura (°C)", row=1, col=1)
fig_tendencias.update_yaxes(title_text="Rendimiento (t/ha)", row=1, col=2)
fig_tendencias.update_yaxes(title_text="Ingresos (K$)", row=2, col=1)
fig_tendencias.update_yaxes(title_text="Eficiencia (%)", row=2, col=2)

st.plotly_chart(fig_tendencias, use_container_width=True)

# Análisis por categorías
st.markdown('<h2 class="section-title">📊 Análisis por Categorías</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Métricas meteorológicas
    st.markdown("#### 🌤️ Métricas Meteorológicas")
    
    df_meteo = df_global[['Fecha', 'Temperatura', 'Precipitacion', 'Humedad']].copy()
    
    fig_meteo = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Temperatura', 'Precipitación', 'Humedad'),
        vertical_spacing=0.05
    )
    
    fig_meteo.add_trace(
        go.Scatter(x=df_meteo['Fecha'], y=df_meteo['Temperatura'], 
                  name='Temperatura', line=dict(color='#e74c3c')),
        row=1, col=1
    )
    
    fig_meteo.add_trace(
        go.Bar(x=df_meteo['Fecha'], y=df_meteo['Precipitacion'], 
               name='Precipitación', marker_color='#3498db'),
        row=2, col=1
    )
    
    fig_meteo.add_trace(
        go.Scatter(x=df_meteo['Fecha'], y=df_meteo['Humedad'], 
                  name='Humedad', line=dict(color='#9b59b6')),
        row=3, col=1
    )
    
    fig_meteo.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_meteo, use_container_width=True)

with col2:
    # Métricas ambientales
    st.markdown("#### 🌍 Métricas Ambientales")
    
    fig_ambiental = make_subplots(
        rows=2, cols=1,
        subplot_titles=('CO₂ Atmosférico', 'Biodiversidad'),
        vertical_spacing=0.1
    )
    
    fig_ambiental.add_trace(
        go.Scatter(x=df_global['Fecha'], y=df_global['CO2'], 
                  name='CO₂', line=dict(color='#e67e22', width=3)),
        row=1, col=1
    )
    
    fig_ambiental.add_trace(
        go.Scatter(x=df_global['Fecha'], y=df_global['Biodiversidad'], 
                  name='Biodiversidad', line=dict(color='#27ae60', width=3)),
        row=2, col=1
    )
    
    fig_ambiental.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_ambiental, use_container_width=True)

# Análisis comparativo anual
st.markdown('<h2 class="section-title">📅 Análisis Comparativo Anual</h2>', unsafe_allow_html=True)

# Agrupar por año
df_anual = df_global.groupby('Año').agg({
    'Temperatura': 'mean',
    'Rendimiento': 'mean',
    'Ingreso_Total': 'sum',
    'Eficiencia_Riego': 'mean',
    'Biodiversidad': 'mean'
}).reset_index()

col1, col2 = st.columns(2)

with col1:
    # Comparación de años
    fig_comparacion = px.bar(df_anual, x='Año', y=['Temperatura', 'Rendimiento', 'Eficiencia_Riego'],
                            title='📊 Comparación Anual de Métricas Principales',
                            color_discrete_sequence=['#e74c3c', '#27ae60', '#3498db'])
    fig_comparacion.update_layout(height=400)
    st.plotly_chart(fig_comparacion, use_container_width=True)

with col2:
    # Tendencias de crecimiento
    fig_crecimiento = px.line(df_anual, x='Año', y='Ingreso_Total',
                             title='💰 Evolución de Ingresos Anuales',
                             line_shape='spline')
    fig_crecimiento.update_traces(line=dict(color='#f39c12', width=4))
    fig_crecimiento.update_layout(height=400)
    st.plotly_chart(fig_crecimiento, use_container_width=True)

# Resumen ejecutivo
st.markdown('<h2 class="section-title">📋 Resumen Ejecutivo</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📈 Tendencias Positivas")
    tendencias_positivas = [
        "🌾 Rendimiento agrícola en aumento",
        "💧 Mejora en eficiencia de riego",
        "💰 Crecimiento sostenido de ingresos",
        "📊 Calidad de productos mejorando"
    ]
    
    for tendencia in tendencias_positivas:
        st.success(tendencia)

with col2:
    st.markdown("#### ⚠️ Áreas de Atención")
    areas_atencion = [
        "🌡️ Tendencia al aumento de temperatura",
        "🌧️ Reducción en precipitaciones",
        "🌍 Pérdida gradual de biodiversidad",
        "💨 Aumento de CO₂ atmosférico"
    ]
    
    for area in areas_atencion:
        st.warning(area)

with col3:
    st.markdown("#### 🎯 Recomendaciones")
    recomendaciones = [
        "🔄 Implementar riego inteligente",
        "🌱 Adoptar prácticas sustentables",
        "📊 Monitorear indicadores ambientales",
        "💰 Diversificar fuentes de ingresos"
    ]
    
    for rec in recomendaciones:
        st.info(rec)

# Información del análisis global
st.markdown('<h2 class="section-title">ℹ️ Información del Análisis Global</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **📅 Período Analizado:** {periodo_global}
    **⏱️ Granularidad:** {granularidad}
    **📊 Tipo de Métrica:** {tipo_metrica}
    **🕐 Registros:** {len(df_global):,} mediciones
    """)

with col2:
    st.info(f"""
    **📈 Datos Generados:** {datetime.now().strftime("%H:%M:%S")}
    **🔄 Actualización:** Automática
    **📱 Optimizado:** Móvil
    **🎨 Diseño:** Profesional Global
    """)

with col3:
    st.info(f"""
    **🌡️ Temp. Promedio:** {df_global['Temperatura'].mean():.1f}°C
    **🌾 Rend. Promedio:** {df_global['Rendimiento'].mean():.1f} t/ha
    **💰 Ingreso Total:** ${df_global['Ingreso_Total'].sum():,.0f}K
    **💧 Eficiencia Promedio:** {df_global['Eficiencia_Riego'].mean():.1f}%
    """)

# Footer profesional
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px;">
    <p>📈 <strong>Sistema METGO</strong> - Dashboard Global de Métricas</p>
    <p>Análisis integral de 5 años con métricas globales y tendencias históricas</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
