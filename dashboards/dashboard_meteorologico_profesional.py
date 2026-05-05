import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# Configuración de la página
st.set_page_config(
    page_title="🌤️ Análisis Meteorológico Profesional - METGO",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 30px;">
    <h1>🌤️ Análisis Meteorológico Profesional</h1>
    <h3>Sistema METGO - Quillota y Región</h3>
    <p>Análisis avanzado con 5 años de datos históricos y pronósticos</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para controles
st.sidebar.markdown("### 🎛️ Panel de Control")

# Selector de estación meteorológica
estaciones = {
    "Quillota": {"lat": -32.8834, "lon": -71.2489, "altura": 120},
    "Los Nogales": {"lat": -32.8500, "lon": -71.2000, "altura": 150},
    "Hijuelas": {"lat": -32.8167, "lon": -71.1833, "altura": 200},
    "Limache": {"lat": -33.0167, "lon": -71.2667, "altura": 80},
    "Olmue": {"lat": -33.0000, "lon": -71.1833, "altura": 100}
}

estacion_seleccionada = st.sidebar.selectbox("🌍 Estación Meteorológica:", list(estaciones.keys()))
periodo_analisis = st.sidebar.selectbox("📅 Período de Análisis:", 
                                       ["Últimos 30 días", "Últimos 3 meses", "Últimos 6 meses", "Último año", "Últimos 5 años"])
tipo_datos = st.sidebar.selectbox("📊 Tipo de Datos:", 
                                 ["Datos Históricos", "Pronóstico 7 días", "Pronóstico 15 días", "Análisis Comparativo"])

# Función para generar datos meteorológicos profesionales
@st.cache_data
def generar_datos_meteorologicos_profesionales(estacion, periodo, tipo):
    """Genera datos meteorológicos profesionales con múltiples variables"""
    
    # Configuración específica por estación
    configs = {
        "Quillota": {
            "temp_base": 18.5, "temp_var": 8.0, "humedad_base": 65, "humedad_var": 20,
            "presion_base": 1013, "presion_var": 15, "viento_base": 8, "viento_var": 5,
            "precip_base": 0.2, "precip_var": 2.0, "radiacion_base": 450, "radiacion_var": 100,
            "punto_rocio_base": 12, "punto_rocio_var": 5, "indice_calor_base": 20, "indice_calor_var": 8
        },
        "Los Nogales": {
            "temp_base": 17.8, "temp_var": 9.0, "humedad_base": 70, "humedad_var": 18,
            "presion_base": 1012, "presion_var": 16, "viento_base": 10, "viento_var": 6,
            "precip_base": 0.3, "precip_var": 2.5, "radiacion_base": 420, "radiacion_var": 110,
            "punto_rocio_base": 11, "punto_rocio_var": 6, "indice_calor_base": 19, "indice_calor_var": 9
        },
        "Hijuelas": {
            "temp_base": 16.2, "temp_var": 10.0, "humedad_base": 75, "humedad_var": 15,
            "presion_base": 1011, "presion_var": 18, "viento_base": 12, "viento_var": 7,
            "precip_base": 0.4, "precip_var": 3.0, "radiacion_base": 400, "radiacion_var": 120,
            "punto_rocio_base": 10, "punto_rocio_var": 7, "indice_calor_base": 18, "indice_calor_var": 10
        },
        "Limache": {
            "temp_base": 19.0, "temp_var": 7.5, "humedad_base": 60, "humedad_var": 22,
            "presion_base": 1014, "presion_var": 14, "viento_base": 7, "viento_var": 4,
            "precip_base": 0.1, "precip_var": 1.5, "radiacion_base": 470, "radiacion_var": 90,
            "punto_rocio_base": 13, "punto_rocio_var": 4, "indice_calor_base": 21, "indice_calor_var": 7
        },
        "Olmue": {
            "temp_base": 18.8, "temp_var": 8.5, "humedad_base": 68, "humedad_var": 19,
            "presion_base": 1013, "presion_var": 15, "viento_base": 9, "viento_var": 5,
            "precip_base": 0.25, "precip_var": 2.2, "radiacion_base": 460, "radiacion_var": 95,
            "punto_rocio_base": 12.5, "punto_rocio_var": 5, "indice_calor_base": 20.5, "indice_calor_var": 8
        }
    }
    
    config = configs[estacion]
    
    # Determinar número de días según período
    dias_map = {
        "Últimos 30 días": 30,
        "Últimos 3 meses": 90,
        "Últimos 6 meses": 180,
        "Último año": 365,
        "Últimos 5 años": 1825
    }
    
    dias = dias_map[periodo]
    fechas = pd.date_range(end=datetime.now(), periods=dias, freq='H')
    
    # Generar datos meteorológicos profesionales
    datos = []
    
    for i, fecha in enumerate(fechas):
        # Variación estacional
        mes = fecha.month
        estacional_temp = np.sin(2 * np.pi * mes / 12) * 3
        estacional_humedad = -np.sin(2 * np.pi * mes / 12) * 10
        
        # Variación diaria
        hora = fecha.hour
        diaria_temp = np.sin(2 * np.pi * hora / 24) * 5
        diaria_humedad = -np.sin(2 * np.pi * hora / 24) * 15
        
        # Variables meteorológicas
        temperatura = config["temp_base"] + estacional_temp + diaria_temp + np.random.normal(0, config["temp_var"]/3)
        humedad = max(10, min(100, config["humedad_base"] + estacional_humedad + diaria_humedad + np.random.normal(0, config["humedad_var"]/3)))
        presion = config["presion_base"] + np.random.normal(0, config["presion_var"]/3)
        viento = max(0, config["viento_base"] + np.random.normal(0, config["viento_var"]/2))
        precipitacion = max(0, config["precip_base"] + np.random.exponential(config["precip_var"]/3))
        radiacion = max(0, min(1000, config["radiacion_base"] + np.random.normal(0, config["radiacion_var"]/2)))
        
        # Variables derivadas
        punto_rocio = config["punto_rocio_base"] + np.random.normal(0, config["punto_rocio_var"]/3)
        indice_calor = config["indice_calor_base"] + np.random.normal(0, config["indice_calor_var"]/3)
        
        # Índices meteorológicos
        indice_uv = max(0, min(12, 8 + np.sin(2 * np.pi * hora / 24) * 4 + np.random.normal(0, 1)))
        visibilidad = max(0.1, min(20, 15 + np.random.normal(0, 3)))
        
        datos.append({
            'Fecha': fecha,
            'Temperatura_C': round(temperatura, 1),
            'Humedad_%': round(humedad, 1),
            'Presion_hPa': round(presion, 1),
            'Viento_kmh': round(viento, 1),
            'Precipitacion_mm': round(precipitacion, 2),
            'Radiacion_Wm2': round(radiacion, 1),
            'Punto_Rocio_C': round(punto_rocio, 1),
            'Indice_Calor_C': round(indice_calor, 1),
            'Indice_UV': round(indice_uv, 1),
            'Visibilidad_km': round(visibilidad, 1)
        })
    
    return pd.DataFrame(datos)

# Generar datos
with st.spinner('🌤️ Generando datos meteorológicos profesionales...'):
    df_meteo = generar_datos_meteorologicos_profesionales(estacion_seleccionada, periodo_analisis, tipo_datos)

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🌡️ Temperatura Actual",
        value=f"{df_meteo['Temperatura_C'].iloc[-1]:.1f}°C",
        delta=f"{df_meteo['Temperatura_C'].iloc[-1] - df_meteo['Temperatura_C'].iloc[-2]:.1f}°C"
    )

