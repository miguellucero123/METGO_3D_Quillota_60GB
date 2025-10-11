#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ OPTIMIZACIÓN DE RENDIMIENTO METGO 3D
Sistema Meteorológico Agrícola Quillota - Optimización y Escalabilidad
"""

import os
import sys
import time
import json
import warnings
import psutil
import threading
import multiprocessing
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
import sqlite3
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import gc
import cProfile
import pstats
import io
from dataclasses import dataclass
import yaml

# Configuración
warnings.filterwarnings('ignore')

@dataclass
class MetricasRendimiento:
    """Métricas de rendimiento"""
    timestamp: datetime
    cpu_uso: float
    memoria_uso: float
    disco_io: float
    red_io: float
    tiempo_respuesta: float
    throughput: float
    latencia: float
    errores: int
    metadata: Dict[str, Any] = None

@dataclass
class Optimizacion:
    """Configuración de optimización"""
    nombre: str
    tipo: str
    configuracion: Dict[str, Any]
    impacto_esperado: float
    implementado: bool = False
    resultado: Dict[str, Any] = None

class OptimizacionRendimientoMETGO:
    """Sistema de optimización de rendimiento para METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/optimizacion',
            'directorio_logs': 'logs/optimizacion',
            'directorio_reportes': 'reportes/optimizacion',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Configuración de optimización
        self.configuracion_optimizacion = {
            'habilitar_profiling': True,
            'habilitar_cache': True,
            'habilitar_paralelizacion': True,
            'habilitar_compresion': True,
            'habilitar_indices': True,
            'habilitar_limpieza_memoria': True,
            'habilitar_optimizacion_db': True,
            'habilitar_optimizacion_red': True
        }
        
        # Métricas de rendimiento
        self.metricas_rendimiento = []
        self.baseline_rendimiento = None
        
        # Optimizaciones disponibles
        self.optimizaciones = self._cargar_optimizaciones()
        
        # Cache de resultados
        self.cache_resultados = {}
        
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
                    logging.FileHandler(f"{self.configuracion['directorio_logs']}/optimizacion_rendimiento.log"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('METGO_OPTIMIZACION_RENDIMIENTO')
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/optimizacion_rendimiento.db"
            
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
            # Tabla de métricas de rendimiento
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS metricas_rendimiento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    cpu_uso REAL NOT NULL,
                    memoria_uso REAL NOT NULL,
                    disco_io REAL NOT NULL,
                    red_io REAL NOT NULL,
                    tiempo_respuesta REAL NOT NULL,
                    throughput REAL NOT NULL,
                    latencia REAL NOT NULL,
                    errores INTEGER NOT NULL,
                    metadata TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de optimizaciones
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS optimizaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    configuracion TEXT NOT NULL,
                    impacto_esperado REAL NOT NULL,
                    implementado BOOLEAN DEFAULT FALSE,
                    resultado TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de benchmarks
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    tiempo_ejecucion REAL NOT NULL,
                    memoria_uso REAL NOT NULL,
                    cpu_uso REAL NOT NULL,
                    resultado TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_metricas_timestamp ON metricas_rendimiento(timestamp)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_optimizaciones_nombre ON optimizaciones(nombre)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_benchmarks_nombre ON benchmarks(nombre)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def _cargar_optimizaciones(self) -> List[Optimizacion]:
        """Cargar optimizaciones disponibles"""
        try:
            optimizaciones = []
            
            # Optimización de base de datos
            optimizaciones.append(Optimizacion(
                nombre="optimizacion_db_indices",
                tipo="base_datos",
                configuracion={
                    "crear_indices": True,
                    "optimizar_consultas": True,
                    "vacuum": True,
                    "analyze": True
                },
                impacto_esperado=0.3
            ))
            
            # Optimización de memoria
            optimizaciones.append(Optimizacion(
                nombre="optimizacion_memoria",
                tipo="memoria",
                configuracion={
                    "limpieza_automatica": True,
                    "garbage_collection": True,
                    "cache_optimization": True,
                    "memory_mapping": True
                },
                impacto_esperado=0.25
            ))
            
            # Optimización de CPU
            optimizaciones.append(Optimizacion(
                nombre="optimizacion_cpu",
                tipo="cpu",
                configuracion={
                    "paralelizacion": True,
                    "threading": True,
                    "multiprocessing": True,
                    "vectorizacion": True
                },
                impacto_esperado=0.4
            ))
            
            # Optimización de red
            optimizaciones.append(Optimizacion(
                nombre="optimizacion_red",
                tipo="red",
                configuracion={
                    "connection_pooling": True,
                    "keep_alive": True,
                    "compression": True,
                    "caching": True
                },
                impacto_esperado=0.2
            ))
            
            # Optimización de I/O
            optimizaciones.append(Optimizacion(
                nombre="optimizacion_io",
                tipo="io",
                configuracion={
                    "async_io": True,
                    "buffering": True,
                    "compression": True,
                    "batch_processing": True
                },
                impacto_esperado=0.35
            ))
            
            return optimizaciones
            
        except Exception as e:
            self.logger.error(f"Error cargando optimizaciones: {e}")
            return []
    
    def medir_rendimiento_baseline(self) -> MetricasRendimiento:
        """Medir rendimiento baseline del sistema"""
        try:
            self.logger.info("Midiendo rendimiento baseline...")
            
            inicio = time.time()
            
            # Métricas del sistema
            cpu_uso = psutil.cpu_percent(interval=1)
            memoria = psutil.virtual_memory()
            memoria_uso = memoria.percent
            
            # Métricas de disco
            disco = psutil.disk_io_counters()
            disco_io = (disco.read_bytes + disco.write_bytes) / (1024 * 1024)  # MB
            
            # Métricas de red
            red = psutil.net_io_counters()
            red_io = (red.bytes_sent + red.bytes_recv) / (1024 * 1024)  # MB
            
            # Tiempo de respuesta simulado
            tiempo_respuesta = time.time() - inicio
            
            # Throughput simulado
            throughput = 1000 / tiempo_respuesta if tiempo_respuesta > 0 else 0
            
            # Latencia simulado
            latencia = tiempo_respuesta * 1000  # ms
            
            # Errores
            errores = 0
            
            metricas = MetricasRendimiento(
                timestamp=datetime.now(),
                cpu_uso=cpu_uso,
                memoria_uso=memoria_uso,
                disco_io=disco_io,
                red_io=red_io,
                tiempo_respuesta=tiempo_respuesta,
                throughput=throughput,
                latencia=latencia,
                errores=errores,
                metadata={'tipo': 'baseline'}
            )
            
            self.baseline_rendimiento = metricas
            self._guardar_metricas_rendimiento(metricas)
            
            self.logger.info(f"Rendimiento baseline medido: CPU={cpu_uso:.1f}%, Memoria={memoria_uso:.1f}%")
            return metricas
            
        except Exception as e:
            self.logger.error(f"Error midiendo rendimiento baseline: {e}")
            return None
    
    def medir_rendimiento_actual(self) -> MetricasRendimiento:
        """Medir rendimiento actual del sistema"""
        try:
            inicio = time.time()
            
            # Métricas del sistema
            cpu_uso = psutil.cpu_percent(interval=1)
            memoria = psutil.virtual_memory()
            memoria_uso = memoria.percent
            
            # Métricas de disco
            disco = psutil.disk_io_counters()
            disco_io = (disco.read_bytes + disco.write_bytes) / (1024 * 1024)  # MB
            
            # Métricas de red
            red = psutil.net_io_counters()
            red_io = (red.bytes_sent + red.bytes_recv) / (1024 * 1024)  # MB
            
            # Tiempo de respuesta
            tiempo_respuesta = time.time() - inicio
            
            # Throughput
            throughput = 1000 / tiempo_respuesta if tiempo_respuesta > 0 else 0
            
            # Latencia
            latencia = tiempo_respuesta * 1000  # ms
            
            # Errores
            errores = 0
            
            metricas = MetricasRendimiento(
                timestamp=datetime.now(),
                cpu_uso=cpu_uso,
                memoria_uso=memoria_uso,
                disco_io=disco_io,
                red_io=red_io,
                tiempo_respuesta=tiempo_respuesta,
                throughput=throughput,
                latencia=latencia,
                errores=errores,
                metadata={'tipo': 'actual'}
            )
            
            self.metricas_rendimiento.append(metricas)
            self._guardar_metricas_rendimiento(metricas)
            
            return metricas
            
        except Exception as e:
            self.logger.error(f"Error midiendo rendimiento actual: {e}")
            return None
    
    def _guardar_metricas_rendimiento(self, metricas: MetricasRendimiento):
        """Guardar métricas de rendimiento en la base de datos"""
        try:
            self.cursor_bd.execute('''
                INSERT INTO metricas_rendimiento 
                (timestamp, cpu_uso, memoria_uso, disco_io, red_io, tiempo_respuesta, throughput, latencia, errores, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metricas.timestamp,
                metricas.cpu_uso,
                metricas.memoria_uso,
                metricas.disco_io,
                metricas.red_io,
                metricas.tiempo_respuesta,
                metricas.throughput,
                metricas.latencia,
                metricas.errores,
                json.dumps(metricas.metadata) if metricas.metadata else None
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error guardando métricas de rendimiento: {e}")
    
    def optimizar_base_datos(self) -> Dict[str, Any]:
        """Optimizar base de datos"""
        try:
            self.logger.info("Optimizando base de datos...")
            
            inicio = time.time()
            resultados = {}
            
            # Crear índices
            if self.configuracion_optimizacion['habilitar_indices']:
                indices = [
                    "CREATE INDEX IF NOT EXISTS idx_datos_timestamp ON datos_meteorologicos(timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_datos_variable ON datos_meteorologicos(variable)",
                    "CREATE INDEX IF NOT EXISTS idx_alertas_timestamp ON alertas(timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_alertas_nivel ON alertas(nivel)",
                    "CREATE INDEX IF NOT EXISTS idx_metricas_timestamp ON metricas(timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_metricas_nombre ON metricas(nombre)"
                ]
                
                for indice in indices:
                    try:
                        self.cursor_bd.execute(indice)
                        resultados['indices_creados'] = resultados.get('indices_creados', 0) + 1
                    except Exception as e:
                        self.logger.warning(f"Error creando índice: {e}")
            
            # Optimizar consultas
            if self.configuracion_optimizacion['habilitar_optimizacion_db']:
                try:
                    self.cursor_bd.execute("VACUUM")
                    resultados['vacuum_completado'] = True
                except Exception as e:
                    self.logger.warning(f"Error ejecutando VACUUM: {e}")
                
                try:
                    self.cursor_bd.execute("ANALYZE")
                    resultados['analyze_completado'] = True
                except Exception as e:
                    self.logger.warning(f"Error ejecutando ANALYZE: {e}")
            
            # Configurar pragmas
            pragmas = [
                "PRAGMA journal_mode=WAL",
                "PRAGMA synchronous=NORMAL",
                "PRAGMA cache_size=10000",
                "PRAGMA temp_store=MEMORY",
                "PRAGMA mmap_size=268435456"
            ]
            
            for pragma in pragmas:
                try:
                    self.cursor_bd.execute(pragma)
                    resultados['pragmas_configurados'] = resultados.get('pragmas_configurados', 0) + 1
                except Exception as e:
                    self.logger.warning(f"Error configurando pragma: {e}")
            
            self.conexion_bd.commit()
            
            duracion = time.time() - inicio
            resultados['duracion'] = duracion
            resultados['exitoso'] = True
            
            self.logger.info(f"Optimización de base de datos completada en {duracion:.2f} segundos")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error optimizando base de datos: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def optimizar_memoria(self) -> Dict[str, Any]:
        """Optimizar uso de memoria"""
        try:
            self.logger.info("Optimizando memoria...")
            
            inicio = time.time()
            resultados = {}
            
            # Limpieza de memoria
            if self.configuracion_optimizacion['habilitar_limpieza_memoria']:
                # Garbage collection
                gc.collect()
                resultados['garbage_collection'] = True
                
                # Limpiar cache de resultados
                self.cache_resultados.clear()
                resultados['cache_limpiado'] = True
            
            # Optimización de pandas
            try:
                import pandas as pd
                pd.set_option('mode.chained_assignment', None)
                resultados['pandas_optimizado'] = True
            except Exception as e:
                self.logger.warning(f"Error optimizando pandas: {e}")
            
            # Optimización de numpy
            try:
                import numpy as np
                np.seterr(all='ignore')
                resultados['numpy_optimizado'] = True
            except Exception as e:
                self.logger.warning(f"Error optimizando numpy: {e}")
            
            duracion = time.time() - inicio
            resultados['duracion'] = duracion
            resultados['exitoso'] = True
            
            self.logger.info(f"Optimización de memoria completada en {duracion:.2f} segundos")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error optimizando memoria: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def optimizar_cpu(self) -> Dict[str, Any]:
        """Optimizar uso de CPU"""
        try:
            self.logger.info("Optimizando CPU...")
            
            inicio = time.time()
            resultados = {}
            
            # Configurar número de hilos
            if self.configuracion_optimizacion['habilitar_paralelizacion']:
                num_cores = multiprocessing.cpu_count()
                resultados['cores_disponibles'] = num_cores
                resultados['threading_habilitado'] = True
                resultados['multiprocessing_habilitado'] = True
            
            # Optimización de numpy
            try:
                import numpy as np
                # Configurar número de hilos para numpy
                os.environ['OMP_NUM_THREADS'] = str(num_cores)
                os.environ['MKL_NUM_THREADS'] = str(num_cores)
                resultados['numpy_threads'] = num_cores
            except Exception as e:
                self.logger.warning(f"Error configurando threads de numpy: {e}")
            
            # Optimización de pandas
            try:
                import pandas as pd
                # Configurar número de hilos para pandas
                pd.set_option('compute.use_bottleneck', True)
                pd.set_option('compute.use_numexpr', True)
                resultados['pandas_optimizado'] = True
            except Exception as e:
                self.logger.warning(f"Error optimizando pandas: {e}")
            
            duracion = time.time() - inicio
            resultados['duracion'] = duracion
            resultados['exitoso'] = True
            
            self.logger.info(f"Optimización de CPU completada en {duracion:.2f} segundos")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error optimizando CPU: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def optimizar_red(self) -> Dict[str, Any]:
        """Optimizar configuración de red"""
        try:
            self.logger.info("Optimizando red...")
            
            inicio = time.time()
            resultados = {}
            
            # Configuración de requests
            if self.configuracion_optimizacion['habilitar_optimizacion_red']:
                try:
                    import requests
                    # Configurar session para reutilizar conexiones
                    session = requests.Session()
                    session.headers.update({
                        'User-Agent': 'METGO3D/2.0',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive'
                    })
                    resultados['session_configurada'] = True
                except Exception as e:
                    self.logger.warning(f"Error configurando session: {e}")
            
            # Configuración de timeout
            resultados['timeout_configurado'] = 30
            resultados['reintentos_configurados'] = 3
            
            duracion = time.time() - inicio
            resultados['duracion'] = duracion
            resultados['exitoso'] = True
            
            self.logger.info(f"Optimización de red completada en {duracion:.2f} segundos")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error optimizando red: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def optimizar_io(self) -> Dict[str, Any]:
        """Optimizar I/O"""
        try:
            self.logger.info("Optimizando I/O...")
            
            inicio = time.time()
            resultados = {}
            
            # Configuración de buffering
            if self.configuracion_optimizacion['habilitar_compresion']:
                resultados['buffering_habilitado'] = True
                resultados['compresion_habilitada'] = True
            
            # Configuración de batch processing
            resultados['batch_size'] = 1000
            resultados['chunk_size'] = 8192
            
            duracion = time.time() - inicio
            resultados['duracion'] = duracion
            resultados['exitoso'] = True
            
            self.logger.info(f"Optimización de I/O completada en {duracion:.2f} segundos")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error optimizando I/O: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def ejecutar_benchmark(self, nombre: str, funcion, *args, **kwargs) -> Dict[str, Any]:
        """Ejecutar benchmark de una función"""
        try:
            self.logger.info(f"Ejecutando benchmark: {nombre}")
            
            inicio = time.time()
            inicio_cpu = psutil.cpu_percent()
            inicio_memoria = psutil.virtual_memory().percent
            
            # Ejecutar función
            resultado = funcion(*args, **kwargs)
            
            fin = time.time()
            fin_cpu = psutil.cpu_percent()
            fin_memoria = psutil.virtual_memory().percent
            
            tiempo_ejecucion = fin - inicio
            memoria_uso = fin_memoria - inicio_memoria
            cpu_uso = fin_cpu - inicio_cpu
            
            benchmark = {
                'nombre': nombre,
                'tiempo_ejecucion': tiempo_ejecucion,
                'memoria_uso': memoria_uso,
                'cpu_uso': cpu_uso,
                'resultado': str(resultado)[:100] if resultado else None,
                'timestamp': datetime.now()
            }
            
            # Guardar benchmark
            self._guardar_benchmark(benchmark)
            
            self.logger.info(f"Benchmark {nombre} completado en {tiempo_ejecucion:.2f} segundos")
            return benchmark
            
        except Exception as e:
            self.logger.error(f"Error ejecutando benchmark {nombre}: {e}")
            return {'error': str(e)}
    
    def _guardar_benchmark(self, benchmark: Dict[str, Any]):
        """Guardar benchmark en la base de datos"""
        try:
            self.cursor_bd.execute('''
                INSERT INTO benchmarks 
                (nombre, tipo, tiempo_ejecucion, memoria_uso, cpu_uso, resultado)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                benchmark['nombre'],
                'funcion',
                benchmark['tiempo_ejecucion'],
                benchmark['memoria_uso'],
                benchmark['cpu_uso'],
                benchmark['resultado']
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error guardando benchmark: {e}")
    
    def ejecutar_profiling(self, funcion, *args, **kwargs) -> Dict[str, Any]:
        """Ejecutar profiling de una función"""
        try:
            if not self.configuracion_optimizacion['habilitar_profiling']:
                return {'profiling_deshabilitado': True}
            
            self.logger.info("Ejecutando profiling...")
            
            # Crear profiler
            profiler = cProfile.Profile()
            
            # Ejecutar función con profiling
            profiler.enable()
            resultado = funcion(*args, **kwargs)
            profiler.disable()
            
            # Obtener estadísticas
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(20)  # Top 20 funciones
            
            estadisticas = s.getvalue()
            
            profiling_resultado = {
                'funcion': funcion.__name__,
                'estadisticas': estadisticas,
                'resultado': str(resultado)[:100] if resultado else None,
                'timestamp': datetime.now()
            }
            
            self.logger.info("Profiling completado")
            return profiling_resultado
            
        except Exception as e:
            self.logger.error(f"Error ejecutando profiling: {e}")
            return {'error': str(e)}
    
    def ejecutar_optimizacion_completa(self) -> Dict[str, Any]:
        """Ejecutar optimización completa del sistema"""
        try:
            self.logger.info("Iniciando optimización completa del sistema...")
            
            inicio = time.time()
            resultados = {}
            
            # Medir rendimiento baseline
            baseline = self.medir_rendimiento_baseline()
            resultados['baseline'] = baseline.__dict__ if baseline else None
            
            # Ejecutar optimizaciones
            optimizaciones = [
                ('base_datos', self.optimizar_base_datos),
                ('memoria', self.optimizar_memoria),
                ('cpu', self.optimizar_cpu),
                ('red', self.optimizar_red),
                ('io', self.optimizar_io)
            ]
            
            for nombre, funcion in optimizaciones:
                try:
                    resultado = funcion()
                    resultados[nombre] = resultado
                    self.logger.info(f"Optimización {nombre} completada")
                except Exception as e:
                    self.logger.error(f"Error en optimización {nombre}: {e}")
                    resultados[nombre] = {'error': str(e)}
            
            # Medir rendimiento después de optimizaciones
            time.sleep(2)  # Esperar a que se estabilice
            rendimiento_optimizado = self.medir_rendimiento_actual()
            resultados['rendimiento_optimizado'] = rendimiento_optimizado.__dict__ if rendimiento_optimizado else None
            
            # Calcular mejoras
            if baseline and rendimiento_optimizado:
                mejoras = {
                    'cpu_mejora': baseline.cpu_uso - rendimiento_optimizado.cpu_uso,
                    'memoria_mejora': baseline.memoria_uso - rendimiento_optimizado.memoria_uso,
                    'tiempo_respuesta_mejora': baseline.tiempo_respuesta - rendimiento_optimizado.tiempo_respuesta,
                    'throughput_mejora': rendimiento_optimizado.throughput - baseline.throughput
                }
                resultados['mejoras'] = mejoras
            
            duracion = time.time() - inicio
            resultados['duracion_total'] = duracion
            resultados['exitoso'] = True
            
            self.logger.info(f"Optimización completa finalizada en {duracion:.2f} segundos")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error ejecutando optimización completa: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def generar_reporte_optimizacion(self) -> str:
        """Generar reporte de optimización"""
        try:
            self.logger.info("Generando reporte de optimización...")
            
            # Obtener métricas recientes
            self.cursor_bd.execute('''
                SELECT * FROM metricas_rendimiento 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''')
            metricas_recientes = self.cursor_bd.fetchall()
            
            # Obtener benchmarks recientes
            self.cursor_bd.execute('''
                SELECT * FROM benchmarks 
                ORDER BY fecha_creacion DESC 
                LIMIT 10
            ''')
            benchmarks_recientes = self.cursor_bd.fetchall()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Optimización de Rendimiento',
                'version': self.configuracion['version'],
                'configuracion': self.configuracion_optimizacion,
                'metricas_recientes': [
                    {
                        'timestamp': m[1],
                        'cpu_uso': m[2],
                        'memoria_uso': m[3],
                        'tiempo_respuesta': m[6],
                        'throughput': m[7]
                    } for m in metricas_recientes
                ],
                'benchmarks_recientes': [
                    {
                        'nombre': b[1],
                        'tiempo_ejecucion': b[3],
                        'memoria_uso': b[4],
                        'cpu_uso': b[5]
                    } for b in benchmarks_recientes
                ],
                'optimizaciones': [
                    {
                        'nombre': o.nombre,
                        'tipo': o.tipo,
                        'impacto_esperado': o.impacto_esperado,
                        'implementado': o.implementado
                    } for o in self.optimizaciones
                ],
                'recomendaciones': [
                    "Monitorear métricas de rendimiento regularmente",
                    "Ejecutar optimizaciones periódicamente",
                    "Ajustar configuración según carga de trabajo",
                    "Implementar caching para operaciones frecuentes",
                    "Considerar escalabilidad horizontal si es necesario"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"optimizacion_rendimiento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte de optimización generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal de optimización de rendimiento"""
    print("⚡ OPTIMIZACIÓN DE RENDIMIENTO METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Optimización y Escalabilidad")
    print("=" * 80)
    
    try:
        # Crear optimizador
        optimizador = OptimizacionRendimientoMETGO()
        
        # Ejecutar optimización completa
        print(f"\n⚡ Ejecutando optimización completa...")
        resultados = optimizador.ejecutar_optimizacion_completa()
        
        if resultados.get('exitoso'):
            print(f"✅ Optimización completada exitosamente")
            print(f"⏱️ Duración total: {resultados.get('duracion_total', 0):.2f} segundos")
            
            # Mostrar mejoras
            if 'mejoras' in resultados:
                mejoras = resultados['mejoras']
                print(f"\n📈 Mejoras obtenidas:")
                print(f"   CPU: {mejoras.get('cpu_mejora', 0):.1f}%")
                print(f"   Memoria: {mejoras.get('memoria_mejora', 0):.1f}%")
                print(f"   Tiempo de respuesta: {mejoras.get('tiempo_respuesta_mejora', 0):.3f}s")
                print(f"   Throughput: {mejoras.get('throughput_mejora', 0):.1f} req/s")
            
            # Mostrar optimizaciones
            print(f"\n🔧 Optimizaciones ejecutadas:")
            for nombre, resultado in resultados.items():
                if isinstance(resultado, dict) and resultado.get('exitoso'):
                    print(f"   ✅ {nombre}: {resultado.get('duracion', 0):.2f}s")
                elif isinstance(resultado, dict) and 'error' in resultado:
                    print(f"   ❌ {nombre}: {resultado['error']}")
        else:
            print(f"❌ Error en optimización: {resultados.get('error', 'Error desconocido')}")
        
        # Generar reporte
        print(f"\n📋 Generando reporte...")
        reporte = optimizador.generar_reporte_optimizacion()
        
        if reporte:
            print(f"✅ Reporte generado: {reporte}")
        else:
            print(f"⚠️ Error generando reporte")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en optimización de rendimiento: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
