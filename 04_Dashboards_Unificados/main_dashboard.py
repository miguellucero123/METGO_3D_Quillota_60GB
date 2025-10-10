#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Unificado METGO_3D - Script Principal
Dashboard principal con acceso a todos los módulos
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Unificado METGO_3D",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🏠 Dashboard Unificado METGO_3D")
    st.markdown("### Sistema Integrado de Gestión Agrícola y Meteorológica")
    
    # Sidebar con navegación
    st.sidebar.header("🧭 Navegación")
    
    # Menú de módulos
    modulos = {
        "🌤️ Sistema Meteorológico": "01_Sistema_Meteorologico",
        "🌾 Sistema Agrícola": "02_Sistema_Agricola", 
        "🚁 IoT y Drones": "03_Sistema_IoT_Drones",
        "🤖 Modelos ML/IA": "06_Modelos_ML_IA",
        "📈 Monitoreo": "07_Sistema_Monitoreo",
        "💾 Gestión de Datos": "08_Gestion_Datos"
    }
    
    modulo_seleccionado = st.sidebar.selectbox("Seleccionar módulo", list(modulos.keys()))
    
    # Información general del sistema
    st.header("📊 Resumen del Sistema")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Módulos Activos",
            value="12",
            delta="+2 desde última actualización"
        )
    
    with col2:
        st.metric(
            label="Datos Procesados",
            value="1,247",
            delta="+156 hoy"
        )
    
    with col3:
        st.metric(
            label="Predicciones Generadas",
            value="89",
            delta="+12 esta semana"
        )
    
    with col4:
        st.metric(
            label="Uptime Sistema",
            value="99.8%",
            delta="+0.2%"
        )
    
    # Estado de los módulos
    st.header("🔧 Estado de Módulos")
    
    # Datos de ejemplo para el estado de módulos
    modulos_estado = {
        "Sistema Meteorológico": {"estado": "Activo", "ultima_actualizacion": "2 min", "registros": 1247},
        "Sistema Agrícola": {"estado": "Activo", "ultima_actualizacion": "5 min", "registros": 892},
        "IoT y Drones": {"estado": "Activo", "ultima_actualizacion": "1 min", "registros": 3456},
        "Modelos ML/IA": {"estado": "Activo", "ultima_actualizacion": "3 min", "registros": 567},
        "Monitoreo": {"estado": "Activo", "ultima_actualizacion": "1 min", "registros": 2341},
        "Gestión de Datos": {"estado": "Activo", "ultima_actualizacion": "4 min", "registros": 4567}
    }
    
    # Crear tabla de estado
    df_estado = pd.DataFrame(modulos_estado).T
    df_estado.reset_index(inplace=True)
    df_estado.columns = ['Módulo', 'Estado', 'Última Actualización', 'Registros']
    
    st.dataframe(df_estado, use_container_width=True)
    
    # Gráficos de resumen
    st.header("📈 Métricas del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de uso de módulos
        fig_uso = px.pie(
            values=list(modulos_estado.values()),
            names=list(modulos_estado.keys()),
            title="Distribución de Registros por Módulo"
        )
        st.plotly_chart(fig_uso, use_container_width=True)
    
    with col2:
        # Gráfico de tendencia temporal (datos simulados)
        fechas = pd.date_range(start='2025-01-01', end='2025-01-30', freq='D')
        datos_tendencia = pd.DataFrame({
            'fecha': fechas,
            'temperatura': np.random.normal(25, 5, len(fechas)),
            'humedad': np.random.normal(60, 10, len(fechas)),
            'precipitacion': np.random.exponential(2, len(fechas))
        })
        
        fig_tendencia = px.line(
            datos_tendencia,
            x='fecha',
            y='temperatura',
            title="Tendencia de Temperatura (Último Mes)"
        )
        st.plotly_chart(fig_tendencia, use_container_width=True)
    
    # Alertas y notificaciones
    st.header("🚨 Alertas del Sistema")
    
    alertas = [
        {"tipo": "info", "mensaje": "Sistema funcionando correctamente", "tiempo": "Hace 2 minutos"},
        {"tipo": "warning", "mensaje": "Humedad del suelo baja en sector A", "tiempo": "Hace 15 minutos"},
        {"tipo": "success", "mensaje": "Predicción meteorológica actualizada", "tiempo": "Hace 30 minutos"},
        {"tipo": "info", "mensaje": "Respaldo automático completado", "tiempo": "Hace 1 hora"}
    ]
    
    for alerta in alertas:
        if alerta["tipo"] == "warning":
            st.warning(f"⚠️ {alerta['mensaje']} - {alerta['tiempo']}")
        elif alerta["tipo"] == "success":
            st.success(f"✅ {alerta['mensaje']} - {alerta['tiempo']}")
        else:
            st.info(f"ℹ️ {alerta['mensaje']} - {alerta['tiempo']}")
    
    # Acceso rápido a funcionalidades
    st.header("⚡ Acceso Rápido")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("🌤️ Ver Pronóstico Meteorológico", key="btn_meteo")
        st.button("🌾 Análisis Agrícola", key="btn_agricola")
    
    with col2:
        st.button("📊 Generar Reporte", key="btn_reporte")
        st.button("🔧 Configurar Sistema", key="btn_config")
    
    with col3:
        st.button("📈 Ver Métricas", key="btn_metricas")
        st.button("🚨 Gestionar Alertas", key="btn_alertas")
    
    # Información del sistema en sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Información del Sistema")
    st.sidebar.info(f"Versión: 3.0.0")
    st.sidebar.info(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.sidebar.info(f"Módulos activos: {len(modulos)}")
    
    st.sidebar.markdown("### 🔗 Enlaces Rápidos")
    st.sidebar.markdown("- [Sistema Meteorológico](http://localhost:8501)")
    st.sidebar.markdown("- [Sistema Agrícola](http://localhost:8502)")
    st.sidebar.markdown("- [Dashboard Unificado](http://localhost:8503)")
    st.sidebar.markdown("- [Modelos ML/IA](http://localhost:8504)")

if __name__ == "__main__":
    main()
