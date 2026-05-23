#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 DASHBOARD GLOBAL METGO 3D - INTEGRACIÓN COMPLETA
Sistema Meteorológico Agrícola Quillota - Dashboard Global con Todos los Módulos
"""

import os
import sys
import time
import json
import warnings
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
import sqlite3
import subprocess
import nbformat
from nbconvert import PythonExporter
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

# Configuración
warnings.filterwarnings('ignore')

class DashboardGlobalMETGO:
    """Dashboard global que integra todos los módulos, notebooks, datos satelitales y más"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/dashboard_global',
            'directorio_logs': 'logs/dashboard_global',
            'directorio_graficos': 'graficos/dashboard_global',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Módulos del sistema METGO 3D
        self.modulos_sistema = {
            'notebooks': {
                '00_sistema_principal': {
                    'nombre': 'Sistema Principal MIP Quillota',
                    'archivo': '00_Sistema_Principal_MIP_Quillota.ipynb',
                    'descripcion': 'Sistema principal operativo',
                    'categoria': 'core',
                    'estado': 'activo'
                },
                '01_configuracion': {
                    'nombre': 'Configuración e Imports',
                    'archivo': '01_Configuracion_e_imports.ipynb',
                    'descripcion': 'Configuración y imports del sistema',
                    'categoria': 'config',
                    'estado': 'activo'
                },
                '02_procesamiento': {
                    'nombre': 'Carga y Procesamiento de Datos',
                    'archivo': '02_Carga_y_Procesamiento_Datos.ipynb',
                    'descripcion': 'Procesamiento de datos meteorológicos',
                    'categoria': 'data',
                    'estado': 'activo'
                },
                '03_analisis': {
                    'nombre': 'Análisis Meteorológico',
                    'archivo': '03_Analisis_Meteorologico.ipynb',
                    'descripcion': 'Análisis meteorológico avanzado',
                    'categoria': 'analysis',
                    'estado': 'activo'
                },
                '04_visualizaciones': {
                    'nombre': 'Visualizaciones',
                    'archivo': '04_Visualizaciones.ipynb',
                    'descripcion': 'Visualizaciones y gráficos',
                    'categoria': 'visualization',
                    'estado': 'activo'
                },
                '05_modelos_ml': {
                    'nombre': 'Modelos de Machine Learning',
                    'archivo': '05_Modelos_ML.ipynb',
                    'descripcion': 'Modelos de ML y predicciones',
                    'categoria': 'ml',
                    'estado': 'activo'
                }
            },
            'modulos_avanzados': {
                'ia_avanzada': {
                    'nombre': 'IA Avanzada METGO',
                    'archivo': 'ia_avanzada_metgo.py',
                    'descripcion': 'Modelos de IA avanzada (LSTM, Transformer)',
                    'categoria': 'ai',
                    'estado': 'activo'
                },
                'sistema_iot': {
                    'nombre': 'Sistema IoT METGO',
                    'archivo': 'sistema_iot_metgo.py',
                    'descripcion': 'Sistema IoT con sensores inteligentes',
                    'categoria': 'iot',
                    'estado': 'activo'
                },
                'analisis_avanzado': {
                    'nombre': 'Análisis Avanzado METGO',
                    'archivo': 'analisis_avanzado_metgo.py',
                    'descripcion': 'Análisis avanzado de series temporales',
                    'categoria': 'analysis',
                    'estado': 'activo'
                },
                'visualizacion_3d': {
                    'nombre': 'Visualización 3D METGO',
                    'archivo': 'visualizacion_3d_metgo.py',
                    'descripcion': 'Visualizaciones 3D e inmersivas',
                    'categoria': 'visualization',
                    'estado': 'activo'
                },
                'apis_avanzadas': {
                    'nombre': 'APIs Avanzadas METGO',
                    'archivo': 'apis_avanzadas_metgo.py',
                    'descripcion': 'APIs avanzadas con microservicios',
                    'categoria': 'api',
                    'estado': 'activo'
                }
            },
            'datos_satelitales': {
                'imagenes_satelitales': {
                    'nombre': 'Imágenes Satelitales',
                    'descripcion': 'Procesamiento de imágenes satelitales',
                    'categoria': 'satellite',
                    'estado': 'activo',
                    'datos': 'data/satelitales/imagenes/'
                },
                'metadatos_satelitales': {
                    'nombre': 'Metadatos Satelitales',
                    'descripcion': 'Metadatos de imágenes satelitales',
                    'categoria': 'satellite',
                    'estado': 'activo',
                    'datos': 'data/satelitales/metadatos/'
                },
                'analisis_satelital': {
                    'nombre': 'Análisis Satelital',
                    'descripcion': 'Análisis de datos satelitales',
                    'categoria': 'satellite',
                    'estado': 'activo',
                    'datos': 'data/satelitales/'
                }
            },
            'sistemas_especializados': {
                'monitoreo_avanzado': {
                    'nombre': 'Monitoreo Avanzado',
                    'archivo': 'monitoreo_avanzado_metgo.py',
                    'descripcion': 'Sistema de monitoreo avanzado',
                    'categoria': 'monitoring',
                    'estado': 'activo'
                },
                'respaldos_automaticos': {
                    'nombre': 'Respaldos Automáticos',
                    'archivo': 'respaldos_automaticos_metgo.py',
                    'descripcion': 'Sistema de respaldos automáticos',
                    'categoria': 'backup',
                    'estado': 'activo'
                },
                'optimizacion_rendimiento': {
                    'nombre': 'Optimización de Rendimiento',
                    'archivo': 'optimizacion_rendimiento_metgo.py',
                    'descripcion': 'Optimización de rendimiento del sistema',
                    'categoria': 'optimization',
                    'estado': 'activo'
                },
                'escalabilidad': {
                    'nombre': 'Escalabilidad',
                    'archivo': 'escalabilidad_metgo.py',
                    'descripcion': 'Sistema de escalabilidad',
                    'categoria': 'scalability',
                    'estado': 'activo'
                }
            },
            'integracion_completa': {
                'orquestador_avanzado': {
                    'nombre': 'Orquestador Avanzado',
                    'archivo': 'orquestador_metgo_avanzado.py',
                    'descripcion': 'Orquestador principal del sistema',
                    'categoria': 'orchestration',
                    'estado': 'activo'
                },
                'pipeline_completo': {
                    'nombre': 'Pipeline Completo',
                    'archivo': 'pipeline_completo_metgo.py',
                    'descripcion': 'Pipeline completo de datos',
                    'categoria': 'pipeline',
                    'estado': 'activo'
                },
                'configuracion_unificada': {
                    'nombre': 'Configuración Unificada',
                    'archivo': 'configuracion_unificada_metgo.py',
                    'descripcion': 'Configuración unificada del sistema',
                    'categoria': 'configuration',
                    'estado': 'activo'
                },
                'sistema_unificado': {
                    'nombre': 'Sistema Unificado',
                    'archivo': 'sistema_unificado_metgo.py',
                    'descripcion': 'Sistema unificado principal',
                    'categoria': 'unified',
                    'estado': 'activo'
                }
            }
        }
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Estado del sistema
        self.estado_sistema = {
            'modulos_activos': 0,
            'modulos_totales': 0,
            'notebooks_ejecutados': 0,
            'datos_procesados': 0,
            'errores': 0,
            'ultima_sincronizacion': datetime.now().isoformat()
        }
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        try:
            for directorio in self.configuracion.values():
                if isinstance(directorio, str) and '/' in directorio:
                    Path(directorio).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")
    
    def _configurar_logging(self):
        """Configurar sistema de logging"""
        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(f"{self.configuracion['directorio_logs']}/dashboard_global.log"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('METGO_DASHBOARD_GLOBAL')
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/dashboard_global.db"
            
            self.conexion_bd = sqlite3.connect(archivo_bd, check_same_thread=False)
            self.cursor_bd = self.conexion_bd.cursor()
            
            # Crear tablas
            self._crear_tablas_bd()
            
            self.logger.info(f"Base de datos inicializada: {archivo_bd}")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def _crear_tablas_bd(self):
        """Crear tablas en la base de datos"""
        try:
            # Tabla de módulos
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS modulos (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    archivo TEXT,
                    categoria TEXT,
                    estado TEXT,
                    ultima_ejecucion DATETIME,
                    resultado TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de ejecuciones
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS ejecuciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    modulo_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    duracion REAL,
                    exitoso BOOLEAN,
                    errores TEXT,
                    resultado TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de datos satelitales
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS datos_satelitales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    archivo TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    procesado BOOLEAN DEFAULT FALSE,
                    resultado TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_modulos_categoria ON modulos(categoria)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_ejecuciones_modulo ON ejecuciones(modulo_id)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_datos_satelitales_tipo ON datos_satelitales(tipo)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def verificar_modulos(self) -> Dict[str, Any]:
        """Verificar estado de todos los módulos"""
        try:
            self.logger.info("Verificando módulos del sistema...")
            
            resultados = {}
            modulos_activos = 0
            modulos_totales = 0
            
            for categoria, modulos in self.modulos_sistema.items():
                resultados[categoria] = {}
                
                for modulo_id, modulo_info in modulos.items():
                    modulos_totales += 1
                    
                    # Verificar si el archivo existe
                    archivo = modulo_info.get('archivo', '')
                    existe = False
                    
                    if archivo:
                        existe = Path(archivo).exists()
                        if existe:
                            modulos_activos += 1
                    
                    # Verificar datos satelitales
                    datos_path = modulo_info.get('datos', '')
                    datos_existen = False
                    
                    if datos_path:
                        datos_existen = Path(datos_path).exists()
                        if datos_existen:
                            modulos_activos += 1
                    
                    resultados[categoria][modulo_id] = {
                        'nombre': modulo_info['nombre'],
                        'descripcion': modulo_info['descripcion'],
                        'categoria': modulo_info['categoria'],
                        'estado': modulo_info['estado'],
                        'archivo': archivo,
                        'existe': existe,
                        'datos': datos_path,
                        'datos_existen': datos_existen
                    }
            
            # Actualizar estado del sistema
            self.estado_sistema['modulos_activos'] = modulos_activos
            self.estado_sistema['modulos_totales'] = modulos_totales
            
            self.logger.info(f"Verificación completada: {modulos_activos}/{modulos_totales} módulos activos")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error verificando módulos: {e}")
            return {}
    
    def crear_dashboard_streamlit(self):
        """Crear dashboard global con Streamlit"""
        try:
            # Configurar página
            st.set_page_config(
                page_title="METGO 3D - Dashboard Global",
                page_icon="🌐",
                layout="wide",
                initial_sidebar_state="expanded"
            )
            
            # Título principal
            st.title("🌐 METGO 3D - Dashboard Global")
            st.markdown("### Sistema Meteorológico Agrícola Quillota - Integración Completa")
            
            # Sidebar
            with st.sidebar:
                st.header("⚙️ Configuración Global")
                
                # Selector de categoría
                categorias = list(self.modulos_sistema.keys())
                categoria_seleccionada = st.selectbox(
                    "📂 Categoría de Módulos",
                    ["Todas"] + categorias
                )
                
                # Selector de acción
                accion = st.selectbox(
                    "🎯 Acción",
                    ["Ver estado", "Ejecutar módulo", "Ver datos satelitales", "Dashboard completo"]
                )
            
            # Contenido principal
            if accion == "Ver estado":
                self._mostrar_estado_modulos(categoria_seleccionada)
            elif accion == "Ejecutar módulo":
                self._mostrar_ejecucion_modulos(categoria_seleccionada)
            elif accion == "Ver datos satelitales":
                self._mostrar_datos_satelitales()
            elif accion == "Dashboard completo":
                self._mostrar_dashboard_completo()
            
        except Exception as e:
            st.error(f"Error creando dashboard global: {e}")
            self.logger.error(f"Error creando dashboard global: {e}")
    
    def _mostrar_estado_modulos(self, categoria: str):
        """Mostrar estado de los módulos"""
        try:
            st.header("📊 Estado de los Módulos del Sistema")
            
            # Verificar módulos si no están verificados
            if not hasattr(self, 'estado_modulos') or not self.estado_modulos:
                with st.spinner("Verificando módulos..."):
                    self.estado_modulos = self.verificar_modulos()
            
            # Filtrar por categoría
            modulos_filtrados = self.estado_modulos
            if categoria != "Todas":
                modulos_filtrados = {categoria: self.estado_modulos.get(categoria, {})}
            
            # Mostrar métricas generales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Módulos Totales", self.estado_sistema['modulos_totales'])
            
            with col2:
                st.metric("Módulos Activos", self.estado_sistema['modulos_activos'])
            
            with col3:
                porcentaje = (self.estado_sistema['modulos_activos'] / self.estado_sistema['modulos_totales'] * 100) if self.estado_sistema['modulos_totales'] > 0 else 0
                st.metric("Porcentaje Activo", f"{porcentaje:.1f}%")
            
            with col4:
                st.metric("Última Sincronización", self.estado_sistema['ultima_sincronizacion'][:19])
            
            # Mostrar módulos por categoría
            for cat, modulos in modulos_filtrados.items():
                st.subheader(f"📁 {cat.replace('_', ' ').title()}")
                
                # Crear DataFrame
                datos = []
                for modulo_id, info in modulos.items():
                    datos.append({
                        'ID': modulo_id,
                        'Nombre': info['nombre'],
                        'Categoría': info['categoria'],
                        'Estado': '✅' if info['existe'] or info['datos_existen'] else '❌',
                        'Archivo': '✅' if info['existe'] else '❌',
                        'Datos': '✅' if info['datos_existen'] else '❌',
                        'Descripción': info['descripcion']
                    })
                
                if datos:
                    df = pd.DataFrame(datos)
                    st.dataframe(df, width='stretch')
                else:
                    st.info(f"No hay módulos en la categoría {cat}")
            
        except Exception as e:
            st.error(f"Error mostrando estado: {e}")
    
    def _mostrar_ejecucion_modulos(self, categoria: str):
        """Mostrar interfaz de ejecución de módulos"""
        try:
            st.header("🚀 Ejecutar Módulos del Sistema")
            
            # Verificar módulos si no están verificados
            if not hasattr(self, 'estado_modulos') or not self.estado_modulos:
                with st.spinner("Verificando módulos..."):
                    self.estado_modulos = self.verificar_modulos()
            
            # Filtrar por categoría
            modulos_filtrados = self.estado_modulos
            if categoria != "Todas":
                modulos_filtrados = {categoria: self.estado_modulos.get(categoria, {})}
            
            # Selector de módulo
            modulos_disponibles = {}
            for cat, modulos in modulos_filtrados.items():
                for modulo_id, info in modulos.items():
                    if info.get('existe', False):
                        modulos_disponibles[f"{cat}_{modulo_id}"] = info
            
            if modulos_disponibles:
                modulo_seleccionado = st.selectbox(
                    "📓 Seleccionar módulo",
                    list(modulos_disponibles.keys()),
                    format_func=lambda x: modulos_disponibles[x]['nombre']
                )
                
                # Información del módulo
                info = modulos_disponibles[modulo_seleccionado]
                st.info(f"**Descripción:** {info.get('descripcion', 'N/A')}")
                st.info(f"**Archivo:** {info.get('archivo', 'N/A')}")
                
                # Botón de ejecución
                if st.button("▶️ Ejecutar Módulo", type="primary"):
                    with st.spinner("Ejecutando módulo..."):
                        resultado = self._ejecutar_modulo(modulo_seleccionado, info)
                    
                    if resultado.get('exitoso', False):
                        st.success(f"✅ Módulo ejecutado exitosamente en {resultado.get('duracion', 0):.2f} segundos")
                        
                        # Mostrar salida
                        if resultado.get('salida'):
                            with st.expander("📋 Salida del módulo"):
                                st.text(resultado['salida'])
                    else:
                        st.error(f"❌ Error ejecutando módulo: {resultado.get('error', 'Error desconocido')}")
                        
                        # Mostrar errores
                        if resultado.get('errores'):
                            with st.expander("⚠️ Errores"):
                                st.text(resultado['errores'])
            else:
                st.warning("No hay módulos disponibles para ejecutar en la categoría seleccionada")
                
        except Exception as e:
            st.error(f"Error en ejecución: {e}")
    
    def _ejecutar_modulo(self, modulo_id: str, info: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar un módulo específico"""
        try:
            self.logger.info(f"Ejecutando módulo: {modulo_id}")
            
            inicio = time.time()
            
            archivo = info.get('archivo', '')
            if not archivo or not Path(archivo).exists():
                return {'exitoso': False, 'error': 'Archivo no encontrado'}
            
            try:
                # Ejecutar módulo
                resultado = subprocess.run([
                    sys.executable, archivo
                ], capture_output=True, text=True, timeout=300)  # 5 minutos timeout
                
                duracion = time.time() - inicio
                
                if resultado.returncode == 0:
                    resultado_ejecucion = {
                        'exitoso': True,
                        'duracion': duracion,
                        'salida': resultado.stdout,
                        'errores': resultado.stderr,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    resultado_ejecucion = {
                        'exitoso': False,
                        'duracion': duracion,
                        'salida': resultado.stdout,
                        'errores': resultado.stderr,
                        'timestamp': datetime.now().isoformat()
                    }
                
                self.logger.info(f"Módulo {modulo_id} ejecutado en {duracion:.2f}s")
                return resultado_ejecucion
                
            except subprocess.TimeoutExpired:
                duracion = time.time() - inicio
                return {
                    'exitoso': False,
                    'duracion': duracion,
                    'error': 'Timeout: El módulo tardó más de 5 minutos',
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                duracion = time.time() - inicio
                return {
                    'exitoso': False,
                    'duracion': duracion,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error ejecutando módulo {modulo_id}: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def _mostrar_datos_satelitales(self):
        """Mostrar datos satelitales"""
        try:
            st.header("🛰️ Datos Satelitales")
            
            # Verificar datos satelitales
            datos_satelitales = self.modulos_sistema['datos_satelitales']
            
            for tipo, info in datos_satelitales.items():
                st.subheader(f"🛰️ {info['nombre']}")
                
                # Verificar si existen datos
                datos_path = info.get('datos', '')
                if datos_path and Path(datos_path).exists():
                    st.success(f"✅ Datos disponibles en: {datos_path}")
                    
                    # Listar archivos
                    try:
                        archivos = list(Path(datos_path).glob('*'))
                        if archivos:
                            st.write(f"**Archivos encontrados:** {len(archivos)}")
                            
                            # Mostrar algunos archivos
                            for archivo in archivos[:5]:
                                st.write(f"- {archivo.name}")
                            
                            if len(archivos) > 5:
                                st.write(f"... y {len(archivos) - 5} archivos más")
                        else:
                            st.info("No hay archivos en el directorio")
                    except Exception as e:
                        st.error(f"Error listando archivos: {e}")
                else:
                    st.warning(f"❌ Datos no disponibles en: {datos_path}")
                
                st.write(f"**Descripción:** {info['descripcion']}")
                st.write(f"**Estado:** {info['estado']}")
                st.write("---")
            
        except Exception as e:
            st.error(f"Error mostrando datos satelitales: {e}")
    
    def _mostrar_dashboard_completo(self):
        """Mostrar dashboard completo del sistema"""
        try:
            st.header("🌐 Dashboard Completo del Sistema METGO 3D")
            
            # Métricas generales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Módulos", self.estado_sistema['modulos_totales'])
            
            with col2:
                st.metric("Módulos Activos", self.estado_sistema['modulos_activos'])
            
            with col3:
                porcentaje = (self.estado_sistema['modulos_activos'] / self.estado_sistema['modulos_totales'] * 100) if self.estado_sistema['modulos_totales'] > 0 else 0
                st.metric("Porcentaje Activo", f"{porcentaje:.1f}%")
            
            with col4:
                st.metric("Versión del Sistema", self.configuracion['version'])
            
            # Gráfico de categorías
            if hasattr(self, 'estado_modulos') and self.estado_modulos:
                categorias_count = {}
                for categoria, modulos in self.estado_modulos.items():
                    categorias_count[categoria] = len(modulos)
                
                fig = px.pie(
                    values=list(categorias_count.values()),
                    names=list(categorias_count.keys()),
                    title='Distribución de Módulos por Categoría'
                )
                st.plotly_chart(fig, config=PLOTLY_CONFIG, width='stretch')
            
            # Estado del sistema
            st.subheader("🔧 Estado del Sistema")
            
            # Verificar componentes
            componentes = {
                'Base de datos': Path(f"{self.configuracion['directorio_datos']}/dashboard_global.db").exists(),
                'Logs': Path(self.configuracion['directorio_logs']).exists(),
                'Módulos verificados': hasattr(self, 'estado_modulos') and len(self.estado_modulos) > 0,
                'Datos satelitales': Path('data/satelitales').exists()
            }
            
            for componente, estado in componentes.items():
                if estado:
                    st.success(f"✅ {componente}")
                else:
                    st.error(f"❌ {componente}")
            
            # Resumen de módulos
            st.subheader("📋 Resumen de Módulos")
            
            if hasattr(self, 'estado_modulos') and self.estado_modulos:
                for categoria, modulos in self.estado_modulos.items():
                    st.write(f"**{categoria.replace('_', ' ').title()}:** {len(modulos)} módulos")
            else:
                st.info("Ejecuta 'Ver estado' para cargar información de módulos")
                    
        except Exception as e:
            st.error(f"Error mostrando dashboard completo: {e}")
    
    def generar_reporte_dashboard(self) -> str:
        """Generar reporte del dashboard global"""
        try:
            self.logger.info("Generando reporte del dashboard global...")
            
            # Verificar módulos si no están verificados
            if not hasattr(self, 'estado_modulos') or not self.estado_modulos:
                self.estado_modulos = self.verificar_modulos()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Dashboard Global',
                'version': self.configuracion['version'],
                'estado_sistema': self.estado_sistema,
                'modulos_sistema': self.modulos_sistema,
                'estado_modulos': self.estado_modulos,
                'resumen': {
                    'total_modulos': self.estado_sistema['modulos_totales'],
                    'modulos_activos': self.estado_sistema['modulos_activos'],
                    'porcentaje_activo': (self.estado_sistema['modulos_activos'] / self.estado_sistema['modulos_totales'] * 100) if self.estado_sistema['modulos_totales'] > 0 else 0,
                    'categorias': len(self.modulos_sistema),
                    'ultima_sincronizacion': self.estado_sistema['ultima_sincronizacion']
                },
                'recomendaciones': [
                    "Verificar módulos faltantes",
                    "Ejecutar módulos críticos regularmente",
                    "Monitorear datos satelitales",
                    "Revisar errores de ejecución",
                    "Actualizar configuraciones de módulos"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"dashboard_global_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte del dashboard global generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal del dashboard global"""
    print("DASHBOARD GLOBAL METGO 3D - INTEGRACION COMPLETA")
    print("Sistema Meteorologico Agricola Quillota - Version 2.0")
    print("=" * 70)
    
    try:
        # Crear dashboard
        dashboard = DashboardGlobalMETGO()
        
        # Verificar módulos
        print("\nVerificando modulos del sistema...")
        estado = dashboard.verificar_modulos()
        
        if estado:
            print(f"Verificacion completada: {dashboard.estado_sistema['modulos_activos']}/{dashboard.estado_sistema['modulos_totales']} modulos activos")
            
            # Mostrar resumen
            print(f"\nResumen:")
            print(f"   Total modulos: {dashboard.estado_sistema['modulos_totales']}")
            print(f"   Modulos activos: {dashboard.estado_sistema['modulos_activos']}")
            print(f"   Porcentaje activo: {(dashboard.estado_sistema['modulos_activos']/dashboard.estado_sistema['modulos_totales']*100):.1f}%")
            print(f"   Categorias: {len(dashboard.modulos_sistema)}")
            
            # Generar reporte
            print(f"\nGenerando reporte...")
            reporte = dashboard.generar_reporte_dashboard()
            
            if reporte:
                print(f"Reporte generado: {reporte}")
            else:
                print(f"Error generando reporte")
            
            # Iniciar dashboard Streamlit
            print(f"\nIniciando dashboard global con Streamlit...")
            print(f"   Ejecuta: streamlit run dashboard_global_metgo.py")
            print(f"   URL: http://localhost:8503")
            
        else:
            print("Error verificando modulos")
        
        return True
        
    except Exception as e:
        print(f"\nError en dashboard global: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