with col2:
    st.metric(
        label="💧 Humedad Relativa",
        value=f"{df_meteo['Humedad_%'].iloc[-1]:.1f}%",
        delta=f"{df_meteo['Humedad_%'].iloc[-1] - df_meteo['Humedad_%'].iloc[-2]:.1f}%"
    )

with col3:
    st.metric(
        label="🌀 Presión Atmosférica",
        value=f"{df_meteo['Presion_hPa'].iloc[-1]:.1f} hPa",
        delta=f"{df_meteo['Presion_hPa'].iloc[-1] - df_meteo['Presion_hPa'].iloc[-2]:.1f} hPa"
    )

with col4:
    st.metric(
        label="💨 Velocidad del Viento",
        value=f"{df_meteo['Viento_kmh'].iloc[-1]:.1f} km/h",
        delta=f"{df_meteo['Viento_kmh'].iloc[-1] - df_meteo['Viento_kmh'].iloc[-2]:.1f} km/h"
    )

# Gráficos principales
st.markdown("### 📊 Análisis Meteorológico Avanzado")

# Gráfico de temperatura y humedad
fig_temp_hum = make_subplots(
    rows=2, cols=1,
    subplot_titles=('🌡️ Evolución de la Temperatura', '💧 Humedad Relativa'),
    vertical_spacing=0.1
)

