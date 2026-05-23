#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutar Visualizaciones METGO_3D
Script para ejecutar las visualizaciones del dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configurar página
st.set_page_config(
    page_title="METGO_3D - Visualizaciones Avanzadas",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de colores específica para Quillota
COLORS_QUILLOTA = {
    'primary': '#2E7D32',      # Verde oscuro (agricultura)
    'secondary': '#4CAF50',     # Verde claro
    'accent': '#81C784',        # Verde suave
    'temperature_hot': '#FF5722',  # Rojo para calor
    'temperature_cold': '#2196F3', # Azul para frío
    'precipitation': '#03A9F4',    # Azul lluvia
    'wind': '#9C27B0',            # Púrpura viento
    'humidity': '#00BCD4',        # Cian humedad
    'alert': '#FF9800',           # Naranja alerta
    'danger': '#F44336',          # Rojo peligro
    'success': '#4CAF50',         # Verde éxito
    'warning': '#FFC107',         # Amarillo advertencia
    'info': '#17A2B8'             # Azul información
}

def generar_datos_prueba():
    """Generar datos de prueba para las visualizaciones"""
    
    # Crear rango de fechas para el último año
    fecha_inicio = datetime.now() - timedelta(days=365)
    fechas = pd.date_range(start=fecha_inicio, end=datetime.now(), freq='D')
    
    # Generar datos meteorológicos simulados
    np.random.seed(42)  # Para reproducibilidad
    
    datos = pd.DataFrame({
        'fecha': fechas,
        'temperatura_max': 25 + 10 * np.sin(np.arange(len(fechas)) * 2 * np.pi / 365) + np.random.normal(0, 2, len(fechas)),
        'temperatura_min': 15 + 8 * np.sin(np.arange(len(fechas)) * 2 * np.pi / 365) + np.random.normal(0, 2, len(fechas)),
        'humedad_relativa': 60 + 20 * np.sin(np.arange(len(fechas)) * 2 * np.pi / 365 + np.pi) + np.random.normal(0, 5, len(fechas)),
        'precipitacion': np.random.exponential(2, len(fechas)) * (np.random.random(len(fechas)) < 0.2),
        'velocidad_viento': 10 + 5 * np.sin(np.arange(len(fechas)) * 2 * np.pi / 365) + np.random.normal(0, 2, len(fechas)),
        'presion_atmosferica': 1013 + 10 * np.sin(np.arange(len(fechas)) * 2 * np.pi / 365) + np.random.normal(0, 2, len(fechas)),
        'radiacion_solar': 20 + 10 * np.sin(np.arange(len(fechas)) * 2 * np.pi / 365) + np.random.normal(0, 3, len(fechas))
    })
    
    # Calcular variables derivadas
    datos['temperatura_promedio'] = (datos['temperatura_max'] + datos['temperatura_min']) / 2
    datos['amplitud_termica'] = datos['temperatura_max'] - datos['temperatura_min']
    datos['mes'] = datos['fecha'].dt.month
    datos['estacion'] = datos['mes'].map({
        12: 'Verano', 1: 'Verano', 2: 'Verano',
        3: 'Otoño', 4: 'Otoño', 5: 'Otoño',
        6: 'Invierno', 7: 'Invierno', 8: 'Invierno',
        9: 'Primavera', 10: 'Primavera', 11: 'Primavera'
    })
    
    # Asegurar valores realistas
    datos['humedad_relativa'] = datos['humedad_relativa'].clip(0, 100)
    datos['velocidad_viento'] = datos['velocidad_viento'].clip(0, 50)
    datos['precipitacion'] = datos['precipitacion'].clip(0, 100)
    
    return datos

def crear_dashboard_temperaturas(datos):
    """Crear dashboard de temperaturas"""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('🌡️ Dashboard de Temperaturas - Quillota', fontsize=16, fontweight='bold')
    
    # 1. Evolución temporal
    ax1 = axes[0, 0]
    ax1.plot(datos['fecha'], datos['temperatura_max'], 
             color=COLORS_QUILLOTA['temperature_hot'], linewidth=2, label='Máxima')
    ax1.plot(datos['fecha'], datos['temperatura_min'], 
             color=COLORS_QUILLOTA['temperature_cold'], linewidth=2, label='Mínima')
    ax1.plot(datos['fecha'], datos['temperatura_promedio'], 
             color=COLORS_QUILLOTA['primary'], linewidth=2, label='Promedio')
    
    ax1.set_title('Evolución Temporal de Temperaturas')
    ax1.set_xlabel('Fecha')
    ax1.set_ylabel('Temperatura (°C)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Distribución
    ax2 = axes[0, 1]
    ax2.hist(datos['temperatura_max'], bins=20, alpha=0.7, 
             color=COLORS_QUILLOTA['temperature_hot'], label='Máxima')
    ax2.hist(datos['temperatura_min'], bins=20, alpha=0.7, 
             color=COLORS_QUILLOTA['temperature_cold'], label='Mínima')
    ax2.set_title('Distribución de Temperaturas')
    ax2.set_xlabel('Temperatura (°C)')
    ax2.set_ylabel('Frecuencia')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Amplitud térmica mensual
    ax3 = axes[1, 0]
    amplitud_mensual = datos.groupby('mes')['amplitud_termica'].mean()
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
             'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    bars = ax3.bar(range(1, 13), amplitud_mensual, 
                   color=COLORS_QUILLOTA['accent'], alpha=0.8)
    ax3.set_title('Amplitud Térmica Promedio por Mes')
    ax3.set_xlabel('Mes')
    ax3.set_ylabel('Amplitud Térmica (°C)')
    ax3.set_xticks(range(1, 13))
    ax3.set_xticklabels(meses)
    ax3.grid(True, alpha=0.3)
    
    # 4. Box plot por estación
    ax4 = axes[1, 1]
    datos_box = []
    etiquetas_box = []
    
    for estacion in datos['estacion'].unique():
        datos_estacion = datos[datos['estacion'] == estacion]['temperatura_promedio']
        datos_box.append(datos_estacion)
        etiquetas_box.append(estacion)
    
    bp = ax4.boxplot(datos_box, labels=etiquetas_box, patch_artist=True)
    colors_box = [COLORS_QUILLOTA['primary'], COLORS_QUILLOTA['secondary'], 
                  COLORS_QUILLOTA['accent'], COLORS_QUILLOTA['info']]
    
    for patch, color in zip(bp['boxes'], colors_box):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax4.set_title('Distribución de Temperatura por Estación')
    ax4.set_xlabel('Estación')
    ax4.set_ylabel('Temperatura Promedio (°C)')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def crear_dashboard_precipitacion(datos):
    """Crear dashboard de precipitación"""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('🌧️ Dashboard de Precipitación - Quillota', fontsize=16, fontweight='bold')
    
    # 1. Evolución temporal
    ax1 = axes[0, 0]
    bars = ax1.bar(datos['fecha'], datos['precipitacion'], 
                   color=COLORS_QUILLOTA['precipitation'], alpha=0.7, width=1)
    
    # Resaltar días con lluvia intensa
    lluvia_intensa = datos['precipitacion'] >= 20
    if lluvia_intensa.any():
        ax1.bar(datos[lluvia_intensa]['fecha'], 
               datos[lluvia_intensa]['precipitacion'],
               color=COLORS_QUILLOTA['danger'], alpha=0.8, width=1)
    
    ax1.set_title('Evolución Temporal de Precipitación')
    ax1.set_xlabel('Fecha')
    ax1.set_ylabel('Precipitación (mm)')
    ax1.grid(True, alpha=0.3)
    
    # 2. Precipitación acumulada mensual
    ax2 = axes[0, 1]
    precip_mensual = datos.groupby('mes')['precipitacion'].sum()
    
    # Definir meses para el gráfico
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
             'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    bars2 = ax2.bar(range(1, 13), precip_mensual, 
                    color=COLORS_QUILLOTA['precipitation'], alpha=0.8)
    ax2.set_title('Precipitación Acumulada por Mes')
    ax2.set_xlabel('Mes')
    ax2.set_ylabel('Precipitación (mm)')
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(meses)
    ax2.grid(True, alpha=0.3)
    
    # 3. Distribución de días con/sin lluvia
    ax3 = axes[1, 0]
    dias_con_lluvia = (datos['precipitacion'] > 0).sum()
    dias_sin_lluvia = len(datos) - dias_con_lluvia
    
    sizes = [dias_con_lluvia, dias_sin_lluvia]
    labels = [f'Con lluvia\n({dias_con_lluvia} días)', 
              f'Sin lluvia\n({dias_sin_lluvia} días)']
    colors = [COLORS_QUILLOTA['precipitation'], COLORS_QUILLOTA['secondary']]
    
    wedges, texts, autotexts = ax3.pie(sizes, labels=labels, colors=colors, 
                                       autopct='%1.1f%%', startangle=90)
    ax3.set_title('Distribución de Días con/sin Lluvia')
    
    # 4. Intensidad de lluvia por estación
    ax4 = axes[1, 1]
    intensidad_estacional = datos.groupby('estacion').agg({
        'precipitacion': ['mean', 'max']
    }).round(2)
    
    estaciones = intensidad_estacional.index
    intensidad_promedio = intensidad_estacional[('precipitacion', 'mean')]
    intensidad_maxima = intensidad_estacional[('precipitacion', 'max')]
    
    x = range(len(estaciones))
    width = 0.35
    
    bars1 = ax4.bar([i - width/2 for i in x], intensidad_promedio, 
                    width, label='Promedio', color=COLORS_QUILLOTA['precipitation'], alpha=0.7)
    bars2 = ax4.bar([i + width/2 for i in x], intensidad_maxima, 
                    width, label='Máxima', color=COLORS_QUILLOTA['danger'], alpha=0.7)
    
    ax4.set_title('Intensidad de Lluvia por Estación')
    ax4.set_xlabel('Estación')
    ax4.set_ylabel('Precipitación (mm)')
    ax4.set_xticks(x)
    ax4.set_xticklabels(estaciones)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def crear_dashboard_interactivo_plotly(datos):
    """Crear dashboard interactivo con Plotly"""
    
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=('Temperaturas', 'Precipitación', 
                       'Humedad Relativa', 'Velocidad de Viento',
                       'Presión Atmosférica', 'Radiación Solar'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. Temperaturas
    fig.add_trace(
        go.Scatter(x=datos['fecha'], y=datos['temperatura_max'],
                  name='Temp. Máxima', line=dict(color='red', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=datos['fecha'], y=datos['temperatura_min'],
                  name='Temp. Mínima', line=dict(color='blue', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=datos['fecha'], y=datos['temperatura_promedio'],
                  name='Temp. Promedio', line=dict(color='green', width=2)),
        row=1, col=1
    )
    
    # 2. Precipitación
    fig.add_trace(
        go.Bar(x=datos['fecha'], y=datos['precipitacion'],
               name='Precipitación', marker_color='lightblue'),
        row=1, col=2
    )
    
    # 3. Humedad relativa
    fig.add_trace(
        go.Scatter(x=datos['fecha'], y=datos['humedad_relativa'],
                  name='Humedad', line=dict(color='cyan', width=2)),
        row=2, col=1
    )
    
    # 4. Velocidad de viento
    fig.add_trace(
        go.Scatter(x=datos['fecha'], y=datos['velocidad_viento'],
                  name='Viento', line=dict(color='purple', width=2)),
        row=2, col=2
    )
    
    # 5. Presión atmosférica
    fig.add_trace(
        go.Scatter(x=datos['fecha'], y=datos['presion_atmosferica'],
                  name='Presión', line=dict(color='orange', width=2)),
        row=3, col=1
    )
    
    # 6. Radiación solar
    fig.add_trace(
        go.Scatter(x=datos['fecha'], y=datos['radiacion_solar'],
                  name='Radiación', line=dict(color='yellow', width=2)),
        row=3, col=2
    )
    
    # Actualizar layout
    fig.update_layout(
        title_text='📊 Dashboard Interactivo - Quillota',
        title_x=0.5,
        height=800,
        showlegend=True,
        template="plotly_white"
    )
    
    return fig

def main():
    """Función principal de Streamlit"""
    
    # Título principal
    st.title("🌾 METGO_3D - Visualizaciones Avanzadas")
    st.markdown("### Sistema Meteorológico Agrícola Quillota")
    
    # Sidebar para controles
    st.sidebar.header("🎛️ Controles del Dashboard")
    
    # Generar datos de prueba
    if st.sidebar.button("🔄 Generar Nuevos Datos"):
        st.cache_data.clear()
    
    @st.cache_data
    def cargar_datos():
        return generar_datos_prueba()
    
    datos = cargar_datos()
    
    # Mostrar información básica
    st.sidebar.markdown("### 📊 Información de los Datos")
    st.sidebar.metric("📅 Período", f"{len(datos)} días")
    st.sidebar.metric("🌡️ Temp. Promedio", f"{datos['temperatura_promedio'].mean():.1f}°C")
    st.sidebar.metric("🌧️ Precipitación Total", f"{datos['precipitacion'].sum():.1f} mm")
    st.sidebar.metric("💧 Humedad Promedio", f"{datos['humedad_relativa'].mean():.0f}%")
    
    # Selección de visualizaciones
    st.sidebar.header("📈 Visualizaciones")
    
    opciones = st.sidebar.multiselect(
        "Seleccionar dashboards:",
        ["🌡️ Temperaturas", "🌧️ Precipitación", "📊 Dashboard Interactivo"],
        default=["🌡️ Temperaturas", "🌧️ Precipitación", "📊 Dashboard Interactivo"]
    )
    
    # Mostrar visualizaciones seleccionadas
    if "🌡️ Temperaturas" in opciones:
        st.header("🌡️ Dashboard de Temperaturas")
        
        with st.spinner("Generando dashboard de temperaturas..."):
            fig_temp = crear_dashboard_temperaturas(datos)
            st.pyplot(fig_temp)
        
        # Métricas de temperatura
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌡️ Temp. Máxima", f"{datos['temperatura_max'].max():.1f}°C")
        with col2:
            st.metric("🌡️ Temp. Mínima", f"{datos['temperatura_min'].min():.1f}°C")
        with col3:
            st.metric("🌡️ Temp. Promedio", f"{datos['temperatura_promedio'].mean():.1f}°C")
        with col4:
            st.metric("🌡️ Amplitud Térmica", f"{datos['amplitud_termica'].mean():.1f}°C")
    
    if "🌧️ Precipitación" in opciones:
        st.header("🌧️ Dashboard de Precipitación")
        
        with st.spinner("Generando dashboard de precipitación..."):
            fig_precip = crear_dashboard_precipitacion(datos)
            st.pyplot(fig_precip)
        
        # Métricas de precipitación
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌧️ Precipitación Total", f"{datos['precipitacion'].sum():.1f} mm")
        with col2:
            st.metric("🌧️ Días con Lluvia", f"{(datos['precipitacion'] > 0).sum()}")
        with col3:
            st.metric("🌧️ Precipitación Máxima", f"{datos['precipitacion'].max():.1f} mm")
        with col4:
            st.metric("🌧️ Precipitación Promedio", f"{datos['precipitacion'].mean():.2f} mm/día")
    
    if "📊 Dashboard Interactivo" in opciones:
        st.header("📊 Dashboard Interactivo con Plotly")
        
        with st.spinner("Generando dashboard interactivo..."):
            fig_interactivo = crear_dashboard_interactivo_plotly(datos)
            st.plotly_chart(fig_interactivo, use_container_width=True)
    
    # Información adicional
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Información")
    st.sidebar.info("""
    **METGO_3D - Sistema Meteorológico Agrícola**
    
    Este dashboard muestra visualizaciones avanzadas de datos meteorológicos para la región de Quillota.
    
    **Características:**
    - Datos simulados realistas
    - Visualizaciones interactivas
    - Análisis estacional
    - Métricas agrícolas
    """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            🌾 METGO_3D - Sistema Meteorológico Agrícola Quillota | 
            Desarrollado para análisis agroclimático avanzado
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
