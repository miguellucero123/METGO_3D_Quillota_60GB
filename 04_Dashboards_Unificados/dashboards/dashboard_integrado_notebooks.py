#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎛️ DASHBOARD INTEGRADO CON TODOS LOS NOTEBOOKS METGO 3D
Sistema Meteorológico Agrícola Quillota - Dashboard Unificado
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

class DashboardIntegradoNotebooks:
    """Dashboard que integra todos los notebooks de METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_notebooks': '.',
            'directorio_datos': 'data/dashboard',
            'directorio_logs': 'logs/dashboard',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Lista de notebooks a integrar
        self.notebooks = [
            {
                'id': '00_sistema_principal',
                'nombre': 'Sistema Principal MIP Quillota',
                'archivo': '00_Sistema_Principal_MIP_Quillota.ipynb',
                'descripcion': 'Sistema principal operativo',
                'categoria': 'core'
            },
            {
                'id': '01_configuracion',
                'nombre': 'Configuración e Imports',
                'archivo': '01_Configuracion_e_imports.ipynb',
                'descripcion': 'Configuración y imports del sistema',
                'categoria': 'config'
            },
            {
                'id': '02_procesamiento',
                'nombre': 'Carga y Procesamiento de Datos',
                'archivo': '02_Carga_y_Procesamiento_Datos.ipynb',
                'descripcion': 'Procesamiento de datos meteorológicos',
                'categoria': 'data'
            },
            {
                'id': '03_analisis',
                'nombre': 'Análisis Meteorológico',
                'archivo': '03_Analisis_Meteorologico.ipynb',
                'descripcion': 'Análisis meteorológico avanzado',
                'categoria': 'analysis'
            },
            {
                'id': '04_visualizaciones',
                'nombre': 'Visualizaciones',
                'archivo': '04_Visualizaciones.ipynb',
                'descripcion': 'Visualizaciones y gráficos',
                'categoria': 'visualization'
            },
            {
                'id': '05_modelos_ml',
                'nombre': 'Modelos de Machine Learning',
                'archivo': '05_Modelos_ML.ipynb',
                'descripcion': 'Modelos de ML y predicciones',
                'categoria': 'ml'
            },
            {
                'id': '06_dashboard',
                'nombre': 'Dashboard Interactivo',
                'archivo': '06_Dashboard_Interactivo.ipynb',
                'descripcion': 'Dashboard interactivo con Streamlit',
                'categoria': 'dashboard'
            },
            {
                'id': '07_reportes',
                'nombre': 'Reportes Automáticos',
                'archivo': '07_Reportes_Automaticos.ipynb',
                'descripcion': 'Generación de reportes automáticos',
                'categoria': 'reports'
            },
            {
                'id': '08_apis',
                'nombre': 'APIs Externas',
                'archivo': '08_APIs_Externas.ipynb',
                'descripcion': 'Integración con APIs externas',
                'categoria': 'api'
            },
            {
                'id': '09_testing',
                'nombre': 'Testing y Validación',
                'archivo': '09_Testing_Validacion.ipynb',
                'descripcion': 'Testing y validación del sistema',
                'categoria': 'testing'
            },
            {
                'id': '10_deployment',
                'nombre': 'Deployment en Producción',
                'archivo': '10_Deployment_Produccion.ipynb',
                'descripcion': 'Deployment y producción',
                'categoria': 'deployment'
            },
            {
                'id': '11_monitoreo',
                'nombre': 'Monitoreo en Tiempo Real',
                'archivo': '11_Monitoreo_Tiempo_Real.ipynb',
                'descripcion': 'Monitoreo en tiempo real',
                'categoria': 'monitoring'
            },
            {
                'id': '12_respaldos',
                'nombre': 'Respaldos Automáticos',
                'archivo': '12_Respaldos_Automaticos.ipynb',
                'descripcion': 'Sistema de respaldos automáticos',
                'categoria': 'backup'
            },
            {
                'id': '13_optimizacion',
                'nombre': 'Optimización y Mantenimiento',
                'archivo': '13_Optimizacion_Mantenimiento.ipynb',
                'descripcion': 'Optimización y mantenimiento',
                'categoria': 'optimization'
            },
            {
                'id': '14_reportes_avanzados',
                'nombre': 'Reportes Avanzados',
                'archivo': '14_Reportes_Avanzados.ipynb',
                'descripcion': 'Reportes avanzados y análisis',
                'categoria': 'advanced_reports'
            },
            {
                'id': '15_apis_externas',
                'nombre': 'Integración APIs Externas',
                'archivo': '15_Integracion_APIs_Externas.ipynb',
                'descripcion': 'Integración avanzada con APIs',
                'categoria': 'external_apis'
            }
        ]
        
        # Estado de los notebooks
        self.estado_notebooks = {}
        self.resultados_notebooks = {}
        
        # Base de datos
        self._inicializar_base_datos()
    
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
                    logging.FileHandler(f"{self.configuracion['directorio_logs']}/dashboard_integrado.log"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('METGO_DASHBOARD_INTEGRADO')
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/dashboard_integrado.db"
            
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
            # Tabla de notebooks
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS notebooks (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    archivo TEXT NOT NULL,
                    descripcion TEXT,
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
                    notebook_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    duracion REAL,
                    exitoso BOOLEAN,
                    errores TEXT,
                    resultado TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_notebooks_categoria ON notebooks(categoria)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_ejecuciones_notebook ON ejecuciones(notebook_id)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_ejecuciones_timestamp ON ejecuciones(timestamp)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def verificar_notebooks(self) -> Dict[str, Any]:
        """Verificar estado de todos los notebooks"""
        try:
            self.logger.info("Verificando notebooks...")
            
            resultados = {}
            
            for notebook in self.notebooks:
                try:
                    archivo = Path(notebook['archivo'])
                    
                    if archivo.exists():
                        # Verificar tamaño
                        tamaño = archivo.stat().st_size
                        
                        # Verificar formato
                        try:
                            with open(archivo, 'r', encoding='utf-8') as f:
                                contenido = f.read()
                                if '"cell_type"' in contenido and '"source"' in contenido:
                                    formato = 'valido'
                                else:
                                    formato = 'invalido'
                        except Exception as e:
                            formato = f'error: {e}'
                        
                        # Verificar última modificación
                        ultima_modificacion = datetime.fromtimestamp(archivo.stat().st_mtime)
                        
                        resultados[notebook['id']] = {
                            'nombre': notebook['nombre'],
                            'archivo': notebook['archivo'],
                            'existe': True,
                            'tamaño': tamaño,
                            'formato': formato,
                            'ultima_modificacion': ultima_modificacion.isoformat(),
                            'categoria': notebook['categoria'],
                            'descripcion': notebook['descripcion']
                        }
                        
                        # Actualizar estado en base de datos
                        self._actualizar_estado_notebook(notebook['id'], 'disponible')
                        
                    else:
                        resultados[notebook['id']] = {
                            'nombre': notebook['nombre'],
                            'archivo': notebook['archivo'],
                            'existe': False,
                            'categoria': notebook['categoria'],
                            'descripcion': notebook['descripcion']
                        }
                        
                        # Actualizar estado en base de datos
                        self._actualizar_estado_notebook(notebook['id'], 'no_encontrado')
                        
                except Exception as e:
                    self.logger.error(f"Error verificando notebook {notebook['id']}: {e}")
                    resultados[notebook['id']] = {
                        'nombre': notebook['nombre'],
                        'archivo': notebook['archivo'],
                        'existe': False,
                        'error': str(e),
                        'categoria': notebook['categoria'],
                        'descripcion': notebook['descripcion']
                    }
            
            self.estado_notebooks = resultados
            self.logger.info(f"Verificación completada: {len(resultados)} notebooks")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error verificando notebooks: {e}")
            return {}
    
    def _actualizar_estado_notebook(self, notebook_id: str, estado: str):
        """Actualizar estado de notebook en la base de datos"""
        try:
            self.cursor_bd.execute('''
                INSERT OR REPLACE INTO notebooks 
                (id, nombre, archivo, descripcion, categoria, estado, ultima_ejecucion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                notebook_id,
                self.notebooks[notebook_id]['nombre'] if notebook_id in self.notebooks else notebook_id,
                self.notebooks[notebook_id]['archivo'] if notebook_id in self.notebooks else '',
                self.notebooks[notebook_id]['descripcion'] if notebook_id in self.notebooks else '',
                self.notebooks[notebook_id]['categoria'] if notebook_id in self.notebooks else '',
                estado,
                datetime.now()
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error actualizando estado del notebook: {e}")
    
    def ejecutar_notebook(self, notebook_id: str) -> Dict[str, Any]:
        """Ejecutar un notebook específico"""
        try:
            self.logger.info(f"Ejecutando notebook: {notebook_id}")
            
            if notebook_id not in self.estado_notebooks:
                return {'exitoso': False, 'error': 'Notebook no encontrado'}
            
            notebook_info = self.estado_notebooks[notebook_id]
            
            if not notebook_info.get('existe', False):
                return {'exitoso': False, 'error': 'Archivo de notebook no existe'}
            
            inicio = time.time()
            
            try:
                # Convertir notebook a Python
                archivo_notebook = notebook_info['archivo']
                
                with open(archivo_notebook, 'r', encoding='utf-8') as f:
                    notebook = nbformat.read(f, as_version=4)
                
                # Exportar a Python
                exporter = PythonExporter()
                (body, resources) = exporter.from_notebook_node(notebook)
                
                # Guardar script Python temporal
                script_temp = f"temp_{notebook_id}.py"
                with open(script_temp, 'w', encoding='utf-8') as f:
                    f.write(body)
                
                # Ejecutar script
                resultado = subprocess.run([
                    sys.executable, script_temp
                ], capture_output=True, text=True, timeout=300)  # 5 minutos timeout
                
                # Limpiar archivo temporal
                if Path(script_temp).exists():
                    Path(script_temp).unlink()
                
                duracion = time.time() - inicio
                
                if resultado.returncode == 0:
                    resultado_ejecucion = {
                        'exitoso': True,
                        'duracion': duracion,
                        'salida': resultado.stdout,
                        'errores': resultado.stderr,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Guardar ejecución exitosa
                    self._guardar_ejecucion(notebook_id, duracion, True, None, resultado.stdout)
                    
                else:
                    resultado_ejecucion = {
                        'exitoso': False,
                        'duracion': duracion,
                        'salida': resultado.stdout,
                        'errores': resultado.stderr,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Guardar ejecución fallida
                    self._guardar_ejecucion(notebook_id, duracion, False, resultado.stderr, resultado.stdout)
                
                self.resultados_notebooks[notebook_id] = resultado_ejecucion
                self.logger.info(f"Notebook {notebook_id} ejecutado en {duracion:.2f}s")
                return resultado_ejecucion
                
            except subprocess.TimeoutExpired:
                duracion = time.time() - inicio
                resultado_ejecucion = {
                    'exitoso': False,
                    'duracion': duracion,
                    'error': 'Timeout: El notebook tardó más de 5 minutos',
                    'timestamp': datetime.now().isoformat()
                }
                
                self._guardar_ejecucion(notebook_id, duracion, False, 'Timeout', None)
                return resultado_ejecucion
                
            except Exception as e:
                duracion = time.time() - inicio
                resultado_ejecucion = {
                    'exitoso': False,
                    'duracion': duracion,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                
                self._guardar_ejecucion(notebook_id, duracion, False, str(e), None)
                return resultado_ejecucion
                
        except Exception as e:
            self.logger.error(f"Error ejecutando notebook {notebook_id}: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def _guardar_ejecucion(self, notebook_id: str, duracion: float, exitoso: bool, errores: str, resultado: str):
        """Guardar ejecución en la base de datos"""
        try:
            self.cursor_bd.execute('''
                INSERT INTO ejecuciones 
                (notebook_id, timestamp, duracion, exitoso, errores, resultado)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                notebook_id,
                datetime.now(),
                duracion,
                exitoso,
                errores,
                resultado
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error guardando ejecución: {e}")
    
    def crear_dashboard_streamlit(self):
        """Crear dashboard con Streamlit"""
        try:
            # Configurar página
            st.set_page_config(
                page_title="METGO 3D - Dashboard Integrado",
                page_icon="🌾",
                layout="wide",
                initial_sidebar_state="expanded"
            )
            
            # Título principal
            st.title("🌾 METGO 3D - Dashboard Integrado de Notebooks")
            st.markdown("### Sistema Meteorológico Agrícola Quillota - Versión 2.0")
            
            # Sidebar
            with st.sidebar:
                st.header("⚙️ Configuración")
                
                # Selector de categoría
                categorias = list(set(notebook['categoria'] for notebook in self.notebooks))
                categoria_seleccionada = st.selectbox(
                    "📂 Categoría",
                    ["Todas"] + categorias
                )
                
                # Selector de acción
                accion = st.selectbox(
                    "🎯 Acción",
                    ["Ver estado", "Ejecutar notebook", "Ver resultados", "Dashboard completo"]
                )
            
            # Contenido principal
            if accion == "Ver estado":
                self._mostrar_estado_notebooks(categoria_seleccionada)
            elif accion == "Ejecutar notebook":
                self._mostrar_ejecucion_notebooks(categoria_seleccionada)
            elif accion == "Ver resultados":
                self._mostrar_resultados_notebooks(categoria_seleccionada)
            elif accion == "Dashboard completo":
                self._mostrar_dashboard_completo()
            
        except Exception as e:
            st.error(f"Error creando dashboard: {e}")
            self.logger.error(f"Error creando dashboard: {e}")
    
    def _mostrar_estado_notebooks(self, categoria: str):
        """Mostrar estado de los notebooks"""
        try:
            st.header("📊 Estado de los Notebooks")
            
            # Verificar notebooks si no están verificados
            if not self.estado_notebooks:
                with st.spinner("Verificando notebooks..."):
                    self.verificar_notebooks()
            
            # Filtrar por categoría
            notebooks_filtrados = self.estado_notebooks
            if categoria != "Todas":
                notebooks_filtrados = {
                    k: v for k, v in self.estado_notebooks.items() 
                    if v.get('categoria') == categoria
                }
            
            # Crear DataFrame
            datos = []
            for notebook_id, info in notebooks_filtrados.items():
                datos.append({
                    'ID': notebook_id,
                    'Nombre': info.get('nombre', ''),
                    'Archivo': info.get('archivo', ''),
                    'Categoría': info.get('categoria', ''),
                    'Existe': '✅' if info.get('existe', False) else '❌',
                    'Tamaño (KB)': f"{info.get('tamaño', 0) / 1024:.1f}" if info.get('tamaño') else 'N/A',
                    'Formato': info.get('formato', 'N/A'),
                    'Última Modificación': info.get('ultima_modificacion', 'N/A')
                })
            
            if datos:
                df = pd.DataFrame(datos)
                st.dataframe(df, width='stretch')
                
                # Estadísticas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Notebooks", len(datos))
                
                with col2:
                    existentes = sum(1 for d in datos if d['Existe'] == '✅')
                    st.metric("Existentes", existentes)
                
                with col3:
                    faltantes = len(datos) - existentes
                    st.metric("Faltantes", faltantes)
                
                with col4:
                    porcentaje = (existentes / len(datos) * 100) if datos else 0
                    st.metric("Completitud", f"{porcentaje:.1f}%")
            else:
                st.warning("No se encontraron notebooks para la categoría seleccionada")
                
        except Exception as e:
            st.error(f"Error mostrando estado: {e}")
    
    def _mostrar_ejecucion_notebooks(self, categoria: str):
        """Mostrar interfaz de ejecución de notebooks"""
        try:
            st.header("🚀 Ejecutar Notebooks")
            
            # Verificar notebooks si no están verificados
            if not self.estado_notebooks:
                with st.spinner("Verificando notebooks..."):
                    self.verificar_notebooks()
            
            # Filtrar por categoría
            notebooks_filtrados = self.estado_notebooks
            if categoria != "Todas":
                notebooks_filtrados = {
                    k: v for k, v in self.estado_notebooks.items() 
                    if v.get('categoria') == categoria
                }
            
            # Selector de notebook
            notebooks_disponibles = {
                k: v for k, v in notebooks_filtrados.items() 
                if v.get('existe', False)
            }
            
            if notebooks_disponibles:
                notebook_seleccionado = st.selectbox(
                    "📓 Seleccionar notebook",
                    list(notebooks_disponibles.keys()),
                    format_func=lambda x: notebooks_disponibles[x]['nombre']
                )
                
                # Información del notebook
                info = notebooks_disponibles[notebook_seleccionado]
                st.info(f"**Descripción:** {info.get('descripcion', 'N/A')}")
                
                # Botón de ejecución
                if st.button("▶️ Ejecutar Notebook", type="primary"):
                    with st.spinner("Ejecutando notebook..."):
                        resultado = self.ejecutar_notebook(notebook_seleccionado)
                    
                    if resultado.get('exitoso', False):
                        st.success(f"✅ Notebook ejecutado exitosamente en {resultado.get('duracion', 0):.2f} segundos")
                        
                        # Mostrar salida
                        if resultado.get('salida'):
                            with st.expander("📋 Salida del notebook"):
                                st.text(resultado['salida'])
                    else:
                        st.error(f"❌ Error ejecutando notebook: {resultado.get('error', 'Error desconocido')}")
                        
                        # Mostrar errores
                        if resultado.get('errores'):
                            with st.expander("⚠️ Errores"):
                                st.text(resultado['errores'])
            else:
                st.warning("No hay notebooks disponibles para ejecutar en la categoría seleccionada")
                
        except Exception as e:
            st.error(f"Error en ejecución: {e}")
    
    def _mostrar_resultados_notebooks(self, categoria: str):
        """Mostrar resultados de ejecuciones"""
        try:
            st.header("📈 Resultados de Ejecuciones")
            
            # Obtener ejecuciones recientes
            self.cursor_bd.execute('''
                SELECT e.*, n.nombre, n.categoria 
                FROM ejecuciones e
                JOIN notebooks n ON e.notebook_id = n.id
                ORDER BY e.timestamp DESC
                LIMIT 50
            ''')
            ejecuciones = self.cursor_bd.fetchall()
            
            if ejecuciones:
                # Crear DataFrame
                datos = []
                for ejecucion in ejecuciones:
                    datos.append({
                        'Notebook': ejecucion[7],  # nombre
                        'Categoría': ejecucion[8],  # categoria
                        'Timestamp': ejecucion[2],  # timestamp
                        'Duración (s)': f"{ejecucion[3]:.2f}" if ejecucion[3] else 'N/A',  # duracion
                        'Exitoso': '✅' if ejecucion[4] else '❌',  # exitoso
                        'Errores': ejecucion[5] if ejecucion[5] else 'N/A'  # errores
                    })
                
                df = pd.DataFrame(datos)
                st.dataframe(df, width='stretch')
                
                # Gráfico de éxito
                fig = px.pie(
                    df, 
                    names='Exitoso', 
                    title='Distribución de Ejecuciones Exitosas vs Fallidas'
                )
                st.plotly_chart(fig, config=PLOTLY_CONFIG, width='stretch')
                
                # Gráfico de duración
                df_numeric = df.copy()
                df_numeric['Duración (s)'] = pd.to_numeric(df_numeric['Duración (s)'], errors='coerce')
                
                fig2 = px.bar(
                    df_numeric, 
                    x='Notebook', 
                    y='Duración (s)',
                    title='Duración de Ejecuciones por Notebook'
                )
                st.plotly_chart(fig2, config=PLOTLY_CONFIG, width='stretch')
            else:
                st.info("No hay ejecuciones registradas")
                
        except Exception as e:
            st.error(f"Error mostrando resultados: {e}")
    
    def _mostrar_dashboard_completo(self):
        """Mostrar dashboard completo"""
        try:
            st.header("🎛️ Dashboard Completo del Sistema")
            
            # Métricas generales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Notebooks", len(self.notebooks))
            
            with col2:
                if self.estado_notebooks:
                    existentes = sum(1 for v in self.estado_notebooks.values() if v.get('existe', False))
                    st.metric("Notebooks Existentes", existentes)
                else:
                    st.metric("Notebooks Existentes", "N/A")
            
            with col3:
                if self.resultados_notebooks:
                    exitosos = sum(1 for v in self.resultados_notebooks.values() if v.get('exitoso', False))
                    st.metric("Ejecuciones Exitosas", exitosos)
                else:
                    st.metric("Ejecuciones Exitosas", "0")
            
            with col4:
                st.metric("Versión del Sistema", self.configuracion['version'])
            
            # Gráfico de categorías
            if self.estado_notebooks:
                categorias_count = {}
                for info in self.estado_notebooks.values():
                    categoria = info.get('categoria', 'Sin categoría')
                    categorias_count[categoria] = categorias_count.get(categoria, 0) + 1
                
                fig = px.pie(
                    values=list(categorias_count.values()),
                    names=list(categorias_count.keys()),
                    title='Distribución de Notebooks por Categoría'
                )
                st.plotly_chart(fig, config=PLOTLY_CONFIG, width='stretch')
            
            # Estado del sistema
            st.subheader("🔧 Estado del Sistema")
            
            # Verificar componentes
            componentes = {
                'Base de datos': Path(f"{self.configuracion['directorio_datos']}/dashboard_integrado.db").exists(),
                'Logs': Path(self.configuracion['directorio_logs']).exists(),
                'Notebooks verificados': len(self.estado_notebooks) > 0,
                'Resultados disponibles': len(self.resultados_notebooks) > 0
            }
            
            for componente, estado in componentes.items():
                if estado:
                    st.success(f"✅ {componente}")
                else:
                    st.error(f"❌ {componente}")
                    
        except Exception as e:
            st.error(f"Error mostrando dashboard completo: {e}")
    
    def generar_reporte_dashboard(self) -> str:
        """Generar reporte del dashboard"""
        try:
            self.logger.info("Generando reporte del dashboard...")
            
            # Verificar notebooks si no están verificados
            if not self.estado_notebooks:
                self.verificar_notebooks()
            
            # Obtener estadísticas
            total_notebooks = len(self.notebooks)
            notebooks_existentes = sum(1 for v in self.estado_notebooks.values() if v.get('existe', False))
            notebooks_faltantes = total_notebooks - notebooks_existentes
            porcentaje_completitud = (notebooks_existentes / total_notebooks * 100) if total_notebooks > 0 else 0
            
            # Obtener ejecuciones
            self.cursor_bd.execute('''
                SELECT COUNT(*) as total, 
                       SUM(CASE WHEN exitoso = 1 THEN 1 ELSE 0 END) as exitosas,
                       AVG(duracion) as duracion_promedio
                FROM ejecuciones
            ''')
            stats_ejecuciones = self.cursor_bd.fetchone()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Dashboard Integrado de Notebooks',
                'version': self.configuracion['version'],
                'estadisticas': {
                    'total_notebooks': total_notebooks,
                    'notebooks_existentes': notebooks_existentes,
                    'notebooks_faltantes': notebooks_faltantes,
                    'porcentaje_completitud': porcentaje_completitud,
                    'total_ejecuciones': stats_ejecuciones[0] if stats_ejecuciones[0] else 0,
                    'ejecuciones_exitosas': stats_ejecuciones[1] if stats_ejecuciones[1] else 0,
                    'duracion_promedio': stats_ejecuciones[2] if stats_ejecuciones[2] else 0
                },
                'notebooks': self.estado_notebooks,
                'resultados': self.resultados_notebooks,
                'recomendaciones': [
                    "Verificar notebooks faltantes",
                    "Ejecutar notebooks críticos regularmente",
                    "Monitorear duración de ejecuciones",
                    "Revisar errores de ejecución",
                    "Actualizar notebooks desactualizados"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"dashboard_integrado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte del dashboard generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal del dashboard integrado"""
    print("DASHBOARD INTEGRADO DE NOTEBOOKS METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Version 2.0")
    print("=" * 70)
    
    try:
        # Crear dashboard
        dashboard = DashboardIntegradoNotebooks()
        
        # Verificar notebooks
        print("\nVerificando notebooks...")
        estado = dashboard.verificar_notebooks()
        
        if estado:
            print(f"Verificacion completada: {len(estado)} notebooks")
            
            # Mostrar resumen
            existentes = sum(1 for v in estado.values() if v.get('existe', False))
            faltantes = len(estado) - existentes
            
            print(f"\nResumen:")
            print(f"   Total notebooks: {len(estado)}")
            print(f"   Existentes: {existentes}")
            print(f"   Faltantes: {faltantes}")
            print(f"   Completitud: {(existentes/len(estado)*100):.1f}%")
            
            # Generar reporte
            print(f"\nGenerando reporte...")
            reporte = dashboard.generar_reporte_dashboard()
            
            if reporte:
                print(f"Reporte generado: {reporte}")
            else:
                print(f"Error generando reporte")
            
            # Iniciar dashboard Streamlit
            print(f"\nIniciando dashboard Streamlit...")
            print(f"   Ejecuta: streamlit run dashboard_integrado_notebooks.py")
            
        else:
            print("Error verificando notebooks")
        
        return True
        
    except Exception as e:
        print(f"\nError en dashboard integrado: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
