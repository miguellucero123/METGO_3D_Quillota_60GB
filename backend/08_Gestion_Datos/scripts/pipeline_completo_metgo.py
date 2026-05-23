#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔄 PIPELINE COMPLETO METGO 3D
Sistema Meteorológico Agrícola Quillota - Pipeline Integrado de Datos
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
import sqlite3
from dataclasses import dataclass
from enum import Enum

# Configuración
warnings.filterwarnings('ignore')

class EstadoProcesamiento(Enum):
    """Estados del procesamiento"""
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADO = "completado"
    ERROR = "error"
    CANCELADO = "cancelado"

@dataclass
class DatosMeteorologicos:
    """Estructura de datos meteorológicos"""
    timestamp: datetime
    temperatura: float
    precipitacion: float
    viento_velocidad: float
    viento_direccion: float
    humedad: float
    presion: float
    radiacion_solar: float
    punto_rocio: float
    fuente: str = "sintetico"
    calidad: float = 1.0

@dataclass
class DatosIoT:
    """Estructura de datos IoT"""
    sensor_id: str
    timestamp: datetime
    tipo: str
    valor: float
    unidad: str
    bateria: float
    senal: float
    ubicacion: Dict

@dataclass
class PrediccionML:
    """Estructura de predicción ML"""
    timestamp: datetime
    modelo: str
    variable: str
    prediccion: float
    confianza: float
    horizonte: int

@dataclass
class Alerta:
    """Estructura de alerta"""
    timestamp: datetime
    tipo: str
    nivel: str
    mensaje: str
    activa: bool = True

