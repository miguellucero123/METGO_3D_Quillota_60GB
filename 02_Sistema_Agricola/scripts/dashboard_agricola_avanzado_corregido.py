"""
DASHBOARD AGRÍCOLA AVANZADO CORREGIDO - METGO 3D QUILLOTA
Versión corregida con mejor manejo de errores y descarga de datos reales
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import os
from conector_apis_meteorologicas_reales import ConectorAPIsMeteorologicas

# Configuración de la página
st.set_page_config(
    page_title="METGO 3D - Dashboard Agrícola Avanzado",
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

class DashboardAgricolaAvanzadoCorregido:
    def __init__(self):
        self.conector_apis = ConectorAPIsMeteorologicas()
        self._inicializar_session_state()
    
    def _inicializar_session_state(self):
        """Inicializar variables de sesión"""
        if 'datos_meteorologicos' not in st.session_state:
            st.session_state.datos_meteorologicos = None
        if 'datos_reales_apis' not in st.session_state:
            st.session_state.datos_reales_apis = None
        if 'ultima_actualizacion' not in st.session_state:
            st.session_state.ultima_actualizacion = None
        if 'estado_descarga' not in st.session_state:
            st.session_state.estado_descarga = "Pendiente"
    
    def _obtener_datos_reales_apis(self):
        """Obtener datos reales de las APIs meteorológicas con mejor manejo de errores"""
        try:
            st.session_state.estado_descarga = "Descargando..."
            
            # Coordenadas de las 6 estaciones meteorológicas del Valle de Quillota
            estaciones = {
                "Quillota_Centro": {"lat": -32.8833, "lon": -71.2667},
                "La_Cruz": {"lat": -32.8167, "lon": -71.2167},
                "Nogales": {"lat": -32.7500, "lon": -71.2167},
                "San_Isidro": {"lat": -32.9167, "lon": -71.2333},
                "Pocochay": {"lat": -32.8500, "lon": -71.3000},
                "Valle_Hermoso": {"lat": -32.9333, "lon": -71.2833}
            }
            
            datos_reales = {}
            errores = []
            exitosos = 0
            
            # Crear barra de progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_estaciones = len(estaciones)
            
            for i, (nombre_estacion, coordenadas) in enumerate(estaciones.items()):
                try:
                    status_text.text(f"Descargando datos de {nombre_estacion}...")
                    
                    # Obtener datos de OpenMeteo
                    datos_estacion = self.conector_apis.obtener_datos_openmeteo_coordenadas(
                        coordenadas["lat"], 
                        coordenadas["lon"]
                    )
                    
                    if datos_estacion and isinstance(datos_estacion, dict):
                        datos_reales[nombre_estacion] = datos_estacion
                        exitosos += 1
                        st.success(f"✅ {nombre_estacion}: Datos obtenidos correctamente")
                    else:
                        errores.append(f"{nombre_estacion}: Datos vacíos o inválidos")
                        st.warning(f"⚠️ {nombre_estacion}: Datos vacíos o inválidos")
                        
                except Exception as e:
                    error_msg = f"{nombre_estacion}: {str(e)}"
                    errores.append(error_msg)
                    st.error(f"❌ {nombre_estacion}: {str(e)}")
                
                # Actualizar barra de progreso
                progress = (i + 1) / total_estaciones
                progress_bar.progress(progress)
            
            # Limpiar elementos temporales
            progress_bar.empty()
            status_text.empty()
            
            if datos_reales:
                st.session_state.datos_reales_apis = datos_reales
                st.session_state.ultima_actualizacion = datetime.now()
                st.session_state.estado_descarga = "Completado"
                
                # Mostrar resumen
                st.success(f"🌡️ Descarga completada: {exitosos}/{total_estaciones} estaciones exitosas")
                
                if errores:
                    st.warning(f"⚠️ {len(errores)} errores detectados:")
                    for error in errores:
                        st.text(f"   - {error}")
                
                return datos_reales
            else:
                st.session_state.estado_descarga = "Error"
                st.error("❌ No se pudieron obtener datos de ninguna estación")
                if errores:
                    st.error("Errores detallados:")
                    for error in errores:
                        st.text(f"   - {error}")
                return None
                
        except Exception as e:
            st.session_state.estado_descarga = "Error"
            st.error(f"❌ Error general obteniendo datos de APIs: {str(e)}")
            return None
    
    def _mostrar_resumen_datos(self, datos_reales):
        """Mostrar resumen de los datos obtenidos"""
        if not datos_reales:
            st.warning("No hay datos para mostrar")
            return
        
        st.subheader("📊 Resumen de Datos Meteorológicos")
        
        # Crear DataFrame con datos resumidos
        resumen_data = []
        
        for estacion, datos in datos_reales.items():
            if datos and isinstance(datos, dict):
                resumen_data.append({
                    "Estación": estacion.replace("_", " "),
                    "Temperatura (°C)": datos.get("temperatura_actual", "N/A"),
                    "Humedad (%)": datos.get("humedad_relativa", "N/A"),
                    "Presión (hPa)": datos.get("presion_atmosferica", "N/A"),
                    "Viento (km/h)": datos.get("velocidad_viento", "N/A"),
                    "Precipitación (mm)": datos.get("precipitacion", "N/A"),
                    "Última Actualización": datos.get("fecha_actualizacion", "N/A")
                })
        
        if resumen_data:
            df_resumen = pd.DataFrame(resumen_data)
            st.dataframe(df_resumen, width='stretch')
            
            # Mostrar estadísticas generales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                temp_vals = [float(d.get('temperatura_actual', 0)) for d in resumen_data if d.get('temperatura_actual', 'N/A') != 'N/A' and str(d.get('temperatura_actual', 'N/A')).replace('.', '').replace('-', '').isdigit()]
                st.metric("🌡️ Temp. Promedio", f"{np.mean(temp_vals):.1f}°C" if temp_vals else "N/A")
            
            with col2:
                hum_vals = [float(d.get('Humedad (%)', 0)) for d in resumen_data if d.get('Humedad (%)', 'N/A') != 'N/A' and str(d.get('Humedad (%)', 'N/A')).replace('.', '').replace('-', '').isdigit()]
                st.metric("💧 Humedad Promedio", f"{np.mean(hum_vals):.1f}%" if hum_vals else "N/A")
            
            with col3:
                pres_vals = [float(d.get('Presión (hPa)', 0)) for d in resumen_data if d.get('Presión (hPa)', 'N/A') != 'N/A' and str(d.get('Presión (hPa)', 'N/A')).replace('.', '').replace('-', '').isdigit()]
                st.metric("🌀 Presión Promedio", f"{np.mean(pres_vals):.1f} hPa" if pres_vals else "N/A")
            
            with col4:
                viento_vals = [float(d.get('Viento (km/h)', 0)) for d in resumen_data if d.get('Viento (km/h)', 'N/A') != 'N/A' and str(d.get('Viento (km/h)', 'N/A')).replace('.', '').replace('-', '').isdigit()]
                st.metric("💨 Viento Promedio", f"{np.mean(viento_vals):.1f} km/h" if viento_vals else "N/A")
    
    def _mostrar_graficos_temperatura(self, datos_reales):
        """Mostrar gráficos de temperatura por estación"""
        if not datos_reales:
            return
        
        st.subheader("🌡️ Análisis de Temperaturas por Estación")
        
        # Preparar datos para gráficos
        estaciones = []
        temperaturas = []
        humedades = []
        
        for estacion, datos in datos_reales.items():
            if datos and isinstance(datos, dict):
                temp = datos.get("temperatura_actual", None)
                hum = datos.get("humedad_relativa", None)
                
                if temp is not None and hum is not None:
                    estaciones.append(estacion.replace("_", " "))
                    temperaturas.append(float(temp))
                    humedades.append(float(hum))
        
        if estaciones:
            # Gráfico de barras de temperatura
            fig_temp = go.Figure(data=[
                go.Bar(
                    x=estaciones,
                    y=temperaturas,
                    name='Temperatura (°C)',
                    marker_color='red',
                    text=temperaturas,
                    textposition='auto'
                )
            ])
            
            fig_temp.update_layout(
                title='Temperatura Actual por Estación',
                xaxis_title='Estación',
                yaxis_title='Temperatura (°C)',
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_temp, config=PLOTLY_CONFIG, width='stretch')
            
            # Gráfico de dispersión temperatura vs humedad
            fig_scatter = go.Figure(data=go.Scatter(
                x=temperaturas,
                y=humedades,
                mode='markers+text',
                text=estaciones,
                textposition='top center',
                marker=dict(
                    size=10,
                    color=temperaturas,
                    colorscale='RdYlBu_r',
                    showscale=True,
                    colorbar=dict(title="Temperatura (°C)")
                ),
                name='Temperatura vs Humedad'
            ))
            
            fig_scatter.update_layout(
                title='Relación Temperatura vs Humedad por Estación',
                xaxis_title='Temperatura (°C)',
                yaxis_title='Humedad Relativa (%)',
                height=400
            )
            
            st.plotly_chart(fig_scatter, config=PLOTLY_CONFIG, width='stretch')
    
    def _mostrar_recomendaciones_agricolas(self, datos_reales):
        """Mostrar recomendaciones agrícolas basadas en los datos meteorológicos"""
        if not datos_reales:
            st.warning("No hay datos suficientes para generar recomendaciones")
            return
        
        st.subheader("🌱 Recomendaciones Agrícolas")
        
        # Calcular promedios regionales
        temp_valores = [float(d.get('temperatura_actual', 0)) for d in datos_reales.values() 
                       if d and isinstance(d, dict) and d.get('temperatura_actual', 'N/A') != 'N/A' and str(d.get('temperatura_actual', 'N/A')).replace('.', '').replace('-', '').isdigit()]
        hum_valores = [float(d.get('humedad_relativa', 0)) for d in datos_reales.values() 
                      if d and isinstance(d, dict) and d.get('humedad_relativa', 'N/A') != 'N/A' and str(d.get('humedad_relativa', 'N/A')).replace('.', '').replace('-', '').isdigit()]
        viento_valores = [float(d.get('velocidad_viento', 0)) for d in datos_reales.values() 
                         if d and isinstance(d, dict) and d.get('velocidad_viento', 'N/A') != 'N/A' and str(d.get('velocidad_viento', 'N/A')).replace('.', '').replace('-', '').isdigit()]
        
        temp_promedio = np.mean(temp_valores) if temp_valores else 0
        hum_promedio = np.mean(hum_valores) if hum_valores else 0
        viento_promedio = np.mean(viento_valores) if viento_valores else 0
        
        # Generar recomendaciones
        recomendaciones = []
        
        # Recomendaciones de riego
        if hum_promedio < 40:
            recomendaciones.append("🚿 **Riego**: Humedad baja detectada. Incrementar frecuencia de riego.")
        elif hum_promedio > 80:
            recomendaciones.append("⛔ **Riego**: Humedad alta. Reducir riego para evitar enfermedades.")
        else:
            recomendaciones.append("✅ **Riego**: Condiciones de humedad adecuadas.")
        
        # Recomendaciones de temperatura
        if temp_promedio < 5:
            recomendaciones.append("❄️ **Heladas**: Temperatura baja. Activar sistema de protección contra heladas.")
        elif temp_promedio > 35:
            recomendaciones.append("☀️ **Calor**: Temperatura alta. Incrementar riego y sombreado.")
        else:
            recomendaciones.append("🌡️ **Temperatura**: Condiciones térmicas favorables.")
        
        # Recomendaciones de viento
        if viento_promedio > 20:
            recomendaciones.append("💨 **Viento**: Vientos fuertes. Revisar estructuras y evitar aplicaciones.")
        else:
            recomendaciones.append("🌬️ **Viento**: Condiciones de viento favorables.")
        
        # Mostrar recomendaciones
        for i, rec in enumerate(recomendaciones, 1):
            st.info(f"{i}. {rec}")
        
        # Mostrar métricas actuales
        st.subheader("📊 Condiciones Actuales del Valle")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌡️ Temperatura", f"{temp_promedio:.1f}°C")
        
        with col2:
            st.metric("💧 Humedad", f"{hum_promedio:.1f}%")
        
        with col3:
            st.metric("💨 Viento", f"{viento_promedio:.1f} km/h")
        
        with col4:
            estado_general = "Favorable"
            if temp_promedio < 5 or temp_promedio > 35 or hum_promedio < 30 or viento_promedio > 25:
                estado_general = "Atención"
            st.metric("🎯 Estado", estado_general)
    
    def ejecutar(self):
        """Ejecutar el dashboard principal"""
        # Header principal
        st.title("🌱 METGO 3D - Dashboard Agrícola Avanzado")
        st.markdown("**Sistema Integral de Gestión Agrícola para el Valle de Quillota**")
        st.markdown("---")
        
        # Sidebar con controles
        with st.sidebar:
            st.header("🎛️ Controles del Sistema")
            
            # Estado actual
            st.subheader("📊 Estado Actual")
            st.text(f"Estado: {st.session_state.estado_descarga}")
            if st.session_state.ultima_actualizacion:
                st.text(f"Última actualización: {st.session_state.ultima_actualizacion.strftime('%H:%M:%S')}")
            
            st.markdown("---")
            
            # Botón para descargar datos
            if st.button("🔄 Descargar Datos Reales", width='stretch'):
                with st.spinner("Descargando datos meteorológicos..."):
                    self._obtener_datos_reales_apis()
            
            # Botón para limpiar datos
            if st.button("🗑️ Limpiar Datos", width='stretch'):
                st.session_state.datos_reales_apis = None
                st.session_state.estado_descarga = "Pendiente"
                st.rerun()
            
            st.markdown("---")
            
            # Información del sistema
            st.subheader("ℹ️ Información")
            st.info("""
            **Estaciones Monitoreadas:**
            - Quillota Centro
            - La Cruz
            - Nogales
            - San Isidro
            - Pocochay
            - Valle Hermoso
            
            **Fuente de Datos:**
            OpenMeteo API (Gratuita)
            """)
        
        # Contenido principal
        if st.session_state.datos_reales_apis:
            # Mostrar resumen de datos
            self._mostrar_resumen_datos(st.session_state.datos_reales_apis)
            
            st.markdown("---")
            
            # Mostrar gráficos
            self._mostrar_graficos_temperatura(st.session_state.datos_reales_apis)
            
            st.markdown("---")
            
            # Mostrar recomendaciones
            self._mostrar_recomendaciones_agricolas(st.session_state.datos_reales_apis)
            
        else:
            # Mostrar mensaje de bienvenida
            st.info("👆 Use el botón 'Descargar Datos Reales' en la barra lateral para comenzar")
            
            # Mostrar información sobre el sistema
            st.subheader("🌱 Sistema de Gestión Agrícola METGO 3D")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **Funcionalidades Principales:**
                - 📊 Monitoreo meteorológico en tiempo real
                - 🌡️ Análisis de temperaturas por estación
                - 💧 Control de humedad y riego
                - 💨 Monitoreo de vientos
                - 🌱 Recomendaciones agrícolas automáticas
                - 📈 Visualizaciones interactivas
                """)
            
            with col2:
                st.markdown("""
                **Beneficios:**
                - ⏰ Datos actualizados cada hora
                - 🎯 Recomendaciones personalizadas
                - 📱 Interfaz intuitiva y fácil de usar
                - 🔄 Actualización automática de datos
                - 📊 Reportes detallados por estación
                - 🌍 Cobertura completa del Valle de Quillota
                """)

def main():
    dashboard = DashboardAgricolaAvanzadoCorregido()
    dashboard.ejecutar()

if __name__ == "__main__":
    main()
