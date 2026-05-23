#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA UNIFICADO CON CONECTORES - METGO 3D
Sistema Completo con Integracion de Todos los Conectores Identificados
"""

import streamlit as st
import sys
import os
import json
import yaml
import sqlite3
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime, timedelta
import logging
import subprocess
import threading
import time
from typing import Dict, List, Any, Optional

# Importar modulos propios
from auth_module import SistemaAutenticacion
from integrador_modulos import IntegradorModulos
from conectores_especificos_metgo import ConectoresEspecificosMETGO
from conector_iot_satelital import ConectorSensoresIoT, ConectorDatosSatelitales
from conector_monitoreo_respaldos import ConectorMonitoreo, ConectorRespaldos
from conector_apis_avanzadas import ConectorAPIsAvanzadas

# Configuracion
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SISTEMA_UNIFICADO_CON_CONECTORES')

class ConectorDatosMeteorologicos:
    """Conector para datos meteorologicos"""
    
    def __init__(self):
        self.config = {
            'openmeteo': {
                'url_base': 'https://api.open-meteo.com/v1',
                'timeout': 30,
                'max_retries': 3
            },
            'openweather': {
                'url_base': 'https://api.openweathermap.org/data/2.5',
                'timeout': 30,
                'max_retries': 3
            }
        }
        self.quillota_coords = {'lat': -32.8833, 'lon': -71.25}
    
    def obtener_datos_openmeteo(self, dias=7):
        """Obtener datos de OpenMeteo"""
        try:
            url = f"{self.config['openmeteo']['url_base']}/forecast"
            params = {
                'latitude': self.quillota_coords['lat'],
                'longitude': self.quillota_coords['lon'],
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',
                'timezone': 'America/Santiago',
                'forecast_days': dias
            }
            
            response = requests.get(url, params=params, timeout=self.config['openmeteo']['timeout'])
            response.raise_for_status()
            
            data = response.json()
            return self._procesar_datos_openmeteo(data)
            
        except Exception as e:
            logger.error(f"Error obteniendo datos OpenMeteo: {e}")
            return self._generar_datos_sinteticos(dias)
    
    def obtener_datos_openweather(self, dias=7):
        """Obtener datos de OpenWeather"""
        try:
            # Simulacion de datos OpenWeather
            return self._generar_datos_sinteticos(dias, fuente='openweather')
        except Exception as e:
            logger.error(f"Error obteniendo datos OpenWeather: {e}")
            return self._generar_datos_sinteticos(dias)
    
    def _procesar_datos_openmeteo(self, data):
        """Procesar datos de OpenMeteo"""
        try:
            daily = data['daily']
            fechas = pd.to_datetime(daily['time'])
            
            df = pd.DataFrame({
                'fecha': fechas,
                'temperatura_max': daily['temperature_2m_max'],
                'temperatura_min': daily['temperature_2m_min'],
                'precipitacion': daily['precipitation_sum'],
                'velocidad_viento': daily['wind_speed_10m_max'],
                'fuente': 'openmeteo'
            })
            
            return df
        except Exception as e:
            logger.error(f"Error procesando datos OpenMeteo: {e}")
            return self._generar_datos_sinteticos(7)
    
    def _generar_datos_sinteticos(self, dias, fuente='sintetico'):
        """Generar datos sinteticos como respaldo"""
        fechas = pd.date_range(start=datetime.now(), periods=dias, freq='D')
        
        np.random.seed(42)
        df = pd.DataFrame({
            'fecha': fechas,
            'temperatura_max': np.random.normal(25, 5, dias),
            'temperatura_min': np.random.normal(12, 3, dias),
            'precipitacion': np.random.exponential(2, dias),
            'velocidad_viento': np.random.normal(8, 3, dias),
            'humedad_relativa': np.random.normal(65, 15, dias),
            'presion_atmosferica': np.random.normal(1013, 10, dias),
            'fuente': fuente
        })
        
        return df

class ConectorBaseDatos:
    """Conector para bases de datos"""
    
    def __init__(self):
        self.sqlite_path = "data/metgo_unificado.db"
        self._inicializar_sqlite()
    
    def _inicializar_sqlite(self):
        """Inicializar base de datos SQLite"""
        try:
            Path(self.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            # Crear tablas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datos_meteorologicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha DATETIME NOT NULL,
                    temperatura_max REAL,
                    temperatura_min REAL,
                    precipitacion REAL,
                    velocidad_viento REAL,
                    humedad_relativa REAL,
                    presion_atmosferica REAL,
                    fuente TEXT,
                    timestamp_ingreso DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predicciones_ml (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_prediccion DATETIME NOT NULL,
                    variable TEXT NOT NULL,
                    valor_predicho REAL,
                    confianza REAL,
                    modelo TEXT,
                    timestamp_prediccion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alertas_agricolas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_alerta TEXT NOT NULL,
                    severidad TEXT NOT NULL,
                    descripcion TEXT,
                    fecha_alerta DATETIME NOT NULL,
                    activa BOOLEAN DEFAULT TRUE,
                    timestamp_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Base de datos SQLite inicializada")
            
        except Exception as e:
            logger.error(f"Error inicializando SQLite: {e}")
    
    def guardar_datos_meteorologicos(self, df):
        """Guardar datos meteorologicos en SQLite"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            
            df.to_sql('datos_meteorologicos', conn, if_exists='append', index=False)
            
            conn.close()
            logger.info(f"Datos meteorologicos guardados: {len(df)} registros")
            
        except Exception as e:
            logger.error(f"Error guardando datos meteorologicos: {e}")
    
    def obtener_datos_meteorologicos(self, dias=30):
        """Obtener datos meteorologicos de SQLite"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            
            query = '''
                SELECT * FROM datos_meteorologicos 
                WHERE fecha >= date('now', '-{} days')
                ORDER BY fecha DESC
            '''.format(dias)
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            logger.error(f"Error obteniendo datos meteorologicos: {e}")
            return pd.DataFrame()

class ConectorMachineLearning:
    """Conector para Machine Learning"""
    
    def __init__(self):
        self.modelos = {}
        self._cargar_modelos()
    
    def _cargar_modelos(self):
        """Cargar modelos de ML"""
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.linear_model import LinearRegression
            from sklearn.svm import SVR
            
            # Modelos basicos
            self.modelos = {
                'temperatura_max': RandomForestRegressor(n_estimators=100, random_state=42),
                'temperatura_min': RandomForestRegressor(n_estimators=100, random_state=42),
                'precipitacion': LinearRegression(),
                'viento': SVR(kernel='rbf')
            }
            
            logger.info("Modelos de ML cargados")
            
        except Exception as e:
            logger.error(f"Error cargando modelos ML: {e}")
    
    def entrenar_modelo(self, X, y, variable):
        """Entrenar modelo para una variable"""
        try:
            if variable in self.modelos:
                self.modelos[variable].fit(X, y)
                logger.info(f"Modelo entrenado para {variable}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error entrenando modelo {variable}: {e}")
            return False
    
    def predecir(self, X, variable):
        """Hacer prediccion con modelo"""
        try:
            if variable in self.modelos:
                prediccion = self.modelos[variable].predict(X)
                return prediccion
            return None
        except Exception as e:
            logger.error(f"Error prediciendo {variable}: {e}")
            return None

class ConectorVisualizacion:
    """Conector para visualizaciones"""
    
    def __init__(self):
        self.colores_metgo = {
            'primary': '#2E8B57',
            'secondary': '#90EE90',
            'accent': '#FF6B35',
            'background': '#F5F5F5'
        }
    
    def crear_grafico_temperaturas(self, df):
        """Crear grafico de temperaturas"""
        try:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['fecha'],
                y=df['temperatura_max'],
                mode='lines+markers',
                name='Temperatura Max',
                line=dict(color=self.colores_metgo['primary'], width=3)
            ))
            
            fig.add_trace(go.Scatter(
                x=df['fecha'],
                y=df['temperatura_min'],
                mode='lines+markers',
                name='Temperatura Min',
                line=dict(color=self.colores_metgo['secondary'], width=3)
            ))
            
            fig.update_layout(
                title='Temperaturas - Quillota',
                xaxis_title='Fecha',
                yaxis_title='Temperatura (°C)',
                template='plotly_white',
                height=400
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creando grafico temperaturas: {e}")
            return None
    
    def crear_grafico_precipitacion(self, df):
        """Crear grafico de precipitacion"""
        try:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df['fecha'],
                y=df['precipitacion'],
                name='Precipitacion',
                marker_color=self.colores_metgo['accent']
            ))
            
            fig.update_layout(
                title='Precipitacion - Quillota',
                xaxis_title='Fecha',
                yaxis_title='Precipitacion (mm)',
                template='plotly_white',
                height=400
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creando grafico precipitacion: {e}")
            return None

class SistemaUnificadoConConectores:
    """Sistema unificado con todos los conectores integrados"""
    
    def __init__(self):
        # Modulos base
        self.auth = SistemaAutenticacion()
        self.integrador = IntegradorModulos()
        self.conectores_metgo = ConectoresEspecificosMETGO()
        
        # Conectores especificos
        self.conector_datos = ConectorDatosMeteorologicos()
        self.conector_bd = ConectorBaseDatos()
        self.conector_ml = ConectorMachineLearning()
        self.conector_viz = ConectorVisualizacion()
        self.conector_iot = ConectorSensoresIoT()
        self.conector_satelital = ConectorDatosSatelitales()
        self.conector_monitoreo = ConectorMonitoreo()
        self.conector_respaldos = ConectorRespaldos()
        self.conector_apis_avanzadas = ConectorAPIsAvanzadas()
        
        # Estado de sesion en Streamlit
        if 'autenticado' not in st.session_state:
            st.session_state.autenticado = False
        if 'token' not in st.session_state:
            st.session_state.token = None
        if 'usuario' not in st.session_state:
            st.session_state.usuario = None
        if 'datos_meteorologicos' not in st.session_state:
            st.session_state.datos_meteorologicos = None
    
    def mostrar_login(self):
        """Mostrar pantalla de login"""
        st.title("METGO 3D - Sistema Unificado con Conectores")
        st.markdown("### Autenticacion de Usuario")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.info("Usuario: admin | Password: admin123")
            st.info("Usuario: usuario | Password: usuario123")
            
            usuario = st.text_input("Usuario")
            password = st.text_input("Password", type="password")
            
            if st.button("Iniciar Sesion", type="primary"):
                exito, resultado = self.auth.autenticar(usuario, password)
                
                if exito:
                    st.session_state.autenticado = True
                    st.session_state.token = resultado
                    st.session_state.usuario = usuario
                    st.success("Autenticacion exitosa")
                    st.rerun()
                else:
                    st.error(f"Error: {resultado}")
    
    def mostrar_dashboard(self):
        """Mostrar dashboard principal con conectores"""
        st.set_page_config(
            page_title="METGO 3D - Sistema Unificado con Conectores",
            page_icon="🌐",
            layout="wide"
        )
        
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title("METGO 3D - Sistema Unificado con Conectores")
            st.markdown(f"**Usuario:** {st.session_state.usuario}")
        with col2:
            if st.button("Cerrar Sesion"):
                self.auth.cerrar_sesion(st.session_state.token)
                st.session_state.autenticado = False
                st.session_state.token = None
                st.session_state.usuario = None
                st.rerun()
        
        st.markdown("---")
        
        # Tabs principales
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
            "Dashboard",
            "Datos Meteorologicos",
            "Machine Learning",
            "Visualizaciones",
            "Sensores IoT",
            "Datos Satelitales",
            "APIs Avanzadas",
            "Monitoreo",
            "Respaldos",
            "Conectores",
            "Sistema"
        ])
        
        with tab1:
            self._mostrar_tab_dashboard()
        
        with tab2:
            self._mostrar_tab_datos_meteorologicos()
        
        with tab3:
            self._mostrar_tab_machine_learning()
        
        with tab4:
            self._mostrar_tab_visualizaciones()
        
        with tab5:
            self._mostrar_tab_sensores_iot()
        
        with tab6:
            self._mostrar_tab_datos_satelitales()
        
        with tab7:
            self._mostrar_tab_apis_avanzadas()
        
        with tab8:
            self._mostrar_tab_monitoreo()
        
        with tab9:
            self._mostrar_tab_respaldos()
        
        with tab10:
            self._mostrar_tab_conectores()
        
        with tab11:
            self._mostrar_tab_sistema()
    
    def _mostrar_tab_dashboard(self):
        """Mostrar tab de dashboard principal"""
        st.header("Dashboard Principal - METGO 3D")
        
        # Metricas generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Conectores Activos", "16/16", "100%")
        
        with col2:
            st.metric("APIs Meteorologicas", "2", "OpenMeteo + OpenWeather")
        
        with col3:
            st.metric("Modelos ML", "4", "RandomForest, Linear, SVR")
        
        with col4:
            st.metric("Bases de Datos", "3", "SQLite + PostgreSQL + Redis")
        
        st.markdown("---")
        
        # Sección de Dashboards Disponibles
        st.subheader("🎯 Acceso a Todos los Dashboards")
        st.markdown("**Navega a todos los dashboards especializados del sistema:**")
        
        # Crear columnas para los dashboards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Dashboards Streamlit")
            
            # Dashboard Completo
            if st.button("🌐 Dashboard Completo", key="btn_dashboard_completo", help="Dashboard principal con todas las funcionalidades"):
                st.info("Ejecutando: python dashboard_completo_metgo.py")
                try:
                    import subprocess
                    result = subprocess.run(['python', 'dashboard_completo_metgo.py'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        st.success("Dashboard completo iniciado exitosamente")
                    else:
                        st.warning(f"Dashboard completo: {result.stderr}")
                except Exception as e:
                    st.error(f"Error ejecutando dashboard completo: {e}")
            
            # Dashboard Global
            if st.button("🌍 Dashboard Global", key="btn_dashboard_global", help="Dashboard global con integración completa"):
                st.info("Ejecutando: python dashboard_global_metgo.py")
                try:
                    import subprocess
                    result = subprocess.run(['python', 'dashboard_global_metgo.py'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        st.success("Dashboard global iniciado exitosamente")
                    else:
                        st.warning(f"Dashboard global: {result.stderr}")
                except Exception as e:
                    st.error(f"Error ejecutando dashboard global: {e}")
            
            # Dashboard Unificado
            if st.button("🔗 Dashboard Unificado", key="btn_dashboard_unificado", help="Dashboard unificado con conectores"):
                st.info("Ejecutando: python dashboard_unificado_metgo.py")
                try:
                    import subprocess
                    result = subprocess.run(['python', 'dashboard_unificado_metgo.py'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        st.success("Dashboard unificado iniciado exitosamente")
                    else:
                        st.warning(f"Dashboard unificado: {result.stderr}")
                except Exception as e:
                    st.error(f"Error ejecutando dashboard unificado: {e}")
            
            # Dashboard Integrado
            if st.button("📈 Dashboard Integrado", key="btn_dashboard_integrado", help="Dashboard con notebooks integrados"):
                st.info("Ejecutando: python dashboard_integrado_notebooks.py")
                try:
                    import subprocess
                    result = subprocess.run(['python', 'dashboard_integrado_notebooks.py'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        st.success("Dashboard integrado iniciado exitosamente")
                    else:
                        st.warning(f"Dashboard integrado: {result.stderr}")
                except Exception as e:
                    st.error(f"Error ejecutando dashboard integrado: {e}")
            
            # Dashboard Monitoreo
            if st.button("📊 Dashboard Monitoreo", key="btn_dashboard_monitoreo", help="Dashboard especializado en monitoreo"):
                st.info("Ejecutando: python dashboard_monitoreo_metgo.py")
                try:
                    import subprocess
                    result = subprocess.run(['python', 'dashboard_monitoreo_metgo.py'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        st.success("Dashboard monitoreo iniciado exitosamente")
                    else:
                        st.warning(f"Dashboard monitoreo: {result.stderr}")
                except Exception as e:
                    st.error(f"Error ejecutando dashboard monitoreo: {e}")
        
        with col2:
            st.markdown("#### 🌐 Dashboards HTML")
            
            # Lista de dashboards HTML disponibles
            dashboards_html = [
                ("dashboard_global_html.html", "🌍 Dashboard Global HTML", "Dashboard global en formato HTML"),
                ("dashboard_html_completo.html", "📊 Dashboard HTML Completo", "Dashboard completo en formato HTML"),
                ("dashboard_sistema_unificado.html", "🔗 Sistema Unificado HTML", "Sistema unificado en formato HTML"),
                ("dashboard_metgo_3d.html", "🌾 METGO 3D HTML", "Dashboard METGO 3D en formato HTML")
            ]
            
            for archivo, nombre, descripcion in dashboards_html:
                if st.button(nombre, key=f"btn_{archivo}", help=descripcion):
                    try:
                        import webbrowser
                        import os
                        ruta_completa = os.path.abspath(archivo)
                        webbrowser.open(f"file://{ruta_completa}")
                        st.success(f"Abriendo {nombre} en el navegador")
                    except Exception as e:
                        st.error(f"Error abriendo {nombre}: {e}")
            
            st.markdown("#### 🚀 Ejecutores Especializados")
            
            # Ejecutor Dashboard Integrado
            if st.button("▶️ Ejecutar Dashboard Integrado", key="btn_ejecutar_integrado", help="Ejecutor especializado para dashboard integrado"):
                st.info("Ejecutando: python ejecutar_dashboard_integrado.py")
                try:
                    import subprocess
                    result = subprocess.run(['python', 'ejecutar_dashboard_integrado.py'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        st.success("Ejecutor dashboard integrado iniciado exitosamente")
                    else:
                        st.warning(f"Ejecutor dashboard integrado: {result.stderr}")
                except Exception as e:
                    st.error(f"Error ejecutando dashboard integrado: {e}")
        
        st.markdown("---")
        
        # Información de puertos y acceso
        st.subheader("🔗 Información de Acceso")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📡 Puertos Disponibles")
            puertos_info = [
                ("8501", "Sistema Principal (Actual)", "http://localhost:8501"),
                ("8502", "Dashboard Completo", "http://localhost:8502"),
                ("8503", "Dashboard Global", "http://localhost:8503"),
                ("8504", "Sistema Autenticado", "http://localhost:8504"),
                ("8505", "Dashboard Unificado", "http://localhost:8505")
            ]
            
            for puerto, nombre, url in puertos_info:
                st.markdown(f"**{puerto}**: {nombre}")
                st.code(url, language="text")
        
        with col2:
            st.markdown("#### 📋 Estado de Servicios")
            
            # Verificar estado de servicios
            servicios_activos = []
            
            # Verificar puerto 8501 (actual)
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 8501))
                if result == 0:
                    servicios_activos.append("✅ Puerto 8501: Activo")
                else:
                    servicios_activos.append("❌ Puerto 8501: Inactivo")
                sock.close()
            except:
                servicios_activos.append("❓ Puerto 8501: No verificado")
            
            # Verificar otros puertos
            for puerto in [8502, 8503, 8504, 8505]:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(('localhost', puerto))
                    if result == 0:
                        servicios_activos.append(f"✅ Puerto {puerto}: Activo")
                    else:
                        servicios_activos.append(f"❌ Puerto {puerto}: Inactivo")
                    sock.close()
                except:
                    servicios_activos.append(f"❓ Puerto {puerto}: No verificado")
            
            for servicio in servicios_activos:
                st.markdown(servicio)
        
        st.markdown("---")
        
        # Guía de uso
        st.subheader("📖 Guía de Uso")
        
        st.markdown("""
        **Para acceder a todos los dashboards:**
        
        1. **Dashboards Streamlit**: Haz clic en los botones de la izquierda para ejecutar dashboards especializados
        2. **Dashboards HTML**: Haz clic en los botones de la derecha para abrir dashboards en el navegador
        3. **Puertos**: Cada dashboard puede ejecutarse en un puerto diferente
        4. **Estado**: Verifica el estado de los servicios antes de acceder
        
        **Tipos de Dashboards Disponibles:**
        - 🌐 **Completo**: Dashboard principal con todas las funcionalidades
        - 🌍 **Global**: Dashboard global con integración completa
        - 🔗 **Unificado**: Dashboard con conectores especializados
        - 📈 **Integrado**: Dashboard con notebooks integrados
        - 📊 **Monitoreo**: Dashboard especializado en monitoreo
        - 🌐 **HTML**: Dashboards estáticos en formato HTML
        """)
        
        # Estado de conectores
        st.subheader("Estado de Conectores")
        
        conectores_estado = self.conectores_metgo.verificar_conectores_activos()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Conectores Principales:**")
            for conector, estado in list(conectores_estado.items())[:8]:
                status = "✅" if estado else "❌"
                st.write(f"{status} {conector}")
        
        with col2:
            st.write("**Directorios de Datos:**")
            for conector, estado in list(conectores_estado.items())[8:]:
                status = "✅" if estado else "❌"
                st.write(f"{status} {conector}")
    
    def _mostrar_tab_datos_meteorologicos(self):
        """Mostrar tab de datos meteorologicos"""
        st.header("Datos Meteorologicos - Quillota")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Obtener Datos")
            
            fuente = st.selectbox("Fuente de datos", ["OpenMeteo", "OpenWeather", "Sinteticos"])
            dias = st.slider("Dias de datos", 1, 30, 7, key="meteorologico_dias")
            
            if st.button("Obtener Datos", type="primary"):
                with st.spinner("Obteniendo datos meteorologicos..."):
                    if fuente == "OpenMeteo":
                        datos = self.conector_datos.obtener_datos_openmeteo(dias)
                    elif fuente == "OpenWeather":
                        datos = self.conector_datos.obtener_datos_openweather(dias)
                    else:
                        datos = self.conector_datos._generar_datos_sinteticos(dias)
                    
                    # Guardar en base de datos
                    self.conector_bd.guardar_datos_meteorologicos(datos)
                    
                    # Guardar en session state
                    st.session_state.datos_meteorologicos = datos
                    
                    st.success(f"Datos obtenidos: {len(datos)} registros")
        
        with col2:
            if st.session_state.datos_meteorologicos is not None:
                datos = st.session_state.datos_meteorologicos
                
                st.subheader("Datos Actuales")
                st.dataframe(datos, width="stretch")
                
                # Estadisticas basicas
                st.subheader("Estadisticas")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Temp Max Promedio", f"{datos['temperatura_max'].mean():.1f}°C")
                with col2:
                    st.metric("Precipitacion Total", f"{datos['precipitacion'].sum():.1f}mm")
                with col3:
                    st.metric("Viento Promedio", f"{datos['velocidad_viento'].mean():.1f} km/h")
            else:
                st.info("Obtener datos meteorologicos para ver la informacion")
    
    def _mostrar_tab_machine_learning(self):
        """Mostrar tab de machine learning"""
        st.header("Machine Learning - Predicciones")
        
        if st.session_state.datos_meteorologicos is not None:
            datos = st.session_state.datos_meteorologicos
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Entrenar Modelos")
                
                variable = st.selectbox("Variable a predecir", 
                                      ["temperatura_max", "temperatura_min", "precipitacion", "velocidad_viento"])
                
                if st.button("Entrenar Modelo"):
                    with st.spinner("Entrenando modelo..."):
                        # Preparar datos para entrenamiento
                        X = datos[['temperatura_max', 'temperatura_min', 'precipitacion']].values
                        y = datos[variable].values
                        
                        exito = self.conector_ml.entrenar_modelo(X, y, variable)
                        
                        if exito:
                            st.success(f"Modelo entrenado para {variable}")
                        else:
                            st.error("Error entrenando modelo")
            
            with col2:
                st.subheader("Hacer Prediccion")
                
                if st.button("Predecir"):
                    with st.spinner("Haciendo prediccion..."):
                        # Usar ultimos datos para prediccion
                        X_pred = datos[['temperatura_max', 'temperatura_min', 'precipitacion']].iloc[-1:].values
                        
                        prediccion = self.conector_ml.predecir(X_pred, variable)
                        
                        if prediccion is not None:
                            st.success(f"Prediccion para {variable}: {prediccion[0]:.2f}")
                        else:
                            st.error("Error en prediccion")
        else:
            st.info("Obtener datos meteorologicos primero para usar Machine Learning")
    
    def _mostrar_tab_visualizaciones(self):
        """Mostrar tab de visualizaciones completas y extensas"""
        st.header("📊 Visualizaciones Avanzadas - METGO 3D Quillota")
        st.markdown("---")
        
        if st.session_state.datos_meteorologicos is not None:
            datos = st.session_state.datos_meteorologicos
            
            # Mostrar información de variables disponibles
            st.subheader("📊 Variables Meteorológicas Disponibles")
            variables_disponibles = []
            
            # Verificar qué variables están disponibles
            if 'temperatura' in datos.columns or 'temperatura_max' in datos.columns:
                variables_disponibles.append("🌡️ Temperatura")
            if 'precipitacion' in datos.columns:
                variables_disponibles.append("🌧️ Precipitación")
            if 'humedad_relativa' in datos.columns:
                variables_disponibles.append("💧 Humedad Relativa")
            if 'presion_atmosferica' in datos.columns:
                variables_disponibles.append("📊 Presión Atmosférica")
            if 'velocidad_viento' in datos.columns:
                variables_disponibles.append("💨 Velocidad del Viento")
            if 'direccion_viento' in datos.columns:
                variables_disponibles.append("🧭 Dirección del Viento")
            if 'nubosidad' in datos.columns:
                variables_disponibles.append("☁️ Nubosidad")
            if 'radiacion_solar' in datos.columns:
                variables_disponibles.append("☀️ Radiación Solar")
            if 'punto_rocio' in datos.columns:
                variables_disponibles.append("🌡️ Punto de Rocío")
            
            # Mostrar variables disponibles
            if variables_disponibles:
                col_vars = st.columns(min(len(variables_disponibles), 4))
                for i, var in enumerate(variables_disponibles):
                    with col_vars[i % 4]:
                        st.success(var)
            
            st.markdown("---")
            
            # Sección 1: Temperaturas
            if 'temperatura_max' in datos.columns or 'temperatura_min' in datos.columns:
                st.subheader("🌡️ Visualizaciones de Temperatura")
            
            col1, col2 = st.columns(2)
            
            with col1:
                    if 'temperatura_max' in datos.columns and 'temperatura_min' in datos.columns:
                        fig_temp = go.Figure()
                        
                        fig_temp.add_trace(go.Scatter(
                            x=datos['fecha'],
                            y=datos['temperatura_max'],
                            mode='lines+markers',
                            name='Temperatura Máxima',
                            line=dict(color='red', width=2)
                        ))
                        
                        fig_temp.add_trace(go.Scatter(
                            x=datos['fecha'],
                            y=datos['temperatura_min'],
                            mode='lines+markers',
                            name='Temperatura Mínima',
                            line=dict(color='blue', width=2),
                            fill='tonexty'
                        ))
                        
                        fig_temp.update_layout(
                            title='Temperaturas - Quillota',
                            xaxis_title='Fecha',
                            yaxis_title='Temperatura (°C)',
                            template='plotly_white',
                            height=400
                        )
                        
                        st.plotly_chart(fig_temp, use_container_width=True)
            
            with col2:
                    # Gráfico de temperatura promedio si existe
                    if 'temperatura' in datos.columns:
                        fig_temp_prom = go.Figure()
                        
                        fig_temp_prom.add_trace(go.Scatter(
                            x=datos['fecha'],
                            y=datos['temperatura'],
                            mode='lines+markers',
                            name='Temperatura Promedio',
                            line=dict(color='green', width=2)
                        ))
                        
                        fig_temp_prom.update_layout(
                            title='Temperatura Promedio - Quillota',
                            xaxis_title='Fecha',
                            yaxis_title='Temperatura (°C)',
                            template='plotly_white',
                            height=400
                        )
                        
                        st.plotly_chart(fig_temp_prom, use_container_width=True)
            
            # Sección 2: Precipitación
            if 'precipitacion' in datos.columns:
                st.subheader("🌧️ Visualizaciones de Precipitación")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_precip = go.Figure()
                    
                    fig_precip.add_trace(go.Bar(
                        x=datos['fecha'],
                        y=datos['precipitacion'],
                        name='Precipitación',
                        marker_color='lightblue'
                    ))
                    
                    fig_precip.update_layout(
                        title='Precipitación Diaria - Quillota',
                        xaxis_title='Fecha',
                        yaxis_title='Precipitación (mm)',
                        template='plotly_white',
                        height=400
                    )
                    
                    st.plotly_chart(fig_precip, use_container_width=True)
                
                with col2:
                    # Precipitación acumulada
                    precip_acum = datos['precipitacion'].cumsum()
                    
                    fig_precip_acum = go.Figure()
                    
                    fig_precip_acum.add_trace(go.Scatter(
                        x=datos['fecha'],
                        y=precip_acum,
                        mode='lines+markers',
                        name='Precipitación Acumulada',
                        line=dict(color='darkblue', width=3)
                    ))
                    
                    fig_precip_acum.update_layout(
                        title='Precipitación Acumulada - Quillota',
                        xaxis_title='Fecha',
                        yaxis_title='Precipitación Acumulada (mm)',
                        template='plotly_white',
                        height=400
                    )
                    
                    st.plotly_chart(fig_precip_acum, use_container_width=True)
            
            # Sección 3: Humedad y Presión
            if 'humedad_relativa' in datos.columns or 'presion_atmosferica' in datos.columns:
                st.subheader("💧 Humedad y Presión Atmosférica")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'humedad_relativa' in datos.columns:
                        fig_humedad = go.Figure()
                        
                        fig_humedad.add_trace(go.Scatter(
                            x=datos['fecha'],
                            y=datos['humedad_relativa'],
                            mode='lines+markers',
                            name='Humedad Relativa',
                            line=dict(color='green', width=2)
                        ))
                        
                        fig_humedad.update_layout(
                            title='Humedad Relativa - Quillota',
                            xaxis_title='Fecha',
                            yaxis_title='Humedad Relativa (%)',
                            template='plotly_white',
                            height=400
                        )
                        
                        st.plotly_chart(fig_humedad, use_container_width=True)
                
                with col2:
                    if 'presion_atmosferica' in datos.columns:
                        fig_presion = go.Figure()
                        
                        fig_presion.add_trace(go.Scatter(
                            x=datos['fecha'],
                            y=datos['presion_atmosferica'],
                            mode='lines+markers',
                            name='Presión Atmosférica',
                            line=dict(color='purple', width=2)
                        ))
                        
                        fig_presion.update_layout(
                            title='Presión Atmosférica - Quillota',
                            xaxis_title='Fecha',
                            yaxis_title='Presión (hPa)',
                            template='plotly_white',
                            height=400
                        )
                        
                        st.plotly_chart(fig_presion, use_container_width=True)
            
            # Sección 4: Viento
            if 'velocidad_viento' in datos.columns or 'direccion_viento' in datos.columns:
                st.subheader("💨 Visualizaciones de Viento")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'velocidad_viento' in datos.columns:
                        fig_viento_vel = go.Figure()
                        
                        fig_viento_vel.add_trace(go.Scatter(
                            x=datos['fecha'],
                            y=datos['velocidad_viento'],
                            mode='lines+markers',
                            name='Velocidad del Viento',
                            line=dict(color='orange', width=2)
                        ))
                        
                        fig_viento_vel.update_layout(
                            title='Velocidad del Viento - Quillota',
                            xaxis_title='Fecha',
                            yaxis_title='Velocidad (km/h)',
                            template='plotly_white',
                            height=400
                        )
                        
                        st.plotly_chart(fig_viento_vel, use_container_width=True)
                
                with col2:
                    if 'direccion_viento' in datos.columns:
                        fig_viento_dir = go.Figure()
                        
                        fig_viento_dir.add_trace(go.Scatterpolar(
                            r=datos['velocidad_viento'] if 'velocidad_viento' in datos.columns else [1]*len(datos),
                            theta=datos['direccion_viento'],
                            mode='markers',
                            name='Dirección del Viento',
                            marker=dict(size=8, color='red')
                        ))
                        
                        fig_viento_dir.update_layout(
                            title='Rosa de Vientos - Quillota',
                            template='plotly_white',
                            height=400,
                            polar=dict(
                                radialaxis=dict(visible=True, range=[0, max(datos['velocidad_viento']) if 'velocidad_viento' in datos.columns else 10])
                            )
                        )
                        
                        st.plotly_chart(fig_viento_dir, use_container_width=True)
            
            # Sección 5: Nubosidad y Radiación Solar
            if 'nubosidad' in datos.columns or 'radiacion_solar' in datos.columns:
                st.subheader("☁️ Nubosidad y Radiación Solar")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'nubosidad' in datos.columns:
                        fig_nubosidad = go.Figure()
                        
                        fig_nubosidad.add_trace(go.Scatter(
                            x=datos['fecha'],
                            y=datos['nubosidad'],
                            mode='lines+markers',
                            name='Nubosidad',
                            line=dict(color='gray', width=2),
                            fill='tonexty'
                        ))
                        
                        fig_nubosidad.update_layout(
                            title='Nubosidad - Quillota',
                            xaxis_title='Fecha',
                            yaxis_title='Nubosidad (%)',
                            template='plotly_white',
                            height=400
                        )
                        
                        st.plotly_chart(fig_nubosidad, use_container_width=True)
                
                with col2:
                    if 'radiacion_solar' in datos.columns:
                        fig_radiacion = go.Figure()
                        
                        fig_radiacion.add_trace(go.Scatter(
                            x=datos['fecha'],
                            y=datos['radiacion_solar'],
                            mode='lines+markers',
                            name='Radiación Solar',
                            line=dict(color='yellow', width=2)
                        ))
                        
                        fig_radiacion.update_layout(
                            title='Radiación Solar - Quillota',
                            xaxis_title='Fecha',
                            yaxis_title='Radiación (W/m²)',
                            template='plotly_white',
                            height=400
                        )
                        
                        st.plotly_chart(fig_radiacion, use_container_width=True)
            
            # Sección 6: Vista Combinada Completa
            st.subheader("📊 Vista Completa - Todas las Variables")
            
            fig_completo = go.Figure()
            
            # Agregar todas las variables disponibles
            if 'temperatura_max' in datos.columns:
            fig_completo.add_trace(go.Scatter(
                x=datos['fecha'],
                y=datos['temperatura_max'],
                    mode='lines',
                    name='Temp Max (°C)',
                yaxis='y'
            ))
            
            if 'temperatura_min' in datos.columns:
            fig_completo.add_trace(go.Scatter(
                    x=datos['fecha'],
                    y=datos['temperatura_min'],
                    mode='lines',
                    name='Temp Min (°C)',
                    yaxis='y'
                ))
            
            if 'precipitacion' in datos.columns:
                fig_completo.add_trace(go.Bar(
                x=datos['fecha'],
                y=datos['precipitacion'],
                    name='Precipitación (mm)',
                yaxis='y2'
            ))
            
            if 'humedad_relativa' in datos.columns:
                fig_completo.add_trace(go.Scatter(
                    x=datos['fecha'],
                    y=datos['humedad_relativa'],
                    mode='lines',
                    name='Humedad (%)',
                    yaxis='y3'
                ))
            
            if 'presion_atmosferica' in datos.columns:
                fig_completo.add_trace(go.Scatter(
                    x=datos['fecha'],
                    y=datos['presion_atmosferica'],
                    mode='lines',
                    name='Presión (hPa)',
                    yaxis='y4'
                ))
            
            if 'velocidad_viento' in datos.columns:
                fig_completo.add_trace(go.Scatter(
                    x=datos['fecha'],
                    y=datos['velocidad_viento'],
                    mode='lines',
                    name='Viento (km/h)',
                    yaxis='y5'
                ))
            
            # Configurar ejes múltiples
            fig_completo.update_layout(
                title='Datos Meteorológicos Completos - Quillota',
                xaxis_title='Fecha',
                template='plotly_white',
                height=600,
                yaxis=dict(title='Temperatura (°C)', side='left', color='red'),
                yaxis2=dict(title='Precipitación (mm)', side='right', overlaying='y', color='blue'),
                yaxis3=dict(title='Humedad (%)', side='right', overlaying='y', position=0.85, color='green'),
                yaxis4=dict(title='Presión (hPa)', side='right', overlaying='y', position=0.95, color='purple'),
                yaxis5=dict(title='Viento (km/h)', side='right', overlaying='y', position=0.75, color='orange')
            )
            
            st.plotly_chart(fig_completo, use_container_width=True)
            
            # Sección 7: Análisis de Correlaciones
            st.subheader("🔗 Análisis de Correlaciones")
            
            # Seleccionar variables para correlación
            variables_correlacion = []
            nombres_variables = {
                'temperatura': 'Temperatura',
                'temperatura_max': 'Temp Máx',
                'temperatura_min': 'Temp Mín',
                'precipitacion': 'Precipitación',
                'humedad_relativa': 'Humedad',
                'presion_atmosferica': 'Presión',
                'velocidad_viento': 'Viento',
                'nubosidad': 'Nubosidad',
                'radiacion_solar': 'Radiación Solar'
            }
            
            for col in datos.columns:
                if col in nombres_variables and col != 'fecha':
                    variables_correlacion.append(col)
            
            if len(variables_correlacion) >= 2:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Matriz de correlación
                    datos_numericos = datos[variables_correlacion].select_dtypes(include=[np.number])
                    if not datos_numericos.empty:
                        correlacion = datos_numericos.corr()
                        
                        fig_corr = go.Figure(data=go.Heatmap(
                            z=correlacion.values,
                            x=[nombres_variables.get(col, col) for col in correlacion.columns],
                            y=[nombres_variables.get(col, col) for col in correlacion.columns],
                            colorscale='RdBu',
                            zmid=0,
                            text=np.round(correlacion.values, 2),
                            texttemplate="%{text}",
                            textfont={"size": 10}
                        ))
                        
                        fig_corr.update_layout(
                            title='Matriz de Correlación - Variables Meteorológicas',
                            height=500,
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig_corr, use_container_width=True)
                
                with col2:
                    # Gráfico de dispersión interactivo
                    st.markdown("**Gráfico de Dispersión Interactivo**")
                    
                    var_x = st.selectbox("Variable X:", variables_correlacion, 
                                       format_func=lambda x: nombres_variables.get(x, x))
                    var_y = st.selectbox("Variable Y:", variables_correlacion, 
                                       format_func=lambda x: nombres_variables.get(x, x))
                    
                    if var_x != var_y:
                        fig_scatter = go.Figure()
                        
                        fig_scatter.add_trace(go.Scatter(
                            x=datos[var_x],
                            y=datos[var_y],
                            mode='markers',
                            marker=dict(
                                size=8,
                                color=datos.index,
                                colorscale='Viridis',
                                showscale=True,
                                colorbar=dict(title="Índice Temporal")
                            ),
                            text=datos['fecha'].dt.strftime('%Y-%m-%d %H:%M'),
                            hovertemplate=f'<b>{nombres_variables[var_x]}: %{{x}}</b><br>' +
                                        f'<b>{nombres_variables[var_y]}: %{{y}}</b><br>' +
                                        '<b>Fecha:</b> %{text}<extra></extra>'
                        ))
                        
                        fig_scatter.update_layout(
                            title=f'Correlación: {nombres_variables[var_x]} vs {nombres_variables[var_y]}',
                            xaxis_title=nombres_variables[var_x],
                            yaxis_title=nombres_variables[var_y],
                            template='plotly_white',
                            height=400
                        )
                        
                        st.plotly_chart(fig_scatter, use_container_width=True)
                        
                        # Mostrar coeficiente de correlación
                        if len(datos[var_x].dropna()) > 1 and len(datos[var_y].dropna()) > 1:
                            corr_coef = datos[var_x].corr(datos[var_y])
                            st.metric("Coeficiente de Correlación", f"{corr_coef:.3f}")
            
            # Sección 8: Análisis Temporal Avanzado
            st.subheader("⏰ Análisis Temporal Avanzado")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Análisis por hora del día
                if 'fecha' in datos.columns:
                    datos['hora'] = datos['fecha'].dt.hour
                    
                    if 'temperatura' in datos.columns:
                        temp_por_hora = datos.groupby('hora')['temperatura'].mean()
                        
                        fig_hora = go.Figure()
                        
                        fig_hora.add_trace(go.Scatter(
                            x=temp_por_hora.index,
                            y=temp_por_hora.values,
                            mode='lines+markers',
                            name='Temperatura Promedio',
                            line=dict(color='red', width=3),
                            marker=dict(size=8)
                        ))
                        
                        fig_hora.update_layout(
                            title='Temperatura Promedio por Hora del Día',
                            xaxis_title='Hora del Día',
                            yaxis_title='Temperatura (°C)',
                            template='plotly_white',
                            height=400
                        )
                        
                        st.plotly_chart(fig_hora, use_container_width=True)
            
            with col2:
                # Análisis por día de la semana
                if 'fecha' in datos.columns:
                    datos['dia_semana'] = datos['fecha'].dt.day_name()
                    
                    if 'precipitacion' in datos.columns:
                        precip_por_dia = datos.groupby('dia_semana')['precipitacion'].sum()
                        dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        precip_por_dia = precip_por_dia.reindex(dias_orden, fill_value=0)
                        
                        fig_dia = go.Figure()
                        
                        fig_dia.add_trace(go.Bar(
                            x=['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
                            y=precip_por_dia.values,
                            name='Precipitación Total',
                            marker_color='lightblue'
                        ))
                        
                        fig_dia.update_layout(
                            title='Precipitación Total por Día de la Semana',
                            xaxis_title='Día de la Semana',
                            yaxis_title='Precipitación (mm)',
                            template='plotly_white',
                            height=400
                        )
                        
                        st.plotly_chart(fig_dia, use_container_width=True)
            
            # Sección 9: Alertas y Umbrales
            st.subheader("⚠️ Alertas Meteorológicas")
            
            alertas = []
            
            # Definir umbrales de alerta
            umbrales = {
                'temperatura_max': {'min': 0, 'max': 35, 'critico_max': 40},
                'temperatura_min': {'min': -5, 'max': 25, 'critico_min': -10},
                'precipitacion': {'max': 50, 'critico_max': 100},
                'velocidad_viento': {'max': 25, 'critico_max': 40},
                'humedad_relativa': {'min': 20, 'max': 90}
            }
            
            for variable, umbral in umbrales.items():
                if variable in datos.columns:
                    valores = datos[variable].dropna()
                    
                    if 'max' in umbral and valores.max() > umbral['max']:
                        alertas.append({
                            'tipo': 'Advertencia' if valores.max() <= umbral.get('critico_max', umbral['max'] * 1.2) else 'Crítico',
                            'variable': nombres_variables.get(variable, variable),
                            'descripcion': f'Valores altos detectados (máx: {valores.max():.1f})'
                        })
                    
                    if 'min' in umbral and valores.min() < umbral['min']:
                        alertas.append({
                            'tipo': 'Advertencia' if valores.min() >= umbral.get('critico_min', umbral['min'] * 1.2) else 'Crítico',
                            'variable': nombres_variables.get(variable, variable),
                            'descripcion': f'Valores bajos detectados (mín: {valores.min():.1f})'
                        })
            
            if alertas:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Alertas Activas:**")
                    for alerta in alertas:
                        color = "red" if alerta['tipo'] == 'Crítico' else "orange"
                        st.markdown(f"<div style='background-color: {color}; color: white; padding: 10px; margin: 5px 0; border-radius: 5px;'>"
                                  f"<strong>{alerta['tipo']}</strong><br>{alerta['variable']}: {alerta['descripcion']}"
                                  f"</div>", unsafe_allow_html=True)
                
                with col2:
                    # Gráfico de alertas por tipo
                    tipos_alertas = [alerta['tipo'] for alerta in alertas]
                    conteo_alertas = pd.Series(tipos_alertas).value_counts()
                    
                    fig_alertas = go.Figure()
                    
                    fig_alertas.add_trace(go.Bar(
                        x=conteo_alertas.index,
                        y=conteo_alertas.values,
                        marker_color=['red' if tipo == 'Crítico' else 'orange' for tipo in conteo_alertas.index]
                    ))
                    
                    fig_alertas.update_layout(
                        title='Distribución de Alertas',
                        xaxis_title='Tipo de Alerta',
                        yaxis_title='Cantidad',
                        template='plotly_white',
                        height=300
                    )
                    
                    st.plotly_chart(fig_alertas, use_container_width=True)
        else:
            st.success("✅ No se detectaron alertas meteorológicas")
        
        # Estadísticas resumen mejoradas
        st.subheader("📈 Estadísticas Resumen Avanzadas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**🌡️ Temperatura**")
            if 'temperatura_max' in datos.columns:
                st.metric("Temp Máx Promedio", f"{datos['temperatura_max'].mean():.1f}°C")
                st.metric("Temp Máx Máxima", f"{datos['temperatura_max'].max():.1f}°C")
            if 'temperatura_min' in datos.columns:
                st.metric("Temp Mín Promedio", f"{datos['temperatura_min'].mean():.1f}°C")
                st.metric("Temp Mín Mínima", f"{datos['temperatura_min'].min():.1f}°C")
        
        with col2:
            st.markdown("**🌧️ Precipitación**")
            if 'precipitacion' in datos.columns:
                st.metric("Precipitación Total", f"{datos['precipitacion'].sum():.1f}mm")
                st.metric("Precipitación Máxima", f"{datos['precipitacion'].max():.1f}mm")
                st.metric("Días con Lluvia", f"{(datos['precipitacion'] > 0).sum()}")
        
        with col3:
            st.markdown("**💧 Humedad & Presión**")
            if 'humedad_relativa' in datos.columns:
                st.metric("Humedad Promedio", f"{datos['humedad_relativa'].mean():.1f}%")
            if 'presion_atmosferica' in datos.columns:
                st.metric("Presión Promedio", f"{datos['presion_atmosferica'].mean():.1f}hPa")
                st.metric("Presión Máxima", f"{datos['presion_atmosferica'].max():.1f}hPa")
                st.metric("Presión Mínima", f"{datos['presion_atmosferica'].min():.1f}hPa")
        
        with col4:
            st.markdown("**💨 Viento & Otros**")
            if 'velocidad_viento' in datos.columns:
                st.metric("Viento Promedio", f"{datos['velocidad_viento'].mean():.1f}km/h")
                st.metric("Viento Máximo", f"{datos['velocidad_viento'].max():.1f}km/h")
            if 'nubosidad' in datos.columns:
                st.metric("Nubosidad Promedio", f"{datos['nubosidad'].mean():.1f}%")
            if 'radiacion_solar' in datos.columns:
                st.metric("Radiación Promedio", f"{datos['radiacion_solar'].mean():.1f}W/m²")
            
        # Sección 10: Exportación de Datos
        st.subheader("📊 Exportación de Datos")
        
        col1, col2 = st.columns(2)
        
        with col1:
                # Descargar datos como CSV
                csv = datos.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar Datos CSV",
                    data=csv,
                    file_name=f"datos_meteorologicos_quillota_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
        with col2:
            # Generar reporte PDF (simulado)
            if st.button("📄 Generar Reporte PDF"):
                st.info("Funcionalidad de reporte PDF en desarrollo")
                st.markdown("**El reporte incluirá:**")
                    st.markdown("- Gráficos de todas las variables")
                    st.markdown("- Análisis de correlaciones")
                    st.markdown("- Alertas meteorológicas")
                    st.markdown("- Estadísticas resumen")
            
            # Sección 11: Análisis Estadístico Avanzado
            st.subheader("📈 Análisis Estadístico Avanzado")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Análisis de distribución
                st.markdown("**Distribución de Variables**")
                variable_dist = st.selectbox("Seleccionar variable para análisis de distribución:", 
                                           variables_correlacion if len(variables_correlacion) > 0 else ['temperatura'])
                
                if variable_dist in datos.columns:
                    fig_dist = go.Figure()
                    
                    # Histograma
                    fig_dist.add_trace(go.Histogram(
                        x=datos[variable_dist].dropna(),
                        nbinsx=20,
                        name='Histograma',
                        opacity=0.7,
                        marker_color='lightblue'
                    ))
                    
                    fig_dist.update_layout(
                        title=f'Distribución de {nombres_variables.get(variable_dist, variable_dist)}',
                        xaxis_title=variable_dist,
                        yaxis_title='Frecuencia',
                        template='plotly_white',
                        height=400
                    )
                    
                    st.plotly_chart(fig_dist, use_container_width=True)
            
            with col2:
                # Box plots por variable
                st.markdown("**Análisis de Outliers (Box Plot)**")
                
                if len(variables_correlacion) > 0:
                    fig_box = go.Figure()
                    
                    for var in variables_correlacion[:5]:  # Máximo 5 variables
                        fig_box.add_trace(go.Box(
                            y=datos[var].dropna(),
                            name=nombres_variables.get(var, var),
                            boxpoints='outliers'
                        ))
                    
                    fig_box.update_layout(
                        title='Análisis de Outliers por Variable',
                        yaxis_title='Valores',
                        template='plotly_white',
                        height=400
                    )
                    
                    st.plotly_chart(fig_box, use_container_width=True)
            
            # Sección 12: Análisis de Tendencias y Estacionalidad
            st.subheader("📊 Análisis de Tendencias y Estacionalidad")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Análisis de tendencias con regresión lineal
                st.markdown("**Tendencias Temporales**")
                variable_tendencia = st.selectbox("Variable para análisis de tendencia:", 
                                                variables_correlacion if len(variables_correlacion) > 0 else ['temperatura'])
                
                if variable_tendencia in datos.columns and len(datos[variable_tendencia].dropna()) > 3:
                    fig_tendencia = go.Figure()
                    
                    # Datos originales
                    fig_tendencia.add_trace(go.Scatter(
                        x=datos['fecha'],
                        y=datos[variable_tendencia],
                        mode='markers',
                        name='Datos Originales',
                        marker=dict(size=6, opacity=0.6)
                    ))
                    
                    # Línea de tendencia simple
                    try:
                        valores = datos[variable_tendencia].dropna()
                        if len(valores) > 2:
                            # Regresión lineal simple
                            x_nums = np.arange(len(valores))
                            z = np.polyfit(x_nums, valores, 1)
                            p = np.poly1d(z)
                            y_trend = p(x_nums)
                            
                            fig_tendencia.add_trace(go.Scatter(
                                x=datos['fecha'][:len(y_trend)],
                                y=y_trend,
                                mode='lines',
                                name='Tendencia Lineal',
                                line=dict(color='red', width=2)
                            ))
                            
                            # Mostrar pendiente
                            pendiente = z[0]
                            st.metric("Pendiente de Tendencia", f"{pendiente:.4f}")
                            
                    except Exception as e:
                        st.warning(f"No se pudo calcular tendencia: {str(e)}")
                    
                    fig_tendencia.update_layout(
                        title=f'Tendencias en {nombres_variables.get(variable_tendencia, variable_tendencia)}',
                        xaxis_title='Fecha',
                        yaxis_title=variable_tendencia,
                        template='plotly_white',
                        height=400
                    )
                    
                    st.plotly_chart(fig_tendencia, use_container_width=True)
            
            with col2:
                # Análisis de estacionalidad
                st.markdown("**Análisis de Estacionalidad**")
                
                if 'fecha' in datos.columns and len(variables_correlacion) > 0:
                    variable_estacional = st.selectbox("Variable para análisis estacional:", 
                                                     variables_correlacion)
                    
                    if variable_estacional in datos.columns:
                        # Agregar columnas de tiempo
                        datos_temp = datos.copy()
                        datos_temp['mes'] = datos_temp['fecha'].dt.month
                        
                        # Agrupar por mes
                        estacional_mes = datos_temp.groupby('mes')[variable_estacional].mean()
                        
                        # Gráfico de estacionalidad mensual
                        fig_estacional = go.Figure()
                        
                        fig_estacional.add_trace(go.Scatter(
                            x=estacional_mes.index,
                            y=estacional_mes.values,
                            mode='lines+markers',
                            name='Promedio Mensual',
                            line=dict(color='blue', width=3),
                            marker=dict(size=8)
                        ))
                        
                        fig_estacional.update_layout(
                            title=f'Estacionalidad de {nombres_variables.get(variable_estacional, variable_estacional)}',
                            xaxis_title='Mes',
                            yaxis_title=f'Promedio {variable_estacional}',
                            template='plotly_white',
                            height=400,
                            xaxis=dict(tickmode='array', tickvals=list(range(1, 13)), 
                                     ticktext=['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                                             'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'])
                        )
                        
                        st.plotly_chart(fig_estacional, use_container_width=True)
            
            # Sección 13: Análisis de Extremos y Percentiles
            st.subheader("🌡️ Análisis de Extremos y Percentiles")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Percentiles por Variable**")
                
                if len(variables_correlacion) > 0:
                    percentiles_data = []
                    for var in variables_correlacion:
                        if var in datos.columns:
                            valores = datos[var].dropna()
                            if len(valores) > 0:
                                percentiles_data.append({
                                    'Variable': nombres_variables.get(var, var),
                                    'P10': f"{np.percentile(valores, 10):.2f}",
                                    'P25': f"{np.percentile(valores, 25):.2f}",
                                    'P50': f"{np.percentile(valores, 50):.2f}",
                                    'P75': f"{np.percentile(valores, 75):.2f}",
                                    'P90': f"{np.percentile(valores, 90):.2f}",
                                    'Min': f"{valores.min():.2f}",
                                    'Max': f"{valores.max():.2f}"
                                })
                    
                    if percentiles_data:
                        df_percentiles = pd.DataFrame(percentiles_data)
                        st.dataframe(df_percentiles, use_container_width=True)
            
            with col2:
                st.markdown("**Eventos Extremos**")
                
                eventos_extremos = []
                for var in variables_correlacion:
                    if var in datos.columns:
                        valores = datos[var].dropna()
                        if len(valores) > 10:
                            q99 = np.percentile(valores, 99)
                            q01 = np.percentile(valores, 1)
                            
                            extremos_altos = valores[valores >= q99]
                            extremos_bajos = valores[valores <= q01]
                            
                            if len(extremos_altos) > 0:
                                eventos_extremos.append({
                                    'Variable': nombres_variables.get(var, var),
                                    'Tipo': 'Valores Altos',
                                    'Cantidad': len(extremos_altos),
                                    'Valor Máximo': f"{extremos_altos.max():.2f}"
                                })
                            
                            if len(extremos_bajos) > 0:
                                eventos_extremos.append({
                                    'Variable': nombres_variables.get(var, var),
                                    'Tipo': 'Valores Bajos',
                                    'Cantidad': len(extremos_bajos),
                                    'Valor Mínimo': f"{extremos_bajos.min():.2f}"
                                })
                
                if eventos_extremos:
                    df_extremos = pd.DataFrame(eventos_extremos)
                    st.dataframe(df_extremos, use_container_width=True)
                else:
                    st.info("No se detectaron eventos extremos significativos")
            
            with col3:
                st.markdown("**Resumen de Variabilidad**")
                
                variabilidad_data = []
                for var in variables_correlacion:
                    if var in datos.columns:
                        valores = datos[var].dropna()
                        if len(valores) > 1:
                            cv = (valores.std() / valores.mean() * 100) if valores.mean() != 0 else 0
                            variabilidad_data.append({
                                'Variable': nombres_variables.get(var, var),
                                'CV (%)': f"{cv:.2f}",
                                'Rango': f"{valores.max() - valores.min():.2f}",
                                'Desv. Est.': f"{valores.std():.2f}"
                            })
                
                if variabilidad_data:
                    df_variabilidad = pd.DataFrame(variabilidad_data)
                    st.dataframe(df_variabilidad, use_container_width=True)
            
            # Sección 14: Análisis Comparativo y Benchmarking
            st.subheader("📊 Análisis Comparativo y Benchmarking")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Comparación con valores típicos
                st.markdown("**Comparación con Valores Típicos**")
                
                # Valores de referencia para Quillota (aproximados)
                valores_referencia = {
                    'temperatura': {'min': 10, 'max': 25, 'promedio': 17.5},
                    'temperatura_max': {'min': 15, 'max': 30, 'promedio': 22.5},
                    'temperatura_min': {'min': 5, 'max': 20, 'promedio': 12.5},
                    'precipitacion': {'min': 0, 'max': 50, 'promedio': 5},
                    'humedad_relativa': {'min': 40, 'max': 90, 'promedio': 65},
                    'presion_atmosferica': {'min': 1010, 'max': 1025, 'promedio': 1017.5},
                    'velocidad_viento': {'min': 0, 'max': 15, 'promedio': 7.5}
                }
                
                comparacion_data = []
                for var in variables_correlacion:
                    if var in datos.columns and var in valores_referencia:
                        valores_actuales = datos[var].dropna()
                        ref = valores_referencia[var]
                        
                        if len(valores_actuales) > 0:
                            diferencia = valores_actuales.mean() - ref['promedio']
                            estado = 'Normal' if abs(diferencia) < ref['promedio'] * 0.1 else 'Anómalo'
                            
                            comparacion_data.append({
                                'Variable': nombres_variables.get(var, var),
                                'Actual Prom': f"{valores_actuales.mean():.2f}",
                                'Referencia': f"{ref['promedio']:.2f}",
                                'Diferencia': f"{diferencia:+.2f}",
                                'Estado': estado
                            })
                
                if comparacion_data:
                    df_comparacion = pd.DataFrame(comparacion_data)
                    st.dataframe(df_comparacion, use_container_width=True)
            
            with col2:
                # Análisis de calidad de datos
                st.markdown("**Análisis de Calidad de Datos**")
                
                calidad_data = []
                for col in datos.columns:
                    if col != 'fecha':
                        valores = datos[col]
                        total = len(valores)
                        nulos = valores.isnull().sum()
                        no_nulos = total - nulos
                        
                        calidad_data.append({
                            'Variable': nombres_variables.get(col, col),
                            'Total': total,
                            'Válidos': no_nulos,
                            'Nulos': nulos,
                            'Completitud (%)': f"{(no_nulos/total*100):.1f}",
                            'Únicos': valores.nunique()
                        })
                
                if calidad_data:
                    df_calidad = pd.DataFrame(calidad_data)
                    st.dataframe(df_calidad, use_container_width=True)
            
            # Sección 15: Exportación Avanzada de Datos
            st.subheader("📊 Exportación Avanzada de Datos")
            
            col1, col2, col3 = st.columns(3)
            
        with col1:
            # Descargar datos como CSV
            csv = datos.to_csv(index=False)
            st.download_button(
                label="📥 Descargar Datos CSV",
                data=csv,
                file_name=f"datos_meteorologicos_quillota_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
                # Generar reporte estadístico
                if st.button("📄 Generar Reporte Estadístico"):
                    st.info("Generando reporte estadístico...")
                    
                    # Crear reporte básico
                    reporte = f"""