class PipelineCompletoMETGO:
    """Pipeline completo de procesamiento de datos para METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/pipeline',
            'directorio_logs': 'logs/pipeline',
            'directorio_temporal': 'temp/pipeline',
            'directorio_resultados': 'resultados/pipeline',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Configuración del pipeline
        self.configuracion_pipeline = {
            'frecuencia_procesamiento': 60,  # segundos
            'batch_size': 1000,
            'timeout_procesamiento': 300,  # segundos
            'max_reintentos': 3,
            'habilitar_paralelismo': True,
            'habilitar_cache': True,
            'habilitar_validacion': True,
            'habilitar_limpieza': True
        }
        
        # Estado del pipeline
        self.estado_pipeline = {
            'activo': False,
            'ultima_ejecucion': None,
            'procesos_activos': 0,
            'errores': [],
            'metricas': {}
        }
        
        # Colas de datos
        self.cola_datos_entrada = queue.Queue()
        self.cola_datos_procesados = queue.Queue()
        self.cola_alertas = queue.Queue()
        self.cola_predicciones = queue.Queue()
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Cache de datos
        self.cache_datos = {}
        self.cache_predicciones = {}
        
        # Hilos de procesamiento
        self.hilos_activos = []
        self.detener_hilos = threading.Event()
    
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
                    logging.FileHandler(f"{self.configuracion['directorio_logs']}/pipeline.log"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('METGO_PIPELINE')
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/pipeline_metgo3d.db"
            
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
            # Tabla de datos meteorológicos
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS datos_meteorologicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    temperatura REAL,
                    precipitacion REAL,
                    viento_velocidad REAL,
                    viento_direccion REAL,
                    humedad REAL,
                    presion REAL,
                    radiacion_solar REAL,
                    punto_rocio REAL,
                    fuente TEXT,
                    calidad REAL,
                    procesado BOOLEAN DEFAULT FALSE,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de datos IoT
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS datos_iot (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    tipo TEXT NOT NULL,
                    valor REAL NOT NULL,
                    unidad TEXT,
                    bateria REAL,
                    senal REAL,
                    ubicacion TEXT,
                    procesado BOOLEAN DEFAULT FALSE,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de predicciones ML
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS predicciones_ml (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    modelo TEXT NOT NULL,
                    variable TEXT NOT NULL,
                    prediccion REAL NOT NULL,
                    confianza REAL,
                    horizonte INTEGER,
                    procesado BOOLEAN DEFAULT FALSE,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de alertas
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS alertas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    tipo TEXT NOT NULL,
                    nivel TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    activa BOOLEAN DEFAULT TRUE,
                    procesada BOOLEAN DEFAULT FALSE,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de métricas del pipeline
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS metricas_pipeline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    etapa TEXT NOT NULL,
                    duracion_segundos REAL,
                    registros_procesados INTEGER,
                    errores INTEGER,
                    estado TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_datos_meteorologicos_timestamp ON datos_meteorologicos(timestamp)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_datos_iot_timestamp ON datos_iot(timestamp)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_predicciones_ml_timestamp ON predicciones_ml(timestamp)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_alertas_timestamp ON alertas(timestamp)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def generar_datos_sinteticos(self, cantidad: int = 1000) -> List[DatosMeteorologicos]:
        """Generar datos meteorológicos sintéticos"""
        try:
            self.logger.info(f"Generando {cantidad} registros de datos sintéticos...")
            
            datos = []
            timestamp_base = datetime.now() - timedelta(hours=cantidad)
            
            for i in range(cantidad):
                timestamp = timestamp_base + timedelta(hours=i)
                
                # Generar datos realistas
                temperatura = 15 + 10 * np.sin(2 * np.pi * timestamp.dayofyear / 365) + np.random.normal(0, 3)
                precipitacion = np.random.exponential(0.5) if np.random.random() > 0.9 else 0
                viento_velocidad = np.random.gamma(2, 2)
                viento_direccion = np.random.uniform(0, 360)
                humedad = 80 - (temperatura - 15) * 2 + np.random.normal(0, 5)
                humedad = max(0, min(100, humedad))
                presion = 1013 + np.random.normal(0, 10)
                radiacion_solar = max(0, 800 * np.sin(np.pi * timestamp.hour / 24) + np.random.normal(0, 50))
                punto_rocio = temperatura - (100 - humedad) / 5
                
                dato = DatosMeteorologicos(
                    timestamp=timestamp,
                    temperatura=temperatura,
                    precipitacion=precipitacion,
                    viento_velocidad=viento_velocidad,
                    viento_direccion=viento_direccion,
                    humedad=humedad,
                    presion=presion,
                    radiacion_solar=radiacion_solar,
                    punto_rocio=punto_rocio,
                    fuente="sintetico",
                    calidad=1.0
                )
                
                datos.append(dato)
            
            self.logger.info(f"✅ {len(datos)} registros sintéticos generados")
            return datos
            
        except Exception as e:
            self.logger.error(f"Error generando datos sintéticos: {e}")
            return []
    
    def generar_datos_iot_sinteticos(self, cantidad: int = 100) -> List[DatosIoT]:
        """Generar datos IoT sintéticos"""
        try:
            self.logger.info(f"Generando {cantidad} registros de datos IoT sintéticos...")
            
            datos = []
            sensores = [
                {'id': 'sensor_001', 'tipo': 'temperatura', 'unidad': '°C'},
                {'id': 'sensor_002', 'tipo': 'humedad', 'unidad': '%'},
                {'id': 'sensor_003', 'tipo': 'viento_velocidad', 'unidad': 'm/s'},
                {'id': 'sensor_004', 'tipo': 'precipitacion', 'unidad': 'mm'},
                {'id': 'sensor_005', 'tipo': 'presion', 'unidad': 'hPa'}
            ]
            
            timestamp_base = datetime.now() - timedelta(hours=cantidad)
            
            for i in range(cantidad):
                timestamp = timestamp_base + timedelta(hours=i)
                
                for sensor in sensores:
                    # Generar valor según el tipo de sensor
                    if sensor['tipo'] == 'temperatura':
                        valor = 15 + 10 * np.sin(2 * np.pi * timestamp.dayofyear / 365) + np.random.normal(0, 2)
                    elif sensor['tipo'] == 'humedad':
                        valor = 60 + 20 * np.sin(2 * np.pi * timestamp.hour / 24) + np.random.normal(0, 5)
                        valor = max(0, min(100, valor))
                    elif sensor['tipo'] == 'viento_velocidad':
                        valor = np.random.gamma(2, 2)
                    elif sensor['tipo'] == 'precipitacion':
                        valor = np.random.exponential(0.5) if np.random.random() > 0.9 else 0
                    elif sensor['tipo'] == 'presion':
                        valor = 1013 + np.random.normal(0, 10)
                    else:
                        valor = np.random.uniform(0, 100)
                    
                    dato = DatosIoT(
                        sensor_id=sensor['id'],
                        timestamp=timestamp,
                        tipo=sensor['tipo'],
                        valor=valor,
                        unidad=sensor['unidad'],
                        bateria=100 - i * 0.1,
                        senal=85 + np.random.normal(0, 5),
                        ubicacion={'latitud': -32.8833, 'longitud': -71.2333, 'altitud': 127}
                    )
                    
                    datos.append(dato)
            
            self.logger.info(f"✅ {len(datos)} registros IoT sintéticos generados")
            return datos
            
        except Exception as e:
            self.logger.error(f"Error generando datos IoT sintéticos: {e}")
            return []
    
    def validar_datos_meteorologicos(self, datos: List[DatosMeteorologicos]) -> List[DatosMeteorologicos]:
        """Validar datos meteorológicos"""
        try:
            self.logger.info("Validando datos meteorológicos...")
            
            datos_validos = []
            umbrales = {
                'temperatura': {'min': -5, 'max': 40},
                'precipitacion': {'min': 0, 'max': 100},
                'viento_velocidad': {'min': 0, 'max': 50},
                'humedad': {'min': 0, 'max': 100},
                'presion': {'min': 950, 'max': 1050},
                'radiacion_solar': {'min': 0, 'max': 1200}
            }
            
            for dato in datos:
                valido = True
                calidad = 1.0
                
                # Validar temperatura
                if not (umbrales['temperatura']['min'] <= dato.temperatura <= umbrales['temperatura']['max']):
                    valido = False
                    calidad -= 0.2
                
                # Validar precipitación
                if not (umbrales['precipitacion']['min'] <= dato.precipitacion <= umbrales['precipitacion']['max']):
                    valido = False
                    calidad -= 0.1
                
                # Validar humedad
                if not (umbrales['humedad']['min'] <= dato.humedad <= umbrales['humedad']['max']):
                    valido = False
                    calidad -= 0.1
                
                # Validar presión
                if not (umbrales['presion']['min'] <= dato.presion <= umbrales['presion']['max']):
                    valido = False
                    calidad -= 0.1
                
                # Actualizar calidad
                dato.calidad = max(0.0, calidad)
                
                if valido or calidad > 0.5:  # Aceptar datos con calidad > 50%
                    datos_validos.append(dato)
            
            self.logger.info(f"✅ {len(datos_validos)}/{len(datos)} datos válidos")
            return datos_validos
            
        except Exception as e:
            self.logger.error(f"Error validando datos meteorológicos: {e}")
            return []
    
    def procesar_datos_meteorologicos(self, datos: List[DatosMeteorologicos]) -> List[DatosMeteorologicos]:
        """Procesar datos meteorológicos"""
        try:
            self.logger.info("Procesando datos meteorológicos...")
            
            datos_procesados = []
            
            for dato in datos:
                # Calcular índices agrícolas
                grados_dia = max(0, dato.temperatura - 10)
                confort_termico = 1 - abs(dato.temperatura - 20) / 20 - abs(dato.humedad - 60) / 60
                confort_termico = max(0, min(1, confort_termico))
                
                # Agregar índices al dato (extender la estructura)
                dato.grados_dia = grados_dia
                dato.confort_termico = confort_termico
                
                datos_procesados.append(dato)
            
            self.logger.info(f"✅ {len(datos_procesados)} datos procesados")
            return datos_procesados
            
        except Exception as e:
            self.logger.error(f"Error procesando datos meteorológicos: {e}")
            return []
    
    def generar_predicciones_ml(self, datos: List[DatosMeteorologicos]) -> List[PrediccionML]:
        """Generar predicciones usando ML"""
        try:
            self.logger.info("Generando predicciones ML...")
            
            predicciones = []
            modelos = ['lstm', 'transformer', 'random_forest', 'gradient_boosting']
            variables = ['temperatura', 'precipitacion', 'viento_velocidad', 'humedad']
            
            # Usar los últimos datos para predicciones
            datos_recientes = datos[-24:] if len(datos) >= 24 else datos
            
            for modelo in modelos:
                for variable in variables:
                    # Simular predicción
                    if variable == 'temperatura':
                        valor_base = np.mean([d.temperatura for d in datos_recientes])
                        prediccion = valor_base + np.random.normal(0, 2)
                    elif variable == 'precipitacion':
                        valor_base = np.mean([d.precipitacion for d in datos_recientes])
                        prediccion = max(0, valor_base + np.random.normal(0, 1))
                    elif variable == 'viento_velocidad':
                        valor_base = np.mean([d.viento_velocidad for d in datos_recientes])
                        prediccion = max(0, valor_base + np.random.normal(0, 1))
                    elif variable == 'humedad':
                        valor_base = np.mean([d.humedad for d in datos_recientes])
                        prediccion = max(0, min(100, valor_base + np.random.normal(0, 5)))
                    else:
                        prediccion = np.random.uniform(0, 100)
                    
                    confianza = np.random.uniform(0.7, 0.95)
                    
                    prediccion_ml = PrediccionML(
                        timestamp=datetime.now(),
                        modelo=modelo,
                        variable=variable,
                        prediccion=prediccion,
                        confianza=confianza,
                        horizonte=24
                    )
                    
                    predicciones.append(prediccion_ml)
            
            self.logger.info(f"✅ {len(predicciones)} predicciones generadas")
            return predicciones
            
        except Exception as e:
            self.logger.error(f"Error generando predicciones ML: {e}")
            return []
    
    def evaluar_alertas(self, datos: List[DatosMeteorologicos]) -> List[Alerta]:
        """Evaluar y generar alertas"""
        try:
            self.logger.info("Evaluando alertas...")
            
            alertas = []
            
            for dato in datos:
                # Alerta de heladas
                if dato.temperatura < 0:
                    alerta = Alerta(
                        timestamp=dato.timestamp,
                        tipo="heladas",
                        nivel="critica",
                        mensaje=f"Temperatura crítica: {dato.temperatura:.1f}°C"
                    )
                    alertas.append(alerta)
                
                # Alerta de calor extremo
                elif dato.temperatura > 35:
                    alerta = Alerta(
                        timestamp=dato.timestamp,
                        tipo="calor_extremo",
                        nivel="alta",
                        mensaje=f"Temperatura extrema: {dato.temperatura:.1f}°C"
                    )
                    alertas.append(alerta)
                
                # Alerta de humedad excesiva
                if dato.humedad > 90:
                    alerta = Alerta(
                        timestamp=dato.timestamp,
                        tipo="humedad_excesiva",
                        nivel="media",
                        mensaje=f"Humedad excesiva: {dato.humedad:.1f}%"
                    )
                    alertas.append(alerta)
                
                # Alerta de viento fuerte
                if dato.viento_velocidad > 20:
                    alerta = Alerta(
                        timestamp=dato.timestamp,
                        tipo="viento_fuerte",
                        nivel="alta",
                        mensaje=f"Viento fuerte: {dato.viento_velocidad:.1f} m/s"
                    )
                    alertas.append(alerta)
            
            self.logger.info(f"✅ {len(alertas)} alertas generadas")
            return alertas
            
        except Exception as e:
            self.logger.error(f"Error evaluando alertas: {e}")
            return []
    
    def guardar_datos_bd(self, datos: List, tabla: str) -> bool:
        """Guardar datos en la base de datos"""
        try:
            if not datos:
                return True
            
            if tabla == 'datos_meteorologicos':
                for dato in datos:
                    self.cursor_bd.execute('''
                        INSERT INTO datos_meteorologicos 
                        (timestamp, temperatura, precipitacion, viento_velocidad, viento_direccion,
                         humedad, presion, radiacion_solar, punto_rocio, fuente, calidad)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        dato.timestamp, dato.temperatura, dato.precipitacion,
                        dato.viento_velocidad, dato.viento_direccion, dato.humedad,
                        dato.presion, dato.radiacion_solar, dato.punto_rocio,
                        dato.fuente, dato.calidad
                    ))
            
            elif tabla == 'datos_iot':
                for dato in datos:
                    self.cursor_bd.execute('''
                        INSERT INTO datos_iot 
                        (sensor_id, timestamp, tipo, valor, unidad, bateria, senal, ubicacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        dato.sensor_id, dato.timestamp, dato.tipo, dato.valor,
                        dato.unidad, dato.bateria, dato.senal, json.dumps(dato.ubicacion)
                    ))
            
            elif tabla == 'predicciones_ml':
                for dato in datos:
                    self.cursor_bd.execute('''
                        INSERT INTO predicciones_ml 
                        (timestamp, modelo, variable, prediccion, confianza, horizonte)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        dato.timestamp, dato.modelo, dato.variable,
                        dato.prediccion, dato.confianza, dato.horizonte
                    ))
            
            elif tabla == 'alertas':
                for dato in datos:
                    self.cursor_bd.execute('''
                        INSERT INTO alertas 
                        (timestamp, tipo, nivel, mensaje, activa)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        dato.timestamp, dato.tipo, dato.nivel, dato.mensaje, dato.activa
                    ))
            
            self.conexion_bd.commit()
            self.logger.info(f"✅ {len(datos)} registros guardados en {tabla}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando datos en {tabla}: {e}")
            return False
    
    def ejecutar_pipeline_completo(self) -> Dict:
        """Ejecutar pipeline completo de procesamiento"""
        try:
            self.logger.info("🚀 Ejecutando pipeline completo...")
            
            inicio_pipeline = datetime.now()
            self.estado_pipeline['activo'] = True
            self.estado_pipeline['procesos_activos'] = 0
            
            resultados = {
                'inicio': inicio_pipeline.isoformat(),
                'etapas': {},
                'metricas': {},
                'errores': []
            }
            
            # Etapa 1: Generar datos sintéticos
            self.logger.info("📊 Etapa 1: Generando datos sintéticos...")
            inicio_etapa = datetime.now()
            
            datos_meteorologicos = self.generar_datos_sinteticos(1000)
            datos_iot = self.generar_datos_iot_sinteticos(100)
            
            fin_etapa = datetime.now()
            duracion_etapa = (fin_etapa - inicio_etapa).total_seconds()
            
            resultados['etapas']['generacion_datos'] = {
                'estado': EstadoProcesamiento.COMPLETADO.value,
                'duracion_segundos': duracion_etapa,
                'registros_meteorologicos': len(datos_meteorologicos),
                'registros_iot': len(datos_iot)
            }
            
            # Etapa 2: Validar datos
            self.logger.info("🔍 Etapa 2: Validando datos...")
            inicio_etapa = datetime.now()
            
            datos_validos = self.validar_datos_meteorologicos(datos_meteorologicos)
            
            fin_etapa = datetime.now()
            duracion_etapa = (fin_etapa - inicio_etapa).total_seconds()
            
            resultados['etapas']['validacion'] = {
                'estado': EstadoProcesamiento.COMPLETADO.value,
                'duracion_segundos': duracion_etapa,
                'registros_validos': len(datos_validos),
                'tasa_validacion': len(datos_validos) / len(datos_meteorologicos) if datos_meteorologicos else 0
            }
            
            # Etapa 3: Procesar datos
            self.logger.info("⚙️ Etapa 3: Procesando datos...")
            inicio_etapa = datetime.now()
            
            datos_procesados = self.procesar_datos_meteorologicos(datos_validos)
            
            fin_etapa = datetime.now()
            duracion_etapa = (fin_etapa - inicio_etapa).total_seconds()
            
            resultados['etapas']['procesamiento'] = {
                'estado': EstadoProcesamiento.COMPLETADO.value,
                'duracion_segundos': duracion_etapa,
                'registros_procesados': len(datos_procesados)
            }
            
            # Etapa 4: Generar predicciones ML
            self.logger.info("🤖 Etapa 4: Generando predicciones ML...")
            inicio_etapa = datetime.now()
            
            predicciones = self.generar_predicciones_ml(datos_procesados)
            
            fin_etapa = datetime.now()
            duracion_etapa = (fin_etapa - inicio_etapa).total_seconds()
            
            resultados['etapas']['predicciones_ml'] = {
                'estado': EstadoProcesamiento.COMPLETADO.value,
                'duracion_segundos': duracion_etapa,
                'predicciones_generadas': len(predicciones)
            }
            
            # Etapa 5: Evaluar alertas
            self.logger.info("🚨 Etapa 5: Evaluando alertas...")
            inicio_etapa = datetime.now()
            
            alertas = self.evaluar_alertas(datos_procesados)
            
            fin_etapa = datetime.now()
            duracion_etapa = (fin_etapa - inicio_etapa).total_seconds()
            
            resultados['etapas']['evaluacion_alertas'] = {
                'estado': EstadoProcesamiento.COMPLETADO.value,
                'duracion_segundos': duracion_etapa,
                'alertas_generadas': len(alertas)
            }
            
            # Etapa 6: Guardar en base de datos
            self.logger.info("💾 Etapa 6: Guardando en base de datos...")
            inicio_etapa = datetime.now()
            
            guardado_meteorologicos = self.guardar_datos_bd(datos_procesados, 'datos_meteorologicos')
            guardado_iot = self.guardar_datos_bd(datos_iot, 'datos_iot')
            guardado_predicciones = self.guardar_datos_bd(predicciones, 'predicciones_ml')
            guardado_alertas = self.guardar_datos_bd(alertas, 'alertas')
            
            fin_etapa = datetime.now()
            duracion_etapa = (fin_etapa - inicio_etapa).total_seconds()
            
            resultados['etapas']['guardado_bd'] = {
                'estado': EstadoProcesamiento.COMPLETADO.value,
                'duracion_segundos': duracion_etapa,
                'meteorologicos_guardados': guardado_meteorologicos,
                'iot_guardados': guardado_iot,
                'predicciones_guardadas': guardado_predicciones,
                'alertas_guardadas': guardado_alertas
            }
            
            # Finalizar pipeline
            fin_pipeline = datetime.now()
            duracion_total = (fin_pipeline - inicio_pipeline).total_seconds()
            
            resultados['fin'] = fin_pipeline.isoformat()
            resultados['duracion_total_segundos'] = duracion_total
            resultados['estado'] = EstadoProcesamiento.COMPLETADO.value
            
            # Actualizar estado del pipeline
            self.estado_pipeline['activo'] = False
            self.estado_pipeline['ultima_ejecucion'] = fin_pipeline.isoformat()
            self.estado_pipeline['metricas'] = {
                'duracion_total': duracion_total,
                'etapas_completadas': len(resultados['etapas']),
                'registros_procesados': len(datos_procesados),
                'predicciones_generadas': len(predicciones),
                'alertas_generadas': len(alertas)
            }
            
            self.logger.info(f"✅ Pipeline completo ejecutado en {duracion_total:.2f} segundos")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error ejecutando pipeline completo: {e}")
            self.estado_pipeline['activo'] = False
            self.estado_pipeline['errores'].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            })
            return {'error': str(e)}
    
    def obtener_metricas_pipeline(self) -> Dict:
        """Obtener métricas del pipeline"""
        try:
            # Consultar métricas de la base de datos
            self.cursor_bd.execute('''
                SELECT COUNT(*) as total_datos FROM datos_meteorologicos
            ''')
            total_datos = self.cursor_bd.fetchone()[0]
            
            self.cursor_bd.execute('''
                SELECT COUNT(*) as total_iot FROM datos_iot
            ''')
            total_iot = self.cursor_bd.fetchone()[0]
            
            self.cursor_bd.execute('''
                SELECT COUNT(*) as total_predicciones FROM predicciones_ml
            ''')
            total_predicciones = self.cursor_bd.fetchone()[0]
            
            self.cursor_bd.execute('''
                SELECT COUNT(*) as total_alertas FROM alertas WHERE activa = 1
            ''')
            total_alertas = self.cursor_bd.fetchone()[0]
            
            return {
                'timestamp': datetime.now().isoformat(),
                'estado_pipeline': self.estado_pipeline,
                'metricas_bd': {
                    'total_datos_meteorologicos': total_datos,
                    'total_datos_iot': total_iot,
                    'total_predicciones': total_predicciones,
                    'total_alertas_activas': total_alertas
                },
                'configuracion': self.configuracion_pipeline
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas: {e}")
            return {}
    
    def generar_reporte_pipeline(self) -> str:
        """Generar reporte del pipeline"""
        try:
            self.logger.info("📋 Generando reporte del pipeline...")
            
            metricas = self.obtener_metricas_pipeline()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Pipeline Completo',
                'version': self.configuracion['version'],
                'resumen': {
                    'pipeline_activo': self.estado_pipeline['activo'],
                    'ultima_ejecucion': self.estado_pipeline.get('ultima_ejecucion'),
                    'total_errores': len(self.estado_pipeline.get('errores', [])),
                    'metricas': self.estado_pipeline.get('metricas', {})
                },
                'metricas': metricas,
                'configuracion': self.configuracion_pipeline,
                'recomendaciones': [
                    "Monitorear regularmente el rendimiento del pipeline",
                    "Optimizar la frecuencia de procesamiento según la carga",
                    "Implementar alertas para fallos del pipeline",
                    "Mantener respaldos de la base de datos",
                    "Revisar y limpiar datos antiguos periódicamente"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"pipeline_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Reporte del pipeline generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""
    
    def cerrar_pipeline(self):
        """Cerrar pipeline y limpiar recursos"""
        try:
            self.logger.info("🛑 Cerrando pipeline...")
            
            # Detener hilos
            self.detener_hilos.set()
            
            # Cerrar base de datos
            if hasattr(self, 'conexion_bd'):
                self.conexion_bd.close()
            
            # Limpiar cache
            self.cache_datos.clear()
            self.cache_predicciones.clear()
            
            self.logger.info("✅ Pipeline cerrado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error cerrando pipeline: {e}")

def main():
    """Función principal del pipeline completo"""
    print("🔄 PIPELINE COMPLETO METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Pipeline Integrado de Datos")
    print("=" * 80)
    
    try:
        # Crear pipeline
        pipeline = PipelineCompletoMETGO()
        
        # Ejecutar pipeline completo
        print(f"\n🚀 Ejecutando pipeline completo...")
        resultados = pipeline.ejecutar_pipeline_completo()
        
        if 'error' in resultados:
            print(f"\n❌ Error en pipeline: {resultados['error']}")
            return False
        
        # Mostrar resultados
        print(f"\n📊 Resultados del pipeline:")
        print(f"   Duración total: {resultados.get('duracion_total_segundos', 0):.2f} segundos")
        print(f"   Etapas completadas: {len(resultados.get('etapas', {}))}")
        
        for etapa, info in resultados.get('etapas', {}).items():
            print(f"   - {etapa}: {info.get('duracion_segundos', 0):.2f}s")
        
        # Obtener métricas
        print(f"\n📈 Métricas del pipeline:")
        metricas = pipeline.obtener_metricas_pipeline()
        if metricas:
            print(f"   Datos meteorológicos: {metricas.get('metricas_bd', {}).get('total_datos_meteorologicos', 0)}")
            print(f"   Datos IoT: {metricas.get('metricas_bd', {}).get('total_datos_iot', 0)}")
            print(f"   Predicciones: {metricas.get('metricas_bd', {}).get('total_predicciones', 0)}")
            print(f"   Alertas activas: {metricas.get('metricas_bd', {}).get('total_alertas_activas', 0)}")
        
        # Generar reporte
        print(f"\n📋 Generando reporte...")
        reporte = pipeline.generar_reporte_pipeline()
        
        if reporte:
            print(f"\n✅ Pipeline completo ejecutado exitosamente")
            print(f"📄 Reporte generado: {reporte}")
        else:
            print(f"\n⚠️ Error generando reporte")
        
        # Cerrar pipeline
        pipeline.cerrar_pipeline()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en pipeline completo: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

