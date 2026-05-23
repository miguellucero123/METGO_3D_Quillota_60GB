#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Meteorológico METGO_3D - Script Principal Avanzado
Sistema completo de pronósticos meteorológicos con características avanzadas
Versión: 2.0
Autor: METGO_3D Team
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sqlite3
import requests
import time
from typing import Dict, List, Optional
import logging
import sys

# Agregar directorio de scripts al path para importar sistema de validación
sys.path.append('scripts')

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar sistema de validación avanzado
try:
    from validador_flexible import ValidadorFlexible
    from limpiador_datos_meteorologicos import LimpiadorDatosMeteorologicos
    from monitor_simple import MonitorSimple
    from sistema_alertas_automaticas import SistemaAlertas
    
    # Inicializar sistemas de validación
    validador = ValidadorFlexible()
    limpiador = LimpiadorDatosMeteorologicos()
    monitor = MonitorSimple()
    sistema_alertas = SistemaAlertas()
    
    SISTEMA_VALIDACION_ACTIVO = True
    SISTEMA_ALERTAS_ACTIVO = True
    logger.info("Sistema de validación avanzado y alertas cargados correctamente")
    
except ImportError as e:
    logger.warning(f"No se pudo cargar sistema de validación/alertas: {e}")
    SISTEMA_VALIDACION_ACTIVO = False
    SISTEMA_ALERTAS_ACTIVO = False