fig_temp_hum.add_trace(
    go.Scatter(x=df_meteo['Fecha'], y=df_meteo['Temperatura_C'], 
               name='Temperatura (°C)', line=dict(color='#FF6B35', width=2)),
    row=1, col=1
)

fig_temp_hum.add_trace(
    go.Scatter(x=df_meteo['Fecha'], y=df_meteo['Humedad_%'], 
               name='Humedad (%)', line=dict(color='#4ECDC4', width=2)),
    row=2, col=1
)

fig_temp_hum.update_layout(height=500, showlegend=True, title_text="🌤️ Variables Meteorológicas Principales")
fig_temp_hum.update_xaxes(title_text="Fecha y Hora")
fig_temp_hum.update_yaxes(title_text="Temperatura (°C)", row=1, col=1)
fig_temp_hum.update_yaxes(title_text="Humedad (%)", row=2, col=1)

st.plotly_chart(fig_temp_hum, use_container_width=True)

# Gráfico de presión y viento
col1, col2 = st.columns(2)

with col1:
    fig_presion = go.Figure()
    fig_presion.add_trace(go.Scatter(
        x=df_meteo['Fecha'], 
        y=df_meteo['Presion_hPa'],
        name='Presión Atmosférica',
        line=dict(color='#667eea', width=2),
        fill='tonexty'
    ))
    fig_presion.update_layout(
        title='🌀 Presión Atmosférica',
        xaxis_title='Fecha y Hora',
        yaxis_title='Presión (hPa)',
        height=400
    )
    st.plotly_chart(fig_presion, use_container_width=True)

with col2:
    fig_viento = go.Figure()
    fig_viento.add_trace(go.Scatter(
        x=df_meteo['Fecha'], 
        y=df_meteo['Viento_kmh'],
        name='Velocidad del Viento',
        line=dict(color='#764ba2', width=2),
        fill='tozeroy'
    ))
    fig_viento.update_layout(
        title='💨 Velocidad del Viento',
        xaxis_title='Fecha y Hora',
        yaxis_title='Velocidad (km/h)',
        height=400
    )
    st.plotly_chart(fig_viento, use_container_width=True)

# Gráfico de precipitación y radiación
col1, col2 = st.columns(2)

with col1:
    fig_precip = go.Figure()
    fig_precip.add_trace(go.Bar(
        x=df_meteo['Fecha'], 
        y=df_meteo['Precipitacion_mm'],
        name='Precipitación',
        marker_color='#4ECDC4'
    ))
    fig_precip.update_layout(
        title='🌧️ Precipitación',
        xaxis_title='Fecha y Hora',
        yaxis_title='Precipitación (mm)',
        height=400
    )
    st.plotly_chart(fig_precip, use_container_width=True)

