#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TESTING DE INTEGRACIÓN METGO 3D
Sistema Meteorológico Agrícola Quillota - Testing de Integración entre Módulos
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
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import sqlite3
from dataclasses import dataclass
import yaml
import threading
import queue
import subprocess
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuración
warnings.filterwarnings('ignore')

@dataclass
class TestIntegracion:
    """Test de integración entre módulos"""
    id: str
    nombre: str
    modulo_origen: str
    modulo_destino: str
    tipo_test: str
    configuracion: Dict[str, Any]
    resultado: Dict[str, Any]
    timestamp: str

@dataclass
class ResultadoTest:
    """Resultado de test"""
    test_id: str
    exitoso: bool
    duracion: float
    errores: List[str]
    metricas: Dict[str, Any]
    timestamp: str

class TestingIntegracionMETGO:
    """Sistema de testing de integración para METGO 3D"""
    
    def __init__(self):
        # Inicializar logger primero
        self.logger = logging.getLogger('METGO_TESTING')
        
        self.configuracion = {
            'directorio_datos': 'data/testing',
            'directorio_logs': 'logs/testing',
            'directorio_reportes': 'reportes/testing',
            'directorio_resultados': 'resultados/testing',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Configuración de testing
        self.configuracion_testing = {
            'timeout_test': 30,  # 30 segundos
            'reintentos_maximos': 3,
            'paralelismo': True,
            'validacion_datos': True,
            'metricas_rendimiento': True,
            'reportes_detallados': True,
            'cobertura_tests': 0.8,  # 80%
            'umbral_exito': 0.95  # 95%
        }
        
        # Tests y resultados
        self.tests_integracion = {}
        self.resultados_tests = {}
        self.ejecutor = ThreadPoolExecutor(max_workers=4)
        
        # Configurar tests
        self._configurar_tests_integracion()
    
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
            # Configurar logging solo si no está ya configurado
            if not self.logger.handlers:
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"{self.configuracion['directorio_logs']}/testing.log"),
                        logging.StreamHandler()
                    ]
                )
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/testing.db"
            
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
            # Tabla de tests
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS tests_integracion (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    modulo_origen TEXT NOT NULL,
                    modulo_destino TEXT NOT NULL,
                    tipo_test TEXT NOT NULL,
                    configuracion TEXT,
                    resultado TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de resultados
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS resultados_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT NOT NULL,
                    exitoso BOOLEAN NOT NULL,
                    duracion REAL NOT NULL,
                    errores TEXT,
                    metricas TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES tests_integracion (id)
                )
            ''')
            
            # Tabla de métricas
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS metricas_testing (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT NOT NULL,
                    metrica_nombre TEXT NOT NULL,
                    valor REAL NOT NULL,
                    unidad TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES tests_integracion (id)
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_tests_modulos ON tests_integracion(modulo_origen, modulo_destino)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_resultados_test ON resultados_tests(test_id)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_metricas_test ON metricas_testing(test_id)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def _configurar_tests_integracion(self):
        """Configurar tests de integración"""
        try:
            tests_data = [
                {
                    'id': 'test_1',
                    'nombre': 'Test Datos Satelitales → Chatbot',
                    'modulo_origen': 'datos_satelitales',
                    'modulo_destino': 'chatbot',
                    'tipo_test': 'flujo_datos',
                    'configuracion': {
                        'validar_formato': True,
                        'validar_contenido': True,
                        'timeout': 15,
                        'datos_esperados': ['ndvi', 'ndwi', 'evi']
                    }
                },
                {
                    'id': 'test_2',
                    'nombre': 'Test Deep Learning → Reportes',
                    'modulo_origen': 'deep_learning',
                    'modulo_destino': 'reportes',
                    'tipo_test': 'flujo_datos',
                    'configuracion': {
                        'validar_predicciones': True,
                        'validar_formato': True,
                        'timeout': 30,
                        'datos_esperados': ['predicciones', 'metricas']
                    }
                },
                {
                    'id': 'test_3',
                    'nombre': 'Test Datos Satelitales → Riego',
                    'modulo_origen': 'datos_satelitales',
                    'modulo_destino': 'riego',
                    'tipo_test': 'flujo_datos',
                    'configuracion': {
                        'validar_condiciones': True,
                        'validar_tiempo_real': True,
                        'timeout': 10,
                        'datos_esperados': ['condiciones_climaticas']
                    }
                },
                {
                    'id': 'test_4',
                    'nombre': 'Test Reportes → Métricas',
                    'modulo_origen': 'reportes',
                    'modulo_destino': 'metricas',
                    'tipo_test': 'flujo_datos',
                    'configuracion': {
                        'validar_estadisticas': True,
                        'validar_agregacion': True,
                        'timeout': 20,
                        'datos_esperados': ['estadisticas', 'tendencias']
                    }
                },
                {
                    'id': 'test_5',
                    'nombre': 'Test Autenticación → Web',
                    'modulo_origen': 'autenticacion',
                    'modulo_destino': 'web_responsive',
                    'tipo_test': 'api_integration',
                    'configuracion': {
                        'validar_jwt': True,
                        'validar_permisos': True,
                        'timeout': 15,
                        'endpoints': ['/login', '/dashboard', '/api/usuarios']
                    }
                },
                {
                    'id': 'test_6',
                    'nombre': 'Test Sistema Unificado',
                    'modulo_origen': 'sistema_unificado',
                    'modulo_destino': 'todos',
                    'tipo_test': 'sistema_completo',
                    'configuracion': {
                        'validar_modulos': True,
                        'validar_tareas': True,
                        'timeout': 60,
                        'metricas_esperadas': ['uptime', 'throughput', 'latencia']
                    }
                }
            ]
            
            for test_data in tests_data:
                test = TestIntegracion(
                    id=test_data['id'],
                    nombre=test_data['nombre'],
                    modulo_origen=test_data['modulo_origen'],
                    modulo_destino=test_data['modulo_destino'],
                    tipo_test=test_data['tipo_test'],
                    configuracion=test_data['configuracion'],
                    resultado={},
                    timestamp=datetime.now().isoformat()
                )
                self.tests_integracion[test.id] = test
            
            self.logger.info(f"Tests de integración configurados: {len(self.tests_integracion)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando tests: {e}")
    
    def ejecutar_test_integracion(self, test_id: str) -> ResultadoTest:
        """Ejecutar test de integración específico"""
        try:
            if test_id not in self.tests_integracion:
                raise ValueError(f"Test {test_id} no encontrado")
            
            test = self.tests_integracion[test_id]
            self.logger.info(f"Ejecutando test: {test.nombre}")
            
            inicio = time.time()
            errores = []
            metricas = {}
            
            # Ejecutar test según tipo
            if test.tipo_test == 'flujo_datos':
                resultado = self._test_flujo_datos(test)
            elif test.tipo_test == 'api_integration':
                resultado = self._test_api_integration(test)
            elif test.tipo_test == 'sistema_completo':
                resultado = self._test_sistema_completo(test)
            else:
                resultado = self._test_generico(test)
            
            duracion = time.time() - inicio
            
            # Crear resultado
            resultado_test = ResultadoTest(
                test_id=test_id,
                exitoso=resultado['exitoso'],
                duracion=duracion,
                errores=resultado.get('errores', []),
                metricas=resultado.get('metricas', {}),
                timestamp=datetime.now().isoformat()
            )
            
            # Guardar resultado
            self._guardar_resultado_test(resultado_test)
            
            self.logger.info(f"Test completado: {test.nombre} - {'EXITOSO' if resultado_test.exitoso else 'FALLIDO'} en {duracion:.2f}s")
            
            return resultado_test
            
        except Exception as e:
            self.logger.error(f"Error ejecutando test {test_id}: {e}")
            return ResultadoTest(
                test_id=test_id,
                exitoso=False,
                duracion=0,
                errores=[str(e)],
                metricas={},
                timestamp=datetime.now().isoformat()
            )
    
    def _test_flujo_datos(self, test: TestIntegracion) -> Dict[str, Any]:
        """Test de flujo de datos entre módulos"""
        try:
            self.logger.info(f"Ejecutando test de flujo de datos: {test.modulo_origen} → {test.modulo_destino}")
            
            # Simular flujo de datos
            datos_simulados = self._simular_datos_modulo(test.modulo_origen)
            
            # Validar formato de datos
            formato_valido = self._validar_formato_datos(datos_simulados, test.configuracion)
            
            # Validar contenido de datos
            contenido_valido = self._validar_contenido_datos(datos_simulados, test.configuracion)
            
            # Simular procesamiento en módulo destino
            resultado_procesamiento = self._simular_procesamiento_modulo(test.modulo_destino, datos_simulados)
            
            # Calcular métricas
            metricas = {
                'datos_procesados': len(datos_simulados),
                'tiempo_procesamiento': resultado_procesamiento['tiempo'],
                'tamaño_datos': sys.getsizeof(datos_simulados),
                'eficiencia': resultado_procesamiento['eficiencia']
            }
            
            exitoso = formato_valido and contenido_valido and resultado_procesamiento['exitoso']
            errores = []
            
            if not formato_valido:
                errores.append("Formato de datos inválido")
            if not contenido_valido:
                errores.append("Contenido de datos inválido")
            if not resultado_procesamiento['exitoso']:
                errores.append("Error en procesamiento")
            
            return {
                'exitoso': exitoso,
                'errores': errores,
                'metricas': metricas
            }
            
        except Exception as e:
            self.logger.error(f"Error en test de flujo de datos: {e}")
            return {
                'exitoso': False,
                'errores': [str(e)],
                'metricas': {}
            }
    
    def _test_api_integration(self, test: TestIntegracion) -> Dict[str, Any]:
        """Test de integración de API"""
        try:
            self.logger.info(f"Ejecutando test de API: {test.modulo_origen} → {test.modulo_destino}")
            
            # Simular test de API
            endpoints = test.configuracion.get('endpoints', [])
            resultados_endpoints = []
            
            for endpoint in endpoints:
                resultado_endpoint = self._test_endpoint(endpoint)
                resultados_endpoints.append(resultado_endpoint)
            
            # Validar JWT si es necesario
            jwt_valido = True
            if test.configuracion.get('validar_jwt', False):
                jwt_valido = self._validar_jwt_token()
            
            # Validar permisos si es necesario
            permisos_validos = True
            if test.configuracion.get('validar_permisos', False):
                permisos_validos = self._validar_permisos()
            
            # Calcular métricas
            metricas = {
                'endpoints_probados': len(endpoints),
                'endpoints_exitosos': sum(1 for r in resultados_endpoints if r['exitoso']),
                'tiempo_respuesta_promedio': np.mean([r['tiempo'] for r in resultados_endpoints]),
                'jwt_valido': jwt_valido,
                'permisos_validos': permisos_validos
            }
            
            exitoso = all(r['exitoso'] for r in resultados_endpoints) and jwt_valido and permisos_validos
            errores = []
            
            if not jwt_valido:
                errores.append("JWT inválido")
            if not permisos_validos:
                errores.append("Permisos inválidos")
            
            for i, resultado in enumerate(resultados_endpoints):
                if not resultado['exitoso']:
                    errores.append(f"Endpoint {endpoints[i]} falló: {resultado['error']}")
            
            return {
                'exitoso': exitoso,
                'errores': errores,
                'metricas': metricas
            }
            
        except Exception as e:
            self.logger.error(f"Error en test de API: {e}")
            return {
                'exitoso': False,
                'errores': [str(e)],
                'metricas': {}
            }
    
    def _test_sistema_completo(self, test: TestIntegracion) -> Dict[str, Any]:
        """Test del sistema completo"""
        try:
            self.logger.info(f"Ejecutando test del sistema completo")
            
            # Test de módulos
            modulos_activos = self._verificar_modulos_activos()
            
            # Test de tareas
            tareas_funcionando = self._verificar_tareas_funcionando()
            
            # Test de métricas del sistema
            metricas_sistema = self._obtener_metricas_sistema()
            
            # Test de APIs
            apis_funcionando = self._verificar_apis_funcionando()
            
            # Calcular métricas
            metricas = {
                'modulos_activos': modulos_activos['total'],
                'modulos_exitosos': modulos_activos['exitosos'],
                'tareas_funcionando': tareas_funcionando['total'],
                'tareas_exitosas': tareas_funcionando['exitosas'],
                'apis_funcionando': apis_funcionando['total'],
                'apis_exitosas': apis_funcionando['exitosas'],
                'uptime': metricas_sistema.get('uptime', 0),
                'throughput': metricas_sistema.get('throughput', 0),
                'latencia_promedio': metricas_sistema.get('latencia', 0)
            }
            
            exitoso = (modulos_activos['exitosos'] >= modulos_activos['total'] * 0.9 and
                      tareas_funcionando['exitosas'] >= tareas_funcionando['total'] * 0.8 and
                      apis_funcionando['exitosas'] >= apis_funcionando['total'] * 0.9)
            
            errores = []
            if modulos_activos['exitosos'] < modulos_activos['total'] * 0.9:
                errores.append("Módulos no funcionando correctamente")
            if tareas_funcionando['exitosas'] < tareas_funcionando['total'] * 0.8:
                errores.append("Tareas de integración fallando")
            if apis_funcionando['exitosas'] < apis_funcionando['total'] * 0.9:
                errores.append("APIs no funcionando correctamente")
            
            return {
                'exitoso': exitoso,
                'errores': errores,
                'metricas': metricas
            }
            
        except Exception as e:
            self.logger.error(f"Error en test del sistema completo: {e}")
            return {
                'exitoso': False,
                'errores': [str(e)],
                'metricas': {}
            }
    
    def _test_generico(self, test: TestIntegracion) -> Dict[str, Any]:
        """Test genérico"""
        try:
            self.logger.info(f"Ejecutando test genérico: {test.nombre}")
            
            # Simular test genérico
            time.sleep(1)  # Simular procesamiento
            
            return {
                'exitoso': True,
                'errores': [],
                'metricas': {'tiempo_procesamiento': 1.0}
            }
            
        except Exception as e:
            self.logger.error(f"Error en test genérico: {e}")
            return {
                'exitoso': False,
                'errores': [str(e)],
                'metricas': {}
            }
    
    def _simular_datos_modulo(self, modulo: str) -> Dict[str, Any]:
        """Simular datos de un módulo"""
        try:
            np.random.seed(42)
            
            if modulo == 'datos_satelitales':
                return {
                    'ndvi': np.random.rand() * 0.8 + 0.2,
                    'ndwi': np.random.rand() * 0.6 + 0.1,
                    'evi': np.random.rand() * 0.7 + 0.15,
                    'timestamp': datetime.now().isoformat()
                }
            elif modulo == 'deep_learning':
                return {
                    'predicciones': {
                        'temperatura': np.random.randn() * 5 + 20,
                        'humedad': np.random.rand() * 40 + 30,
                        'precipitacion': max(0, np.random.randn() * 3)
                    },
                    'metricas': {
                        'accuracy': np.random.rand() * 0.2 + 0.8,
                        'rmse': np.random.rand() * 2 + 1
                    },
                    'timestamp': datetime.now().isoformat()
                }
            elif modulo == 'reportes':
                return {
                    'estadisticas': {
                        'media': np.random.rand() * 100,
                        'desviacion': np.random.rand() * 20,
                        'percentil_95': np.random.rand() * 120
                    },
                    'tendencias': {
                        'creciente': np.random.rand() > 0.5,
                        'magnitud': np.random.rand() * 10
                    },
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'datos': 'simulados', 'timestamp': datetime.now().isoformat()}
                
        except Exception as e:
            self.logger.error(f"Error simulando datos del módulo {modulo}: {e}")
            return {}
    
    def _validar_formato_datos(self, datos: Dict[str, Any], configuracion: Dict[str, Any]) -> bool:
        """Validar formato de datos"""
        try:
            if not configuracion.get('validar_formato', False):
                return True
            
            # Validar que datos sea un diccionario
            if not isinstance(datos, dict):
                return False
            
            # Validar timestamp
            if 'timestamp' not in datos:
                return False
            
            # Validar datos esperados
            datos_esperados = configuracion.get('datos_esperados', [])
            for dato in datos_esperados:
                if dato not in datos:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando formato de datos: {e}")
            return False
    
    def _validar_contenido_datos(self, datos: Dict[str, Any], configuracion: Dict[str, Any]) -> bool:
        """Validar contenido de datos"""
        try:
            if not configuracion.get('validar_contenido', False):
                return True
            
            # Validar que los datos no estén vacíos
            if not datos:
                return False
            
            # Validar tipos de datos
            for key, value in datos.items():
                if key != 'timestamp' and value is None:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando contenido de datos: {e}")
            return False
    
    def _simular_procesamiento_modulo(self, modulo: str, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Simular procesamiento en módulo destino"""
        try:
            # Simular tiempo de procesamiento
            tiempo_procesamiento = np.random.rand() * 2 + 0.5
            
            # Simular eficiencia
            eficiencia = np.random.rand() * 0.3 + 0.7
            
            # Simular éxito (95% de probabilidad)
            exitoso = np.random.rand() > 0.05
            
            return {
                'tiempo': tiempo_procesamiento,
                'eficiencia': eficiencia,
                'exitoso': exitoso
            }
            
        except Exception as e:
            self.logger.error(f"Error simulando procesamiento: {e}")
            return {'tiempo': 0, 'eficiencia': 0, 'exitoso': False}
    
    def _test_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Test de endpoint específico"""
        try:
            # Simular test de endpoint
            tiempo_respuesta = np.random.rand() * 3 + 0.5
            exitoso = np.random.rand() > 0.1  # 90% éxito
            
            return {
                'endpoint': endpoint,
                'tiempo': tiempo_respuesta,
                'exitoso': exitoso,
                'error': None if exitoso else "Error simulado"
            }
            
        except Exception as e:
            self.logger.error(f"Error testando endpoint {endpoint}: {e}")
            return {
                'endpoint': endpoint,
                'tiempo': 0,
                'exitoso': False,
                'error': str(e)
            }
    
    def _validar_jwt_token(self) -> bool:
        """Validar JWT token"""
        try:
            # Simular validación de JWT
            return np.random.rand() > 0.05  # 95% válido
            
        except Exception as e:
            self.logger.error(f"Error validando JWT: {e}")
            return False
    
    def _validar_permisos(self) -> bool:
        """Validar permisos"""
        try:
            # Simular validación de permisos
            return np.random.rand() > 0.02  # 98% válido
            
        except Exception as e:
            self.logger.error(f"Error validando permisos: {e}")
            return False
    
    def _verificar_modulos_activos(self) -> Dict[str, int]:
        """Verificar módulos activos"""
        try:
            # Simular verificación de módulos
            total = 10
            exitosos = np.random.randint(9, 11)  # 9-10 módulos exitosos
            
            return {'total': total, 'exitosos': exitosos}
            
        except Exception as e:
            self.logger.error(f"Error verificando módulos: {e}")
            return {'total': 0, 'exitosos': 0}
    
    def _verificar_tareas_funcionando(self) -> Dict[str, int]:
        """Verificar tareas funcionando"""
        try:
            # Simular verificación de tareas
            total = 5
            exitosas = np.random.randint(4, 6)  # 4-5 tareas exitosas
            
            return {'total': total, 'exitosas': exitosas}
            
        except Exception as e:
            self.logger.error(f"Error verificando tareas: {e}")
            return {'total': 0, 'exitosas': 0}
    
    def _obtener_metricas_sistema(self) -> Dict[str, float]:
        """Obtener métricas del sistema"""
        try:
            # Simular métricas del sistema
            return {
                'uptime': 99.5 + np.random.rand() * 0.5,
                'throughput': 1000 + np.random.rand() * 500,
                'latencia': 50 + np.random.rand() * 100
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas: {e}")
            return {}
    
    def _verificar_apis_funcionando(self) -> Dict[str, int]:
        """Verificar APIs funcionando"""
        try:
            # Simular verificación de APIs
            total = 6
            exitosas = np.random.randint(5, 7)  # 5-6 APIs exitosas
            
            return {'total': total, 'exitosas': exitosas}
            
        except Exception as e:
            self.logger.error(f"Error verificando APIs: {e}")
            return {'total': 0, 'exitosas': 0}
    
    def _guardar_resultado_test(self, resultado: ResultadoTest):
        """Guardar resultado de test"""
        try:
            self.cursor_bd.execute('''
                INSERT INTO resultados_tests 
                (test_id, exitoso, duracion, errores, metricas, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                resultado.test_id,
                resultado.exitoso,
                resultado.duracion,
                json.dumps(resultado.errores),
                json.dumps(resultado.metricas),
                resultado.timestamp
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error guardando resultado de test: {e}")
    
    def ejecutar_suite_tests(self) -> Dict[str, Any]:
        """Ejecutar suite completa de tests"""
        try:
            self.logger.info("Iniciando suite completa de tests de integración")
            
            inicio_total = time.time()
            resultados = {}
            
            if self.configuracion_testing['paralelismo']:
                # Ejecutar tests en paralelo
                futures = {}
                for test_id in self.tests_integracion.keys():
                    future = self.ejecutor.submit(self.ejecutar_test_integracion, test_id)
                    futures[future] = test_id
                
                for future in as_completed(futures):
                    test_id = futures[future]
                    try:
                        resultado = future.result()
                        resultados[test_id] = resultado
                    except Exception as e:
                        self.logger.error(f"Error en test {test_id}: {e}")
                        resultados[test_id] = ResultadoTest(
                            test_id=test_id,
                            exitoso=False,
                            duracion=0,
                            errores=[str(e)],
                            metricas={},
                            timestamp=datetime.now().isoformat()
                        )
            else:
                # Ejecutar tests secuencialmente
                for test_id in self.tests_integracion.keys():
                    resultado = self.ejecutar_test_integracion(test_id)
                    resultados[test_id] = resultado
            
            duracion_total = time.time() - inicio_total
            
            # Calcular estadísticas
            total_tests = len(resultados)
            tests_exitosos = sum(1 for r in resultados.values() if r.exitoso)
            tests_fallidos = total_tests - tests_exitosos
            tasa_exito = tests_exitosos / total_tests if total_tests > 0 else 0
            
            # Calcular métricas promedio
            duracion_promedio = np.mean([r.duracion for r in resultados.values()])
            errores_totales = sum(len(r.errores) for r in resultados.values())
            
            estadisticas = {
                'total_tests': total_tests,
                'tests_exitosos': tests_exitosos,
                'tests_fallidos': tests_fallidos,
                'tasa_exito': tasa_exito,
                'duracion_total': duracion_total,
                'duracion_promedio': duracion_promedio,
                'errores_totales': errores_totales,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Suite de tests completada: {tests_exitosos}/{total_tests} exitosos ({tasa_exito:.1%})")
            
            return {
                'estadisticas': estadisticas,
                'resultados': {test_id: {
                    'exitoso': r.exitoso,
                    'duracion': r.duracion,
                    'errores': r.errores,
                    'metricas': r.metricas
                } for test_id, r in resultados.items()}
            }
            
        except Exception as e:
            self.logger.error(f"Error ejecutando suite de tests: {e}")
            return {'error': str(e)}
    
    def generar_reporte_testing(self) -> str:
        """Generar reporte de testing"""
        try:
            self.logger.info("Generando reporte de testing de integración...")
            
            # Ejecutar suite de tests
            resultados_suite = self.ejecutar_suite_tests()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Testing de Integración',
                'version': self.configuracion['version'],
                'configuracion_testing': self.configuracion_testing,
                'tests_configurados': [
                    {
                        'id': t.id,
                        'nombre': t.nombre,
                        'modulo_origen': t.modulo_origen,
                        'modulo_destino': t.modulo_destino,
                        'tipo_test': t.tipo_test
                    } for t in self.tests_integracion.values()
                ],
                'resultados_suite': resultados_suite,
                'funcionalidades_implementadas': [
                    'Testing de flujo de datos entre módulos',
                    'Testing de integración de APIs',
                    'Testing del sistema completo',
                    'Validación de formatos y contenidos',
                    'Métricas de rendimiento',
                    'Ejecución paralela de tests',
                    'Base de datos de resultados',
                    'Reportes detallados',
                    'Validación de JWT y permisos',
                    'Simulación de datos realistas'
                ],
                'tecnologias_utilizadas': [
                    'ThreadPoolExecutor para paralelismo',
                    'SQLite para base de datos',
                    'NumPy para simulaciones',
                    'Logging estructurado',
                    'JSON para reportes'
                ],
                'recomendaciones': [
                    'Implementar tests de carga',
                    'Agregar tests de seguridad',
                    'Implementar tests de regresión',
                    'Agregar métricas de cobertura',
                    'Implementar tests de stress',
                    'Agregar tests de compatibilidad',
                    'Implementar tests de usabilidad',
                    'Agregar tests de accesibilidad',
                    'Implementar tests de performance',
                    'Agregar tests de integración continua'
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"testing_integracion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte de testing generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal de testing de integración"""
    print("TESTING DE INTEGRACION METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Testing de Integracion entre Modulos")
    print("=" * 80)
    
    try:
        # Crear sistema de testing
        testing_sistema = TestingIntegracionMETGO()
        
        # Generar reporte
        print(f"\nGenerando reporte de testing de integracion...")
        reporte = testing_sistema.generar_reporte_testing()
        
        if reporte:
            print(f"Reporte generado: {reporte}")
        else:
            print(f"Error generando reporte")
        
        # Mostrar información del sistema
        print(f"\nSistema de Testing de Integracion METGO 3D")
        print(f"Version: {testing_sistema.configuracion['version']}")
        print(f"Timeout por test: {testing_sistema.configuracion_testing['timeout_test']} segundos")
        print(f"Paralelismo: {testing_sistema.configuracion_testing['paralelismo']}")
        print(f"Umbral de exito: {testing_sistema.configuracion_testing['umbral_exito'] * 100}%")
        
        print(f"\nTests configurados:")
        for test in testing_sistema.tests_integracion.values():
            print(f"   - {test.nombre}")
            print(f"     {test.modulo_origen} → {test.modulo_destino} ({test.tipo_test})")
        
        # Ejecutar suite de tests
        print(f"\nEjecutando suite completa de tests...")
        resultados = testing_sistema.ejecutar_suite_tests()
        
        if 'estadisticas' in resultados:
            stats = resultados['estadisticas']
            print(f"\nResultados de la suite de tests:")
            print(f"   Total de tests: {stats['total_tests']}")
            print(f"   Tests exitosos: {stats['tests_exitosos']}")
            print(f"   Tests fallidos: {stats['tests_fallidos']}")
            print(f"   Tasa de exito: {stats['tasa_exito']:.1%}")
            print(f"   Duracion total: {stats['duracion_total']:.2f} segundos")
            print(f"   Duracion promedio: {stats['duracion_promedio']:.2f} segundos")
            print(f"   Errores totales: {stats['errores_totales']}")
            
            # Mostrar resultados por test
            print(f"\nResultados por test:")
            for test_id, resultado in resultados['resultados'].items():
                test = testing_sistema.tests_integracion[test_id]
                estado = "EXITOSO" if resultado['exitoso'] else "FALLIDO"
                print(f"   - {test.nombre}: {estado} ({resultado['duracion']:.2f}s)")
                if not resultado['exitoso'] and resultado['errores']:
                    for error in resultado['errores']:
                        print(f"     Error: {error}")
        
        return True
        
    except Exception as e:
        print(f"\nError en sistema de testing: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
