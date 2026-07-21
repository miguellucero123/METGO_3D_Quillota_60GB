#!/usr/bin/env python3
"""
Dashboard Integrado METGO 3D - Recomendaciones Agrícolas Inteligentes
Combina datos meteorológicos en tiempo real con recomendaciones agrícolas avanzadas
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
import sys
from pathlib import Path

_DASH = Path(__file__).resolve().parent
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))

from metgo_dashboard_init import page_config_and_theme

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "Recomendaciones Agrícolas Integradas",
    "Meteorología en tiempo real + decisiones de campo",
    module="agricola",
    page_icon="🌾",
)

class DashboardIntegradoRecomendaciones:
    def __init__(self, db_path="datos_meteorologicos.db"):
        self.db_path = db_path
        self.estaciones = ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'hijuelas', 'calera']
        self.cultivos = {
            'paltos': {'nombre': 'Paltos', 'temp_optima': (15, 25), 'humedad_optima': (60, 80)},
            'citricos': {'nombre': 'Cítricos', 'temp_optima': (12, 28), 'humedad_optima': (50, 70)},
            'vides': {'nombre': 'Vides', 'temp_optima': (10, 30), 'humedad_optima': (40, 60)},
            'tomates': {'nombre': 'Tomates', 'temp_optima': (18, 25), 'humedad_optima': (60, 80)},
            'lechugas': {'nombre': 'Lechugas', 'temp_optima': (10, 20), 'humedad_optima': (70, 90)}
        }
    
    def obtener_datos_actuales(self):
        """Obtener datos meteorológicos actuales"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = '''
                SELECT estacion, fecha, temperatura, humedad, presion, precipitacion,
                       velocidad_viento, direccion_viento, nubosidad, indice_uv
                FROM datos_meteorologicos
                WHERE fecha = (
                    SELECT MAX(fecha) 
                    FROM datos_meteorologicos d2 
                    WHERE d2.estacion = datos_meteorologicos.estacion
                )
                ORDER BY estacion
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            
            return df
        except Exception as e:
            st.error(f"Error obteniendo datos actuales: {e}")
            return pd.DataFrame()
    
    def obtener_datos_historicos(self, dias=7):
        """Obtener datos históricos"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = '''
                SELECT estacion, fecha, temperatura, humedad, presion, precipitacion,
                       velocidad_viento, direccion_viento, nubosidad, indice_uv
                FROM datos_meteorologicos
                ORDER BY fecha DESC
                LIMIT ?
            '''
            df = pd.read_sql_query(query, conn, params=[dias * 24 * len(self.estaciones)])
            conn.close()
            
            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                # Filtrar por los últimos N días
                fecha_limite = datetime.now() - timedelta(days=dias)
                df = df[df['fecha'] >= fecha_limite]
            
            return df
        except Exception as e:
            st.error(f"Error obteniendo datos históricos: {e}")
            return pd.DataFrame()
    
    def analizar_condiciones_agricolas(self, datos):
        """Analizar condiciones para recomendaciones agrícolas"""
        if datos.empty:
            return {}
        
        analisis = {}
        
        # Temperatura promedio
        temp_promedio = datos['temperatura'].mean()
        temp_max = datos['temperatura'].max()
        temp_min = datos['temperatura'].min()
        
        # Humedad promedio
        humedad_promedio = datos['humedad'].mean()
        
        # Precipitación total
        precipitacion_total = datos['precipitacion'].sum()
        
        # Viento promedio
        viento_promedio = datos['velocidad_viento'].mean()
        
        analisis = {
            'temperatura': {
                'promedio': temp_promedio,
                'maxima': temp_max,
                'minima': temp_min,
                'variabilidad': temp_max - temp_min
            },
            'humedad': {
                'promedio': humedad_promedio,
                'nivel': 'alta' if humedad_promedio > 70 else 'media' if humedad_promedio > 50 else 'baja'
            },
            'precipitacion': {
                'total': precipitacion_total,
                'dias_lluvia': (datos['precipitacion'] > 0).sum(),
                'intensidad': 'alta' if precipitacion_total > 20 else 'media' if precipitacion_total > 5 else 'baja'
            },
            'viento': {
                'promedio': viento_promedio,
                'nivel': 'fuerte' if viento_promedio > 20 else 'moderado' if viento_promedio > 10 else 'suave'
            }
        }
        
        return analisis
    
    def generar_recomendaciones_riego(self, analisis, cultivo):
        """Generar recomendaciones de riego basadas en condiciones meteorológicas"""
        recomendaciones = []
        
        temp_promedio = analisis['temperatura']['promedio']
        humedad_promedio = analisis['humedad']['promedio']
        precipitacion_total = analisis['precipitacion']['total']
        viento_promedio = analisis['viento']['promedio']
        
        cultivo_info = self.cultivos.get(cultivo, {})
        temp_optima = cultivo_info.get('temp_optima', (15, 25))
        humedad_optima = cultivo_info.get('humedad_optima', (60, 80))
        
        # Recomendaciones de riego
        if precipitacion_total > 15:
            recomendaciones.append({
                'tipo': 'riego',
                'nivel': 'info',
                'mensaje': 'Precipitación abundante detectada. Reducir riego manual.',
                'accion': 'Suspender riego por 2-3 días'
            })
        elif precipitacion_total < 5 and humedad_promedio < 50:
            recomendaciones.append({
                'tipo': 'riego',
                'nivel': 'warning',
                'mensaje': 'Condiciones secas. Incrementar frecuencia de riego.',
                'accion': 'Aumentar riego en 20-30%'
            })
        
        # Recomendaciones de temperatura
        if temp_promedio < temp_optima[0]:
            recomendaciones.append({
                'tipo': 'temperatura',
                'nivel': 'warning',
                'mensaje': 'Temperatura baja para el cultivo.',
                'accion': 'Considerar protección térmica o retrasar siembra'
            })
        elif temp_promedio > temp_optima[1]:
            recomendaciones.append({
                'tipo': 'temperatura',
                'nivel': 'warning',
                'mensaje': 'Temperatura alta. Riesgo de estrés térmico.',
                'accion': 'Aumentar riego y sombreado'
            })
        
        # Recomendaciones de humedad
        if humedad_promedio > humedad_optima[1]:
            recomendaciones.append({
                'tipo': 'humedad',
                'nivel': 'warning',
                'mensaje': 'Humedad alta. Riesgo de enfermedades fúngicas.',
                'accion': 'Mejorar ventilación y aplicar fungicidas preventivos'
            })
        elif humedad_promedio < humedad_optima[0]:
            recomendaciones.append({
                'tipo': 'humedad',
                'nivel': 'info',
                'mensaje': 'Humedad baja. Considerar riego foliar.',
                'accion': 'Aplicar riego foliar en horas frescas'
            })
        
        return recomendaciones
    
    def generar_alertas_plagas(self, analisis):
        """Generar alertas de plagas basadas en condiciones meteorológicas"""
        alertas = []
        
        temp_promedio = analisis['temperatura']['promedio']
        humedad_promedio = analisis['humedad']['promedio']
        viento_promedio = analisis['viento']['promedio']
        
        # Alerta de áfidos (condiciones favorables: temp 20-25°C, humedad 60-80%)
        if 20 <= temp_promedio <= 25 and 60 <= humedad_promedio <= 80:
            alertas.append({
                'plaga': 'Áfidos',
                'nivel': 'warning',
                'mensaje': 'Condiciones favorables para desarrollo de áfidos',
                'prevencion': 'Aplicar aceite mineral o insecticida sistémico'
            })
        
        # Alerta de hongos (alta humedad)
        if humedad_promedio > 75:
            alertas.append({
                'plaga': 'Enfermedades Fúngicas',
                'nivel': 'danger',
                'mensaje': 'Alta humedad favorece desarrollo de hongos',
                'prevencion': 'Aplicar fungicida preventivo y mejorar ventilación'
            })
        
        # Alerta de ácaros (baja humedad y viento)
        if humedad_promedio < 45 and viento_promedio > 15:
            alertas.append({
                'plaga': 'Ácaros',
                'nivel': 'info',
                'mensaje': 'Condiciones secas y ventosas favorecen ácaros',
                'prevencion': 'Aumentar humedad y aplicar acaricida'
            })
        
        return alertas
    
    def generar_alertas_heladas(self, analisis, pronostico_7_dias=None):
        """Generar alertas de heladas"""
        alertas = []
        
        temp_minima = analisis['temperatura']['minima']
        temp_promedio = analisis['temperatura']['promedio']
        viento_promedio = analisis['viento']['promedio']
        nubosidad_promedio = analisis.get('nubosidad', {}).get('promedio', 50)
        
        # Alerta inmediata de helada
        if temp_minima < 2:
            alertas.append({
                'tipo': 'helada',
                'nivel': 'danger',
                'mensaje': 'Riesgo CRÍTICO de helada detectado',
                'accion': 'Activar sistema de protección inmediatamente'
            })
        elif temp_minima < 5:
            alertas.append({
                'tipo': 'helada',
                'nivel': 'warning',
                'mensaje': 'Riesgo de helada moderado',
                'accion': 'Preparar sistemas de protección'
            })
        
        # Condiciones favorables para heladas
        if temp_promedio < 10 and viento_promedio < 5 and nubosidad_promedio < 30:
            alertas.append({
                'tipo': 'helada',
                'nivel': 'info',
                'mensaje': 'Condiciones favorables para heladas nocturnas',
                'accion': 'Monitorear temperaturas nocturnas'
            })
        
        return alertas
    
    def crear_grafico_condiciones_agricolas(self, analisis):
        """Crear gráfico de condiciones agrícolas"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Temperatura', 'Humedad', 'Precipitación', 'Viento'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # Temperatura
        fig.add_trace(go.Indicator(
            mode = "gauge+number+delta",
            value = analisis['temperatura']['promedio'],
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
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 30
                }
            }
        ), row=1, col=1)
        
        # Humedad
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = analisis['humedad']['promedio'],
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
        
        # Precipitación
        fig.add_trace(go.Indicator(
            mode = "number+delta",
            value = analisis['precipitacion']['total'],
            title = {'text': "Precipitación (mm)"},
            delta = {'reference': 10}
        ), row=2, col=1)
        
        # Viento
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = analisis['viento']['promedio'],
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
        ), row=2, col=2)
        
        fig.update_layout(
            height=600, 
            title_text="Condiciones Meteorológicas para Agricultura",
            showlegend=False
        , showlegend=False)
        return fig

