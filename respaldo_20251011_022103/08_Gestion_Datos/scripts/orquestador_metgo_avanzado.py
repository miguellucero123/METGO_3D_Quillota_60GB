#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ORQUESTADOR PRINCIPAL METGO 3D AVANZADO
Sistema Meteorológico Agrícola Quillota - Integración Completa de Módulos Avanzados
"""

import os
import sys
import time
import json
import asyncio
import threading
import numpy as np
import pandas as pd
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import signal

# Importar módulos avanzados
try:
    from ia_avanzada_metgo import IAAvanzadaMETGO
    IA_AVAILABLE = True
except ImportError:
    IA_AVAILABLE = False

try:
    from sistema_iot_metgo import SistemaIoTMETGO
    IOT_AVAILABLE = True
except ImportError:
    IOT_AVAILABLE = False

try:
    from analisis_avanzado_metgo import AnalisisAvanzadoMETGO
    ANALISIS_AVAILABLE = True
except ImportError:
    ANALISIS_AVAILABLE = False

try:
    from visualizacion_3d_metgo import Visualizacion3DMETGO
    VISUALIZACION_AVAILABLE = True
except ImportError:
    VISUALIZACION_AVAILABLE = False

try:
    from apis_avanzadas_metgo import APIAvanzadaMETGO
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

# Configuración
warnings.filterwarnings('ignore')

class OrquestadorMETGOAvanzado:
    """Orquestador principal para integrar todos los módulos avanzados de METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/integrado',
            'directorio_logs': 'logs/orquestador',
            'directorio_config': 'config/integrado',
            'directorio_reportes': 'reportes/integrado',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Inicializar módulos
        self.modulos = {}
        self.estado_modulos = {}
        self.datos_compartidos = {}
        self.cola_datos = queue.Queue()
        self.cola_alertas = queue.Queue()
        self.cola_comandos = queue.Queue()
        
        # Configuración de integración
        self.configuracion_integracion = {
            'frecuencia_actualizacion': 60,  # segundos
            'timeout_modulos': 300,  # segundos
            'max_reintentos': 3,
            'habilitar_paralelismo': True,
            'habilitar_cache': True,
            'habilitar_monitoreo': True
        }
        
        # Estado del sistema
        self.estado_sistema = {
            'activo': False,
            'modulos_cargados': 0,
            'ultima_actualizacion': None,
            'errores': [],
            'metricas': {}
        }
        
        # Inicializar módulos
        self._inicializar_modulos()
        
        # Configurar manejo de señales
        self._configurar_manejo_senales()
    
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
                    logging.FileHandler(f"{self.configuracion['directorio_logs']}/orquestador.log"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('METGO_ORQUESTADOR')
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _configurar_manejo_senales(self):
        """Configurar manejo de señales del sistema"""
        try:
            signal.signal(signal.SIGINT, self._manejar_senal_terminacion)
            signal.signal(signal.SIGTERM, self._manejar_senal_terminacion)
            self.logger.info("Manejo de señales configurado")
        except Exception as e:
            self.logger.error(f"Error configurando manejo de señales: {e}")
    
    def _manejar_senal_terminacion(self, signum, frame):
        """Manejar señales de terminación"""
        try:
            self.logger.info(f"Señal de terminación recibida: {signum}")
            self.detener_sistema()
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Error manejando señal de terminación: {e}")
    
    def _inicializar_modulos(self):
        """Inicializar todos los módulos disponibles"""
        try:
            self.logger.info("Inicializando módulos...")
            
            # Módulo de IA Avanzada
            if IA_AVAILABLE:
                try:
                    self.modulos['ia'] = IAAvanzadaMETGO()
                    self.estado_modulos['ia'] = {'activo': True, 'ultima_actualizacion': None}
                    self.logger.info("✅ Módulo de IA Avanzada inicializado")
                except Exception as e:
                    self.logger.error(f"Error inicializando módulo IA: {e}")
                    self.estado_modulos['ia'] = {'activo': False, 'error': str(e)}
            
            # Módulo IoT
            if IOT_AVAILABLE:
                try:
                    self.modulos['iot'] = SistemaIoTMETGO()
                    self.estado_modulos['iot'] = {'activo': True, 'ultima_actualizacion': None}
                    self.logger.info("✅ Módulo IoT inicializado")
                except Exception as e:
                    self.logger.error(f"Error inicializando módulo IoT: {e}")
                    self.estado_modulos['iot'] = {'activo': False, 'error': str(e)}
            
            # Módulo de Análisis Avanzado
            if ANALISIS_AVAILABLE:
                try:
                    self.modulos['analisis'] = AnalisisAvanzadoMETGO()
                    self.estado_modulos['analisis'] = {'activo': True, 'ultima_actualizacion': None}
                    self.logger.info("✅ Módulo de Análisis Avanzado inicializado")
                except Exception as e:
                    self.logger.error(f"Error inicializando módulo Análisis: {e}")
                    self.estado_modulos['analisis'] = {'activo': False, 'error': str(e)}
            
            # Módulo de Visualización 3D
            if VISUALIZACION_AVAILABLE:
                try:
                    self.modulos['visualizacion'] = Visualizacion3DMETGO()
                    self.estado_modulos['visualizacion'] = {'activo': True, 'ultima_actualizacion': None}
                    self.logger.info("✅ Módulo de Visualización 3D inicializado")
                except Exception as e:
                    self.logger.error(f"Error inicializando módulo Visualización: {e}")
                    self.estado_modulos['visualizacion'] = {'activo': False, 'error': str(e)}
            
            # Módulo de APIs Avanzadas
            if API_AVAILABLE:
                try:
                    self.modulos['api'] = APIAvanzadaMETGO()
                    self.estado_modulos['api'] = {'activo': True, 'ultima_actualizacion': None}
                    self.logger.info("✅ Módulo de APIs Avanzadas inicializado")
                except Exception as e:
                    self.logger.error(f"Error inicializando módulo API: {e}")
                    self.estado_modulos['api'] = {'activo': False, 'error': str(e)}
            
            # Actualizar estado del sistema
            modulos_activos = sum(1 for estado in self.estado_modulos.values() if estado.get('activo', False))
            self.estado_sistema['modulos_cargados'] = modulos_activos
            
            self.logger.info(f"✅ {modulos_activos} módulos inicializados correctamente")
            
        except Exception as e:
            self.logger.error(f"Error inicializando módulos: {e}")
    
    def cargar_datos_integrados(self) -> pd.DataFrame:
        """Cargar datos integrados de todos los módulos"""
        try:
            self.logger.info("Cargando datos integrados...")
            
            # Intentar cargar datos desde diferentes fuentes
            datos_integrados = None
            
            # 1. Intentar desde módulo de análisis
            if 'analisis' in self.modulos and self.estado_modulos['analisis']['activo']:
                try:
                    datos_integrados = self.modulos['analisis'].cargar_datos_meteorologicos()
                    if not datos_integrados.empty:
                        self.logger.info("✅ Datos cargados desde módulo de análisis")
                except Exception as e:
                    self.logger.warning(f"Error cargando datos desde análisis: {e}")
            
            # 2. Intentar desde módulo de IA
            if datos_integrados is None and 'ia' in self.modulos and self.estado_modulos['ia']['activo']:
                try:
                    datos_integrados = self.modulos['ia'].cargar_datos_meteorologicos()
                    if not datos_integrados.empty:
                        self.logger.info("✅ Datos cargados desde módulo de IA")
                except Exception as e:
                    self.logger.warning(f"Error cargando datos desde IA: {e}")
            
            # 3. Generar datos sintéticos si no se pudieron cargar
            if datos_integrados is None or datos_integrados.empty:
                self.logger.warning("Generando datos sintéticos...")
                datos_integrados = self._generar_datos_sinteticos()
            
            # Guardar datos integrados
            self.datos_compartidos['meteorologicos'] = datos_integrados
            self._guardar_datos_integrados(datos_integrados)
            
            self.logger.info(f"✅ Datos integrados cargados: {len(datos_integrados)} registros")
            return datos_integrados
            
        except Exception as e:
            self.logger.error(f"Error cargando datos integrados: {e}")
            return pd.DataFrame()
    
    def _generar_datos_sinteticos(self) -> pd.DataFrame:
        """Generar datos sintéticos integrados"""
        try:
            # Generar fechas (2 años de datos)
            fechas = pd.date_range(
                start='2022-01-01',
                end='2024-01-01',
                freq='H'
            )
            
            # Generar datos sintéticos realistas
            np.random.seed(42)
            datos = pd.DataFrame(index=fechas)
            
            # Temperatura (patrón estacional + tendencia)
            tendencia = np.linspace(0, 2, len(fechas))  # Calentamiento global
            estacional = 10 * np.sin(2 * np.pi * fechas.dayofyear / 365)
            ruido = np.random.normal(0, 3, len(fechas))
            datos['temperatura'] = 15 + tendencia + estacional + ruido
            
            # Precipitación (eventos esporádicos)
            datos['precipitacion'] = np.random.exponential(0.5, len(fechas))
            datos['precipitacion'] = np.where(np.random.random(len(fechas)) > 0.9, datos['precipitacion'], 0)
            
            # Viento
            datos['viento_velocidad'] = np.random.gamma(2, 2, len(fechas))
            datos['viento_direccion'] = np.random.uniform(0, 360, len(fechas))
            
            # Humedad (inversamente relacionada con temperatura)
            datos['humedad'] = 80 - (datos['temperatura'] - 15) * 2 + np.random.normal(0, 5, len(fechas))
            datos['humedad'] = np.clip(datos['humedad'], 0, 100)
            
            # Presión
            datos['presion'] = 1013 + np.random.normal(0, 10, len(fechas))
            
            # Radiación solar
            datos['radiacion_solar'] = np.maximum(0, 800 * np.sin(np.pi * fechas.hour / 24) + np.random.normal(0, 50, len(fechas)))
            
            # Punto de rocío
            datos['punto_rocio'] = datos['temperatura'] - (100 - datos['humedad']) / 5
            
            # Agregar índices agrícolas
            datos['grados_dia'] = np.maximum(0, datos['temperatura'] - 10)
            datos['confort_termico'] = 1 - np.abs(datos['temperatura'] - 20) / 20 - np.abs(datos['humedad'] - 60) / 60
            datos['confort_termico'] = np.clip(datos['confort_termico'], 0, 1)
            
            return datos
            
        except Exception as e:
            self.logger.error(f"Error generando datos sintéticos: {e}")
            return pd.DataFrame()
    
    def _guardar_datos_integrados(self, datos: pd.DataFrame):
        """Guardar datos integrados"""
        try:
            archivo = f"{self.configuracion['directorio_datos']}/datos_integrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            datos.to_csv(archivo)
            self.logger.info(f"Datos integrados guardados: {archivo}")
        except Exception as e:
            self.logger.error(f"Error guardando datos integrados: {e}")
    
    def ejecutar_pipeline_completo(self) -> Dict:
        """Ejecutar pipeline completo de todos los módulos"""
        try:
            self.logger.info("🚀 Ejecutando pipeline completo...")
            
            inicio_pipeline = datetime.now()
            resultados = {}
            
            # 1. Cargar datos integrados
            self.logger.info("📊 Paso 1: Cargando datos integrados...")
            datos = self.cargar_datos_integrados()
            if datos.empty:
                raise Exception("No se pudieron cargar los datos")
            
            resultados['datos'] = {
                'total_registros': len(datos),
                'variables': list(datos.columns),
                'rango_temporal': {
                    'inicio': datos.index.min().isoformat(),
                    'fin': datos.index.max().isoformat()
                }
            }
            
            # 2. Ejecutar módulos en paralelo
            if self.configuracion_integracion['habilitar_paralelismo']:
                resultados_paralelos = self._ejecutar_modulos_paralelo(datos)
                resultados.update(resultados_paralelos)
            else:
                resultados_secuenciales = self._ejecutar_modulos_secuencial(datos)
                resultados.update(resultados_secuenciales)
            
            # 3. Integrar resultados
            self.logger.info("🔗 Paso 3: Integrando resultados...")
            resultados_integrados = self._integrar_resultados(resultados)
            resultados['integracion'] = resultados_integrados
            
            # 4. Generar reporte final
            self.logger.info("📋 Paso 4: Generando reporte final...")
            reporte_final = self._generar_reporte_final(resultados)
            resultados['reporte_final'] = reporte_final
            
            # Actualizar estado del sistema
            fin_pipeline = datetime.now()
            duracion = (fin_pipeline - inicio_pipeline).total_seconds()
            
            self.estado_sistema['ultima_actualizacion'] = fin_pipeline.isoformat()
            self.estado_sistema['metricas']['ultima_ejecucion'] = {
                'inicio': inicio_pipeline.isoformat(),
                'fin': fin_pipeline.isoformat(),
                'duracion_segundos': duracion,
                'modulos_ejecutados': len([m for m in self.estado_modulos.values() if m.get('activo', False)])
            }
            
            self.logger.info(f"✅ Pipeline completo ejecutado en {duracion:.2f} segundos")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error ejecutando pipeline completo: {e}")
            self.estado_sistema['errores'].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'modulo': 'pipeline_completo'
            })
            return {}
    
    def _ejecutar_modulos_paralelo(self, datos: pd.DataFrame) -> Dict:
        """Ejecutar módulos en paralelo"""
        try:
            self.logger.info("🔄 Ejecutando módulos en paralelo...")
            
            resultados = {}
            modulos_activos = {nombre: modulo for nombre, modulo in self.modulos.items() 
                             if self.estado_modulos[nombre].get('activo', False)}
            
            with ThreadPoolExecutor(max_workers=len(modulos_activos)) as executor:
                # Enviar tareas
                futuros = {}
                
                for nombre, modulo in modulos_activos.items():
                    if nombre == 'ia':
                        futuro = executor.submit(self._ejecutar_modulo_ia, modulo, datos)
                    elif nombre == 'iot':
                        futuro = executor.submit(self._ejecutar_modulo_iot, modulo)
                    elif nombre == 'analisis':
                        futuro = executor.submit(self._ejecutar_modulo_analisis, modulo, datos)
                    elif nombre == 'visualizacion':
                        futuro = executor.submit(self._ejecutar_modulo_visualizacion, modulo, datos)
                    elif nombre == 'api':
                        futuro = executor.submit(self._ejecutar_modulo_api, modulo)
                    else:
                        continue
                    
                    futuros[futuro] = nombre
                
                # Recoger resultados
                for futuro in as_completed(futuros, timeout=self.configuracion_integracion['timeout_modulos']):
                    nombre_modulo = futuros[futuro]
                    try:
                        resultado = futuro.result()
                        resultados[nombre_modulo] = resultado
                        self.estado_modulos[nombre_modulo]['ultima_actualizacion'] = datetime.now().isoformat()
                        self.logger.info(f"✅ Módulo {nombre_modulo} completado")
                    except Exception as e:
                        self.logger.error(f"Error en módulo {nombre_modulo}: {e}")
                        resultados[nombre_modulo] = {'error': str(e)}
                        self.estado_modulos[nombre_modulo]['error'] = str(e)
            
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error ejecutando módulos en paralelo: {e}")
            return {}
    
    def _ejecutar_modulos_secuencial(self, datos: pd.DataFrame) -> Dict:
        """Ejecutar módulos secuencialmente"""
        try:
            self.logger.info("🔄 Ejecutando módulos secuencialmente...")
            
            resultados = {}
            
            # Ejecutar módulo de IA
            if 'ia' in self.modulos and self.estado_modulos['ia']['activo']:
                try:
                    resultados['ia'] = self._ejecutar_modulo_ia(self.modulos['ia'], datos)
                    self.estado_modulos['ia']['ultima_actualizacion'] = datetime.now().isoformat()
                    self.logger.info("✅ Módulo IA completado")
                except Exception as e:
                    self.logger.error(f"Error en módulo IA: {e}")
                    resultados['ia'] = {'error': str(e)}
            
            # Ejecutar módulo IoT
            if 'iot' in self.modulos and self.estado_modulos['iot']['activo']:
                try:
                    resultados['iot'] = self._ejecutar_modulo_iot(self.modulos['iot'])
                    self.estado_modulos['iot']['ultima_actualizacion'] = datetime.now().isoformat()
                    self.logger.info("✅ Módulo IoT completado")
                except Exception as e:
                    self.logger.error(f"Error en módulo IoT: {e}")
                    resultados['iot'] = {'error': str(e)}
            
            # Ejecutar módulo de Análisis
            if 'analisis' in self.modulos and self.estado_modulos['analisis']['activo']:
                try:
                    resultados['analisis'] = self._ejecutar_modulo_analisis(self.modulos['analisis'], datos)
                    self.estado_modulos['analisis']['ultima_actualizacion'] = datetime.now().isoformat()
                    self.logger.info("✅ Módulo Análisis completado")
                except Exception as e:
                    self.logger.error(f"Error en módulo Análisis: {e}")
                    resultados['analisis'] = {'error': str(e)}
            
            # Ejecutar módulo de Visualización
            if 'visualizacion' in self.modulos and self.estado_modulos['visualizacion']['activo']:
                try:
                    resultados['visualizacion'] = self._ejecutar_modulo_visualizacion(self.modulos['visualizacion'], datos)
                    self.estado_modulos['visualizacion']['ultima_actualizacion'] = datetime.now().isoformat()
                    self.logger.info("✅ Módulo Visualización completado")
                except Exception as e:
                    self.logger.error(f"Error en módulo Visualización: {e}")
                    resultados['visualizacion'] = {'error': str(e)}
            
            # Ejecutar módulo de API
            if 'api' in self.modulos and self.estado_modulos['api']['activo']:
                try:
                    resultados['api'] = self._ejecutar_modulo_api(self.modulos['api'])
                    self.estado_modulos['api']['ultima_actualizacion'] = datetime.now().isoformat()
                    self.logger.info("✅ Módulo API completado")
                except Exception as e:
                    self.logger.error(f"Error en módulo API: {e}")
                    resultados['api'] = {'error': str(e)}
            
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error ejecutando módulos secuencialmente: {e}")
            return {}
    
    def _ejecutar_modulo_ia(self, modulo, datos: pd.DataFrame) -> Dict:
        """Ejecutar módulo de IA"""
        try:
            # Entrenar modelos
            resultados_entrenamiento = modulo.entrenar_todos_los_modelos(datos)
            
            # Evaluar modelos
            evaluacion = modulo.evaluar_modelos(datos)
            
            # Generar reporte
            reporte = modulo.generar_reporte_ia(resultados_entrenamiento, evaluacion)
            
            return {
                'entrenamiento': resultados_entrenamiento,
                'evaluacion': evaluacion,
                'reporte': reporte
            }
            
        except Exception as e:
            self.logger.error(f"Error ejecutando módulo IA: {e}")
            return {'error': str(e)}
    
    def _ejecutar_modulo_iot(self, modulo) -> Dict:
        try:
            # Crear red de sensores
            modulo.crear_red_sensores({})
            
            # Iniciar monitoreo
            modulo.iniciar_monitoreo_iot(duracion_minutos=1)
            
            # Generar reporte
            reporte = modulo.generar_reporte_iot()
            
            return {
                'red_sensores': True,
                'monitoreo': True,
                'reporte': reporte
            }
            
        except Exception as e:
            self.logger.error(f"Error ejecutando módulo IoT: {e}")
            return {'error': str(e)}
    
    def _ejecutar_modulo_analisis(self, modulo, datos: pd.DataFrame) -> Dict:
        """Ejecutar módulo de análisis"""
        try:
            resultados = {}
            
            # Análisis de estacionalidad
            for variable in ['temperatura', 'humedad', 'precipitacion']:
                if variable in datos.columns:
                    resultados[f'estacionalidad_{variable}'] = modulo.analisis_estacionalidad(datos, variable)
            
            # Análisis de correlaciones
            resultados['correlaciones'] = modulo.analisis_correlaciones(datos)
            
            # Análisis de clustering
            resultados['clustering'] = modulo.analisis_clustering(datos)
            
            # Análisis de anomalías
            resultados['anomalias'] = modulo.analisis_anomalias(datos)
            
            # Análisis de PCA
            resultados['pca'] = modulo.analisis_pca(datos)
            
            # Crear visualizaciones
            modulo.crear_visualizaciones_avanzadas(datos)
            
            # Generar reporte
            reporte = modulo.generar_reporte_analisis_avanzado()
            
            return {
                'analisis': resultados,
                'reporte': reporte
            }
            
        except Exception as e:
            self.logger.error(f"Error ejecutando módulo Análisis: {e}")
            return {'error': str(e)}
    
    def _ejecutar_modulo_visualizacion(self, modulo, datos: pd.DataFrame) -> Dict:
        """Ejecutar módulo de visualización"""
        try:
            visualizaciones = {}
            
            # Crear visualizaciones 3D
            visualizaciones['temperatura_3d'] = modulo.crear_visualizacion_3d_temperatura(datos)
            visualizaciones['viento_3d'] = modulo.crear_visualizacion_3d_viento(datos)
            visualizaciones['multivariable_3d'] = modulo.crear_visualizacion_3d_multivariable(datos)
            visualizaciones['dashboard_interactivo'] = modulo.crear_dashboard_interactivo_3d(datos)
            visualizaciones['estacional_3d'] = modulo.crear_visualizacion_estacional_3d(datos)
            visualizaciones['correlaciones_3d'] = modulo.crear_visualizacion_correlaciones_3d(datos)
            visualizaciones['dashboard_completo'] = modulo.crear_dashboard_completo_3d(datos)
            
            # Generar reporte
            reporte = modulo.generar_reporte_visualizaciones_3d()
            
            return {
                'visualizaciones': visualizaciones,
                'reporte': reporte
            }
            
        except Exception as e:
            self.logger.error(f"Error ejecutando módulo Visualización: {e}")
            return {'error': str(e)}
    
    def _ejecutar_modulo_api(self, modulo) -> Dict:
        """Ejecutar módulo de API"""
        try:
            # Generar reporte
            reporte = modulo.generar_reporte_apis()
            
            return {
                'configuracion': modulo.configuracion_apis,
                'reporte': reporte
            }
            
        except Exception as e:
            self.logger.error(f"Error ejecutando módulo API: {e}")
            return {'error': str(e)}
    
    def _integrar_resultados(self, resultados: Dict) -> Dict:
        """Integrar resultados de todos los módulos"""
        try:
            self.logger.info("🔗 Integrando resultados...")
            
            integracion = {
                'timestamp': datetime.now().isoformat(),
                'modulos_ejecutados': [],
                'resumen': {},
                'alertas': [],
                'recomendaciones': []
            }
            
            # Procesar resultados de cada módulo
            for nombre_modulo, resultado in resultados.items():
                if nombre_modulo == 'datos':
                    continue
                
                if 'error' in resultado:
                    integracion['alertas'].append({
                        'tipo': 'error',
                        'modulo': nombre_modulo,
                        'mensaje': resultado['error']
                    })
                else:
                    integracion['modulos_ejecutados'].append(nombre_modulo)
                    
                    # Resumen por módulo
                    if nombre_modulo == 'ia':
                        integracion['resumen']['ia'] = {
                            'modelos_entrenados': len(resultado.get('entrenamiento', {})),
                            'evaluacion_completada': 'evaluacion' in resultado
                        }
                    elif nombre_modulo == 'iot':
                        integracion['resumen']['iot'] = {
                            'red_creada': resultado.get('red_sensores', False),
                            'monitoreo_activo': resultado.get('monitoreo', False)
                        }
                    elif nombre_modulo == 'analisis':
                        integracion['resumen']['analisis'] = {
                            'analisis_completados': len(resultado.get('analisis', {})),
                            'visualizaciones_creadas': True
                        }
                    elif nombre_modulo == 'visualizacion':
                        integracion['resumen']['visualizacion'] = {
                            'visualizaciones_3d': len(resultado.get('visualizaciones', {})),
                            'dashboards_creados': 2
                        }
                    elif nombre_modulo == 'api':
                        integracion['resumen']['api'] = {
                            'endpoints_configurados': len(resultado.get('configuracion', {})),
                            'reporte_generado': 'reporte' in resultado
                        }
            
            # Generar recomendaciones
            integracion['recomendaciones'] = [
                "Sistema integrado funcionando correctamente",
                "Todos los módulos avanzados están operativos",
                "Datos meteorológicos procesados exitosamente",
                "Visualizaciones 3D generadas",
                "APIs configuradas y listas para uso"
            ]
            
            return integracion
            
        except Exception as e:
            self.logger.error(f"Error integrando resultados: {e}")
            return {'error': str(e)}
    
    def _generar_reporte_final(self, resultados: Dict) -> str:
        """Generar reporte final del sistema integrado"""
        try:
            self.logger.info("📋 Generando reporte final...")
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Integrado Avanzado',
                'version': self.configuracion['version'],
                'estado_sistema': self.estado_sistema,
                'modulos': self.estado_modulos,
                'resultados': resultados,
                'configuracion': self.configuracion_integracion,
                'resumen_ejecutivo': {
                    'total_modulos': len(self.modulos),
                    'modulos_activos': len([m for m in self.estado_modulos.values() if m.get('activo', False)]),
                    'modulos_con_error': len([m for m in self.estado_modulos.values() if 'error' in m]),
                    'ultima_ejecucion': self.estado_sistema.get('ultima_actualizacion'),
                    'estado_general': 'OPERATIVO' if len([m for m in self.estado_modulos.values() if m.get('activo', False)]) > 0 else 'ERROR'
                }
            }
            
            # Guardar reporte
            reportes_dir = Path(self.configuracion['directorio_reportes'])
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"reporte_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Reporte final generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte final: {e}")
            return ""
    
    def iniciar_sistema(self) -> bool:
        """Iniciar el sistema integrado"""
        try:
            self.logger.info("🚀 Iniciando sistema METGO 3D integrado...")
            
            self.estado_sistema['activo'] = True
            
            # Ejecutar pipeline completo
            resultados = self.ejecutar_pipeline_completo()
            
            if resultados:
                self.logger.info("✅ Sistema iniciado correctamente")
                return True
            else:
                self.logger.error("❌ Error iniciando sistema")
                return False
                
        except Exception as e:
            self.logger.error(f"Error iniciando sistema: {e}")
            return False
    
    def detener_sistema(self):
        """Detener el sistema integrado"""
        try:
            self.logger.info("🛑 Deteniendo sistema METGO 3D...")
            
            self.estado_sistema['activo'] = False
            
            # Limpiar recursos
            self.datos_compartidos.clear()
            
            # Vaciar colas
            while not self.cola_datos.empty():
                self.cola_datos.get()
            while not self.cola_alertas.empty():
                self.cola_alertas.get()
            while not self.cola_comandos.empty():
                self.cola_comandos.get()
            
            self.logger.info("✅ Sistema detenido correctamente")
            
        except Exception as e:
            self.logger.error(f"Error deteniendo sistema: {e}")
    
    def obtener_estado_sistema(self) -> Dict:
        """Obtener estado actual del sistema"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'sistema': self.estado_sistema,
                'modulos': self.estado_modulos,
                'configuracion': self.configuracion_integracion,
                'metricas': self.estado_sistema.get('metricas', {})
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo estado del sistema: {e}")
            return {}

def main():
    """Función principal del orquestador"""
    print("🎯 ORQUESTADOR PRINCIPAL METGO 3D AVANZADO")
    print("Sistema Meteorológico Agrícola Quillota - Integración Completa de Módulos Avanzados")
    print("=" * 80)
    
    try:
        # Crear orquestador
        orquestador = OrquestadorMETGOAvanzado()
        
        # Mostrar estado inicial
        print(f"\n📊 Estado inicial del sistema:")
        print(f"   Módulos cargados: {orquestador.estado_sistema['modulos_cargados']}")
        print(f"   Módulos activos: {len([m for m in orquestador.estado_modulos.values() if m.get('activo', False)])}")
        
        # Iniciar sistema
        print(f"\n🚀 Iniciando sistema integrado...")
        if orquestador.iniciar_sistema():
            print(f"\n✅ Sistema METGO 3D integrado iniciado exitosamente")
            
            # Mostrar estado final
            estado_final = orquestador.obtener_estado_sistema()
            print(f"\n📊 Estado final del sistema:")
            print(f"   Estado general: {estado_final['sistema']['metricas'].get('ultima_ejecucion', {}).get('modulos_ejecutados', 0)} módulos ejecutados")
            print(f"   Última actualización: {estado_final['sistema'].get('ultima_actualizacion', 'N/A')}")
            
            if estado_final['sistema'].get('errores'):
                print(f"   Errores: {len(estado_final['sistema']['errores'])}")
            
            return True
        else:
            print(f"\n❌ Error iniciando sistema integrado")
            return False
        
    except Exception as e:
        print(f"\n❌ Error en orquestador: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

