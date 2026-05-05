#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Simple METGO_3D
Dashboard simplificado que funciona correctamente
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configurar página
st.set_page_config(
    page_title="METGO_3D - Dashboard Simple",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

def generar_datos_prueba():
    """Generar datos de prueba simples"""
    
    # Crear rango de fechas para el último mes
    fecha_inicio = datetime.now() - timedelta(days=30)
    fechas = pd.date_range(start=fecha_inicio, end=datetime.now(), freq='D')
    
    # Generar datos meteorológicos simulados
    np.random.seed(42)
    
    datos = pd.DataFrame({
        'fecha': fechas,
        'temperatura_max': 25 + 5 * np.sin(np.arange(len(fechas)) * 2 * np.pi / 30) + np.random.normal(0, 2, len(fechas)),
        'temperatura_min': 15 + 3 * np.sin(np.arange(len(fechas)) * 2 * np.pi / 30) + np.random.normal(0, 1.5, len(fechas)),
        'humedad_relativa': 60 + 15 * np.sin(np.arange(len(fechas)) * 2 * np.pi / 30 + np.pi) + np.random.normal(0, 5, len(fechas)),
        'precipitacion': np.random.exponential(1, len(fechas)) * (np.random.random(len(fechas)) < 0.3),
        'velocidad_viento': 10 + 3 * np.sin(np.arange(len(fechas)) * 2 * np.pi / 30) + np.random.normal(0, 2, len(fechas))
    })
    
    # Calcular variables derivadas
    datos['temperatura_promedio'] = (datos['temperatura_max'] + datos['temperatura_min']) / 2
    datos['amplitud_termica'] = datos['temperatura_max'] - datos['temperatura_min']
    
    # Asegurar valores realistas
    datos['humedad_relativa'] = datos['humedad_relativa'].clip(0, 100)
    datos['velocidad_viento'] = datos['velocidad_viento'].clip(0, 30)
    datos['precipitacion'] = datos['precipitacion'].clip(0, 50)
    
    return datos

def main():
    """Función principal"""
    
    # Título principal
    st.title("🌾 METGO_3D - Dashboard Simple")
    st.markdown("### Sistema Meteorológico Agrícola Quillota")
    
    # Sidebar
    st.sidebar.header("🎛️ Controles")
    
    # Generar datos
    datos = generar_datos_prueba()
    
    # Mostrar información básica
    st.sidebar.markdown("### 📊 Información de los Datos")
    st.sidebar.metric("📅 Período", f"{len(datos)} días")
    st.sidebar.metric("🌡️ Temp. Promedio", f"{datos['temperatura_promedio'].mean():.1f}°C")
    st.sidebar.metric("🌧️ Precipitación Total", f"{datos['precipitacion'].sum():.1f} mm")
    st.sidebar.metric("💧 Humedad Promedio", f"{datos['humedad_relativa'].mean():.0f}%")
    
    # Métricas principales
    st.header("📊 Métricas Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌡️ Temperatura Máxima",
            f"{datos['temperatura_max'].max():.1f}°C",
            f"{datos['temperatura_max'].iloc[-1] - datos['temperatura_max'].iloc[-2]:+.1f}°C"
        )
    
    with col2:
        st.metric(
            "🌡️ Temperatura Mínima",
            f"{datos['temperatura_min'].min():.1f}°C",
            f"{datos['temperatura_min'].iloc[-1] - datos['temperatura_min'].iloc[-2]:+.1f}°C"
        )
    
    with col3:
        st.metric(
            "🌧️ Precipitación Total",
            f"{datos['precipitacion'].sum():.1f} mm",
            f"{(datos['precipitacion'] > 0).sum()} días"
        )
    
    with col4:
        st.metric(
            "💨 Velocidad Viento",
            f"{datos['velocidad_viento'].mean():.1f} km/h",
            f"{datos['velocidad_viento'].max():.1f} km/h"
        )
    
    # Gráfico de temperaturas
    st.header("🌡️ Evolución de Temperaturas")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(datos['fecha'], datos['temperatura_max'], 
            color='#FF5722', linewidth=2, label='Máxima', marker='o', markersize=4)
    ax.plot(datos['fecha'], datos['temperatura_min'], 
            color='#2196F3', linewidth=2, label='Mínima', marker='o', markersize=4)
    ax.plot(datos['fecha'], datos['temperatura_promedio'], 
            color='#4CAF50', linewidth=2, label='Promedio', marker='o', markersize=4)
    
    ax.fill_between(datos['fecha'], datos['temperatura_min'], 
                   datos['temperatura_max'], alpha=0.2, color='#81C784')
    
    ax.set_title('Evolución de Temperaturas - Últimos 30 Días', fontsize=14, fontweight='bold')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Temperatura (°C)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Formatear fechas
    ax.tick_params(axis='x', rotation=45)
    
    st.pyplot(fig)
    
    # Gráfico de precipitación
    st.header("🌧️ Precipitación Diaria")
    
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    
    bars = ax2.bar(datos['fecha'], datos['precipitacion'], 
                   color='#03A9F4', alpha=0.7, width=0.8)
    
    # Colorear barras según intensidad
    for bar, precip in zip(bars, datos['precipitacion']):
        if precip >= 10:
            bar.set_color('#F44336')  # Rojo para lluvia intensa
        elif precip >= 5:
            bar.set_color('#FF9800')  # Naranja para lluvia moderada
    
    ax2.set_title('Precipitación Diaria - Últimos 30 Días', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Fecha')
    ax2.set_ylabel('Precipitación (mm)')
    ax2.grid(True, alpha=0.3)
    
    # Formatear fechas
    ax2.tick_params(axis='x', rotation=45)
    
    st.pyplot(fig2)
    
    # Gráfico de humedad y viento
    st.header("💧 Humedad y Viento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💧 Humedad Relativa")
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        
        ax3.plot(datos['fecha'], datos['humedad_relativa'], 
                color='#00BCD4', linewidth=2, marker='s', markersize=3)
        ax3.fill_between(datos['fecha'], datos['humedad_relativa'], 
                        alpha=0.3, color='#00BCD4')
        
        # Zonas de confort
        ax3.axhspan(45, 75, alpha=0.2, color='#4CAF50', label='Zona óptima')
        ax3.axhline(y=30, color='#FF9800', linestyle='--', alpha=0.7, label='Muy baja')
        ax3.axhline(y=85, color='#F44336', linestyle='--', alpha=0.7, label='Muy alta')
        
        ax3.set_title('Humedad Relativa (%)')
        ax3.set_ylabel('Humedad (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='x', rotation=45)
        
        st.pyplot(fig3)
    
    with col2:
        st.subheader("💨 Velocidad del Viento")
        fig4, ax4 = plt.subplots(figsize=(8, 4))
        
        ax4.plot(datos['fecha'], datos['velocidad_viento'], 
                color='#9C27B0', linewidth=2, marker='^', markersize=3)
        ax4.fill_between(datos['fecha'], datos['velocidad_viento'], 
                        alpha=0.3, color='#9C27B0')
        
        # Zonas de viento
        ax4.axhspan(5, 15, alpha=0.2, color='#4CAF50', label='Favorable')
        ax4.axhline(y=20, color='#FF9800', linestyle='--', alpha=0.7, label='Moderado')
        ax4.axhline(y=25, color='#F44336', linestyle='--', alpha=0.7, label='Fuerte')
        
        ax4.set_title('Velocidad del Viento (km/h)')
        ax4.set_ylabel('Velocidad (km/h)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.tick_params(axis='x', rotation=45)
        
        st.pyplot(fig4)
    
    # Resumen estadístico
    st.header("📈 Resumen Estadístico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌡️ Temperaturas")
        temp_stats = {
            'Máxima': f"{datos['temperatura_max'].max():.1f}°C",
            'Mínima': f"{datos['temperatura_min'].min():.1f}°C",
            'Promedio': f"{datos['temperatura_promedio'].mean():.1f}°C",
            'Amplitud Térmica': f"{datos['amplitud_termica'].mean():.1f}°C"
        }
        
        for key, value in temp_stats.items():
            st.write(f"**{key}:** {value}")
    
    with col2:
        st.subheader("🌧️ Precipitación y Humedad")
        precip_stats = {
            'Precipitación Total': f"{datos['precipitacion'].sum():.1f} mm",
            'Días con Lluvia': f"{(datos['precipitacion'] > 0).sum()}",
            'Lluvia Máxima': f"{datos['precipitacion'].max():.1f} mm",
            'Humedad Promedio': f"{datos['humedad_relativa'].mean():.0f}%"
        }
        
        for key, value in precip_stats.items():
            st.write(f"**{key}:** {value}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            🌾 METGO_3D - Sistema Meteorológico Agrícola Quillota | 
            Dashboard Simple - Funcional
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