def main():
    """Función principal del dashboard"""
    
    # Título principal
    st.title("🌾 METGO 3D - Dashboard Integrado de Recomendaciones Agrícolas")
    st.markdown("### Sistema Inteligente de Recomendaciones Meteorológicas y Agrícolas")
    
    # Inicializar dashboard
    dashboard = DashboardIntegradoRecomendaciones()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Selector de cultivo
        cultivo = st.selectbox(
            "🌱 Seleccionar Cultivo",
            list(dashboard.cultivos.keys()),
            format_func=lambda x: dashboard.cultivos[x]['nombre']
        )
        
        # Selector de período
        periodo = st.selectbox(
            "📅 Período de Análisis",
            ["Últimas 6 horas", "Últimas 12 horas", "Último día", "Últimos 3 días", "Última semana"],
            index=3
        )
        
        # Mapeo de períodos a días
        dias_map = {
            "Últimas 6 horas": 0.25,
            "Últimas 12 horas": 0.5,
            "Último día": 1,
            "Últimos 3 días": 3,
            "Última semana": 7
        }
        
        dias = int(dias_map[periodo])
        
        # Botón de actualización
        if st.button("🔄 Actualizar Análisis"):
            st.rerun()
    
    # Obtener datos
    datos_actuales = dashboard.obtener_datos_actuales()
    datos_historicos = dashboard.obtener_datos_historicos(dias)
    
    if datos_historicos.empty:
        st.warning("⚠️ No hay datos meteorológicos disponibles para el análisis.")
        return
    
    # Analizar condiciones agrícolas
    analisis = dashboard.analizar_condiciones_agricolas(datos_historicos)
    
    if not analisis:
        st.error("❌ Error en el análisis de condiciones agrícolas.")
        return
    
    # Mostrar gráfico de condiciones
    st.subheader("📊 Condiciones Meteorológicas Actuales")
    fig_condiciones = dashboard.crear_grafico_condiciones_agricolas(analisis)
    st.plotly_chart(fig_condiciones, config=PLOTLY_CONFIG, width='stretch')
    
    # Generar recomendaciones
    recomendaciones_riego = dashboard.generar_recomendaciones_riego(analisis, cultivo)
    alertas_plagas = dashboard.generar_alertas_plagas(analisis)
    alertas_heladas = dashboard.generar_alertas_heladas(analisis)
    
    # Mostrar recomendaciones de riego
    st.subheader("💧 Recomendaciones de Riego")
    if recomendaciones_riego:
        for rec in recomendaciones_riego:
            if rec['nivel'] == 'warning':
                st.warning(f"⚠️ {rec['mensaje']}")
                st.info(f"💡 **Acción recomendada:** {rec['accion']}")
            elif rec['nivel'] == 'info':
                st.info(f"ℹ️ {rec['mensaje']}")
                st.info(f"💡 **Acción recomendada:** {rec['accion']}")
    else:
        st.success("✅ Condiciones de riego normales para el cultivo seleccionado.")
    
    # Mostrar alertas de plagas
    st.subheader("🐛 Alertas de Plagas y Enfermedades")
    if alertas_plagas:
        for alerta in alertas_plagas:
            if alerta['nivel'] == 'danger':
                st.error(f"🚨 **{alerta['plaga']}:** {alerta['mensaje']}")
                st.info(f"🛡️ **Prevención:** {alerta['prevencion']}")
            elif alerta['nivel'] == 'warning':
                st.warning(f"⚠️ **{alerta['plaga']}:** {alerta['mensaje']}")
                st.info(f"🛡️ **Prevención:** {alerta['prevencion']}")
            else:
                st.info(f"ℹ️ **{alerta['plaga']}:** {alerta['mensaje']}")
                st.info(f"🛡️ **Prevención:** {alerta['prevencion']}")
    else:
        st.success("✅ No se detectan condiciones favorables para plagas o enfermedades.")
    
    # Mostrar alertas de heladas
    st.subheader("❄️ Alertas de Heladas")
    if alertas_heladas:
        for alerta in alertas_heladas:
            if alerta['nivel'] == 'danger':
                st.error(f"🚨 {alerta['mensaje']}")
                st.error(f"🚨 **ACCIÓN INMEDIATA:** {alerta['accion']}")
            elif alerta['nivel'] == 'warning':
                st.warning(f"⚠️ {alerta['mensaje']}")
                st.warning(f"⚠️ **Acción recomendada:** {alerta['accion']}")
            else:
                st.info(f"ℹ️ {alerta['mensaje']}")
                st.info(f"ℹ️ **Acción recomendada:** {alerta['accion']}")
    else:
        st.success("✅ No se detectan riesgos de heladas.")
    
    # Resumen ejecutivo
    st.subheader("📋 Resumen Ejecutivo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌡️ Temperatura",
            f"{analisis['temperatura']['promedio']:.1f}°C",
            f"Rango: {analisis['temperatura']['minima']:.1f}°C - {analisis['temperatura']['maxima']:.1f}°C"
        )
    
    with col2:
        st.metric(
            "💧 Humedad",
            f"{analisis['humedad']['promedio']:.1f}%",
            f"Nivel: {analisis['humedad']['nivel']}"
        )
    
    with col3:
        st.metric(
            "🌧️ Precipitación",
            f"{analisis['precipitacion']['total']:.1f}mm",
            f"Días lluvia: {analisis['precipitacion']['dias_lluvia']}"
        )
    
    with col4:
        st.metric(
            "💨 Viento",
            f"{analisis['viento']['promedio']:.1f} km/h",
            f"Nivel: {analisis['viento']['nivel']}"
        )
    
    # Información del sistema
    with st.expander("ℹ️ Información del Sistema"):
        st.write(f"**Cultivo seleccionado:** {dashboard.cultivos[cultivo]['nombre']}")
        st.write(f"**Período analizado:** {periodo}")
        st.write(f"**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Total de alertas:** {len(recomendaciones_riego) + len(alertas_plagas) + len(alertas_heladas)}")
        
        # Condiciones óptimas del cultivo
        cultivo_info = dashboard.cultivos[cultivo]
        st.write(f"**Temperatura óptima:** {cultivo_info['temp_optima'][0]}°C - {cultivo_info['temp_optima'][1]}°C")
        st.write(f"**Humedad óptima:** {cultivo_info['humedad_optima'][0]}% - {cultivo_info['humedad_optima'][1]}%")

if __name__ == "__main__":
    main()