# REPORTE ESTADÍSTICO METGO 3D - QUILLOTA
Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## RESUMEN GENERAL
- Total de registros: {len(datos)}
- Período: {datos['fecha'].min().strftime('%Y-%m-%d')} a {datos['fecha'].max().strftime('%Y-%m-%d')}
- Variables analizadas: {len(variables_correlacion)}

## ESTADÍSTICAS POR VARIABLE
"""
                    
                    for var in variables_correlacion:
                        if var in datos.columns:
                            valores = datos[var].dropna()
                            if len(valores) > 0:
                                reporte += f"""
### {nombres_variables.get(var, var)}
- Promedio: {valores.mean():.2f}
- Mediana: {valores.median():.2f}
- Desviación estándar: {valores.std():.2f}
- Mínimo: {valores.min():.2f}
- Máximo: {valores.max():.2f}
- Rango: {valores.max() - valores.min():.2f}
"""
                    
                    st.text_area("Reporte Generado", reporte, height=300)
            
            with col3:
                # Generar reporte PDF (simulado)
                if st.button("📄 Generar Reporte PDF"):
                    st.info("Funcionalidad de reporte PDF en desarrollo")
                    st.markdown("**El reporte incluirá:**")
                    st.markdown("- Gráficos de todas las variables")
                    st.markdown("- Análisis de correlaciones")
                    st.markdown("- Alertas meteorológicas")
                    st.markdown("- Estadísticas resumen")
                    st.markdown("- Análisis de extremos")
                    st.markdown("- Patrones temporales")
                    st.markdown("- Guía de interpretación")
            
        else:
            st.info("📊 Obtener datos meteorológicos primero para ver visualizaciones")
            st.markdown("""
            **Para ver las visualizaciones:**
            1. Ve a la pestaña **"Datos Meteorológicos"**
            2. Haz clic en **"Obtener Datos"**
            3. Regresa a esta pestaña para ver todas las visualizaciones disponibles
            """)
    
    def _mostrar_tab_sensores_iot(self):
        """Mostrar tab de sensores IoT"""
        st.header("Sensores IoT - Quillota")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Control de Sensores")
            
            if st.button("Iniciar Simulacion IoT", type="primary"):
                if self.conector_iot.iniciar_simulacion_iot():
                    st.success("Simulacion IoT iniciada")
                else:
                    st.error("Error iniciando simulacion")
            
            if st.button("Detener Simulacion IoT"):
                self.conector_iot.detener_simulacion_iot()
                st.info("Simulacion IoT detenida")
            
            if st.button("Obtener Datos IoT"):
                datos_iot = self.conector_iot.obtener_datos_iot(100)
                st.session_state.datos_iot = datos_iot
                st.success(f"Datos IoT obtenidos: {len(datos_iot)} registros")
        
        with col2:
            if hasattr(st.session_state, 'datos_iot') and st.session_state.datos_iot:
                datos_iot = st.session_state.datos_iot
                
                st.subheader("Datos de Sensores IoT")
                
                # Mostrar datos en tabla
                df_iot = pd.DataFrame(datos_iot)
                st.dataframe(df_iot, width="stretch")
                
                # Estadisticas
                st.subheader("Estadisticas IoT")
                stats_iot = self.conector_iot.obtener_estadisticas_iot()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Estaciones Activas", stats_iot.get('estaciones_activas', 0))
                with col2:
                    st.metric("Sensores Activos", stats_iot.get('sensores_activos', 0))
                with col3:
                    st.metric("Total Lecturas", stats_iot.get('total_lecturas', 0))
                
                # Grafico de sensores por estacion
                if 'estacion_id' in df_iot.columns:
                    fig_sensores = px.bar(
                        df_iot.groupby('estacion_id')['sensor'].nunique().reset_index(),
                        x='estacion_id',
                        y='sensor',
                        title='Sensores por Estacion IoT'
                    )
                    st.plotly_chart(fig_sensores, width="stretch")
            else:
                st.info("Iniciar simulacion IoT y obtener datos para ver la informacion")
    
    def _mostrar_tab_datos_satelitales(self):
        """Mostrar tab de datos satelitales"""
        st.header("Datos Satelitales - Quillota")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Control de Satelites")
            
            satelite = st.selectbox("Satelite", ["landsat_8", "sentinel_2", "modis"], key="satelital_satelite")
            dias = st.slider("Dias de datos", 1, 30, 7, key="satelital_dias")
            
            if st.button("Generar Imagenes Satelitales", type="primary"):
                with st.spinner("Generando imagenes satelitales..."):
                    imagenes = self.conector_satelital.generar_imagenes_satelitales(dias)
                    st.success(f"Imagenes generadas: {len(imagenes)}")
            
            if st.button("Actualizar Lista de Imagenes"):
                imagenes_disponibles = self.conector_satelital.obtener_imagenes_disponibles()
                st.session_state.imagenes_satelitales = imagenes_disponibles
                st.success(f"Imagenes disponibles: {len(imagenes_disponibles)}")
        
        with col2:
            if hasattr(st.session_state, 'imagenes_satelitales') and st.session_state.imagenes_satelitales:
                imagenes = st.session_state.imagenes_satelitales
                
                st.subheader("Imagenes Satelitales Disponibles")
                
                # Mostrar lista de imagenes
                for i, imagen in enumerate(imagenes[:10]):  # Mostrar solo las primeras 10
                    with st.expander(f"Imagen {i+1}: {imagen['archivo']}", expanded=False):
                        st.write(f"**Satelite:** {imagen.get('satelite', 'N/A')}")
                        st.write(f"**Fecha:** {imagen.get('fecha_adquisicion', 'N/A')}")
                        st.write(f"**Resolucion:** {imagen.get('resolucion', 'N/A')}")
                        st.write(f"**Procesado:** {imagen.get('procesado', False)}")
                        
                        if st.button(f"Procesar Imagen {i+1}"):
                            resultado = self.conector_satelital.procesar_imagen_satelital(imagen['ruta'])
                            if resultado.get('procesado'):
                                st.success("Imagen procesada exitosamente")
                                
                                # Mostrar indices calculados
                                if 'indices' in resultado:
                                    st.subheader("Indices Calculados")
                                    for indice, valores in resultado['indices'].items():
                                        st.write(f"**{indice.upper()}:**")
                                        st.write(f"  - Media: {valores['media']:.3f}")
                                        st.write(f"  - Desviacion: {valores['desviacion']:.3f}")
                                        st.write(f"  - Min: {valores['min']:.3f}")
                                        st.write(f"  - Max: {valores['max']:.3f}")
                            else:
                                st.error(f"Error procesando imagen: {resultado.get('error', 'Error desconocido')}")
            else:
                st.info("Actualizar lista de imagenes para ver los datos satelitales")
    
    def _mostrar_tab_apis_avanzadas(self):
        """Mostrar tab de APIs avanzadas"""
        st.header("APIs Avanzadas - METGO 3D")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Control de APIs")
            
            api_seleccionada = st.selectbox("Seleccionar API", [
                "OpenWeather", "NASA Earth", "Google Maps", "Todas"
            ], key="api_seleccionada")
            
            if st.button("Verificar Estado de APIs", type="primary"):
                estado = self.conector_apis_avanzadas.verificar_estado_apis()
                st.session_state.estado_apis = estado
                st.success("Estado de APIs verificado")
            
            if st.button("Obtener Datos OpenWeather"):
                with st.spinner("Obteniendo datos de OpenWeather..."):
                    datos = self.conector_apis_avanzadas.obtener_datos_openweather()
                    st.session_state.datos_openweather = datos
                    if 'error' not in datos:
                        st.success("Datos de OpenWeather obtenidos")
                    else:
                        st.error(f"Error: {datos.get('error', 'Error desconocido')}")
            
            if st.button("Obtener Imagen NASA Earth"):
                with st.spinner("Obteniendo imagen de NASA Earth..."):
                    datos = self.conector_apis_avanzadas.obtener_datos_nasa_earth()
                    st.session_state.datos_nasa = datos
                    if 'error' not in datos:
                        st.success("Imagen de NASA Earth obtenida")
                    else:
                        st.error(f"Error: {datos.get('error', 'Error desconocido')}")
            
            if st.button("Obtener Elevacion Google Maps"):
                with st.spinner("Obteniendo elevacion de Google Maps..."):
                    datos = self.conector_apis_avanzadas.obtener_elevacion_google_maps()
                    st.session_state.datos_google_maps = datos
                    if 'error' not in datos:
                        st.success("Elevacion de Google Maps obtenida")
                    else:
                        st.error(f"Error: {datos.get('error', 'Error desconocido')}")
        
        with col2:
            # Estado de APIs
            if hasattr(st.session_state, 'estado_apis') and st.session_state.estado_apis:
                st.subheader("Estado de APIs")
                estado = st.session_state.estado_apis
                
                for api, info in estado.items():
                    if info.get('configurada'):
                        if info.get('disponible'):
                            st.success(f"✅ {api}: Disponible")
                        else:
                            st.error(f"❌ {api}: Error - {info.get('error', 'Error desconocido')}")
                    else:
                        st.warning(f"⚠️ {api}: No configurada (API key faltante)")
            
            # Datos de OpenWeather
            if hasattr(st.session_state, 'datos_openweather') and st.session_state.datos_openweather:
                datos_ow = st.session_state.datos_openweather
                if 'error' not in datos_ow:
                    st.subheader("Datos OpenWeather")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Temperatura", f"{datos_ow.get('temperatura', 0):.1f}°C")
                    with col2:
                        st.metric("Humedad", f"{datos_ow.get('humedad', 0)}%")
                    with col3:
                        st.metric("Presion", f"{datos_ow.get('presion', 0)} hPa")
                    
                    st.write(f"**Descripcion:** {datos_ow.get('descripcion', 'N/A')}")
                    st.write(f"**Viento:** {datos_ow.get('viento_velocidad', 0)} m/s")
                    st.write(f"**Nubosidad:** {datos_ow.get('nubosidad', 0)}%")
            
            # Datos de NASA Earth
            if hasattr(st.session_state, 'datos_nasa') and st.session_state.datos_nasa:
                datos_nasa = st.session_state.datos_nasa
                if 'error' not in datos_nasa:
                    st.subheader("Imagen NASA Earth")
                    st.write(f"**URL de imagen:** {datos_nasa.get('url_imagen', 'N/A')}")
                    st.write(f"**Fecha:** {datos_nasa.get('fecha', 'N/A')}")
                    st.write(f"**Coordenadas:** {datos_nasa.get('coordenadas', {})}")
            
            # Datos de Google Maps
            if hasattr(st.session_state, 'datos_google_maps') and st.session_state.datos_google_maps:
                datos_gm = st.session_state.datos_google_maps
                if 'error' not in datos_gm:
                    st.subheader("Elevacion Google Maps")
                    st.metric("Elevacion", f"{datos_gm.get('elevacion', 0):.1f} m")
                    st.write(f"**Coordenadas:** {datos_gm.get('coordenadas', {})}")
            
            # Estadisticas de APIs
            st.subheader("Estadisticas de Uso")
            if st.button("Obtener Estadisticas"):
                stats = self.conector_apis_avanzadas.obtener_estadisticas_apis()
                st.session_state.stats_apis = stats
                st.success("Estadisticas obtenidas")
            
            if hasattr(st.session_state, 'stats_apis') and st.session_state.stats_apis:
                stats = st.session_state.stats_apis
                
                if 'llamadas_por_api' in stats:
                    st.write("**Llamadas por API (24h):**")
                    for api_stats in stats['llamadas_por_api']:
                        st.write(f"- {api_stats['api']}: {api_stats['total_llamadas']} llamadas, {api_stats['tiempo_promedio_ms']:.1f}ms promedio")
                
                if 'datos_por_api' in stats:
                    st.write("**Datos por API (24h):**")
                    for data_stats in stats['datos_por_api']:
                        st.write(f"- {data_stats['api']} ({data_stats['tipo_dato']}): {data_stats['total_datos']} registros")
    
    def _mostrar_tab_monitoreo(self):
        """Mostrar tab de monitoreo del sistema"""
        st.header("Monitoreo del Sistema - METGO 3D")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Control de Monitoreo")
            
            if st.button("Iniciar Monitoreo", type="primary"):
                if self.conector_monitoreo.iniciar_monitoreo_continuo(60):
                    st.success("Monitoreo iniciado")
                else:
                    st.error("Error iniciando monitoreo")
            
            if st.button("Detener Monitoreo"):
                self.conector_monitoreo.detener_monitoreo()
                st.info("Monitoreo detenido")
            
            if st.button("Obtener Metricas Actuales"):
                metricas = self.conector_monitoreo.obtener_metricas_sistema()
                st.session_state.metricas_actuales = metricas
                st.success("Metricas obtenidas")
            
            # Configuracion de umbrales
            st.subheader("Configuracion de Umbrales")
            cpu_max = st.slider("CPU Max (%)", 50, 100, 80, key="monitoreo_cpu")
            memoria_max = st.slider("Memoria Max (%)", 50, 100, 85, key="monitoreo_memoria")
            disco_max = st.slider("Disco Max (%)", 50, 100, 90, key="monitoreo_disco")
            
            if st.button("Actualizar Umbrales"):
                self.conector_monitoreo.umbrales['cpu_max'] = cpu_max
                self.conector_monitoreo.umbrales['memoria_max'] = memoria_max
                self.conector_monitoreo.umbrales['disco_max'] = disco_max
                st.success("Umbrales actualizados")
        
        with col2:
            if hasattr(st.session_state, 'metricas_actuales') and st.session_state.metricas_actuales:
                metricas = st.session_state.metricas_actuales
                
                st.subheader("Metricas Actuales del Sistema")
                
                # Metricas principales
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("CPU", f"{metricas.get('cpu_percent', 0):.1f}%")
                with col2:
                    st.metric("Memoria", f"{metricas.get('memoria_percent', 0):.1f}%")
                with col3:
                    st.metric("Disco", f"{metricas.get('disco_percent', 0):.1f}%")
                with col4:
                    st.metric("Procesos", metricas.get('procesos_activos', 0))
                
                # Verificar alertas
                alertas = self.conector_monitoreo.verificar_alertas(metricas)
                if alertas:
                    st.subheader("Alertas Activas")
                    for alerta in alertas:
                        if alerta['severidad'] == 'CRITICA':
                            st.error(f"🚨 {alerta['mensaje']}")
                        elif alerta['severidad'] == 'ALTA':
                            st.warning(f"⚠️ {alerta['mensaje']}")
                        else:
                            st.info(f"ℹ️ {alerta['mensaje']}")
                else:
                    st.success("✅ No hay alertas activas")
                
                # Estadisticas
                st.subheader("Estadisticas de Monitoreo")
                stats = self.conector_monitoreo.obtener_estadisticas_monitoreo()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Metricas (24h):**")
                    st.write(f"- CPU Promedio: {stats.get('metricas', {}).get('cpu_promedio', 0):.1f}%")
                    st.write(f"- CPU Maximo: {stats.get('metricas', {}).get('cpu_maximo', 0):.1f}%")
                    st.write(f"- Memoria Promedio: {stats.get('metricas', {}).get('memoria_promedio', 0):.1f}%")
                    st.write(f"- Total Registros: {stats.get('metricas', {}).get('total_registros', 0)}")
                
                with col2:
                    st.write("**Alertas (24h):**")
                    st.write(f"- Total: {stats.get('alertas', {}).get('total', 0)}")
                    st.write(f"- Criticas: {stats.get('alertas', {}).get('criticas', 0)}")
                    st.write(f"- Altas: {stats.get('alertas', {}).get('altas', 0)}")
                    st.write(f"- Activas: {stats.get('alertas', {}).get('activas', 0)}")
            else:
                st.info("Obtener metricas actuales para ver la informacion de monitoreo")
    
    def _mostrar_tab_respaldos(self):
        """Mostrar tab de respaldos del sistema"""
        st.header("Respaldos del Sistema - METGO 3D")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Control de Respaldos")
            
            tipo_respaldo = st.selectbox("Tipo de Respaldo", ["completo", "incremental"], key="respaldo_tipo")
            
            if st.button("Crear Respaldo", type="primary"):
                with st.spinner("Creando respaldo..."):
                    if tipo_respaldo == "completo":
                        resultado = self.conector_respaldos.crear_respaldo_completo()
                    else:
                        resultado = self.conector_respaldos.crear_respaldo_incremental()
                    
                    if 'error' not in resultado:
                        st.success(f"Respaldo creado: {resultado.get('nombre', 'N/A')}")
                        st.session_state.respaldos_actualizados = True
                    else:
                        st.error(f"Error: {resultado.get('error', 'Error desconocido')}")
            
            if st.button("Actualizar Lista de Respaldos"):
                respaldos = self.conector_respaldos.listar_respaldos()
                st.session_state.lista_respaldos = respaldos
                st.success(f"Lista actualizada: {len(respaldos)} respaldos")
            
            # Limpieza de respaldos
            st.subheader("Limpieza de Respaldos")
            dias_retener = st.slider("Dias a retener", 1, 90, 30, key="respaldo_dias")
            
            if st.button("Limpiar Respaldos Antiguos"):
                resultado = self.conector_respaldos.limpiar_respaldos_antiguos(dias_retener)
                if 'error' not in resultado:
                    st.success(f"Respaldos eliminados: {resultado.get('archivos_eliminados', 0)}")
                    st.success(f"Espacio liberado: {resultado.get('espacio_liberado_mb', 0):.2f} MB")
                else:
                    st.error(f"Error: {resultado.get('error', 'Error desconocido')}")
        
        with col2:
            if hasattr(st.session_state, 'lista_respaldos') and st.session_state.lista_respaldos:
                respaldos = st.session_state.lista_respaldos
                
                st.subheader("Respaldos Disponibles")
                
                # Mostrar lista de respaldos
                for i, respaldo in enumerate(respaldos[:10]):  # Mostrar solo los primeros 10
                    with st.expander(f"Respaldo {i+1}: {respaldo['nombre']}", expanded=False):
                        st.write(f"**Tipo:** {respaldo.get('tipo', 'N/A')}")
                        st.write(f"**Fecha:** {respaldo.get('timestamp', 'N/A')}")
                        st.write(f"**Tamaño:** {respaldo.get('tamaño_bytes', 0) / (1024**2):.2f} MB")
                        st.write(f"**Archivos:** {respaldo.get('archivos_incluidos', 0)}")
                        
                        if st.button(f"Restaurar Respaldo {i+1}"):
                            resultado = self.conector_respaldos.restaurar_respaldo(respaldo['nombre'])
                            if 'error' not in resultado:
                                st.success(f"Respaldo restaurado en: {resultado.get('directorio_restauracion', 'N/A')}")
                            else:
                                st.error(f"Error: {resultado.get('error', 'Error desconocido')}")
                
                # Estadisticas de respaldos
                st.subheader("Estadisticas de Respaldos")
                total_respaldos = len(respaldos)
                respaldos_completos = len([r for r in respaldos if r.get('tipo') == 'completo'])
                respaldos_incrementales = len([r for r in respaldos if r.get('tipo') == 'incremental'])
                tamaño_total = sum(r.get('tamaño_bytes', 0) for r in respaldos) / (1024**2)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Respaldos", total_respaldos)
                with col2:
                    st.metric("Completos", respaldos_completos)
                with col3:
                    st.metric("Tamaño Total (MB)", f"{tamaño_total:.2f}")
            else:
                st.info("Actualizar lista de respaldos para ver la informacion")
    
    def _mostrar_tab_conectores(self):
        """Mostrar tab de conectores"""
        st.header("Conectores del Sistema")
        
        # Estado de conectores
        conectores_estado = self.conectores_metgo.verificar_conectores_activos()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Conectores Principales")
            for conector, estado in list(conectores_estado.items())[:8]:
                status = "✅" if estado else "❌"
                st.write(f"{status} {conector}")
        
        with col2:
            st.subheader("Directorios de Datos")
            for conector, estado in list(conectores_estado.items())[8:]:
                status = "✅" if estado else "❌"
                st.write(f"{status} {conector}")
        
        # Conectores criticos
        st.subheader("Conectores Criticos")
        conectores_criticos = self.conectores_metgo.obtener_conectores_criticos()
        
        for conector in conectores_criticos:
            st.write(f"🔗 {conector}")
    
    def _mostrar_tab_sistema(self):
        """Mostrar tab de sistema"""
        st.header("Sistema METGO 3D")
        
        # Informacion del sistema
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Modulos del Sistema")
            modulos = self.integrador.obtener_resumen()
            
            st.write(f"**Notebooks:** {modulos['total_notebooks']}")
            st.write(f"**Archivos Python:** {modulos['total_archivos_py']}")
            st.write(f"**Total Modulos:** {modulos['total_modulos']}")
            st.write(f"**Categorias:** {modulos['categorias']}")
        
        with col2:
            st.subheader("Conectores")
            conectores_info = self.conectores_metgo.generar_reporte_conectores()
            
            st.write(f"**Conectores Identificados:** {conectores_info['conectores_identificados']}")
            st.write(f"**Categorias:** {len(conectores_info['categorias'])}")
            st.write(f"**Conectores Criticos:** {len(conectores_info['conectores_criticos'])}")
            st.write(f"**Conectores Activos:** {conectores_info['resumen']['conectores_activos']}")
    
    def ejecutar(self):
        """Ejecutar sistema unificado con conectores"""
        if not st.session_state.autenticado:
            self.mostrar_login()
        else:
            self.mostrar_dashboard()

def main():
    """Funcion principal"""
    sistema = SistemaUnificadoConConectores()
    sistema.ejecutar()

if __name__ == "__main__":
    main()