# Configuración de la página
st.set_page_config(
    page_title="METGO 3D - Sistema Meteorológico Avanzado",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de actualización automática
AUTO_REFRESH_INTERVAL = 300  # 5 minutos en segundos

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
</style>
""", unsafe_allow_html=True)

class GestorDatosMeteorologicos:
    """Gestor avanzado de datos meteorológicos"""
    
    def __init__(self):
        self.db_path = "scripts/datos_meteorologicos.db"
        self.api_keys_file = "scripts/api_keys_meteorologicas.json"
        self.datos_cache = {}
        self.ultima_actualizacion = None
        self.estado_validacion = None
    
    def cargar_datos(self) -> Dict:
        """Cargar datos desde múltiples fuentes con prioridad y validación"""
        datos = {}
        
        # 1. Intentar cargar desde base de datos local
        datos = self._cargar_desde_db()
        
        # 2. Si no hay datos locales, intentar APIs externas
        if not datos:
            datos = self._cargar_desde_api()
        
        # 3. Si todo falla, generar datos demo
        if not datos:
            datos = self._generar_datos_demo()
            st.warning("⚠️ Usando datos de demostración. Configura APIs para datos reales.")
        
        # 4. Validar datos si el sistema está disponible
        if SISTEMA_VALIDACION_ACTIVO and datos:
            self.estado_validacion = self._validar_datos(datos)
        
        self.datos_cache = datos
        self.ultima_actualizacion = datetime.now()
        return datos
    
    def _cargar_desde_db(self) -> Dict:
        """Cargar datos desde base de datos SQLite"""
        archivos_db = [
            "scripts/datos_meteorologicos.db",
            "scripts/datos_meteorologicos_reales.db",
            "datos/datos_meteorologicos.db"
        ]
        
        for db_path in archivos_db:
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    
                    # Verificar tablas disponibles
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tablas = [row[0] for row in cursor.fetchall()]
                    
                    if 'datos_meteorologicos' in tablas:
                        df = pd.read_sql_query("SELECT * FROM datos_meteorologicos ORDER BY fecha DESC LIMIT 100", conn)
                        conn.close()
                        return df.to_dict('records')
                    elif 'pronosticos' in tablas:
                        df = pd.read_sql_query("SELECT * FROM pronosticos ORDER BY fecha DESC LIMIT 100", conn)
                        conn.close()
                        return df.to_dict('records')
                        
                except Exception as e:
                    logger.error(f"Error cargando BD {db_path}: {e}")
                    continue
        
        return {}
    
    def _cargar_desde_api(self) -> Dict:
        """Cargar datos desde APIs meteorológicas externas"""
        try:
            if os.path.exists(self.api_keys_file):
                with open(self.api_keys_file, 'r') as f:
                    api_config = json.load(f)
                
                # Intentar OpenWeatherMap
                if 'openweathermap_key' in api_config:
                    return self._cargar_openweathermap(api_config['openweathermap_key'])
                
                # Intentar OpenMeteo
                return self._cargar_openmeteo()
                
        except Exception as e:
            logger.error(f"Error cargando desde API: {e}")
        
        return {}
    
    def _cargar_openweathermap(self, api_key: str) -> Dict:
        """Cargar datos desde OpenWeatherMap"""
        try:
            # Coordenadas de Quillota
            lat, lon = -32.8833, -71.2500
            
            url = f"http://api.openweathermap.org/data/2.5/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric',
                'lang': 'es'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            datos = []
            
            for item in data['list'][:40]:  # Próximos 5 días
                datos.append({
                    'fecha': item['dt_txt'],
                    'temperatura_max': item['main']['temp_max'],
                    'temperatura_min': item['main']['temp_min'],
                    'temperatura_promedio': item['main']['temp'],
                    'precipitacion': item.get('rain', {}).get('3h', 0),
                    'humedad': item['main']['humidity'],
                    'presion': item['main']['pressure'],
                    'viento_velocidad': item['wind']['speed'] * 3.6,  # m/s to km/h
                    'viento_direccion': self._convertir_direccion_viento(item['wind']['deg']),
                    'cobertura_nubosa': item['clouds']['all'],
                    'descripcion': item['weather'][0]['description']
                })
            
            return datos
            
        except Exception as e:
            logger.error(f"Error con OpenWeatherMap: {e}")
            return {}
    
    def _cargar_openmeteo(self) -> Dict:
        """Cargar datos desde OpenMeteo (API gratuita)"""
        try:
            # Coordenadas de Quillota
            lat, lon = -32.8833, -71.2500
            
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'hourly': 'temperature_2m,precipitation,relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m,cloud_cover',
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
                'timezone': 'America/Santiago',
                'forecast_days': 7
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            datos = []
            
            # Procesar datos diarios
            for i in range(len(data['daily']['time'])):
                datos.append({
                    'fecha': data['daily']['time'][i],
                    'temperatura_max': data['daily']['temperature_2m_max'][i],
                    'temperatura_min': data['daily']['temperature_2m_min'][i],
                    'temperatura_promedio': (data['daily']['temperature_2m_max'][i] + data['daily']['temperature_2m_min'][i]) / 2,
                    'precipitacion': data['daily']['precipitation_sum'][i],
                    'humedad': data['hourly']['relative_humidity_2m'][i*24] if i*24 < len(data['hourly']['relative_humidity_2m']) else 60,
                    'presion': data['hourly']['pressure_msl'][i*24] if i*24 < len(data['hourly']['pressure_msl']) else 1013,
                    'viento_velocidad': data['hourly']['wind_speed_10m'][i*24] * 3.6 if i*24 < len(data['hourly']['wind_speed_10m']) else 10,
                    'viento_direccion': self._convertir_direccion_viento(data['hourly']['wind_direction_10m'][i*24]) if i*24 < len(data['hourly']['wind_direction_10m']) else 'N',
                    'cobertura_nubosa': data['hourly']['cloud_cover'][i*24] if i*24 < len(data['hourly']['cloud_cover']) else 50
                })
            
            return datos
            
        except Exception as e:
            logger.error(f"Error con OpenMeteo: {e}")
            return {}
    
    def _convertir_direccion_viento(self, grados: float) -> str:
        """Convertir grados a dirección cardinal"""
        direcciones = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        index = int((grados + 22.5) / 45) % 8
        return direcciones[index]
    
    def _generar_datos_demo(self) -> Dict:
        """Generar datos de demostración realistas para Quillota"""
        np.random.seed(42)
        
        fechas = pd.date_range(start='2025-01-01', end='2025-01-30', freq='D')
        datos = []
        
        for i, fecha in enumerate(fechas):
            # Variación estacional para Quillota
            temp_base = 18 + 8 * np.sin(2 * np.pi * i / 365)
            temp_max = temp_base + np.random.normal(8, 3)
            temp_min = temp_base - np.random.normal(5, 2)
            
            # Precipitación más probable en invierno (mayo-agosto)
            prob_precip = 0.4 if fecha.month in [5, 6, 7, 8] else 0.1
            precipitacion = np.random.exponential(8) if np.random.random() < prob_precip else 0
            
            # Otros parámetros con variación realista
            humedad = np.random.normal(75, 15)
            presion = np.random.normal(1013, 15)
            viento_velocidad = np.random.exponential(12)
            viento_direccion = np.random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
            cobertura_nubosa = np.random.normal(45, 25)
            
            datos.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'temperatura_max': round(temp_max, 1),
                'temperatura_min': round(temp_min, 1),
                'temperatura_promedio': round((temp_max + temp_min) / 2, 1),
                'precipitacion': round(max(0, precipitacion), 1),
                'humedad': round(max(0, min(100, humedad)), 1),
                'presion': round(presion, 1),
                'viento_velocidad': round(max(0, viento_velocidad), 1),
                'viento_direccion': viento_direccion,
                'cobertura_nubosa': round(max(0, min(100, cobertura_nubosa)), 1),
                'descripcion': 'Datos de demostración'
            })
        
        return datos
    
    def actualizar_datos(self) -> bool:
        """Forzar actualización de datos"""
        try:
            datos_actualizados = self._cargar_desde_api()
            if datos_actualizados:
                self.datos_cache = datos_actualizados
                self.ultima_actualizacion = datetime.now()
                # Re-validar datos actualizados
                if SISTEMA_VALIDACION_ACTIVO:
                    self.estado_validacion = self._validar_datos(datos_actualizados)
                return True
        except Exception as e:
            logger.error(f"Error actualizando datos: {e}")
        return False
    
    def _validar_datos(self, datos: List[Dict]) -> Dict:
        """Validar datos usando el sistema de validación avanzado"""
        try:
            if not datos:
                return {'es_valido': False, 'puntuacion': 0, 'mensaje': 'No hay datos para validar'}
            
            # Convertir a DataFrame para validación
            df = pd.DataFrame(datos)
            
            # Mapear columnas al formato esperado por el validador
            mapeo_columnas = {
                'temperatura_max': 'temperatura_maxima',
                'temperatura_min': 'temperatura_minima', 
                'temperatura_promedio': 'temperatura_promedio',
                'precipitacion': 'precipitacion_diaria',
                'humedad': 'humedad_relativa',
                'presion': 'presion_atmosferica',
                'viento_velocidad': 'viento_velocidad',
                'viento_direccion': 'viento_direccion',
                'cobertura_nubosa': 'cobertura_nubosa',
                'fecha': 'timestamp'
            }
            
            # Renombrar columnas que existen
            for col_original, col_nuevo in mapeo_columnas.items():
                if col_original in df.columns:
                    df[col_nuevo] = df[col_original]
            
            # Validar con el sistema avanzado
            resultado = validador.validar_dataset_completo(df)
            
            return {
                'es_valido': resultado['porcentaje_validos'] >= 80,
                'puntuacion': resultado['puntuacion_promedio'],
                'porcentaje_validos': resultado['porcentaje_validos'],
                'total_registros': resultado['total_registros'],
                'errores': resultado.get('errores_mas_comunes', {}),
                'advertencias': resultado.get('advertencias_mas_comunes', {}),
                'mensaje': f"Calidad: {resultado['puntuacion_promedio']:.1f}/100"
            }
            
        except Exception as e:
            logger.error(f"Error en validación: {e}")
            return {'es_valido': False, 'puntuacion': 0, 'mensaje': f'Error: {e}'}
    
    def obtener_estado_validacion(self) -> Optional[Dict]:
        """Obtener el estado actual de validación"""
        return self.estado_validacion
    
    def ejecutar_monitoreo_calidad(self) -> Dict:
        """Ejecutar monitoreo de calidad de datos"""
        if not SISTEMA_VALIDACION_ACTIVO:
            return {'calidad': 50, 'alertas': 0, 'mensaje': 'Sistema de monitoreo no disponible'}
        
        try:
            resultado = monitor.ejecutar_monitoreo()
            if resultado['exito']:
                metricas = resultado['metricas']
                return {
                    'calidad': metricas['porcentaje_calidad'],
                    'alertas': resultado['alertas_generadas'],
                    'registros': metricas['total_registros'],
                    'errores': metricas['total_errores'],
                    'mensaje': f"Monitoreo completado: {metricas['porcentaje_calidad']:.1f}% calidad"
                }
            else:
                return {'calidad': 0, 'alertas': 1, 'mensaje': f"Error: {resultado['error']}"}
                
        except Exception as e:
            logger.error(f"Error en monitoreo: {e}")
            return {'calidad': 0, 'alertas': 1, 'mensaje': f'Error: {e}'}
    
    def procesar_alertas_automaticas(self) -> Dict:
        """Procesar y enviar alertas automáticas"""
        if not SISTEMA_ALERTAS_ACTIVO:
            return {'alertas_enviadas': 0, 'mensaje': 'Sistema de alertas no disponible'}
        
        try:
            # Obtener datos actuales
            datos_actuales = self.datos_cache[-1] if self.datos_cache else {}
            
            # Procesar alertas
            resultado = sistema_alertas.procesar_y_enviar_alertas(
                self.estado_validacion, 
                datos_actuales
            )
            
            return {
                'alertas_generadas': resultado['alertas_generadas'],
                'emails_enviados': resultado['emails_enviados'],
                'sms_enviados': resultado['sms_enviados'],
                'errores': resultado['errores'],
                'mensaje': f"Alertas procesadas: {resultado['alertas_generadas']}"
            }
            
        except Exception as e:
            logger.error(f"Error procesando alertas: {e}")
            return {'alertas_enviadas': 0, 'mensaje': f'Error: {e}'}
    
    def obtener_estadisticas_alertas(self) -> Dict:
        """Obtener estadísticas del sistema de alertas"""
        if not SISTEMA_ALERTAS_ACTIVO:
            return {'mensaje': 'Sistema de alertas no disponible'}
        
        try:
            return sistema_alertas.obtener_estadisticas_alertas()
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de alertas: {e}")
            return {'mensaje': f'Error: {e}'}

def generar_datos_demo():
    """Generar datos de demostración si no hay datos reales"""
    fechas = pd.date_range(start='2025-01-01', end='2025-01-30', freq='D')
    
    datos = []
    for fecha in fechas:
        datos.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'temperatura_max': np.random.normal(25, 5),
            'temperatura_min': np.random.normal(15, 3),
            'precipitacion': max(0, np.random.normal(2, 1)),
            'humedad': np.random.normal(60, 10),
            'presion': np.random.normal(1013, 10),
            'viento_velocidad': np.random.normal(10, 3),
            'viento_direccion': np.random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
        })
    
    return datos

def crear_dashboard_avanzado(gestor_datos: GestorDatosMeteorologicos):
    """Crear dashboard meteorológico avanzado"""
    
    # Título principal
    st.title("🌤️ Sistema Meteorológico METGO 3D - Avanzado")
    st.markdown("### Pronósticos y Análisis Climático para Quillota")
    
    # Cargar datos
    with st.spinner("Cargando datos meteorológicos..."):
        datos = gestor_datos.cargar_datos()
    
    if not datos:
        st.error("❌ No se pudieron cargar datos meteorológicos")
        return
    
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    
    # Sidebar con controles avanzados
    st.sidebar.header("🎛️ Panel de Control")
    
    # Selector de vista
    vistas_disponibles = ["📊 Dashboard Principal", "🌡️ Análisis de Temperaturas", "🌧️ Análisis de Precipitación", 
                         "💨 Análisis de Viento", "📈 Tendencias", "🔍 Análisis Detallado"]
    
    if SISTEMA_VALIDACION_ACTIVO:
        vistas_disponibles.append("🔍 Validación de Datos")
    
    if SISTEMA_ALERTAS_ACTIVO:
        vistas_disponibles.append("🚨 Sistema de Alertas")
    
    vista = st.sidebar.selectbox("Seleccionar vista", vistas_disponibles)
    
    # Filtros temporales
    st.sidebar.subheader("📅 Filtros Temporales")
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'])
        fecha_inicio = st.sidebar.date_input("Fecha inicio", df['fecha'].min().date())
        fecha_fin = st.sidebar.date_input("Fecha fin", df['fecha'].max().date())
        
        # Filtrar datos
        df_filtrado = df[(df['fecha'].dt.date >= fecha_inicio) & (df['fecha'].dt.date <= fecha_fin)]
    else:
        df_filtrado = df
    
    # Controles de actualización
    st.sidebar.subheader("🔄 Actualización")
    
    # Auto-refresh
    auto_refresh = st.sidebar.checkbox("🔄 Actualización Automática", value=False)
    if auto_refresh:
        st.sidebar.info(f"⏰ Actualizando cada {AUTO_REFRESH_INTERVAL//60} minutos")
        time.sleep(AUTO_REFRESH_INTERVAL)
        st.experimental_rerun()
    
    # Actualización manual
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Actualizar", type="primary"):
            with st.spinner("Actualizando datos..."):
                if gestor_datos.actualizar_datos():
                    st.sidebar.success("✅ Datos actualizados")
                    st.experimental_rerun()
                else:
                    st.sidebar.error("❌ Error actualizando datos")
    
    with col2:
        if st.button("🚨 Alertas"):
            with st.spinner("Procesando alertas..."):
                resultado = gestor_datos.procesar_alertas_automaticas()
                if resultado['alertas_generadas'] > 0:
                    st.sidebar.success(f"✅ {resultado['alertas_generadas']} alertas")
                else:
                    st.sidebar.info("ℹ️ Sin alertas")
    
    # Información del sistema
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Información del Sistema")
    st.sidebar.info(f"📊 Registros: {len(df)}")
    if gestor_datos.ultima_actualizacion:
        st.sidebar.info(f"🕒 Última actualización: {gestor_datos.ultima_actualizacion.strftime('%H:%M:%S')}")
    
    # Estado de validación
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Estado de Validación")
    
    if SISTEMA_VALIDACION_ACTIVO:
        estado_validacion = gestor_datos.obtener_estado_validacion()
        if estado_validacion:
            puntuacion = estado_validacion['puntuacion']
            es_valido = estado_validacion['es_valido']
            
            # Mostrar puntuación con color
            if puntuacion >= 90:
                st.sidebar.success(f"✅ Calidad Excelente: {puntuacion:.1f}/100")
            elif puntuacion >= 70:
                st.sidebar.warning(f"⚠️ Calidad Buena: {puntuacion:.1f}/100")
            else:
                st.sidebar.error(f"❌ Calidad Baja: {puntuacion:.1f}/100")
            
            # Mostrar detalles si hay errores
            if estado_validacion.get('errores'):
                with st.sidebar.expander("⚠️ Errores Detectados"):
                    for error, cantidad in list(estado_validacion['errores'].items())[:3]:
                        st.write(f"• {error}: {cantidad}")
        else:
            st.sidebar.info("🔄 Validación pendiente")
        
        # Botón para ejecutar monitoreo
        if st.sidebar.button("📊 Ejecutar Monitoreo"):
            with st.spinner("Ejecutando monitoreo..."):
                monitoreo = gestor_datos.ejecutar_monitoreo_calidad()
                st.sidebar.success(f"🎯 Calidad: {monitoreo['calidad']:.1f}%")
                if monitoreo['alertas'] > 0:
                    st.sidebar.warning(f"🚨 {monitoreo['alertas']} alertas activas")
    else:
        st.sidebar.warning("⚠️ Sistema de validación no disponible")
    
    # Dashboard Principal
    if vista == "📊 Dashboard Principal":
        mostrar_dashboard_principal(df_filtrado)
    elif vista == "🌡️ Análisis de Temperaturas":
        mostrar_analisis_temperaturas(df_filtrado)
    elif vista == "🌧️ Análisis de Precipitación":
        mostrar_analisis_precipitacion(df_filtrado)
    elif vista == "💨 Análisis de Viento":
        mostrar_analisis_viento(df_filtrado)
    elif vista == "📈 Tendencias":
        mostrar_tendencias(df_filtrado)
    elif vista == "🔍 Análisis Detallado":
        mostrar_analisis_detallado(df_filtrado)
    elif vista == "🔍 Validación de Datos":
        mostrar_validacion_datos(df_filtrado, gestor_datos)
    elif vista == "🚨 Sistema de Alertas":
        mostrar_sistema_alertas(df_filtrado, gestor_datos)

def mostrar_dashboard_principal(df):
    """Mostrar dashboard principal con métricas clave y tiempo real"""
    
    # Header con información de tiempo real
    st.markdown("### 📊 Dashboard Principal - Tiempo Real")
    
    # Información de última actualización
    ultima_fecha = df['fecha'].iloc[-1] if len(df) > 0 and 'fecha' in df.columns else datetime.now()
    st.info(f"🕒 Última actualización: {ultima_fecha.strftime('%d/%m/%Y %H:%M:%S') if hasattr(ultima_fecha, 'strftime') else ultima_fecha}")
    
    # Métricas principales mejoradas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if len(df) > 0:
            temp_actual = df['temperatura_promedio'].iloc[-1] if 'temperatura_promedio' in df.columns else 0
            temp_max = df['temperatura_max'].iloc[-1] if 'temperatura_max' in df.columns else 0
            temp_min = df['temperatura_min'].iloc[-1] if 'temperatura_min' in df.columns else 0
            
            # Calcular tendencia
            if len(df) > 1 and 'temperatura_promedio' in df.columns:
                tendencia_temp = temp_actual - df['temperatura_promedio'].iloc[-2]
                delta_temp = f"{tendencia_temp:+.1f}°C"
            else:
                delta_temp = f"Máx: {temp_max:.1f}°C / Mín: {temp_min:.1f}°C"
            
            st.metric(
                label="🌡️ Temperatura Actual",
                value=f"{temp_actual:.1f}°C",
                delta=delta_temp
            )
        else:
            st.metric("🌡️ Temperatura Actual", "N/A", "Sin datos")
    
    with col2:
        if len(df) > 0:
            precip_hoy = df['precipitacion'].iloc[-1] if 'precipitacion' in df.columns else 0
            precip_total = df['precipitacion'].sum() if 'precipitacion' in df.columns else 0
            
            # Calcular tendencia de precipitación
            if len(df) > 1 and 'precipitacion' in df.columns:
                tendencia_precip = precip_hoy - df['precipitacion'].iloc[-2]
                delta_precip = f"{tendencia_precip:+.1f} mm"
            else:
                delta_precip = f"Total: {precip_total:.1f} mm"
            
            st.metric(
                label="🌧️ Precipitación",
                value=f"{precip_hoy:.1f} mm",
                delta=delta_precip
            )
        else:
            st.metric("🌧️ Precipitación", "N/A", "Sin datos")
    
    with col3:
        if len(df) > 0:
            humedad = df['humedad'].iloc[-1] if 'humedad' in df.columns else 0
            
            # Calcular tendencia de humedad
            if len(df) > 1 and 'humedad' in df.columns:
                tendencia_humedad = humedad - df['humedad'].iloc[-2]
                delta_humedad = f"{tendencia_humedad:+.1f}%"
            else:
                estado_humedad = "Confortable" if 40 <= humedad <= 60 else "Extrema"
                delta_humedad = estado_humedad
            
            st.metric(
                label="💧 Humedad Relativa",
                value=f"{humedad:.1f}%",
                delta=delta_humedad
            )
        else:
            st.metric("💧 Humedad Relativa", "N/A", "Sin datos")
    
    with col4:
        if len(df) > 0:
            viento = df['viento_velocidad'].iloc[-1] if 'viento_velocidad' in df.columns else 0
            
            # Calcular tendencia de viento
            if len(df) > 1 and 'viento_velocidad' in df.columns:
                tendencia_viento = viento - df['viento_velocidad'].iloc[-2]
                delta_viento = f"{tendencia_viento:+.1f} km/h"
            else:
                estado_viento = "Calmo" if viento < 10 else "Moderado" if viento < 25 else "Fuerte"
                delta_viento = estado_viento
            
            st.metric(
                label="💨 Velocidad del Viento",
                value=f"{viento:.1f} km/h",
                delta=delta_viento
            )
        else:
            st.metric("💨 Velocidad del Viento", "N/A", "Sin datos")
    
    # Gráficos en tiempo real
    st.markdown("---")
    st.subheader("📈 Gráficos en Tiempo Real")
    
    # Seleccionar período para gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        periodo_grafico = st.selectbox(
            "Período de gráficos",
            ["Últimas 24 horas", "Últimos 7 días", "Últimos 30 días", "Todo el período"],
            index=1
        )
    
    with col2:
        tipo_grafico = st.selectbox(
            "Tipo de gráfico",
            ["Líneas", "Barras", "Área", "Scatter"],
            index=0
        )
    
    # Filtrar datos según período seleccionado
    if periodo_grafico == "Últimas 24 horas":
        df_grafico = df.tail(24) if len(df) >= 24 else df
    elif periodo_grafico == "Últimos 7 días":
        df_grafico = df.tail(7) if len(df) >= 7 else df
    elif periodo_grafico == "Últimos 30 días":
        df_grafico = df.tail(30) if len(df) >= 30 else df
    else:
        df_grafico = df
    
    # Crear gráficos dinámicos
    if len(df_grafico) > 0:
        crear_graficos_tiempo_real(df_grafico, tipo_grafico)
    else:
        st.warning("⚠️ No hay datos suficientes para mostrar gráficos")
    
    # Alertas en tiempo real
    st.markdown("---")
    st.subheader("🚨 Alertas en Tiempo Real")
    
    mostrar_alertas_tiempo_real(df)
        estado_humedad = "Confortable" if 40 <= humedad <= 60 else "Extrema"
        
    mostrar_alertas_tiempo_real(df)

def crear_graficos_tiempo_real(df, tipo_grafico):
    """Crear gráficos dinámicos en tiempo real"""
    
    if len(df) == 0:
        st.warning("No hay datos para mostrar gráficos")
        return
    
    # Preparar datos
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'])
        eje_x = 'fecha'
    else:
        eje_x = df.index
    
    # Gráfico de temperaturas
    if 'temperatura_max' in df.columns and 'temperatura_min' in df.columns:
        st.subheader("🌡️ Temperaturas")
        
        if tipo_grafico == "Líneas":
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(x=df[eje_x], y=df['temperatura_max'], 
                                        name='Máxima', line=dict(color='red', width=2)))
            fig_temp.add_trace(go.Scatter(x=df[eje_x], y=df['temperatura_min'], 
                                        name='Mínima', line=dict(color='blue', width=2)))
            if 'temperatura_promedio' in df.columns:
                fig_temp.add_trace(go.Scatter(x=df[eje_x], y=df['temperatura_promedio'], 
                                            name='Promedio', line=dict(color='green', width=2)))
        
        elif tipo_grafico == "Área":
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(x=df[eje_x], y=df['temperatura_max'], 
                                        fill='tonexty', name='Máxima', line=dict(color='red')))
            fig_temp.add_trace(go.Scatter(x=df[eje_x], y=df['temperatura_min'], 
                                        fill='tozeroy', name='Mínima', line=dict(color='blue')))
        
        elif tipo_grafico == "Barras":
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Bar(x=df[eje_x], y=df['temperatura_max'], name='Máxima', marker_color='red'))
            fig_temp.add_trace(go.Bar(x=df[eje_x], y=df['temperatura_min'], name='Mínima', marker_color='blue'))
        
        else:  # Scatter
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(x=df[eje_x], y=df['temperatura_max'], 
                                        mode='markers', name='Máxima', marker=dict(color='red', size=8)))
            fig_temp.add_trace(go.Scatter(x=df[eje_x], y=df['temperatura_min'], 
                                        mode='markers', name='Mínima', marker=dict(color='blue', size=8)))
        
        fig_temp.update_layout(
            title="Temperaturas en Tiempo Real",
            xaxis_title="Tiempo",
            yaxis_title="Temperatura (°C)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
    
    # Gráfico de precipitación
    if 'precipitacion' in df.columns:
        st.subheader("🌧️ Precipitación")
        
        if tipo_grafico == "Barras":
            fig_precip = px.bar(df, x=eje_x, y='precipitacion', 
                              title="Precipitación Diaria",
                              color='precipitacion',
                              color_continuous_scale='Blues')
        elif tipo_grafico == "Área":
            fig_precip = px.area(df, x=eje_x, y='precipitacion', 
                               title="Precipitación Acumulada")
        else:
            fig_precip = px.line(df, x=eje_x, y='precipitacion', 
                               title="Precipitación en Tiempo Real")
        
        fig_precip.update_layout(height=300)
        st.plotly_chart(fig_precip, use_container_width=True)
    
    # Gráfico combinado de humedad y viento
    if 'humedad' in df.columns and 'viento_velocidad' in df.columns:
        st.subheader("💧 Humedad y Viento")
        
        fig_combo = go.Figure()
        
        # Humedad (eje izquierdo)
        fig_combo.add_trace(go.Scatter(x=df[eje_x], y=df['humedad'], 
                                     name='Humedad (%)', 
                                     line=dict(color='green', width=2),
                                     yaxis='y'))
        
        # Viento (eje derecho)
        fig_combo.add_trace(go.Scatter(x=df[eje_x], y=df['viento_velocidad'], 
                                     name='Viento (km/h)', 
                                     line=dict(color='purple', width=2),
                                     yaxis='y2'))
        
        fig_combo.update_layout(
            title="Humedad y Velocidad del Viento",
            xaxis_title="Tiempo",
            yaxis=dict(title="Humedad (%)", side="left"),
            yaxis2=dict(title="Velocidad del Viento (km/h)", side="right", overlaying="y"),
            height=400
        )
        
        st.plotly_chart(fig_combo, use_container_width=True)

def mostrar_alertas_tiempo_real(df):
    """Mostrar alertas en tiempo real basadas en datos actuales"""
    
    if len(df) == 0:
        st.warning("No hay datos para evaluar alertas")
        return
    
    datos_actuales = df.iloc[-1].to_dict()
    alertas = []
    
    # Evaluar alertas de temperatura
    if 'temperatura_max' in datos_actuales and datos_actuales['temperatura_max'] >= 35:
        alertas.append({
            'tipo': 'temperatura_extrema',
            'severidad': 'alta',
            'mensaje': f"🌡️ Temperatura extrema: {datos_actuales['temperatura_max']:.1f}°C",
            'color': 'red'
        })
    
    if 'temperatura_min' in datos_actuales and datos_actuales['temperatura_min'] <= -2:
        alertas.append({
            'tipo': 'helada',
            'severidad': 'critica',
            'mensaje': f"🧊 Riesgo de helada: {datos_actuales['temperatura_min']:.1f}°C",
            'color': 'red'
        })
    
    # Evaluar alertas de precipitación
    if 'precipitacion' in datos_actuales and datos_actuales['precipitacion'] >= 20:
        alertas.append({
            'tipo': 'precipitacion_intensa',
            'severidad': 'alta',
            'mensaje': f"🌧️ Precipitación intensa: {datos_actuales['precipitacion']:.1f} mm",
            'color': 'orange'
        })
    
    # Evaluar alertas de viento
    if 'viento_velocidad' in datos_actuales and datos_actuales['viento_velocidad'] >= 25:
        alertas.append({
            'tipo': 'viento_fuerte',
            'severidad': 'media',
            'mensaje': f"💨 Viento fuerte: {datos_actuales['viento_velocidad']:.1f} km/h",
            'color': 'yellow'
        })
    
    # Evaluar alertas de humedad
    if 'humedad' in datos_actuales:
        humedad = datos_actuales['humedad']
        if humedad <= 30:
            alertas.append({
                'tipo': 'humedad_baja',
                'severidad': 'media',
                'mensaje': f"🏜️ Humedad muy baja: {humedad:.1f}%",
                'color': 'orange'
            })
        elif humedad >= 85:
            alertas.append({
                'tipo': 'humedad_alta',
                'severidad': 'media',
                'mensaje': f"💧 Humedad muy alta: {humedad:.1f}%",
                'color': 'blue'
            })
    
    # Mostrar alertas
    if alertas:
        for alerta in alertas:
            if alerta['severidad'] == 'critica':
                st.error(alerta['mensaje'])
            elif alerta['severidad'] == 'alta':
                st.warning(alerta['mensaje'])
            else:
                st.info(alerta['mensaje'])
    else:
        st.success("✅ Condiciones meteorológicas normales - Sin alertas activas")
    
    # Mostrar recomendaciones agrícolas
    st.markdown("### 🌱 Recomendaciones Agrícolas")
    
    recomendaciones = []
    
    if 'temperatura_min' in datos_actuales and datos_actuales['temperatura_min'] <= 5:
        recomendaciones.append("❄️ **Protección contra heladas:** Cubrir cultivos sensibles")
    
    if 'precipitacion' in datos_actuales and datos_actuales['precipitacion'] >= 10:
        recomendaciones.append("🌧️ **Drenaje:** Verificar sistemas de drenaje")
    
    if 'viento_velocidad' in datos_actuales and datos_actuales['viento_velocidad'] >= 20:
        recomendaciones.append("💨 **Estructuras:** Revisar soportes y estructuras")
    
    if 'humedad' in datos_actuales and datos_actuales['humedad'] <= 40:
        recomendaciones.append("💧 **Riego:** Considerar riego suplementario")
    
    if recomendaciones:
        for rec in recomendaciones:
            st.write(rec)
    else:
        st.info("🌱 Condiciones favorables para actividades agrícolas")

def main():
        direccion = df['viento_direccion'].iloc[-1] if len(df) > 0 else 'N'
        
        st.metric(
            label="💨 Viento",
            value=f"{viento:.1f} km/h",
            delta=direccion
        )
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de temperaturas
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(x=df['fecha'], y=df['temperatura_max'], 
                                    mode='lines+markers', name='Máxima', line=dict(color='red', width=3)))
        fig_temp.add_trace(go.Scatter(x=df['fecha'], y=df['temperatura_min'], 
                                    mode='lines+markers', name='Mínima', line=dict(color='blue', width=3)))
        fig_temp.add_trace(go.Scatter(x=df['fecha'], y=df['temperatura_promedio'], 
                                    mode='lines+markers', name='Promedio', line=dict(color='green', width=2, dash='dash')))
        
        fig_temp.update_layout(
            title='🌡️ Evolución de Temperaturas',
            xaxis_title='Fecha',
            yaxis_title='Temperatura (°C)',
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        # Gráfico de precipitación
        fig_precip = go.Figure()
        fig_precip.add_trace(go.Bar(
            x=df['fecha'], 
            y=df['precipitacion'],
            name='Precipitación',
            marker=dict(
                color=df['precipitacion'],
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title="mm")
            )
        ))
        
        fig_precip.update_layout(
            title='🌧️ Precipitación Diaria',
            xaxis_title='Fecha',
            yaxis_title='Precipitación (mm)',
            height=400
        )
        st.plotly_chart(fig_precip, use_container_width=True)
    
    # Alertas meteorológicas
    st.subheader("🚨 Alertas Meteorológicas")
    mostrar_alertas(df)

def mostrar_analisis_temperaturas(df):
    """Mostrar análisis detallado de temperaturas"""
    st.subheader("🌡️ Análisis de Temperaturas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Estadísticas de temperatura
        st.markdown("#### 📊 Estadísticas")
        temp_stats = {
            'Máxima registrada': f"{df['temperatura_max'].max():.1f}°C",
            'Mínima registrada': f"{df['temperatura_min'].min():.1f}°C",
            'Promedio general': f"{df['temperatura_promedio'].mean():.1f}°C",
            'Amplitud térmica promedio': f"{df['temperatura_max'].mean() - df['temperatura_min'].mean():.1f}°C",
            'Días con temp > 30°C': f"{(df['temperatura_max'] > 30).sum()} días",
            'Días con temp < 10°C': f"{(df['temperatura_min'] < 10).sum()} días"
        }
        
        for key, value in temp_stats.items():
            st.metric(key, value)
    
    with col2:
        # Distribución de temperaturas
        fig_hist = px.histogram(
            df, 
            x='temperatura_promedio',
            nbins=20,
            title='Distribución de Temperaturas Promedio',
            labels={'temperatura_promedio': 'Temperatura (°C)', 'count': 'Frecuencia'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)

def mostrar_analisis_precipitacion(df):
    """Mostrar análisis detallado de precipitación"""
    st.subheader("🌧️ Análisis de Precipitación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Estadísticas de precipitación
        st.markdown("#### 📊 Estadísticas")
        precip_stats = {
            'Total acumulado': f"{df['precipitacion'].sum():.1f} mm",
            'Días con lluvia': f"{(df['precipitacion'] > 0).sum()} días",
            'Intensidad máxima': f"{df['precipitacion'].max():.1f} mm/día",
            'Precipitación promedio': f"{df['precipitacion'].mean():.1f} mm/día",
            'Días secos consecutivos': calcular_dias_secos_consecutivos(df['precipitacion']),
            'Lluvias intensas (>10mm)': f"{(df['precipitacion'] > 10).sum()} días"
        }
        
        for key, value in precip_stats.items():
            st.metric(key, value)
    
    with col2:
        # Gráfico de precipitación acumulada
        df['precip_acumulada'] = df['precipitacion'].cumsum()
        
        fig_acum = px.area(
            df, 
            x='fecha', 
            y='precip_acumulada',
            title='Precipitación Acumulada',
            labels={'precip_acumulada': 'Precipitación Acumulada (mm)'}
        )
        st.plotly_chart(fig_acum, use_container_width=True)

def mostrar_analisis_viento(df):
    """Mostrar análisis detallado de viento"""
    st.subheader("💨 Análisis de Viento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Estadísticas de viento
        st.markdown("#### 📊 Estadísticas")
        viento_stats = {
            'Velocidad promedio': f"{df['viento_velocidad'].mean():.1f} km/h",
            'Velocidad máxima': f"{df['viento_velocidad'].max():.1f} km/h",
            'Días ventosos (>20 km/h)': f"{(df['viento_velocidad'] > 20).sum()} días",
            'Días con viento fuerte (>40 km/h)': f"{(df['viento_velocidad'] > 40).sum()} días"
        }
        
        for key, value in viento_stats.items():
            st.metric(key, value)
    
    with col2:
        # Rosa de vientos
        direcciones = df['viento_direccion'].value_counts()
        
        fig_rosa = go.Figure(data=[go.Pie(
            labels=direcciones.index,
            values=direcciones.values,
            hole=0.3
        )])
        fig_rosa.update_layout(title='Distribución de Direcciones de Viento')
        st.plotly_chart(fig_rosa, use_container_width=True)

def mostrar_tendencias(df):
    """Mostrar análisis de tendencias"""
    st.subheader("📈 Análisis de Tendencias")
    
    # Calcular tendencias
    if len(df) > 1:
        tendencia_temp = np.polyfit(range(len(df)), df['temperatura_promedio'], 1)[0]
        tendencia_precip = np.polyfit(range(len(df)), df['precipitacion'], 1)[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            if tendencia_temp > 0:
                st.success(f"📈 Tendencia de temperatura: +{tendencia_temp:.3f}°C/día")
            else:
                st.info(f"📉 Tendencia de temperatura: {tendencia_temp:.3f}°C/día")
        
        with col2:
            if tendencia_precip > 0:
                st.success(f"📈 Tendencia de precipitación: +{tendencia_precip:.3f} mm/día")
            else:
                st.info(f"📉 Tendencia de precipitación: {tendencia_precip:.3f} mm/día")

def mostrar_analisis_detallado(df):
    """Mostrar análisis detallado con todos los datos"""
    st.subheader("🔍 Análisis Detallado")
    
    # Tabla completa de datos
    st.markdown("#### 📊 Datos Completos")
    st.dataframe(df, use_container_width=True)
    
    # Correlaciones
    if len(df) > 1:
        st.markdown("#### 🔗 Correlaciones entre Variables")
        variables_numericas = df.select_dtypes(include=[np.number]).columns
        if len(variables_numericas) > 1:
            correlaciones = df[variables_numericas].corr()
            
            fig_corr = px.imshow(
                correlaciones,
                text_auto=True,
                aspect="auto",
                title="Matriz de Correlaciones"
            )
            st.plotly_chart(fig_corr, use_container_width=True)

def mostrar_alertas(df):
    """Mostrar alertas meteorológicas basadas en los datos"""
    alertas = []
    
    # Alertas de temperatura
    if len(df) > 0:
        temp_actual = df['temperatura_max'].iloc[-1]
        if temp_actual > 35:
            alertas.append("🔴 **Temperatura alta** - Riesgo de estrés térmico")
        elif temp_actual > 30:
            alertas.append("🟠 **Temperatura elevada** - Monitorear condiciones")
        
        # Alertas de precipitación
        precip_hoy = df['precipitacion'].iloc[-1]
        if precip_hoy > 20:
            alertas.append("🔴 **Lluvia intensa** - Posible encharcamiento")
        elif precip_hoy > 10:
            alertas.append("🟠 **Lluvia moderada** - Precauciones necesarias")
        
        # Alertas de viento
        viento = df['viento_velocidad'].iloc[-1]
        if viento > 40:
            alertas.append("🔴 **Viento fuerte** - Riesgo de daños")
        elif viento > 25:
            alertas.append("🟠 **Viento moderado** - Precauciones en actividades al aire libre")
        
        # Alertas de humedad
        humedad = df['humedad'].iloc[-1]
        if humedad > 80:
            alertas.append("🟠 **Alta humedad** - Condiciones húmedas")
        elif humedad < 30:
            alertas.append("🟠 **Baja humedad** - Condiciones secas")
    
    if alertas:
        for alerta in alertas:
            st.warning(alerta)
    else:
        st.success("✅ **Condiciones meteorológicas normales**")

def calcular_dias_secos_consecutivos(precipitacion):
    """Calcular días secos consecutivos"""
    dias_secos = 0
    for precip in reversed(precipitacion):
        if precip == 0:
            dias_secos += 1
        else:
            break
    return f"{dias_secos} días"

def mostrar_validacion_datos(df, gestor_datos):
    """Mostrar vista de validación de datos"""
    
    st.header("🔍 Validación de Datos Meteorológicos")
    st.markdown("### Análisis de Calidad y Consistencia de Datos")
    
    # Estado actual de validación
    estado_validacion = gestor_datos.obtener_estado_validacion()
    
    if estado_validacion:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            puntuacion = estado_validacion['puntuacion']
            if puntuacion >= 90:
                st.success(f"✅ Calidad Excelente\n{puntuacion:.1f}/100")
            elif puntuacion >= 70:
                st.warning(f"⚠️ Calidad Buena\n{puntuacion:.1f}/100")
            else:
                st.error(f"❌ Calidad Baja\n{puntuacion:.1f}/100")
        
        with col2:
            registros_validos = estado_validacion.get('total_registros', 0)
            porcentaje_validos = estado_validacion.get('porcentaje_validos', 0)
            st.info(f"📊 Registros Válidos\n{porcentaje_validos:.1f}% ({registros_validos})")
        
        with col3:
            errores = len(estado_validacion.get('errores', {}))
            advertencias = len(estado_validacion.get('advertencias', {}))
            st.info(f"⚠️ Problemas Detectados\n{errores} errores, {advertencias} advertencias")
        
        # Detalles de errores
        if estado_validacion.get('errores'):
            st.subheader("🚨 Errores Detectados")
            errores_df = pd.DataFrame([
                {'Tipo de Error': error, 'Cantidad': cantidad}
                for error, cantidad in estado_validacion['errores'].items()
            ])
            st.dataframe(errores_df, use_container_width=True)
        
        # Detalles de advertencias
        if estado_validacion.get('advertencias'):
            st.subheader("⚠️ Advertencias")
            advertencias_df = pd.DataFrame([
                {'Tipo de Advertencia': advertencia, 'Cantidad': cantidad}
                for advertencia, cantidad in estado_validacion['advertencias'].items()
            ])
            st.dataframe(advertencias_df, use_container_width=True)
    
    else:
        st.warning("⚠️ No hay información de validación disponible")
    
    # Monitoreo en tiempo real
    st.subheader("📊 Monitoreo en Tiempo Real")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Ejecutar Validación Completa", type="primary"):
            with st.spinner("Ejecutando validación..."):
                # Re-validar datos actuales
                datos_actuales = df.to_dict('records')
                nuevo_estado = gestor_datos._validar_datos(datos_actuales)
                gestor_datos.estado_validacion = nuevo_estado
                st.success("✅ Validación completada")
                st.experimental_rerun()
    
    with col2:
        if st.button("📊 Ejecutar Monitoreo de Calidad"):
            with st.spinner("Ejecutando monitoreo..."):
                monitoreo = gestor_datos.ejecutar_monitoreo_calidad()
                
                st.success(f"🎯 Calidad General: {monitoreo['calidad']:.1f}%")
                
                if monitoreo.get('registros'):
                    st.info(f"📊 Registros Monitoreados: {monitoreo['registros']}")
                
                if monitoreo.get('errores'):
                    st.warning(f"❌ Errores Detectados: {monitoreo['errores']}")
                
                if monitoreo.get('alertas', 0) > 0:
                    st.error(f"🚨 Alertas Activas: {monitoreo['alertas']}")
    
    # Recomendaciones
    st.subheader("💡 Recomendaciones")
    
    if estado_validacion:
        puntuacion = estado_validacion['puntuacion']
        
        if puntuacion >= 90:
            st.success("✅ Excelente calidad de datos. El sistema está funcionando óptimamente.")
        elif puntuacion >= 70:
            st.warning("⚠️ Buena calidad de datos. Monitorear regularmente para mantener la calidad.")
        else:
            st.error("❌ Calidad de datos baja. Se recomienda:")
            st.write("• Ejecutar limpieza de datos: `python scripts/limpiador_datos_meteorologicos.py`")
            st.write("• Revisar fuentes de datos")
            st.write("• Configurar monitoreo automático")
    
    # Información técnica
    with st.expander("🔧 Información Técnica"):
        st.write("**Sistema de Validación:**")
        st.write(f"• Validador Flexible: {'✅ Activo' if SISTEMA_VALIDACION_ACTIVO else '❌ Inactivo'}")
        st.write(f"• Limpiador de Datos: {'✅ Disponible' if SISTEMA_VALIDACION_ACTIVO else '❌ No disponible'}")
        st.write(f"• Monitor de Calidad: {'✅ Activo' if SISTEMA_VALIDACION_ACTIVO else '❌ Inactivo'}")
        
        st.write("**Configuración:**")
        st.write(f"• Registros en memoria: {len(df)}")
        st.write(f"• Última actualización: {gestor_datos.ultima_actualizacion.strftime('%Y-%m-%d %H:%M:%S') if gestor_datos.ultima_actualizacion else 'N/A'}")

def mostrar_sistema_alertas(df, gestor_datos):
    """Mostrar vista del sistema de alertas"""
    
    st.header("🚨 Sistema de Alertas Automáticas")
    st.markdown("### Gestión de Notificaciones Meteorológicas")
    
    # Estado del sistema de alertas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if SISTEMA_ALERTAS_ACTIVO:
            st.success("✅ Sistema de Alertas Activo")
        else:
            st.error("❌ Sistema de Alertas Inactivo")
    
    with col2:
        stats_alertas = gestor_datos.obtener_estadisticas_alertas()
        if 'total_alertas_24h' in stats_alertas:
            st.info(f"📊 Alertas últimas 24h: {stats_alertas['total_alertas_24h']}")
        else:
            st.info("📊 Sin datos de alertas")
    
    with col3:
        if 'configuracion' in stats_alertas:
            config = stats_alertas['configuracion']
            email_status = "✅" if config['email_habilitado'] else "❌"
            sms_status = "✅" if config['sms_habilitado'] else "❌"
            st.info(f"📧 Email: {email_status} | 📱 SMS: {sms_status}")
    
    # Panel de control de alertas
    st.subheader("🎛️ Panel de Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚨 Procesar Alertas Automáticas", type="primary"):
            with st.spinner("Procesando alertas..."):
                resultado = gestor_datos.procesar_alertas_automaticas()
                
                if resultado['alertas_generadas'] > 0:
                    st.success(f"✅ {resultado['mensaje']}")
                    st.info(f"📧 Emails enviados: {resultado['emails_enviados']}")
                    st.info(f"📱 SMS enviados: {resultado['sms_enviados']}")
                else:
                    st.info("ℹ️ No se generaron alertas")
                
                if resultado.get('errores'):
                    st.error(f"❌ Errores: {resultado['errores']}")
    
    with col2:
        if st.button("📊 Ver Estadísticas de Alertas"):
            with st.spinner("Cargando estadísticas..."):
                stats = gestor_datos.obtener_estadisticas_alertas()
                
                if 'total_alertas_24h' in stats:
                    st.success(f"📊 Alertas últimas 24h: {stats['total_alertas_24h']}")
                    st.info(f"📈 Alertas última semana: {stats['total_alertas_semana']}")
                    
                    if 'tipos_alertas_24h' in stats and stats['tipos_alertas_24h']:
                        st.write("**Tipos de alertas (24h):**")
                        for tipo, cantidad in stats['tipos_alertas_24h'].items():
                            st.write(f"• {tipo}: {cantidad}")
                else:
                    st.warning("⚠️ No hay estadísticas disponibles")
    
    # Configuración de alertas
    st.subheader("⚙️ Configuración de Alertas")
    
    with st.expander("📧 Configuración de Email"):
        st.write("**Estado:** Email no configurado")
        st.write("**Para configurar:**")
        st.write("1. Editar `scripts/config_alertas.json`")
        st.write("2. Configurar credenciales SMTP")
        st.write("3. Agregar destinatarios")
        st.write("4. Habilitar email en configuración")
    
    with st.expander("📱 Configuración de SMS"):
        st.write("**Estado:** SMS no configurado")
        st.write("**Para configurar:**")
        st.write("1. Obtener API key de Twilio")
        st.write("2. Editar `scripts/config_alertas.json`")
        st.write("3. Configurar número de origen")
        st.write("4. Agregar números de destino")
    
    # Tipos de alertas disponibles
    st.subheader("🔔 Tipos de Alertas Disponibles")
    
    tipos_alertas = [
        ("🌡️ Temperatura Extrema", "Temperaturas superiores a 35°C o inferiores a -2°C"),
        ("🌧️ Precipitación Intensa", "Precipitación superior a 20mm"),
        ("💨 Viento Fuerte", "Velocidad de viento superior a 25 km/h"),
        ("💧 Humedad Crítica", "Humedad muy baja (<30%) o muy alta (>85%)"),
        ("📊 Calidad de Datos", "Calidad de datos inferior a 70/100"),
        ("❌ Errores Críticos", "Múltiples errores en los datos meteorológicos")
    ]
    
    for tipo, descripcion in tipos_alertas:
        st.write(f"**{tipo}:** {descripcion}")
    
    # Historial de alertas
    st.subheader("📋 Historial de Alertas")
    
    try:
        # Buscar archivos de historial
        import glob
        archivos_historial = glob.glob("alertas/historial_alertas_*.json")
        
        if archivos_historial:
            # Mostrar el archivo más reciente
            archivo_mas_reciente = max(archivos_historial)
            
            with open(archivo_mas_reciente, 'r', encoding='utf-8') as f:
                historial = json.load(f)
            
            if historial:
                st.write(f"**Archivo:** {archivo_mas_reciente}")
                st.write(f"**Total de alertas:** {len(historial)}")
                
                # Mostrar últimas 5 alertas
                ultimas_alertas = historial[-5:]
                
                for alerta in reversed(ultimas_alertas):
                    timestamp = datetime.fromisoformat(alerta['timestamp'])
                    st.write(f"**{timestamp.strftime('%d/%m/%Y %H:%M')}** - {alerta['titulo']}")
                    st.write(f"   {alerta['mensaje']}")
                    st.write("---")
            else:
                st.info("No hay alertas en el historial")
        else:
            st.info("No se encontraron archivos de historial de alertas")
            
    except Exception as e:
        st.error(f"Error cargando historial: {e}")
    
    # Información técnica
    with st.expander("🔧 Información Técnica"):
        st.write("**Sistema de Alertas:**")
        st.write(f"• Estado: {'✅ Activo' if SISTEMA_ALERTAS_ACTIVO else '❌ Inactivo'}")
        st.write(f"• Configuración: scripts/config_alertas.json")
        st.write(f"• Logs: logs/sistema_alertas.log")
        st.write(f"• Historial: alertas/historial_alertas_*.json")
        
        if SISTEMA_ALERTAS_ACTIVO:
            st.write("**Funcionalidades:**")
            st.write("• Alertas por email (SMTP)")
            st.write("• Alertas por SMS (Twilio)")
            st.write("• Control de frecuencia")
            st.write("• Historial de alertas")
            st.write("• Configuración flexible")

def main():
    """Función principal del sistema meteorológico avanzado"""
    
    # Inicializar gestor de datos
    gestor_datos = GestorDatosMeteorologicos()
    
    # Crear dashboard
    crear_dashboard_avanzado(gestor_datos)

if __name__ == "__main__":
    main()
