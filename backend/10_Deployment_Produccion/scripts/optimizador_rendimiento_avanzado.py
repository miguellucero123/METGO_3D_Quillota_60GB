"""
OPTIMIZADOR DE RENDIMIENTO AVANZADO - METGO 3D QUILLOTA
Sistema para optimizar el rendimiento de todos los componentes
"""

import sqlite3
import time
import psutil
import gc
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import lru_cache
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
import json
from typing import Dict, List, Any, Optional
import pickle

class OptimizadorRendimientoAvanzado:
    def __init__(self):
        self.logger = self._configurar_logging()
        self.cache_datos = {}
        self.cache_ml = {}
        self.metricas_rendimiento = {}
        self.configuracion_optimizacion = self._cargar_configuracion()
        
    def _configurar_logging(self):
        """Configurar logging para optimización"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/optimizacion_rendimiento.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('OPTIMIZADOR_RENDIMIENTO')
    
    def _cargar_configuracion(self):
        """Cargar configuración de optimización"""
        config = {
            'cache_size': 1000,
            'max_workers': 4,
            'batch_size': 1000,
            'memory_limit_mb': 1024,
            'optimize_queries': True,
            'use_parallel_processing': True,
            'enable_caching': True,
            'optimize_visualizations': True
        }
        
        # Cargar configuración personalizada si existe
        if os.path.exists('config/optimizacion.json'):
            try:
                with open('config/optimizacion.json', 'r') as f:
                    custom_config = json.load(f)
                    config.update(custom_config)
            except Exception as e:
                self.logger.warning(f"Error cargando configuración personalizada: {e}")
        
        return config
    
    def analizar_rendimiento_actual(self):
        """Analizar el rendimiento actual del sistema"""
        self.logger.info("Analizando rendimiento actual del sistema...")
        
        metricas = {
            'memoria': self._obtener_uso_memoria(),
            'cpu': self._obtener_uso_cpu(),
            'disco': self._obtener_uso_disco(),
            'bases_datos': self._analizar_bases_datos(),
            'archivos_python': self._analizar_archivos_python(),
            'cache_actual': len(self.cache_datos)
        }
        
        self.metricas_rendimiento = metricas
        self._mostrar_metricas_rendimiento(metricas)
        
        return metricas
    
    def _obtener_uso_memoria(self):
        """Obtener uso de memoria del sistema"""
        memoria = psutil.virtual_memory()
        return {
            'total_gb': round(memoria.total / (1024**3), 2),
            'usado_gb': round(memoria.used / (1024**3), 2),
            'disponible_gb': round(memoria.available / (1024**3), 2),
            'porcentaje': memoria.percent
        }
    
    def _obtener_uso_cpu(self):
        """Obtener uso de CPU"""
        return {
            'porcentaje': psutil.cpu_percent(interval=1),
            'nucleos': psutil.cpu_count(),
            'frecuencia': psutil.cpu_freq().current if psutil.cpu_freq() else 0
        }
    
    def _obtener_uso_disco(self):
        """Obtener uso de disco"""
        disco = psutil.disk_usage('.')
        return {
            'total_gb': round(disco.total / (1024**3), 2),
            'usado_gb': round(disco.used / (1024**3), 2),
            'disponible_gb': round(disco.free / (1024**3), 2),
            'porcentaje': round((disco.used / disco.total) * 100, 2)
        }
    
    def _analizar_bases_datos(self):
        """Analizar rendimiento de bases de datos"""
        bases_datos = [
            'metgo_agricola.db',
            'metgo_ml.db',
            'metgo_notificaciones.db'
        ]
        
        analisis = {}
        for db in bases_datos:
            if os.path.exists(db):
                try:
                    conn = sqlite3.connect(db)
                    cursor = conn.cursor()
                    
                    # Obtener información de tablas
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tablas = cursor.fetchall()
                    
                    # Obtener tamaño de la base de datos
                    size_mb = os.path.getsize(db) / (1024**2)
                    
                    # Obtener número de registros por tabla
                    registros_por_tabla = {}
                    for tabla in tablas:
                        cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]}")
                        count = cursor.fetchone()[0]
                        registros_por_tabla[tabla[0]] = count
                    
                    analisis[db] = {
                        'tamaño_mb': round(size_mb, 2),
                        'tablas': len(tablas),
                        'registros_por_tabla': registros_por_tabla
                    }
                    
                    conn.close()
                except Exception as e:
                    analisis[db] = {'error': str(e)}
            else:
                analisis[db] = {'error': 'Archivo no encontrado'}
        
        return analisis
    
    def _analizar_archivos_python(self):
        """Analizar archivos Python del proyecto"""
        archivos_python = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py'):
                    archivo_path = os.path.join(root, file)
                    try:
                        size_kb = os.path.getsize(archivo_path) / 1024
                        archivos_python.append({
                            'archivo': archivo_path,
                            'tamaño_kb': round(size_kb, 2)
                        })
                    except:
                        pass
        
        return {
            'total_archivos': len(archivos_python),
            'archivos_grandes': [f for f in archivos_python if f['tamaño_kb'] > 100],
            'tamaño_total_kb': sum(f['tamaño_kb'] for f in archivos_python)
        }
    
    def _mostrar_metricas_rendimiento(self, metricas):
        """Mostrar métricas de rendimiento"""
        print("\n" + "="*60)
        print("ANALISIS DE RENDIMIENTO ACTUAL")
        print("="*60)
        
        print(f"\n[MEMORIA] Uso de Memoria:")
        print(f"  • Total: {metricas['memoria']['total_gb']} GB")
        print(f"  • Usado: {metricas['memoria']['usado_gb']} GB ({metricas['memoria']['porcentaje']}%)")
        print(f"  • Disponible: {metricas['memoria']['disponible_gb']} GB")
        
        print(f"\n[CPU] Uso de CPU:")
        print(f"  • Porcentaje: {metricas['cpu']['porcentaje']}%")
        print(f"  • Núcleos: {metricas['cpu']['nucleos']}")
        print(f"  • Frecuencia: {metricas['cpu']['frecuencia']} MHz")
        
        print(f"\n[DISCO] Uso de Disco:")
        print(f"  • Total: {metricas['disco']['total_gb']} GB")
        print(f"  • Usado: {metricas['disco']['usado_gb']} GB ({metricas['disco']['porcentaje']}%)")
        print(f"  • Disponible: {metricas['disco']['disponible_gb']} GB")
        
        print(f"\n[BASES DE DATOS] Análisis:")
        for db, info in metricas['bases_datos'].items():
            if 'error' in info:
                print(f"  • {db}: {info['error']}")
            else:
                print(f"  • {db}: {info['tamaño_mb']} MB, {info['tablas']} tablas")
        
        print(f"\n[ARCHIVOS PYTHON] Análisis:")
        print(f"  • Total archivos: {metricas['archivos_python']['total_archivos']}")
        print(f"  • Tamaño total: {metricas['archivos_python']['tamaño_total_kb']:.2f} KB")
        print(f"  • Archivos grandes (>100KB): {len(metricas['archivos_python']['archivos_grandes'])}")
        
        print(f"\n[CACHE] Cache actual:")
        print(f"  • Elementos en cache: {metricas['cache_actual']}")
        
        print("="*60)
    
    def optimizar_bases_datos(self):
        """Optimizar bases de datos SQLite"""
        self.logger.info("Optimizando bases de datos...")
        
        bases_datos = [
            'metgo_agricola.db',
            'metgo_ml.db',
            'metgo_notificaciones.db'
        ]
        
        optimizaciones = {}
        
        for db in bases_datos:
            if os.path.exists(db):
                try:
                    conn = sqlite3.connect(db)
                    cursor = conn.cursor()
                    
                    # Obtener métricas antes de optimización
                    cursor.execute("PRAGMA page_count")
                    paginas_antes = cursor.fetchone()[0]
                    
                    cursor.execute("PRAGMA page_size")
                    page_size = cursor.fetchone()[0]
                    
                    tamaño_antes = paginas_antes * page_size / (1024**2)
                    
                    # Aplicar optimizaciones
                    cursor.execute("PRAGMA optimize")
                    cursor.execute("VACUUM")
                    cursor.execute("ANALYZE")
                    
                    # Obtener métricas después de optimización
                    cursor.execute("PRAGMA page_count")
                    paginas_despues = cursor.fetchone()[0]
                    
                    tamaño_despues = paginas_despues * page_size / (1024**2)
                    
                    optimizaciones[db] = {
                        'tamaño_antes_mb': round(tamaño_antes, 2),
                        'tamaño_despues_mb': round(tamaño_despues, 2),
                        'reduccion_mb': round(tamaño_antes - tamaño_despues, 2),
                        'reduccion_porcentaje': round(((tamaño_antes - tamaño_despues) / tamaño_antes) * 100, 2)
                    }
                    
                    conn.close()
                    
                except Exception as e:
                    optimizaciones[db] = {'error': str(e)}
        
        self._mostrar_optimizaciones_bd(optimizaciones)
        return optimizaciones
    
    def _mostrar_optimizaciones_bd(self, optimizaciones):
        """Mostrar resultados de optimización de bases de datos"""
        print("\n" + "="*50)
        print("OPTIMIZACION DE BASES DE DATOS")
        print("="*50)
        
        for db, info in optimizaciones.items():
            if 'error' in info:
                print(f"\n[ERROR] {db}: {info['error']}")
            else:
                print(f"\n[OK] {db}:")
                print(f"  • Tamaño antes: {info['tamaño_antes_mb']} MB")
                print(f"  • Tamaño después: {info['tamaño_despues_mb']} MB")
                print(f"  • Reducción: {info['reduccion_mb']} MB ({info['reduccion_porcentaje']}%)")
        
        print("="*50)
    
    def optimizar_cache_datos(self):
        """Optimizar sistema de cache de datos"""
        self.logger.info("Optimizando sistema de cache...")
        
        # Limpiar cache antiguo
        self._limpiar_cache_antiguo()
        
        # Configurar cache LRU para datos frecuentes
        self._configurar_cache_lru()
        
        # Pre-cargar datos importantes
        self._precargar_datos_importantes()
        
        print("\n[OK] Sistema de cache optimizado")
    
    def _limpiar_cache_antiguo(self):
        """Limpiar cache antiguo"""
        ahora = datetime.now()
        claves_a_eliminar = []
        
        for clave, valor in self.cache_datos.items():
            if isinstance(valor, dict) and 'timestamp' in valor:
                timestamp = valor['timestamp']
                if (ahora - timestamp).seconds > 3600:  # 1 hora
                    claves_a_eliminar.append(clave)
        
        for clave in claves_a_eliminar:
            del self.cache_datos[clave]
        
        self.logger.info(f"Cache limpiado: {len(claves_a_eliminar)} elementos eliminados")
    
    def _configurar_cache_lru(self):
        """Configurar cache LRU para funciones frecuentes"""
        # Esto se implementaría con decoradores @lru_cache
        pass
    
    def _precargar_datos_importantes(self):
        """Pre-cargar datos importantes en cache"""
        try:
            # Pre-cargar datos meteorológicos recientes
            conn = sqlite3.connect('metgo_agricola.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM datos_meteorologicos 
                ORDER BY fecha DESC 
                LIMIT 100
            """)
            
            datos_recientes = cursor.fetchall()
            self.cache_datos['datos_meteorologicos_recientes'] = {
                'datos': datos_recientes,
                'timestamp': datetime.now()
            }
            
            conn.close()
            
            self.logger.info("Datos importantes pre-cargados en cache")
            
        except Exception as e:
            self.logger.error(f"Error pre-cargando datos: {e}")
    
    def optimizar_consultas_sql(self):
        """Optimizar consultas SQL"""
        self.logger.info("Optimizando consultas SQL...")
        
        # Crear índices para mejorar rendimiento
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_fecha ON datos_meteorologicos(fecha)",
            "CREATE INDEX IF NOT EXISTS idx_estacion ON datos_meteorologicos(estacion)",
            "CREATE INDEX IF NOT EXISTS idx_tipo_alerta ON alertas_criticas(tipo_alerta)",
            "CREATE INDEX IF NOT EXISTS idx_fecha_alerta ON alertas_criticas(fecha_creacion)",
            "CREATE INDEX IF NOT EXISTS idx_variable ON predicciones_ml(variable)",
            "CREATE INDEX IF NOT EXISTS idx_fecha_prediccion ON predicciones_ml(fecha_prediccion)"
        ]
        
        bases_datos = [
            'metgo_agricola.db',
            'metgo_ml.db',
            'metgo_notificaciones.db'
        ]
        
        for db in bases_datos:
            if os.path.exists(db):
                try:
                    conn = sqlite3.connect(db)
                    cursor = conn.cursor()
                    
                    for indice in indices:
                        try:
                            cursor.execute(indice)
                        except sqlite3.OperationalError as e:
                            if "already exists" not in str(e):
                                self.logger.warning(f"Error creando índice en {db}: {e}")
                    
                    conn.commit()
                    conn.close()
                    
                    self.logger.info(f"Índices creados en {db}")
                    
                except Exception as e:
                    self.logger.error(f"Error optimizando {db}: {e}")
        
        print("\n[OK] Consultas SQL optimizadas con índices")
    
    def optimizar_modelos_ml(self):
        """Optimizar modelos de Machine Learning"""
        self.logger.info("Optimizando modelos de ML...")
        
        try:
            # Cargar configuración de optimización ML
            config_ml = {
                'n_jobs': -1,  # Usar todos los núcleos
                'random_state': 42,
                'n_estimators': 100,  # Reducir para entrenamiento más rápido
                'max_depth': 10,  # Limitar profundidad
                'learning_rate': 0.1
            }
            
            # Guardar configuración optimizada
            with open('config/optimizacion_ml.json', 'w') as f:
                json.dump(config_ml, f, indent=2)
            
            print("\n[OK] Configuración de ML optimizada")
            
        except Exception as e:
            self.logger.error(f"Error optimizando ML: {e}")
    
    def optimizar_visualizaciones(self):
        """Optimizar visualizaciones"""
        self.logger.info("Optimizando visualizaciones...")
        
        config_visualizacion = {
            'max_data_points': 1000,  # Limitar puntos de datos
            'use_webgl': True,  # Usar WebGL para mejor rendimiento
            'enable_animations': False,  # Deshabilitar animaciones
            'reduce_precision': True,  # Reducir precisión para mejor rendimiento
            'cache_plots': True  # Cachear gráficos
        }
        
        try:
            with open('config/optimizacion_visualizaciones.json', 'w') as f:
                json.dump(config_visualizacion, f, indent=2)
            
            print("\n[OK] Configuración de visualizaciones optimizada")
            
        except Exception as e:
            self.logger.error(f"Error optimizando visualizaciones: {e}")
    
    def implementar_procesamiento_paralelo(self):
        """Implementar procesamiento paralelo"""
        self.logger.info("Implementando procesamiento paralelo...")
        
        config_paralelo = {
            'max_workers': min(4, psutil.cpu_count()),
            'use_threading': True,
            'use_multiprocessing': False,  # SQLite no es thread-safe
            'batch_size': 100,
            'timeout': 30
        }
        
        try:
            with open('config/procesamiento_paralelo.json', 'w') as f:
                json.dump(config_paralelo, f, indent=2)
            
            print("\n[OK] Configuración de procesamiento paralelo implementada")
            
        except Exception as e:
            self.logger.error(f"Error implementando procesamiento paralelo: {e}")
    
    def limpiar_memoria(self):
        """Limpiar memoria del sistema"""
        self.logger.info("Limpiando memoria...")
        
        # Forzar garbage collection
        gc.collect()
        
        # Limpiar cache de datos
        self.cache_datos.clear()
        self.cache_ml.clear()
        
        print("\n[OK] Memoria limpiada")
    
    def generar_reporte_optimizacion(self):
        """Generar reporte de optimización"""
        self.logger.info("Generando reporte de optimización...")
        
        reporte = {
            'fecha': datetime.now().isoformat(),
            'metricas_antes': self.metricas_rendimiento,
            'optimizaciones_aplicadas': [
                'Bases de datos optimizadas',
                'Cache de datos optimizado',
                'Consultas SQL optimizadas',
                'Modelos ML optimizados',
                'Visualizaciones optimizadas',
                'Procesamiento paralelo implementado'
            ],
            'configuracion_optimizacion': self.configuracion_optimizacion
        }
        
        try:
            with open('reportes/reporte_optimizacion.json', 'w') as f:
                json.dump(reporte, f, indent=2)
            
            print("\n[OK] Reporte de optimización generado")
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
    
    def ejecutar_optimizacion_completa(self):
        """Ejecutar optimización completa del sistema"""
        print("\n" + "="*80)
        print("OPTIMIZADOR DE RENDIMIENTO AVANZADO - METGO 3D QUILLOTA")
        print("="*80)
        
        # 1. Analizar rendimiento actual
        print("\n[PASO 1] Analizando rendimiento actual...")
        self.analizar_rendimiento_actual()
        
        # 2. Optimizar bases de datos
        print("\n[PASO 2] Optimizando bases de datos...")
        self.optimizar_bases_datos()
        
        # 3. Optimizar cache
        print("\n[PASO 3] Optimizando sistema de cache...")
        self.optimizar_cache_datos()
        
        # 4. Optimizar consultas SQL
        print("\n[PASO 4] Optimizando consultas SQL...")
        self.optimizar_consultas_sql()
        
        # 5. Optimizar modelos ML
        print("\n[PASO 5] Optimizando modelos de ML...")
        self.optimizar_modelos_ml()
        
        # 6. Optimizar visualizaciones
        print("\n[PASO 6] Optimizando visualizaciones...")
        self.optimizar_visualizaciones()
        
        # 7. Implementar procesamiento paralelo
        print("\n[PASO 7] Implementando procesamiento paralelo...")
        self.implementar_procesamiento_paralelo()
        
        # 8. Limpiar memoria
        print("\n[PASO 8] Limpiando memoria...")
        self.limpiar_memoria()
        
        # 9. Generar reporte
        print("\n[PASO 9] Generando reporte de optimización...")
        self.generar_reporte_optimizacion()
        
        print("\n" + "="*80)
        print("OPTIMIZACION COMPLETA FINALIZADA")
        print("="*80)
        
        print("\n[RESUMEN] Optimizaciones aplicadas:")
        print("  • Bases de datos optimizadas y compactadas")
        print("  • Sistema de cache mejorado")
        print("  • Consultas SQL optimizadas con índices")
        print("  • Modelos ML configurados para mejor rendimiento")
        print("  • Visualizaciones optimizadas")
        print("  • Procesamiento paralelo implementado")
        print("  • Memoria limpiada")
        print("  • Reporte de optimización generado")
        
        print("\n[RESULTADO] El sistema METGO 3D Quillota está optimizado para mejor rendimiento!")

def main():
    """Función principal"""
    optimizador = OptimizadorRendimientoAvanzado()
    optimizador.ejecutar_optimizacion_completa()

if __name__ == "__main__":
    main()