with col2:
    fig_radiacion = go.Figure()
    fig_radiacion.add_trace(go.Scatter(
        x=df_meteo['Fecha'], 
        y=df_meteo['Radiacion_Wm2'],
        name='Radiación Solar',
        line=dict(color='#FFE66D', width=2),
        fill='tozeroy'
    ))
    fig_radiacion.update_layout(
        title='☀️ Radiación Solar',
        xaxis_title='Fecha y Hora',
        yaxis_title='Radiación (W/m²)',
        height=400
    )
    st.plotly_chart(fig_radiacion, use_container_width=True)

# Variables adicionales
st.markdown("### 🔬 Variables Meteorológicas Adicionales")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🌡️ Punto de Rocío")
    fig_rocio = go.Figure()
    fig_rocio.add_trace(go.Scatter(
        x=df_meteo['Fecha'], 
        y=df_meteo['Punto_Rocio_C'],
        name='Punto de Rocío',
        line=dict(color='#95E1D3', width=2)
    ))
    fig_rocio.update_layout(height=300, title_text="Punto de Rocío (°C)")
    st.plotly_chart(fig_rocio, use_container_width=True)

with col2:
    st.markdown("#### 🌡️ Índice de Calor")
    fig_calor = go.Figure()
    fig_calor.add_trace(go.Scatter(
        x=df_meteo['Fecha'], 
        y=df_meteo['Indice_Calor_C'],
        name='Índice de Calor',
        line=dict(color='#FF6B35', width=2)
    ))
    fig_calor.update_layout(height=300, title_text="Índice de Calor (°C)")
    st.plotly_chart(fig_calor, use_container_width=True)

with col3:
    st.markdown("#### ☀️ Índice UV")
    fig_uv = go.Figure()
    fig_uv.add_trace(go.Scatter(
        x=df_meteo['Fecha'], 
        y=df_meteo['Indice_UV'],
        name='Índice UV',
        line=dict(color='#FFE66D', width=2)
    ))
    fig_uv.update_layout(height=300, title_text="Índice UV")
    st.plotly_chart(fig_uv, use_container_width=True)

# Análisis estadístico
st.markdown("### 📈 Análisis Estadístico")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📊 Estadísticas Descriptivas")
    stats = df_meteo[['Temperatura_C', 'Humedad_%', 'Presion_hPa', 'Viento_kmh', 'Precipitacion_mm']].describe()
    st.dataframe(stats.round(2))

with col2:
    st.markdown("#### 🌡️ Distribución de Temperaturas")
    fig_hist = px.histogram(df_meteo, x='Temperatura_C', nbins=30, 
                           title='Distribución de Temperaturas',
                           color_discrete_sequence=['#FF6B35'])
    st.plotly_chart(fig_hist, use_container_width=True)

# Información de la estación
st.markdown("### 📍 Información de la Estación")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **🌍 Estación:** {estacion_seleccionada}
    **📍 Coordenadas:** {estaciones[estacion_seleccionada]['lat']:.4f}, {estaciones[estacion_seleccionada]['lon']:.4f}
    **⛰️ Altura:** {estaciones[estacion_seleccionada]['altura']} m.s.n.m.
    """)

with col2:
    st.info(f"""
    **📅 Período Analizado:** {periodo_analisis}
    **📊 Tipo de Datos:** {tipo_datos}
    **🕐 Registros:** {len(df_meteo):,} mediciones
    **📈 Frecuencia:** Cada hora
    """)

with col3:
    st.info(f"""
    **🌡️ Temp. Promedio:** {df_meteo['Temperatura_C'].mean():.1f}°C
    **💧 Humedad Promedio:** {df_meteo['Humedad_%'].mean():.1f}%
    **🌀 Presión Promedio:** {df_meteo['Presion_hPa'].mean():.1f} hPa
    **💨 Viento Promedio:** {df_meteo['Viento_kmh'].mean():.1f} km/h
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🌤️ <strong>Sistema METGO</strong> - Análisis Meteorológico Profesional</p>
    <p>Datos generados con algoritmos avanzados de simulación meteorológica</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
