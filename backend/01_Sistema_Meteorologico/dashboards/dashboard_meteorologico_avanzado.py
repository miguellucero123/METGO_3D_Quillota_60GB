#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Meteorológico Avanzado METGO 3D
Versión especializada para la carpeta dashboards
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuración de la página
st.set_page_config(
    page_title="METGO 3D - Dashboard Meteorológico Avanzado",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado mejorado
st.markdown("""
<style>
.main {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 0.5rem;
    color: white;
    margin: 0.5rem 0;
}
.alert-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    padding: 1rem;
    border-radius: 0.5rem;
    color: white;
    margin: 0.5rem 0;
}
.success-card {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    padding: 1rem;
    border-radius: 0.5rem;
    color: white;
    margin: 0.5rem 0;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: #f0f2f6;
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding-left: 20px;
    padding-right: 20px;
}
.stTabs [aria-selected="true"] {
    background-color: #ff6b6b;
    color: white;
}
</style>
""", unsafe_allow_html=True)

def generar_datos_meteorologicos_avanzados():
    """Generar datos meteorológicos avanzados y realistas para Quillota"""
    np.random.seed(42)
    
    # Generar 30 días de datos con variación estacional
    fechas = [datetime.now() - timedelta(days=i) for i in range(29, -1, -1)]
    
    datos = []
    for i, fecha in enumerate(fechas):
        # Variación estacional para Quillota (clima mediterráneo)
        dia_año = fecha.timetuple().tm_yday
        temp_base = 18 + 8 * np.sin(2 * np.pi * dia_año / 365)
        
        # Temperaturas con variación diurna
        temp_max = temp_base + np.random.normal(8, 3)
        temp_min = temp_base - np.random.normal(5, 2)
        temp_promedio = (temp_max + temp_min) / 2
        
        # Precipitación estacional (más en invierno)
        prob_precip = 0.4 if fecha.month in [5, 6, 7, 8] else 0.1
        precipitacion = np.random.exponential(8) if np.random.random() < prob_precip else 0
        
        # Otros parámetros con variación realista
        humedad = np.random.normal(75, 15)
        presion = np.random.normal(1013, 15)
        viento_velocidad = np.random.exponential(12)
        viento_direccion = np.random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
        cobertura_nubosa = np.random.normal(45, 25)
        
        # Índices adicionales
        indice_uv = np.random.normal(6, 2)  # Índice UV
        punto_rocio = temp_promedio - (100 - humedad) / 5
        sensacion_termica = temp_promedio + np.random.normal(0, 1)
        
        datos.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'hora': f"{np.random.randint(6, 18):02d}:00",
            'temperatura_max': round(temp_max, 1),
            'temperatura_min': round(temp_min, 1),
            'temperatura_promedio': round(temp_promedio, 1),
            'temperatura_sensacion': round(sensacion_termica, 1),
            'precipitacion': round(max(0, precipitacion), 1),
            'humedad_relativa': round(max(0, min(100, humedad)), 1),
            'presion_atmosferica': round(presion, 1),
            'viento_velocidad': round(max(0, viento_velocidad), 1),
            'viento_direccion': viento_direccion,
            'cobertura_nubosa': round(max(0, min(100, cobertura_nubosa)), 1),
            'indice_uv': round(max(0, min(11, indice_uv)), 1),
            'punto_rocio': round(punto_rocio, 1),
            'visibilidad': round(np.random.normal(15, 5), 1),
            'descripcion': 'Datos simulados para Quillota'
        })
    
    return pd.DataFrame(datos)

