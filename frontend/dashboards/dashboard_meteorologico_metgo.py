import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from metgo.streamlit_theme import (
    bootstrap_dashboard,
    classify_weather_from_row,
    weather_scene_html,
    PLOTLY_CONFIG,
    plotly_layout,
)

def generar_datos_meteorologicos():
    """Genera datos meteorológicos simulados para Quillota"""
    np.random.seed(42)
    random.seed(42)
    
    # Generar 30 días de datos
    fechas = [datetime.now() - timedelta(days=i) for i in range(29, -1, -1)]
    
    datos = []
    for fecha in fechas:
        # Temperaturas con variación estacional
        temp_base = 20 + 5 * np.sin(2 * np.pi * fecha.timetuple().tm_yday / 365)
        temp_max = temp_base + np.random.normal(5, 2)
        temp_min = temp_base - np.random.normal(3, 1.5)
        
        # Precipitación (más probable en invierno)
        prob_precip = 0.3 if fecha.month in [5, 6, 7, 8] else 0.1
        precipitacion = np.random.exponential(5) if np.random.random() < prob_precip else 0
        
        # Otros parámetros
        humedad = np.random.normal(70, 10)
        presion = np.random.normal(1013, 10)
        viento_velocidad = np.random.exponential(8)
        viento_direccion = np.random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
        cobertura_nubosa = np.random.normal(40, 25)
        
        datos.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'temp_max': round(temp_max, 1),
            'temp_min': round(temp_min, 1),
            'temp_promedio': round((temp_max + temp_min) / 2, 1),
            'precipitacion': round(precipitacion, 1),
            'humedad_relativa': round(humedad, 1),
            'presion_atmosferica': round(presion, 1),
            'viento_velocidad': round(viento_velocidad, 1),
            'viento_direccion': viento_direccion,
            'cobertura_nubosa': round(max(0, min(100, cobertura_nubosa)), 1)
        })
    
    return pd.DataFrame(datos)

def crear_grafico_temperaturas(datos):
    """Crea gráfico de evolución de temperaturas"""
    fig = go.Figure()
    
    # Líneas de temperatura
    fig.add_trace(go.Scatter(
        x=datos['fecha'], y=datos['temp_max'],
        mode='lines+markers',
        name='Temp. Máxima',
        line=dict(color='red', width=3),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=datos['fecha'], y=datos['temp_min'],
        mode='lines+markers',
        name='Temp. Mínima',
        line=dict(color='blue', width=3),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=datos['fecha'], y=datos['temp_promedio'],
        mode='lines+markers',
        name='Temp. Promedio',
        line=dict(color='green', width=2, dash='dash'),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title='Evolución de Temperaturas - Quillota',
        xaxis_title='Fecha',
        yaxis_title='Temperatura (°C)',
        hovermode='x unified',
        height=400
    )
    
    return fig

def crear_grafico_precipitacion(datos):
    """Crea gráfico de precipitación"""
    fig = go.Figure()
    
    # Barras de precipitación
    fig.add_trace(go.Bar(
        x=datos['fecha'],
        y=datos['precipitacion'],
        name='Precipitación',
        marker=dict(
            color=datos['precipitacion'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="mm")
        )
    ))
    
    fig.update_layout(
        title='Precipitación Diaria - Quillota',
        xaxis_title='Fecha',
        yaxis_title='Precipitación (mm)',
        height=300
    )
    
    return fig

def crear_tabla_pronostico(datos):
    """Crea tabla con pronóstico detallado"""
    # Últimos 7 días
    ultimos_datos = datos.tail(7).copy()
    
    # Formatear para la tabla
    tabla_data = []
    for _, row in ultimos_datos.iterrows():
        tabla_data.append({
            'Fecha': row['fecha'],
            'T. Máx (°C)': row['temp_max'],
            'T. Mín (°C)': row['temp_min'],
            'Precip. (mm)': row['precipitacion'],
            'Humedad (%)': row['humedad_relativa'],
            'Presión (hPa)': row['presion_atmosferica'],
            'Viento (km/h)': row['viento_velocidad'],
            'Dirección': row['viento_direccion'],
            'Nubosidad (%)': row['cobertura_nubosa']
        })
    
    return pd.DataFrame(tabla_data)

def main():
    st.set_page_config(
        page_title="Sistema Meteorológico METGO",
        page_icon="🌤️",
        layout="wide",
    )

    bootstrap_dashboard(
        "Sistema Meteorológico METGO",
        "Pronósticos y datos climáticos · Quillota",
        module="meteo",
    )

    # Generar datos
    datos = generar_datos_meteorologicos()
    ult = datos.iloc[-1]
    cond = classify_weather_from_row(
        {
            "temperatura_min": ult["temp_min"],
            "precipitacion": ult["precipitacion"],
            "humedad_relativa": ult["humedad_relativa"],
            "cobertura_nubosa": ult["cobertura_nubosa"],
        }
    )
    st.markdown(weather_scene_html(cond), unsafe_allow_html=True)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🌡️ Temp. Actual",
            value=f"{datos.iloc[-1]['temp_promedio']:.1f}°C",
            delta=f"{datos.iloc[-1]['temp_max']:.1f}°C / {datos.iloc[-1]['temp_min']:.1f}°C"
        )
    
    with col2:
        st.metric(
            label="🌧️ Precip. Hoy",
            value=f"{datos.iloc[-1]['precipitacion']:.1f} mm",
            delta="Lluvia" if datos.iloc[-1]['precipitacion'] > 0 else "Sin lluvia"
        )
    
    with col3:
        st.metric(
            label="💧 Humedad",
            value=f"{datos.iloc[-1]['humedad_relativa']:.1f}%",
            delta="Confortable" if 40 <= datos.iloc[-1]['humedad_relativa'] <= 60 else "Extrema"
        )
    
    with col4:
        st.metric(
            label="💨 Viento",
            value=f"{datos.iloc[-1]['viento_velocidad']:.1f} km/h",
            delta=datos.iloc[-1]['viento_direccion']
        )
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(crear_grafico_temperaturas(datos), use_container_width=True)
    
    with col2:
        st.plotly_chart(crear_grafico_precipitacion(datos), use_container_width=True)
    
    # Tabla de pronóstico
    st.markdown("### 📊 Pronóstico Detallado (Últimos 7 días)")
    tabla_pronostico = crear_tabla_pronostico(datos)
    
    # Formatear tabla para mejor visualización
    st.dataframe(
        tabla_pronostico,
        use_container_width=True,
        hide_index=True
    )
    
    # Información adicional
    st.markdown("---")
    st.markdown("### 📈 Análisis Climático")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Temperaturas del Período:**")
        st.write(f"- Máxima registrada: {datos['temp_max'].max():.1f}°C")
        st.write(f"- Mínima registrada: {datos['temp_min'].min():.1f}°C")
        st.write(f"- Promedio general: {datos['temp_promedio'].mean():.1f}°C")
    
    with col2:
        st.markdown("**Precipitación del Período:**")
        st.write(f"- Total acumulado: {datos['precipitacion'].sum():.1f} mm")
        st.write(f"- Días con lluvia: {(datos['precipitacion'] > 0).sum()} días")
        st.write(f"- Intensidad máxima: {datos['precipitacion'].max():.1f} mm/día")
    
    # Información del sistema
    st.markdown("---")
    st.info("ℹ️ **Sistema Meteorológico METGO** - Datos simulados para demostración. Para datos reales, configurar conexión con APIs meteorológicas.")

if __name__ == "__main__":
    main()
