#!/usr/bin/env python3
"""
Dashboard Principal Integrado METGO 3D
Sistema unificado que combina todos los dashboards y funcionalidades
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sqlite3
import json
import subprocess
import sys
import os
import sys
from pathlib import Path

_DASH = Path(__file__).resolve().parent
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))

from metgo_dashboard_init import page_config_and_theme

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "Dashboard Principal Integrado",
    "Hub METGO 3D · lanzador de módulos",
    module="unificado",
    page_icon="🌾",
)

class DashboardPrincipalIntegrado:
    def __init__(self):
        self.db_path = "datos_meteorologicos.db"
        self.estaciones = ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'hijuelas', 'calera']
        
        # Configuración de dashboards disponibles
        self.dashboards = {
            "meteorologico": {
                "nombre": "Dashboard Meteorológico",
                "archivo": "dashboard_meteorologico_final.py",
                "puerto": 8502,
                "descripcion": "Datos meteorológicos en tiempo real con pronósticos de 14 días"
            },
            "agricola": {
                "nombre": "Dashboard Agrícola",
                "archivo": "dashboard_agricola_avanzado.py",
                "puerto": 8501,
                "descripcion": "Recomendaciones agrícolas y análisis de cultivos"
            },
            "recomendaciones": {
                "nombre": "Dashboard de Recomendaciones",
                "archivo": "dashboard_integrado_recomendaciones_metgo.py",
                "puerto": 8510,
                "descripcion": "Recomendaciones integradas de riego, plagas y heladas"
            },
            "alertas": {
                "nombre": "Sistema de Alertas",
                "archivo": "sistema_alertas_visuales_integrado_metgo.py",
                "puerto": 8511,
                "descripcion": "Alertas visuales y recomendaciones de emergencia"
            }
        }
    
    def obtener_datos_actuales(self):
        """Obtener datos meteorológicos actuales de la última hora"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = '''
                SELECT estacion, fecha, temperatura, humedad, presion, precipitacion,
                       velocidad_viento, direccion_viento, nubosidad, indice_uv
                FROM datos_meteorologicos
                WHERE fecha >= datetime('now', '-1 hour')
                ORDER BY fecha DESC
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            
            return df
        except Exception as e:
            return pd.DataFrame()
    
    def analizar_estado_general(self, datos):
        """Analizar el estado general del sistema con información específica"""
        if datos.empty:
            return {
                "estado": "sin_datos", 
                "mensaje": "No hay datos disponibles",
                "periodo": "Sin datos",
                "estaciones": [],
                "metricas": {}
            }
        
        # Información del período y estaciones
        fecha_min = datos['fecha'].min()
        fecha_max = datos['fecha'].max()
        estaciones = datos['estacion'].unique().tolist()
        
        # Calcular métricas reales
        temp_promedio = datos['temperatura'].mean()
        temp_max = datos['temperatura'].max()
        temp_min = datos['temperatura'].min()
        humedad_promedio = datos['humedad'].mean()
        viento_promedio = datos['velocidad_viento'].mean()
        viento_max = datos['velocidad_viento'].max()
        precipitacion_total = datos['precipitacion'].sum()
        presion_promedio = datos['presion'].mean()
        
        # Determinar estado general basado en condiciones reales
        estado_puntaje = 100
        alertas = []
        
        # Verificar heladas
        if temp_min <= 2:
            estado_puntaje -= 30
            alertas.append("🚨 Heladas críticas detectadas")
        elif temp_min <= 5:
            estado_puntaje -= 15
            alertas.append("⚠️ Riesgo de heladas")
        
        # Verificar temperatura alta
        if temp_max >= 35:
            estado_puntaje -= 20
            alertas.append("🌡️ Temperaturas altas")
        
        # Verificar vientos fuertes
        if viento_max >= 30:
            estado_puntaje -= 15
            alertas.append("💨 Vientos fuertes")
        
        # Verificar humedad extrema
        if humedad_promedio >= 85:
            estado_puntaje -= 10
            alertas.append("💧 Humedad muy alta")
        elif humedad_promedio <= 30:
            estado_puntaje -= 10
            alertas.append("🏜️ Humedad muy baja")
        
        return {
            "estado": "normal" if estado_puntaje >= 80 else ("advertencia" if estado_puntaje >= 60 else "critico"),
            "puntaje": max(0, estado_puntaje),
            "periodo": f"Última hora ({fecha_min.strftime('%H:%M')} - {fecha_max.strftime('%H:%M')})",
            "estaciones": estaciones,
            "fecha_actualizacion": fecha_max,
            "metricas": {
                "temperatura_promedio": temp_promedio,
                "temperatura_max": temp_max,
                "temperatura_min": temp_min,
                "humedad_promedio": humedad_promedio,
                "viento_promedio": viento_promedio,
                "viento_max": viento_max,
                "precipitacion_total": precipitacion_total,
                "presion_promedio": presion_promedio
            },
            "alertas": alertas
        }
    
    def crear_grafico_estado_general(self, estado):
        """Crear gráfico del estado general del sistema"""
        metricas = estado.get('metricas', {})
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Temperatura', 'Humedad', 'Viento', 'Estado General'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # Temperatura
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = metricas.get('temperatura_promedio', 0),
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Temperatura (°C)"},
            gauge = {
                'axis': {'range': [None, 40]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 15], 'color': "lightblue"},
                    {'range': [15, 25], 'color': "lightgreen"},
                    {'range': [25, 35], 'color': "yellow"},
                    {'range': [35, 40], 'color': "red"}
                ]
            }
        ), row=1, col=1)
        
        # Humedad
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = metricas.get('humedad_promedio', 0),
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Humedad (%)"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 30], 'color': "lightcoral"},
                    {'range': [30, 60], 'color': "lightyellow"},
                    {'range': [60, 80], 'color': "lightgreen"},
                    {'range': [80, 100], 'color': "lightblue"}
                ]
            }
        ), row=1, col=2)
        
        # Viento
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = metricas.get('viento_promedio', 0),
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Viento (km/h)"},
            gauge = {
                'axis': {'range': [0, 50]},
                'bar': {'color': "darkorange"},
                'steps': [
                    {'range': [0, 10], 'color': "lightgreen"},
                    {'range': [10, 20], 'color': "yellow"},
                    {'range': [20, 35], 'color': "orange"},
                    {'range': [35, 50], 'color': "red"}
                ]
            }
        ), row=2, col=1)
        
        # Estado General
        estado_colores = {
            'normal': {'color': 'green', 'value': 100},
            'advertencia': {'color': 'orange', 'value': 60},
            'critico': {'color': 'red', 'value': 20},
            'sin_datos': {'color': 'gray', 'value': 0}
        }
        
        estado_info = estado_colores.get(estado.get('estado', 'sin_datos'), estado_colores['sin_datos'])
        
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = estado_info['value'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Estado General"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': estado_info['color']},
                'steps': [
                    {'range': [0, 30], 'color': "lightcoral"},
                    {'range': [30, 70], 'color': "lightyellow"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ]
            }
        ), row=2, col=2)
        
        fig.update_layout(
            height=600, 
            title_text="Estado General del Sistema METGO 3D",
            showlegend=False
        )
        return fig
    
    def mostrar_panel_alertas(self, estado):
        """Mostrar panel de alertas del estado general"""
        alertas = estado.get('alertas', [])
        
        if not alertas:
            st.success("✅ **Sistema en estado normal** - No hay alertas activas")
            return
        
        # Mostrar alertas según el estado
        if estado.get('estado') == 'critico':
            st.error("🚨 **ESTADO CRÍTICO** - Acción inmediata requerida")
            for alerta in alertas:
                st.error(f"🚨 {alerta}")
        elif estado.get('estado') == 'advertencia':
            st.warning("⚠️ **ESTADO DE ADVERTENCIA** - Monitoreo intensivo recomendado")
            for alerta in alertas:
                st.warning(f"⚠️ {alerta}")
        else:
            st.info("ℹ️ **ALERTAS MENORES**")
            for alerta in alertas:
                st.info(f"ℹ️ {alerta}")
    
    def ejecutar_dashboard(self, dashboard_id):
        """Ejecutar un dashboard específico"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            st.error(f"Dashboard '{dashboard_id}' no encontrado")
            return
        
        try:
            # Verificar si el dashboard ya está ejecutándose
            try:
                import requests
                response = requests.get(f"http://localhost:{dashboard['puerto']}/_stcore/health", timeout=1)
                if response.status_code == 200:
                    st.info(f"✅ {dashboard['nombre']} ya está ejecutándose en http://localhost:{dashboard['puerto']}")
                    st.markdown(f"<a href='http://localhost:{dashboard['puerto']}' target='_blank'>Abrir {dashboard['nombre']}</a>", unsafe_allow_html=True)
                    return
            except:
                pass
            
            # Ejecutar el dashboard
            command = [sys.executable, "-m", "streamlit", "run", dashboard['archivo'], 
                      "--server.port", str(dashboard['puerto']), "--server.headless", "true"]
            
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            st.success(f"🚀 {dashboard['nombre']} iniciado en http://localhost:{dashboard['puerto']}")
            st.markdown(f"<a href='http://localhost:{dashboard['puerto']}' target='_blank'>Abrir {dashboard['nombre']}</a>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error ejecutando {dashboard['nombre']}: {e}")
    
    def mostrar_menu_dashboards(self):
        """Mostrar menú de dashboards disponibles"""
        st.subheader("🎛️ Panel de Control de Dashboards")
        
        # Crear columnas para los botones de dashboard
        cols = st.columns(2)
        
        for i, (dashboard_id, dashboard) in enumerate(self.dashboards.items()):
            col = cols[i % 2]
            
            with col:
                st.markdown(f"### {dashboard['nombre']}")
                st.write(dashboard['descripcion'])
                
                if st.button(f"🚀 Ejecutar {dashboard['nombre']}", key=f"btn_{dashboard_id}"):
                    self.ejecutar_dashboard(dashboard_id)
                
                st.markdown(f"**Puerto:** {dashboard['puerto']}")
                st.markdown("---")

def main():
    """Función principal del dashboard"""
    
    # Título principal
    st.title("🌾 METGO 3D - Dashboard Principal Integrado")
    st.markdown("### Sistema Unificado de Gestión Meteorológica y Agrícola")
    
    # Inicializar dashboard
    dashboard = DashboardPrincipalIntegrado()
    
    # Sidebar con información del sistema
    with st.sidebar:
        st.header("ℹ️ Información del Sistema")
        st.write(f"**Versión:** METGO 3D v2.0")
        st.write(f"**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Base de datos:** {dashboard.db_path}")
        
        # Botón de actualización general
        if st.button("🔄 Actualizar Sistema"):
            st.rerun()
        
        st.markdown("---")
        
        # Enlaces rápidos
        st.header("🔗 Enlaces Rápidos")
        st.markdown("- [Dashboard Meteorológico](http://localhost:8502)")
        st.markdown("- [Dashboard Agrícola](http://localhost:8501)")
        st.markdown("- [Sistema de Autenticación](http://localhost:8500)")
        st.markdown("- [Dashboard Central](http://localhost:8509)")
    
    # Obtener datos actuales
    datos_actuales = dashboard.obtener_datos_actuales()
    
    if datos_actuales.empty:
        st.warning("⚠️ **No hay datos meteorológicos disponibles**")
        st.info("💡 **Recomendación:** Ejecuta el Dashboard Meteorológico para generar datos")
        
        # Mostrar solo el menú de dashboards
        dashboard.mostrar_menu_dashboards()
        return
    
    # Analizar estado general
    estado = dashboard.analizar_estado_general(datos_actuales)
    
    # Mostrar estado general
    st.subheader("📊 Estado General del Sistema")
    
    # Información específica del período y estaciones
    if estado.get('periodo') and estado.get('estaciones'):
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.info(f"📅 **Período:** {estado['periodo']}")
        
        with col_info2:
            estaciones_texto = ", ".join(estado['estaciones'][:3])  # Mostrar máximo 3 estaciones
            if len(estado['estaciones']) > 3:
                estaciones_texto += f" (+{len(estado['estaciones'])-3} más)"
            st.info(f"📍 **Estaciones:** {estaciones_texto}")
        
        with col_info3:
            if estado.get('fecha_actualizacion'):
                fecha_str = estado['fecha_actualizacion'].strftime('%H:%M:%S')
                st.info(f"🕐 **Última actualización:** {fecha_str}")
    
    # Gráfico de estado general
    fig_estado = dashboard.crear_grafico_estado_general(estado)
    st.plotly_chart(fig_estado, config=PLOTLY_CONFIG, width='stretch')
    
    # Panel de alertas
    dashboard.mostrar_panel_alertas(estado)
    
    # Métricas principales
    st.subheader("📈 Métricas Principales")
    metricas = estado.get('metricas', {})
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "🌡️ Temperatura",
            f"{metricas.get('temperatura_promedio', 0):.1f}°C"
        )
    
    with col2:
        st.metric(
            "💧 Humedad",
            f"{metricas.get('humedad_promedio', 0):.1f}%"
        )
    
    with col3:
        st.metric(
            "💨 Viento",
            f"{metricas.get('viento_promedio', 0):.1f} km/h"
        )
    
    with col4:
        st.metric(
            "🌧️ Precipitación",
            f"{metricas.get('precipitacion_total', 0):.1f}mm"
        )
    
    with col5:
        st.metric(
            "📍 Estaciones",
            f"{metricas.get('estaciones_activas', 0)}/6"
        )
    
    # Menú de dashboards
    dashboard.mostrar_menu_dashboards()
    
    # Información adicional
    with st.expander("ℹ️ Información Técnica del Sistema"):
        st.write("**Arquitectura del Sistema:**")
        st.write("- Base de datos SQLite para almacenamiento")
        st.write("- APIs meteorológicas en tiempo real")
        st.write("- Dashboards Streamlit independientes")
        st.write("- Sistema de alertas integrado")
        st.write("- Recomendaciones agrícolas automatizadas")
        
        st.write("**Dashboards Disponibles:**")
        for dashboard_id, info in dashboard.dashboards.items():
            st.write(f"- **{info['nombre']}:** Puerto {info['puerto']}")
        
        st.write("**Última verificación de datos:**")
        if not datos_actuales.empty:
            ultima_fecha = datos_actuales['fecha'].max()
            st.write(f"- {ultima_fecha}")
        else:
            st.write("- No hay datos disponibles")

if __name__ == "__main__":
    main()