def crear_metricas_principales(df):
    """Crear métricas principales del dashboard"""
    if len(df) == 0:
        return
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        temp_actual = df['temperatura_promedio'].iloc[-1]
        temp_max = df['temperatura_max'].iloc[-1]
        temp_min = df['temperatura_min'].iloc[-1]
        
        st.metric(
            label="🌡️ Temperatura",
            value=f"{temp_actual:.1f}°C",
            delta=f"Máx: {temp_max:.1f}°C / Mín: {temp_min:.1f}°C"
        )
    
    with col2:
        precip_hoy = df['precipitacion'].iloc[-1]
        precip_total = df['precipitacion'].sum()
        
        st.metric(
            label="🌧️ Precipitación",
            value=f"{precip_hoy:.1f} mm",
            delta=f"Total: {precip_total:.1f} mm"
        )
    
    with col3:
        humedad = df['humedad_relativa'].iloc[-1]
        estado_humedad = "Confortable" if 40 <= humedad <= 60 else "Extrema"
        
        st.metric(
            label="💧 Humedad",
            value=f"{humedad:.1f}%",
            delta=estado_humedad
        )
    
    with col4:
        viento = df['viento_velocidad'].iloc[-1]
        direccion = df['viento_direccion'].iloc[-1]
        
        st.metric(
            label="💨 Viento",
            value=f"{viento:.1f} km/h",
            delta=direccion
        )
    
    with col5:
        uv = df['indice_uv'].iloc[-1]
        nivel_uv = "Alto" if uv > 6 else "Moderado" if uv > 3 else "Bajo"
        
        st.metric(
            label="☀️ Índice UV",
            value=f"{uv:.1f}",
            delta=nivel_uv
        )

