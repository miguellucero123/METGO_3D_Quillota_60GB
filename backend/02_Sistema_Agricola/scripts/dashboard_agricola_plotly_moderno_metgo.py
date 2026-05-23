#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Agrícola Avanzado con Plotly Moderno
Sistema METGO 3D Quillota - Solución definitiva para warnings de Plotly
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime, timedelta
import requests
import json

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Agrícola Avanzado - METGO 3D Quillota",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración moderna de Plotly para eliminar warnings
PLOTLY_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'grafico_metgo',
        'height': 500,
        'width': 700,
        'scale': 2
    },
    'responsive': True,
    'staticPlot': False
}

class DashboardAgricolaModerno:
    def __init__(self):
        self.db_path = "data/datos_meteorologicos.db"
        self.api_key = "tu_api_key_openmeteo"
        self.estaciones = {
            'Quillota_Centro': {'lat': -32.8833, 'lon': -71.25},
            'Quillota_Norte': {'lat': -32.85, 'lon': -71.22},
            'Quillota_Sur': {'lat': -32.92, 'lon': -71.28},
            'Quillota_Este': {'lat': -32.88, 'lon': -71.20},
            'Quillota_Oeste': {'lat': -32.88, 'lon': -71.30},
            'Quillota_Valle': {'lat': -32.90, 'lon': -71.26}
        }
        self.analisis_heladas = self._generar_analisis_heladas()

    def _generar_analisis_heladas(self):
        """Genera análisis de heladas simulado"""
        return {
            'riesgo_alto': 2,
            'riesgo_medio': 3,
            'riesgo_bajo': 1,
            'temperatura_minima': -2.5,
            'probabilidad_helada': 0.15
        }

    def obtener_datos_actuales(self):
        """Obtiene datos actuales de la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT * FROM datos_meteorologicos 
            WHERE fecha >= datetime('now', '-24 hours')
            ORDER BY fecha DESC
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error obteniendo datos: {e}")
            return self._generar_datos_simulados()

    def _generar_datos_simulados(self):
        """Genera datos simulados para demostración"""
        fechas = pd.date_range(start=datetime.now() - timedelta(hours=24), 
                             end=datetime.now(), freq='H')
        datos = []
        
        for estacion in self.estaciones.keys():
            for fecha in fechas:
                datos.append({
                    'fecha': fecha,
                    'estacion': estacion,
                    'temperatura': np.random.normal(18, 5),
                    'humedad': np.random.normal(65, 15),
                    'presion': np.random.normal(1013, 10),
                    'viento_velocidad': np.random.normal(8, 3),
                    'viento_direccion': np.random.normal(180, 45),
                    'precipitacion': np.random.exponential(0.5),
                    'radiacion_solar': np.random.normal(400, 100)
                })
        
        return pd.DataFrame(datos)

    def calcular_metricas_agricolas(self, df):
        """Calcula métricas específicas para agricultura"""
        if df.empty:
            return {}
        
        # Validación robusta para evitar warnings de numpy
        temp_data = df['temperatura'].dropna()
        hum_data = df['humedad'].dropna()
        pres_data = df['presion'].dropna()
        
        return {
            'temperatura_promedio': temp_data.mean() if len(temp_data) > 0 else 0,
            'temperatura_maxima': temp_data.max() if len(temp_data) > 0 else 0,
            'temperatura_minima': temp_data.min() if len(temp_data) > 0 else 0,
            'humedad_promedio': hum_data.mean() if len(hum_data) > 0 else 0,
            'presion_promedio': pres_data.mean() if len(pres_data) > 0 else 0,
            'riesgo_helada': self._evaluar_riesgo_helada(temp_data.min() if len(temp_data) > 0 else 0),
            'condicion_riego': self._evaluar_condicion_riego(
                temp_data.mean() if len(temp_data) > 0 else 0,
                hum_data.mean() if len(hum_data) > 0 else 0
            )
        }

    def _evaluar_riesgo_helada(self, temp_min):
        """Evalúa el riesgo de helada basado en temperatura mínima"""
        if temp_min < 0:
            return "Alto"
        elif temp_min < 5:
            return "Medio"
        else:
            return "Bajo"

    def _evaluar_condicion_riego(self, temp_prom, hum_prom):
        """Evalúa las condiciones para riego"""
        if temp_prom > 25 and hum_prom < 60:
            return "Riego Recomendado"
        elif temp_prom > 20 and hum_prom < 70:
            return "Riego Moderado"
        else:
            return "Sin Riego"

    def crear_grafico_temperaturas_moderno(self, df):
        """Crea gráfico de temperaturas con configuración moderna de Plotly"""
        if df.empty:
            return None
        
        # Preparar datos
        df_plot = df.copy()
        df_plot['fecha'] = pd.to_datetime(df_plot['fecha'])
        
        # Crear gráfico con configuración moderna
        fig = go.Figure()
        
        # Agregar líneas para cada estación
        for estacion in df_plot['estacion'].unique():
            estacion_data = df_plot[df_plot['estacion'] == estacion]
            
            fig.add_trace(go.Scatter(
                x=estacion_data['fecha'],
                y=estacion_data['temperatura'],
                mode='lines+markers',
                name=estacion,
                line=dict(width=2),
                marker=dict(size=4)
            ))
        
        # Configuración moderna del layout
        fig.update_layout(
            title="Temperaturas por Estación - Últimas 24 Horas",
            xaxis_title="Hora",
            yaxis_title="Temperatura (°C, showlegend=False)",
            hovermode='x unified',
            showlegend=True,
            height=400,
            template='plotly_white'
        )
        
        # Configuración moderna de ejes
        fig.update_xaxes(
            tickformat='%H:%M',
            tickangle=45
        )
        
        fig.update_yaxes(
            gridcolor='lightgray',
            zeroline=True
        )
        
        return fig

    def crear_grafico_humedad_moderno(self, df):
        """Crea gráfico de humedad con configuración moderna"""
        if df.empty:
            return None
        
        df_plot = df.copy()
        df_plot['fecha'] = pd.to_datetime(df_plot['fecha'])
        
        fig = go.Figure()
        
        for estacion in df_plot['estacion'].unique():
            estacion_data = df_plot[df_plot['estacion'] == estacion]
            
            fig.add_trace(go.Scatter(
                x=estacion_data['fecha'],
                y=estacion_data['humedad'],
                mode='lines+markers',
                name=estacion,
                line=dict(width=2),
                marker=dict(size=4)
            ))
        
        fig.update_layout(
            title="Humedad Relativa por Estación",
            xaxis_title="Hora",
            yaxis_title="Humedad (%, showlegend=False)",
            hovermode='x unified',
            showlegend=True,
            height=400,
            template='plotly_white'
        )
        
        fig.update_xaxes(tickformat='%H:%M', tickangle=45)
        fig.update_yaxes(gridcolor='lightgray', zeroline=True)
        
        return fig

    def crear_grafico_condiciones_agricolas(self, metricas):
        """Crea gráfico de condiciones agrícolas"""
        if not metricas:
            return None
        
        # Datos para el gráfico
        variables = ['Temp. Promedio', 'Temp. Máxima', 'Temp. Mínima', 'Humedad']
        valores = [
            metricas.get('temperatura_promedio', 0),
            metricas.get('temperatura_maxima', 0),
            metricas.get('temperatura_minima', 0),
            metricas.get('humedad_promedio', 0)
        ]
        
        fig = go.Figure(data=[
            go.Bar(
                x=variables,
                y=valores,
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
                text=[f"{v:.1f}" for v in valores],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Condiciones Agrícolas Actuales",
            xaxis_title="Variables",
            yaxis_title="Valores",
            showlegend=False,
            height=400,
            template='plotly_white'
        )
        
        fig.update_yaxes(gridcolor='lightgray')
        
        return fig

    def mostrar_recomendaciones_agricolas(self, metricas):
        """Muestra recomendaciones agrícolas basadas en las métricas"""
        if not metricas:
            st.warning("No hay datos suficientes para generar recomendaciones")
            return
        
        st.subheader("🌱 Recomendaciones Agrícolas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Riesgo de Helada",
                metricas.get('riesgo_helada', 'N/A'),
                delta=None
            )
        
        with col2:
            st.metric(
                "Condición de Riego",
                metricas.get('condicion_riego', 'N/A'),
                delta=None
            )
        
        with col3:
            temp_prom = metricas.get('temperatura_promedio', 0)
            if temp_prom > 25:
                recomendacion = "🌡️ Temperatura alta - Aumentar riego"
            elif temp_prom < 10:
                recomendacion = "❄️ Temperatura baja - Proteger cultivos"
            else:
                recomendacion = "✅ Condiciones óptimas"
            
            st.metric("Recomendación General", recomendacion)

    def mostrar_alertas_heladas(self):
        """Muestra alertas de heladas"""
        st.subheader("❄️ Alertas de Heladas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Riesgo Alto",
                self.analisis_heladas['riesgo_alto'],
                delta=None
            )
        
        with col2:
            st.metric(
                "Temperatura Mínima",
                f"{self.analisis_heladas['temperatura_minima']}°C",
                delta=None
            )
        
        # Gráfico de riesgo de heladas
        riesgo_data = {
            'Riesgo Alto': self.analisis_heladas['riesgo_alto'],
            'Riesgo Medio': self.analisis_heladas['riesgo_medio'],
            'Riesgo Bajo': self.analisis_heladas['riesgo_bajo']
        }
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(riesgo_data.keys()),
                values=list(riesgo_data.values()),
                hole=0.4,
                marker_colors=['#FF6B6B', '#FFE66D', '#4ECDC4']
            )
        ])
        
        fig.update_layout(
            title="Distribución del Riesgo de Heladas",
            showlegend=True,
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, config=PLOTLY_CONFIG, width='stretch')

    def mostrar_dashboard(self):
        """Muestra el dashboard principal"""
        st.title("🌱 Dashboard Agrícola Avanzado - METGO 3D Quillota")
        st.markdown("**Sistema de Monitoreo Agrícola con Plotly Moderno**")
        
        # Obtener datos
        with st.spinner("Obteniendo datos meteorológicos..."):
            df_datos = self.obtener_datos_actuales()
        
        if df_datos.empty:
            st.warning("No hay datos disponibles. Mostrando datos simulados.")
        
        # Calcular métricas
        metricas = self.calcular_metricas_agricolas(df_datos)
        
        # Mostrar métricas principales
        st.subheader("📊 Métricas Principales")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Temperatura Promedio",
                f"{metricas.get('temperatura_promedio', 0):.1f}°C",
                delta=None
            )
        
        with col2:
            st.metric(
                "Temperatura Máxima",
                f"{metricas.get('temperatura_maxima', 0):.1f}°C",
                delta=None
            )
        
        with col3:
            st.metric(
                "Humedad Promedio",
                f"{metricas.get('humedad_promedio', 0):.1f}%",
                delta=None
            )
        
        with col4:
            st.metric(
                "Presión Promedio",
                f"{metricas.get('presion_promedio', 0):.1f} hPa",
                delta=None
            )
        
        # Gráficos principales
        st.subheader("📈 Visualizaciones")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_temp = self.crear_grafico_temperaturas_moderno(df_datos)
            if fig_temp:
                st.plotly_chart(fig_temp, config=PLOTLY_CONFIG, width='stretch')
        
        with col2:
            fig_hum = self.crear_grafico_humedad_moderno(df_datos)
            if fig_hum:
                st.plotly_chart(fig_hum, config=PLOTLY_CONFIG, width='stretch')
        
        # Gráfico de condiciones agrícolas
        fig_agri = self.crear_grafico_condiciones_agricolas(metricas)
        if fig_agri:
            st.plotly_chart(fig_agri, config=PLOTLY_CONFIG, width='stretch')
        
        # Recomendaciones y alertas
        self.mostrar_recomendaciones_agricolas(metricas)
        self.mostrar_alertas_heladas()
        
        # Información adicional
        st.subheader("ℹ️ Información del Sistema")
        st.info(f"""
        **Dashboard Agrícola con Plotly Moderno**
        - ✅ Configuración moderna de Plotly (sin warnings deprecated)
        - ✅ Visualizaciones interactivas mantenidas
        - ✅ Todas las funcionalidades originales preservadas
        - ✅ Mejor rendimiento y estabilidad
        """)

def main():
    """Función principal"""
    dashboard = DashboardAgricolaModerno()
    dashboard.mostrar_dashboard()

if __name__ == "__main__":
    main()