def crear_grafico_temperaturas_avanzado(df):
    """Crear gráfico avanzado de temperaturas"""
    fig = go.Figure()
    
    # Área sombreada para rango de temperaturas
    fig.add_trace(go.Scatter(
        x=df['fecha'], y=df['temperatura_max'],
        fill=None, mode='lines', line_color='rgba(0,0,0,0)',
        showlegend=False, hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['fecha'], y=df['temperatura_min'],
        fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)',
        fillcolor='rgba(255, 182, 193, 0.3)',
        name='Rango de temperaturas', showlegend=True
    ))
    
    # Líneas de temperatura
    fig.add_trace(go.Scatter(
        x=df['fecha'], y=df['temperatura_max'],
        mode='lines+markers', name='Máxima',
        line=dict(color='red', width=3),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['fecha'], y=df['temperatura_min'],
        mode='lines+markers', name='Mínima',
        line=dict(color='blue', width=3),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['fecha'], y=df['temperatura_promedio'],
        mode='lines+markers', name='Promedio',
        line=dict(color='green', width=2, dash='dash'),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title='🌡️ Evolución de Temperaturas - Quillota',
        xaxis_title='Fecha',
        yaxis_title='Temperatura (°C)',
        hovermode='x unified',
        height=450,
        showlegend=True
    )
    
    return fig

def crear_grafico_precipitacion_avanzado(df):
    """Crear gráfico avanzado de precipitación"""
    fig = go.Figure()
    
    # Barras de precipitación con colores según intensidad
    colores = ['lightblue' if p < 5 else 'blue' if p < 15 else 'darkblue' for p in df['precipitacion']]
    
    fig.add_trace(go.Bar(
        x=df['fecha'], y=df['precipitacion'],
        marker=dict(color=colores),
        name='Precipitación',
        hovertemplate='<b>%{x}</b><br>Precipitación: %{y:.1f} mm<extra></extra>'
    ))
    
    # Línea de precipitación acumulada
    df_temp = df.copy()
    df_temp['precip_acumulada'] = df_temp['precipitacion'].cumsum()
    
    fig.add_trace(go.Scatter(
        x=df_temp['fecha'], y=df_temp['precip_acumulada'],
        mode='lines', name='Acumulada',
        line=dict(color='purple', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='🌧️ Precipitación Diaria y Acumulada',
        xaxis_title='Fecha',
        yaxis=dict(title='Precipitación Diaria (mm)', side='left'),
        yaxis2=dict(title='Precipitación Acumulada (mm)', side='right', overlaying='y'),
        height=400,
        hovermode='x unified'
    )
    
    return fig

def crear_grafico_viento_rosa(df):
    """Crear rosa de vientos"""
    # Contar frecuencias por dirección
    direcciones = df['viento_direccion'].value_counts()
    
    # Crear rosa de vientos
    fig = go.Figure()
    
    # Colores para cada dirección
    colores = px.colors.qualitative.Set3
    
    fig.add_trace(go.Bar(
        x=direcciones.index,
        y=direcciones.values,
        marker=dict(color=colores[:len(direcciones)]),
        name='Frecuencia de viento'
    ))
    
    fig.update_layout(
        title='💨 Rosa de Vientos - Distribución por Dirección',
        xaxis_title='Dirección',
        yaxis_title='Frecuencia (días)',
        height=350
    )
    
    return fig

def crear_grafico_humedad_presion(df):
    """Crear gráfico de humedad y presión"""
    fig = go.Figure()
    
    # Humedad
    fig.add_trace(go.Scatter(
        x=df['fecha'], y=df['humedad_relativa'],
        mode='lines+markers', name='Humedad Relativa (%)',
        line=dict(color='blue', width=2),
        yaxis='y'
    ))
    
    # Presión
    fig.add_trace(go.Scatter(
        x=df['fecha'], y=df['presion_atmosferica'],
        mode='lines+markers', name='Presión Atmosférica (hPa)',
        line=dict(color='red', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='💧 Humedad Relativa y Presión Atmosférica',
        xaxis_title='Fecha',
        yaxis=dict(title='Humedad Relativa (%)', side='left'),
        yaxis2=dict(title='Presión Atmosférica (hPa)', side='right', overlaying='y'),
        height=400,
        hovermode='x unified'
    )
    
    return fig

def crear_tabla_pronostico_detallado(df):
    """Crear tabla de pronóstico detallado"""
    # Últimos 7 días
    ultimos_datos = df.tail(7).copy()
    
    # Formatear para la tabla
    tabla_data = []
    for _, row in ultimos_datos.iterrows():
        # Determinar condiciones del clima
        if row['precipitacion'] > 10:
            condicion = "🌧️ Lluvia intensa"
        elif row['precipitacion'] > 0:
            condicion = "🌦️ Lluvia ligera"
        elif row['cobertura_nubosa'] > 70:
            condicion = "☁️ Nublado"
        elif row['cobertura_nubosa'] > 30:
            condicion = "⛅ Parcialmente nublado"
        else:
            condicion = "☀️ Despejado"
        
        tabla_data.append({
            'Fecha': row['fecha'],
            'T. Máx': f"{row['temperatura_max']:.1f}°C",
            'T. Mín': f"{row['temperatura_min']:.1f}°C",
            'Precip.': f"{row['precipitacion']:.1f} mm",
            'Humedad': f"{row['humedad_relativa']:.1f}%",
            'Presión': f"{row['presion_atmosferica']:.1f} hPa",
            'Viento': f"{row['viento_velocidad']:.1f} km/h",
            'Dirección': row['viento_direccion'],
            'UV': f"{row['indice_uv']:.1f}",
            'Condición': condicion
        })
    
    return pd.DataFrame(tabla_data)

def mostrar_alertas_meteorologicas(df):
    """Mostrar alertas meteorológicas"""
    if len(df) == 0:
        return
    
    alertas = []
    ultimo_dato = df.iloc[-1]
    
    # Alertas de temperatura
    if ultimo_dato['temperatura_max'] > 35:
        alertas.append(("🔴", "Temperatura muy alta", f"Temperatura máxima de {ultimo_dato['temperatura_max']:.1f}°C - Riesgo de estrés térmico"))
    elif ultimo_dato['temperatura_max'] > 30:
        alertas.append(("🟠", "Temperatura elevada", f"Temperatura máxima de {ultimo_dato['temperatura_max']:.1f}°C - Monitorear condiciones"))
    
    if ultimo_dato['temperatura_min'] < 5:
        alertas.append(("🔴", "Temperatura muy baja", f"Temperatura mínima de {ultimo_dato['temperatura_min']:.1f}°C - Riesgo de heladas"))
    
    # Alertas de precipitación
    if ultimo_dato['precipitacion'] > 20:
        alertas.append(("🔴", "Lluvia intensa", f"Precipitación de {ultimo_dato['precipitacion']:.1f} mm - Posible encharcamiento"))
    elif ultimo_dato['precipitacion'] > 10:
        alertas.append(("🟠", "Lluvia moderada", f"Precipitación de {ultimo_dato['precipitacion']:.1f} mm - Precauciones necesarias"))
    
    # Alertas de viento
    if ultimo_dato['viento_velocidad'] > 40:
        alertas.append(("🔴", "Viento fuerte", f"Velocidad del viento de {ultimo_dato['viento_velocidad']:.1f} km/h - Riesgo de daños"))
    elif ultimo_dato['viento_velocidad'] > 25:
        alertas.append(("🟠", "Viento moderado", f"Velocidad del viento de {ultimo_dato['viento_velocidad']:.1f} km/h - Precauciones"))
    
    # Alertas de humedad
    if ultimo_dato['humedad_relativa'] > 85:
        alertas.append(("🟠", "Alta humedad", f"Humedad relativa del {ultimo_dato['humedad_relativa']:.1f}% - Condiciones muy húmedas"))
    elif ultimo_dato['humedad_relativa'] < 25:
        alertas.append(("🟠", "Baja humedad", f"Humedad relativa del {ultimo_dato['humedad_relativa']:.1f}% - Condiciones muy secas"))
    
    # Alertas de índice UV
    if ultimo_dato['indice_uv'] > 8:
        alertas.append(("🔴", "Índice UV muy alto", f"Índice UV de {ultimo_dato['indice_uv']:.1f} - Protección solar extrema necesaria"))
    elif ultimo_dato['indice_uv'] > 6:
        alertas.append(("🟠", "Índice UV alto", f"Índice UV de {ultimo_dato['indice_uv']:.1f} - Protección solar recomendada"))
    
    # Mostrar alertas
    if alertas:
        st.subheader("🚨 Alertas Meteorológicas")
        for emoji, titulo, descripcion in alertas:
            if emoji == "🔴":
                st.error(f"{emoji} **{titulo}**: {descripcion}")
            else:
                st.warning(f"{emoji} **{titulo}**: {descripcion}")
    else:
        st.success("✅ **Condiciones meteorológicas normales** - No hay alertas activas")

def main():
    """Función principal del dashboard meteorológico avanzado"""
    
    st.title("🌤️ Dashboard Meteorológico Avanzado METGO 3D")
    st.markdown("### Sistema de Pronósticos y Análisis Climático para Quillota")
    st.markdown("---")
    
    # Generar datos
    with st.spinner("Cargando datos meteorológicos..."):
        df = generar_datos_meteorologicos_avanzados()
    
    # Sidebar con controles
    st.sidebar.header("🎛️ Panel de Control")
    
    # Selector de vista
    vista = st.sidebar.selectbox(
        "Seleccionar vista",
        ["📊 Dashboard Principal", "🌡️ Análisis de Temperaturas", "🌧️ Análisis de Precipitación", 
         "💨 Análisis de Viento", "📈 Tendencias", "🔍 Datos Detallados"]
    )
    
    # Filtros temporales
    st.sidebar.subheader("📅 Filtros Temporales")
    if len(df) > 0:
        df['fecha'] = pd.to_datetime(df['fecha'])
        fecha_inicio = st.sidebar.date_input("Fecha inicio", df['fecha'].min().date())
        fecha_fin = st.sidebar.date_input("Fecha fin", df['fecha'].max().date())
        
        # Filtrar datos
        df_filtrado = df[(df['fecha'].dt.date >= fecha_inicio) & (df['fecha'].dt.date <= fecha_fin)]
    else:
        df_filtrado = df
    
    # Información del sistema
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Información del Sistema")
    st.sidebar.info(f"📊 Registros: {len(df)}")
    st.sidebar.info(f"🕒 Última actualización: {datetime.now().strftime('%H:%M:%S')}")
    
    # Dashboard Principal
    if vista == "📊 Dashboard Principal":
        st.subheader("📊 Vista General")
        
        # Métricas principales
        crear_metricas_principales(df_filtrado)
        
        # Gráficos principales
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(crear_grafico_temperaturas_avanzado(df_filtrado), use_container_width=True)
        
        with col2:
            st.plotly_chart(crear_grafico_precipitacion_avanzado(df_filtrado), use_container_width=True)
        
        # Gráfico de humedad y presión
        st.plotly_chart(crear_grafico_humedad_presion(df_filtrado), use_container_width=True)
        
        # Alertas
        mostrar_alertas_meteorologicas(df_filtrado)
    
    elif vista == "🌡️ Análisis de Temperaturas":
        st.subheader("🌡️ Análisis Detallado de Temperaturas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Estadísticas de temperatura
            st.markdown("#### 📊 Estadísticas de Temperatura")
            temp_stats = {
                'Máxima registrada': f"{df_filtrado['temperatura_max'].max():.1f}°C",
                'Mínima registrada': f"{df_filtrado['temperatura_min'].min():.1f}°C",
                'Promedio general': f"{df_filtrado['temperatura_promedio'].mean():.1f}°C",
                'Amplitud térmica promedio': f"{df_filtrado['temperatura_max'].mean() - df_filtrado['temperatura_min'].mean():.1f}°C",
                'Días con temp > 30°C': f"{(df_filtrado['temperatura_max'] > 30).sum()} días",
                'Días con temp < 10°C': f"{(df_filtrado['temperatura_min'] < 10).sum()} días"
            }
            
            for key, value in temp_stats.items():
                st.metric(key, value)
        
        with col2:
            # Distribución de temperaturas
            fig_hist = px.histogram(
                df_filtrado, 
                x='temperatura_promedio',
                nbins=20,
                title='Distribución de Temperaturas Promedio',
                labels={'temperatura_promedio': 'Temperatura (°C)', 'count': 'Frecuencia'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        # Gráfico de temperaturas
        st.plotly_chart(crear_grafico_temperaturas_avanzado(df_filtrado), use_container_width=True)
    
    elif vista == "🌧️ Análisis de Precipitación":
        st.subheader("🌧️ Análisis Detallado de Precipitación")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Estadísticas de precipitación
            st.markdown("#### 📊 Estadísticas de Precipitación")
            precip_stats = {
                'Total acumulado': f"{df_filtrado['precipitacion'].sum():.1f} mm",
                'Días con lluvia': f"{(df_filtrado['precipitacion'] > 0).sum()} días",
                'Intensidad máxima': f"{df_filtrado['precipitacion'].max():.1f} mm/día",
                'Precipitación promedio': f"{df_filtrado['precipitacion'].mean():.1f} mm/día",
                'Lluvias intensas (>10mm)': f"{(df_filtrado['precipitacion'] > 10).sum()} días",
                'Días secos consecutivos': calcular_dias_secos_consecutivos(df_filtrado['precipitacion'])
            }
            
            for key, value in precip_stats.items():
                st.metric(key, value)
        
        with col2:
            # Gráfico de precipitación acumulada
            df_temp = df_filtrado.copy()
            df_temp['precip_acumulada'] = df_temp['precipitacion'].cumsum()
            
            fig_acum = px.area(
                df_temp, 
                x='fecha', 
                y='precip_acumulada',
                title='Precipitación Acumulada',
                labels={'precip_acumulada': 'Precipitación Acumulada (mm)'}
            )
            st.plotly_chart(fig_acum, use_container_width=True)
        
        # Gráfico de precipitación
        st.plotly_chart(crear_grafico_precipitacion_avanzado(df_filtrado), use_container_width=True)
    
    elif vista == "💨 Análisis de Viento":
        st.subheader("💨 Análisis Detallado de Viento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Estadísticas de viento
            st.markdown("#### 📊 Estadísticas de Viento")
            viento_stats = {
                'Velocidad promedio': f"{df_filtrado['viento_velocidad'].mean():.1f} km/h",
                'Velocidad máxima': f"{df_filtrado['viento_velocidad'].max():.1f} km/h",
                'Días ventosos (>20 km/h)': f"{(df_filtrado['viento_velocidad'] > 20).sum()} días",
                'Días con viento fuerte (>40 km/h)': f"{(df_filtrado['viento_velocidad'] > 40).sum()} días"
            }
            
            for key, value in viento_stats.items():
                st.metric(key, value)
        
        with col2:
            # Rosa de vientos
            st.plotly_chart(crear_grafico_viento_rosa(df_filtrado), use_container_width=True)
        
        # Gráfico de velocidad de viento
        fig_viento = px.line(
            df_filtrado, 
            x='fecha', 
            y='viento_velocidad',
            title='Evolución de la Velocidad del Viento',
            labels={'viento_velocidad': 'Velocidad (km/h)'}
        )
        st.plotly_chart(fig_viento, use_container_width=True)
    
    elif vista == "📈 Tendencias":
        st.subheader("📈 Análisis de Tendencias")
        
        if len(df_filtrado) > 1:
            # Calcular tendencias
            tendencia_temp = np.polyfit(range(len(df_filtrado)), df_filtrado['temperatura_promedio'], 1)[0]
            tendencia_precip = np.polyfit(range(len(df_filtrado)), df_filtrado['precipitacion'], 1)[0]
            tendencia_humedad = np.polyfit(range(len(df_filtrado)), df_filtrado['humedad_relativa'], 1)[0]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if tendencia_temp > 0:
                    st.success(f"📈 **Temperatura**: +{tendencia_temp:.3f}°C/día")
                else:
                    st.info(f"📉 **Temperatura**: {tendencia_temp:.3f}°C/día")
            
            with col2:
                if tendencia_precip > 0:
                    st.success(f"📈 **Precipitación**: +{tendencia_precip:.3f} mm/día")
                else:
                    st.info(f"📉 **Precipitación**: {tendencia_precip:.3f} mm/día")
            
            with col3:
                if tendencia_humedad > 0:
                    st.success(f"📈 **Humedad**: +{tendencia_humedad:.3f}%/día")
                else:
                    st.info(f"📉 **Humedad**: {tendencia_humedad:.3f}%/día")
        
        # Gráficos de tendencias
        col1, col2 = st.columns(2)
        
        with col1:
            fig_temp_trend = px.scatter(
                df_filtrado, 
                x='fecha', 
                y='temperatura_promedio',
                trendline="ols",
                title='Tendencia de Temperatura con Regresión Lineal'
            )
            st.plotly_chart(fig_temp_trend, use_container_width=True)
        
        with col2:
            fig_precip_trend = px.scatter(
                df_filtrado, 
                x='fecha', 
                y='precipitacion',
                trendline="ols",
                title='Tendencia de Precipitación con Regresión Lineal'
            )
            st.plotly_chart(fig_precip_trend, use_container_width=True)
    
    elif vista == "🔍 Datos Detallados":
        st.subheader("🔍 Datos Meteorológicos Detallados")
        
        # Tabla de pronóstico detallado
        st.markdown("#### 📊 Pronóstico Detallado (Últimos 7 días)")
        tabla_detallada = crear_tabla_pronostico_detallado(df_filtrado)
        st.dataframe(tabla_detallada, use_container_width=True, hide_index=True)
        
        # Tabla completa de datos
        st.markdown("#### 📋 Datos Completos")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        
        # Correlaciones
        if len(df_filtrado) > 1:
            st.markdown("#### 🔗 Correlaciones entre Variables")
            variables_numericas = df_filtrado.select_dtypes(include=[np.number]).columns
            if len(variables_numericas) > 1:
                correlaciones = df_filtrado[variables_numericas].corr()
                
                fig_corr = px.imshow(
                    correlaciones,
                    text_auto=True,
                    aspect="auto",
                    title="Matriz de Correlaciones"
                )
                st.plotly_chart(fig_corr, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("**METGO 3D - Sistema Meteorológico Avanzado**")
    st.markdown("*Dashboard especializado para análisis climático de Quillota*")

def calcular_dias_secos_consecutivos(precipitacion):
    """Calcular días secos consecutivos"""
    dias_secos = 0
    for precip in reversed(precipitacion):
        if precip == 0:
            dias_secos += 1
        else:
            break
    return f"{dias_secos} días"

if __name__ == "__main__":
    main()
