#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
💧 RIEGO AUTOMATIZADO METGO 3D
Sistema Meteorológico Agrícola Quillota - Sistema de Riego Automatizado
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

# Flask para API del sistema de riego
try:
    from flask import Flask, request, jsonify, render_template
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Configuración
warnings.filterwarnings('ignore')

@dataclass
class SensorRiego:
    """Sensor de riego"""
    id: str
    nombre: str
    tipo: str
    ubicacion: Tuple[float, float]
    estado: str
    ultima_lectura: str
    valor: float
    unidad: str
    configuracion: Dict[str, Any]

@dataclass
class ControladorRiego:
    """Controlador de riego"""
    id: str
    nombre: str
    tipo: str
    ubicacion: Tuple[float, float]
    estado: str
    programacion: Dict[str, Any]
    configuracion: Dict[str, Any]
    historial: List[Dict[str, Any]]

@dataclass
class ProgramacionRiego:
    """Programación de riego"""
    id: str
    nombre: str
    controlador_id: str
    horario_inicio: str
    duracion_minutos: int
    dias_semana: List[int]
    activa: bool
    condiciones: Dict[str, Any]

class RiegoAutomatizadoMETGO:
    """Sistema de riego automatizado para METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/riego',
            'directorio_logs': 'logs/riego',
            'directorio_reportes': 'reportes/riego',
            'directorio_configuracion': 'config/riego',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Configuración del sistema
        self.configuracion_sistema = {
            'modo_automatico': True,
            'intervalo_lectura': 300,  # 5 minutos
            'umbral_humedad': 30,  # %
            'umbral_temperatura': 25,  # °C
            'tiempo_riego_minimo': 10,  # minutos
            'tiempo_riego_maximo': 120,  # minutos
            'horario_riego_inicio': '06:00',
            'horario_riego_fin': '18:00',
            'dias_riego': [0, 1, 2, 3, 4, 5, 6],  # Todos los días
            'notificaciones': True
        }
        
        # Sensores y controladores
        self.sensores = {}
        self.controladores = {}
        self.programaciones = {}
        
        # Estado del sistema
        self.estado_sistema = {
            'activo': True,
            'modo_manual': False,
            'ultima_actualizacion': datetime.now().isoformat(),
            'alertas_activas': []
        }
        
        # Configurar sensores y controladores
        self._configurar_sensores()
        self._configurar_controladores()
        self._configurar_programaciones()
    
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
                    logging.FileHandler(f"{self.configuracion['directorio_logs']}/riego.log"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('METGO_RIEGO')
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/riego.db"
            
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
            # Tabla de sensores
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS sensores_riego (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    ubicacion TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    ultima_lectura DATETIME,
                    valor REAL NOT NULL,
                    unidad TEXT NOT NULL,
                    configuracion TEXT,
                    activo BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Tabla de controladores
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS controladores_riego (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    ubicacion TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    programacion TEXT,
                    configuracion TEXT,
                    activo BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Tabla de programaciones
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS programaciones_riego (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    controlador_id TEXT NOT NULL,
                    horario_inicio TEXT NOT NULL,
                    duracion_minutos INTEGER NOT NULL,
                    dias_semana TEXT NOT NULL,
                    activa BOOLEAN DEFAULT TRUE,
                    condiciones TEXT,
                    FOREIGN KEY (controlador_id) REFERENCES controladores_riego (id)
                )
            ''')
            
            # Tabla de eventos de riego
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS eventos_riego (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    controlador_id TEXT NOT NULL,
                    tipo_evento TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duracion_minutos INTEGER,
                    volumen_litros REAL,
                    estado TEXT NOT NULL,
                    observaciones TEXT,
                    FOREIGN KEY (controlador_id) REFERENCES controladores_riego (id)
                )
            ''')
            
            # Tabla de lecturas de sensores
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS lecturas_sensores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    valor REAL NOT NULL,
                    unidad TEXT NOT NULL,
                    calidad_datos REAL,
                    FOREIGN KEY (sensor_id) REFERENCES sensores_riego (id)
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_sensores_activo ON sensores_riego(activo)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_controladores_activo ON controladores_riego(activo)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_programaciones_activa ON programaciones_riego(activa)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_eventos_controlador ON eventos_riego(controlador_id)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_lecturas_sensor ON lecturas_sensores(sensor_id)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def _configurar_sensores(self):
        """Configurar sensores del sistema"""
        try:
            sensores_data = [
                {
                    'id': 'sensor_humedad_1',
                    'nombre': 'Sensor de Humedad 1',
                    'tipo': 'humedad_suelo',
                    'ubicacion': (-32.8833, -71.2333),
                    'estado': 'activo',
                    'valor': 45.0,
                    'unidad': '%',
                    'configuracion': {
                        'rango_min': 0,
                        'rango_max': 100,
                        'precision': 0.1,
                        'intervalo_lectura': 300
                    }
                },
                {
                    'id': 'sensor_temperatura_1',
                    'nombre': 'Sensor de Temperatura 1',
                    'tipo': 'temperatura_suelo',
                    'ubicacion': (-32.8833, -71.2333),
                    'estado': 'activo',
                    'valor': 18.5,
                    'unidad': '°C',
                    'configuracion': {
                        'rango_min': -10,
                        'rango_max': 50,
                        'precision': 0.1,
                        'intervalo_lectura': 300
                    }
                },
                {
                    'id': 'sensor_presion_1',
                    'nombre': 'Sensor de Presión 1',
                    'tipo': 'presion_agua',
                    'ubicacion': (-32.8833, -71.2333),
                    'estado': 'activo',
                    'valor': 2.5,
                    'unidad': 'bar',
                    'configuracion': {
                        'rango_min': 0,
                        'rango_max': 10,
                        'precision': 0.01,
                        'intervalo_lectura': 300
                    }
                }
            ]
            
            for sensor_data in sensores_data:
                sensor = SensorRiego(
                    id=sensor_data['id'],
                    nombre=sensor_data['nombre'],
                    tipo=sensor_data['tipo'],
                    ubicacion=sensor_data['ubicacion'],
                    estado=sensor_data['estado'],
                    ultima_lectura=datetime.now().isoformat(),
                    valor=sensor_data['valor'],
                    unidad=sensor_data['unidad'],
                    configuracion=sensor_data['configuracion']
                )
                self.sensores[sensor.id] = sensor
            
            self.logger.info(f"Sensores configurados: {len(self.sensores)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando sensores: {e}")
    
    def _configurar_controladores(self):
        """Configurar controladores de riego"""
        try:
            controladores_data = [
                {
                    'id': 'controlador_1',
                    'nombre': 'Controlador Principal',
                    'tipo': 'aspersion',
                    'ubicacion': (-32.8833, -71.2333),
                    'estado': 'activo',
                    'programacion': {
                        'modo': 'automatico',
                        'horario_inicio': '06:00',
                        'horario_fin': '18:00',
                        'duracion_maxima': 120
                    },
                    'configuracion': {
                        'caudal_litros_minuto': 50,
                        'presion_trabajo': 2.5,
                        'radio_cobertura': 15,
                        'eficiencia': 0.85
                    }
                },
                {
                    'id': 'controlador_2',
                    'nombre': 'Controlador Secundario',
                    'tipo': 'goteo',
                    'ubicacion': (-32.8833, -71.2333),
                    'estado': 'activo',
                    'programacion': {
                        'modo': 'automatico',
                        'horario_inicio': '06:00',
                        'horario_fin': '18:00',
                        'duracion_maxima': 180
                    },
                    'configuracion': {
                        'caudal_litros_minuto': 20,
                        'presion_trabajo': 1.5,
                        'radio_cobertura': 5,
                        'eficiencia': 0.95
                    }
                }
            ]
            
            for controlador_data in controladores_data:
                controlador = ControladorRiego(
                    id=controlador_data['id'],
                    nombre=controlador_data['nombre'],
                    tipo=controlador_data['tipo'],
                    ubicacion=controlador_data['ubicacion'],
                    estado=controlador_data['estado'],
                    programacion=controlador_data['programacion'],
                    configuracion=controlador_data['configuracion'],
                    historial=[]
                )
                self.controladores[controlador.id] = controlador
            
            self.logger.info(f"Controladores configurados: {len(self.controladores)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando controladores: {e}")
    
    def _configurar_programaciones(self):
        """Configurar programaciones de riego"""
        try:
            programaciones_data = [
                {
                    'id': 'programacion_1',
                    'nombre': 'Riego Matutino',
                    'controlador_id': 'controlador_1',
                    'horario_inicio': '06:00',
                    'duracion_minutos': 30,
                    'dias_semana': [0, 1, 2, 3, 4, 5, 6],
                    'activa': True,
                    'condiciones': {
                        'humedad_minima': 30,
                        'temperatura_maxima': 30,
                        'precipitacion_maxima': 5
                    }
                },
                {
                    'id': 'programacion_2',
                    'nombre': 'Riego Vespertino',
                    'controlador_id': 'controlador_2',
                    'horario_inicio': '18:00',
                    'duracion_minutos': 45,
                    'dias_semana': [0, 1, 2, 3, 4, 5, 6],
                    'activa': True,
                    'condiciones': {
                        'humedad_minima': 25,
                        'temperatura_maxima': 35,
                        'precipitacion_maxima': 3
                    }
                }
            ]
            
            for programacion_data in programaciones_data:
                programacion = ProgramacionRiego(
                    id=programacion_data['id'],
                    nombre=programacion_data['nombre'],
                    controlador_id=programacion_data['controlador_id'],
                    horario_inicio=programacion_data['horario_inicio'],
                    duracion_minutos=programacion_data['duracion_minutos'],
                    dias_semana=programacion_data['dias_semana'],
                    activa=programacion_data['activa'],
                    condiciones=programacion_data['condiciones']
                )
                self.programaciones[programacion.id] = programacion
            
            self.logger.info(f"Programaciones configuradas: {len(self.programaciones)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando programaciones: {e}")
    
    def leer_sensores(self) -> Dict[str, Any]:
        """Leer valores de todos los sensores"""
        try:
            self.logger.info("Leyendo sensores...")
            
            lecturas = {}
            
            for sensor_id, sensor in self.sensores.items():
                if sensor.estado == 'activo':
                    # Simular lectura del sensor
                    valor_anterior = sensor.valor
                    
                    # Generar variación realista
                    if sensor.tipo == 'humedad_suelo':
                        variacion = np.random.randn() * 2
                        nuevo_valor = max(0, min(100, valor_anterior + variacion))
                    elif sensor.tipo == 'temperatura_suelo':
                        variacion = np.random.randn() * 1
                        nuevo_valor = max(-10, min(50, valor_anterior + variacion))
                    elif sensor.tipo == 'presion_agua':
                        variacion = np.random.randn() * 0.1
                        nuevo_valor = max(0, min(10, valor_anterior + variacion))
                    else:
                        variacion = np.random.randn() * 0.5
                        nuevo_valor = valor_anterior + variacion
                    
                    # Actualizar sensor
                    sensor.valor = nuevo_valor
                    sensor.ultima_lectura = datetime.now().isoformat()
                    
                    # Guardar lectura en base de datos
                    self._guardar_lectura_sensor(sensor_id, nuevo_valor, sensor.unidad)
                    
                    lecturas[sensor_id] = {
                        'valor': nuevo_valor,
                        'unidad': sensor.unidad,
                        'timestamp': sensor.ultima_lectura,
                        'calidad': 0.95 + np.random.rand() * 0.05
                    }
            
            self.logger.info(f"Lecturas completadas: {len(lecturas)} sensores")
            return lecturas
            
        except Exception as e:
            self.logger.error(f"Error leyendo sensores: {e}")
            return {}
    
    def _guardar_lectura_sensor(self, sensor_id: str, valor: float, unidad: str):
        """Guardar lectura de sensor en base de datos"""
        try:
            self.cursor_bd.execute('''
                INSERT INTO lecturas_sensores 
                (sensor_id, timestamp, valor, unidad, calidad_datos)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                sensor_id,
                datetime.now().isoformat(),
                valor,
                unidad,
                0.95 + np.random.rand() * 0.05
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error guardando lectura de sensor: {e}")
    
    def evaluar_condiciones_riego(self) -> Dict[str, Any]:
        """Evaluar condiciones para activar riego"""
        try:
            self.logger.info("Evaluando condiciones de riego...")
            
            # Leer sensores
            lecturas = self.leer_sensores()
            
            # Obtener datos meteorológicos (simulados)
            datos_meteorologicos = self._obtener_datos_meteorologicos()
            
            # Evaluar condiciones
            condiciones = {
                'humedad_suelo': lecturas.get('sensor_humedad_1', {}).get('valor', 50),
                'temperatura_suelo': lecturas.get('sensor_temperatura_1', {}).get('valor', 20),
                'presion_agua': lecturas.get('sensor_presion_1', {}).get('valor', 2.5),
                'temperatura_aire': datos_meteorologicos.get('temperatura', 22),
                'humedad_aire': datos_meteorologicos.get('humedad', 60),
                'precipitacion': datos_meteorologicos.get('precipitacion', 0),
                'viento': datos_meteorologicos.get('viento', 5)
            }
            
            # Evaluar si se debe regar
            debe_regar = self._debe_regar(condiciones)
            
            # Calcular duración de riego
            duracion_riego = self._calcular_duracion_riego(condiciones)
            
            # Determinar controladores a activar
            controladores_activar = self._determinar_controladores(condiciones)
            
            resultado = {
                'debe_regar': debe_regar,
                'duracion_minutos': duracion_riego,
                'controladores': controladores_activar,
                'condiciones': condiciones,
                'timestamp': datetime.now().isoformat(),
                'razon': self._obtener_razon_riego(condiciones, debe_regar)
            }
            
            self.logger.info(f"Evaluación completada - Debe regar: {debe_regar}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error evaluando condiciones de riego: {e}")
            return {'debe_regar': False, 'error': str(e)}
    
    def _obtener_datos_meteorologicos(self) -> Dict[str, float]:
        """Obtener datos meteorológicos (simulados)"""
        try:
            np.random.seed(42)
            
            return {
                'temperatura': 20 + np.random.randn() * 5,
                'humedad': 60 + np.random.randn() * 15,
                'precipitacion': max(0, np.random.randn() * 3),
                'viento': 5 + np.random.randn() * 2,
                'presion': 1013 + np.random.randn() * 10,
                'radiacion': 300 + np.random.randn() * 100
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos meteorológicos: {e}")
            return {}
    
    def _debe_regar(self, condiciones: Dict[str, float]) -> bool:
        """Determinar si se debe regar basado en las condiciones"""
        try:
            # Condiciones para regar
            humedad_suelo = condiciones.get('humedad_suelo', 50)
            temperatura_aire = condiciones.get('temperatura_aire', 22)
            precipitacion = condiciones.get('precipitacion', 0)
            viento = condiciones.get('viento', 5)
            
            # Lógica de decisión
            if humedad_suelo < self.configuracion_sistema['umbral_humedad']:
                if precipitacion < 5:  # No lloviendo
                    if viento < 15:  # No hay viento fuerte
                        if 6 <= datetime.now().hour <= 18:  # Horario permitido
                            return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error determinando si debe regar: {e}")
            return False
    
    def _calcular_duracion_riego(self, condiciones: Dict[str, float]) -> int:
        """Calcular duración del riego en minutos"""
        try:
            humedad_suelo = condiciones.get('humedad_suelo', 50)
            temperatura_aire = condiciones.get('temperatura_aire', 22)
            
            # Duración base
            duracion_base = 30
            
            # Ajustar según humedad
            if humedad_suelo < 20:
                duracion_base += 30
            elif humedad_suelo < 30:
                duracion_base += 15
            
            # Ajustar según temperatura
            if temperatura_aire > 30:
                duracion_base += 15
            elif temperatura_aire > 25:
                duracion_base += 10
            
            # Limitar duración
            duracion_final = max(
                self.configuracion_sistema['tiempo_riego_minimo'],
                min(duracion_base, self.configuracion_sistema['tiempo_riego_maximo'])
            )
            
            return int(duracion_final)
            
        except Exception as e:
            self.logger.error(f"Error calculando duración de riego: {e}")
            return 30
    
    def _determinar_controladores(self, condiciones: Dict[str, float]) -> List[str]:
        """Determinar qué controladores activar"""
        try:
            controladores = []
            
            # Activar controladores según condiciones
            for controlador_id, controlador in self.controladores.items():
                if controlador.estado == 'activo':
                    # Lógica para determinar si activar cada controlador
                    if controlador.tipo == 'aspersion':
                        if condiciones.get('temperatura_aire', 22) > 25:
                            controladores.append(controlador_id)
                    elif controlador.tipo == 'goteo':
                        if condiciones.get('humedad_suelo', 50) < 40:
                            controladores.append(controlador_id)
            
            return controladores
            
        except Exception as e:
            self.logger.error(f"Error determinando controladores: {e}")
            return []
    
    def _obtener_razon_riego(self, condiciones: Dict[str, float], debe_regar: bool) -> str:
        """Obtener razón para la decisión de riego"""
        try:
            if debe_regar:
                humedad_suelo = condiciones.get('humedad_suelo', 50)
                if humedad_suelo < 20:
                    return "Humedad del suelo muy baja - riego de emergencia"
                elif humedad_suelo < 30:
                    return "Humedad del suelo baja - riego programado"
                else:
                    return "Condiciones favorables para riego"
            else:
                humedad_suelo = condiciones.get('humedad_suelo', 50)
                if humedad_suelo >= 50:
                    return "Humedad del suelo adecuada"
                elif condiciones.get('precipitacion', 0) > 5:
                    return "Precipitación activa - riego suspendido"
                elif condiciones.get('viento', 5) > 15:
                    return "Viento fuerte - riego suspendido"
                else:
                    return "Condiciones no favorables para riego"
                    
        except Exception as e:
            self.logger.error(f"Error obteniendo razón de riego: {e}")
            return "Error en evaluación"
    
    def ejecutar_riego(self, controlador_id: str, duracion_minutos: int) -> Dict[str, Any]:
        """Ejecutar riego con un controlador específico"""
        try:
            self.logger.info(f"Ejecutando riego - Controlador: {controlador_id}, Duración: {duracion_minutos} min")
            
            if controlador_id not in self.controladores:
                return {'exitoso': False, 'error': 'Controlador no encontrado'}
            
            controlador = self.controladores[controlador_id]
            
            if controlador.estado != 'activo':
                return {'exitoso': False, 'error': 'Controlador no activo'}
            
            # Calcular volumen de agua
            caudal = controlador.configuracion.get('caudal_litros_minuto', 50)
            volumen_litros = caudal * duracion_minutos
            
            # Simular ejecución de riego
            evento_riego = {
                'controlador_id': controlador_id,
                'tipo_evento': 'riego_automatico',
                'timestamp': datetime.now().isoformat(),
                'duracion_minutos': duracion_minutos,
                'volumen_litros': volumen_litros,
                'estado': 'en_progreso',
                'observaciones': f'Riego automático iniciado'
            }
            
            # Guardar evento en base de datos
            self._guardar_evento_riego(evento_riego)
            
            # Simular progreso del riego
            self._simular_progreso_riego(controlador_id, duracion_minutos)
            
            # Actualizar estado del controlador
            controlador.historial.append(evento_riego)
            
            return {
                'exitoso': True,
                'controlador_id': controlador_id,
                'duracion_minutos': duracion_minutos,
                'volumen_litros': volumen_litros,
                'timestamp': evento_riego['timestamp'],
                'estado': 'completado'
            }
            
        except Exception as e:
            self.logger.error(f"Error ejecutando riego: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def _simular_progreso_riego(self, controlador_id: str, duracion_minutos: int):
        """Simular progreso del riego"""
        try:
            # Simular progreso cada minuto
            for minuto in range(duracion_minutos):
                time.sleep(0.1)  # Simular tiempo real
                
                # Actualizar progreso
                progreso = (minuto + 1) / duracion_minutos * 100
                
                if minuto % 5 == 0:  # Log cada 5 minutos
                    self.logger.info(f"Riego {controlador_id} - Progreso: {progreso:.1f}%")
            
            # Marcar como completado
            self.logger.info(f"Riego {controlador_id} completado")
            
        except Exception as e:
            self.logger.error(f"Error simulando progreso de riego: {e}")
    
    def _guardar_evento_riego(self, evento: Dict[str, Any]):
        """Guardar evento de riego en base de datos"""
        try:
            self.cursor_bd.execute('''
                INSERT INTO eventos_riego 
                (controlador_id, tipo_evento, timestamp, duracion_minutos, volumen_litros, estado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                evento['controlador_id'],
                evento['tipo_evento'],
                evento['timestamp'],
                evento['duracion_minutos'],
                evento['volumen_litros'],
                evento['estado'],
                evento['observaciones']
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error guardando evento de riego: {e}")
    
    def obtener_estadisticas_riego(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de riego"""
        try:
            # Estadísticas de sensores
            sensores_activos = sum(1 for s in self.sensores.values() if s.estado == 'activo')
            
            # Estadísticas de controladores
            controladores_activos = sum(1 for c in self.controladores.values() if c.estado == 'activo')
            
            # Estadísticas de eventos de riego
            self.cursor_bd.execute('''
                SELECT COUNT(*) as total_eventos,
                       SUM(duracion_minutos) as total_minutos,
                       SUM(volumen_litros) as total_litros
                FROM eventos_riego 
                WHERE DATE(timestamp) = DATE('now')
            ''')
            stats_diarias = self.cursor_bd.fetchone()
            
            # Estadísticas semanales
            self.cursor_bd.execute('''
                SELECT COUNT(*) as total_eventos,
                       SUM(duracion_minutos) as total_minutos,
                       SUM(volumen_litros) as total_litros
                FROM eventos_riego 
                WHERE DATE(timestamp) >= DATE('now', '-7 days')
            ''')
            stats_semanales = self.cursor_bd.fetchone()
            
            return {
                'sensores': {
                    'total': len(self.sensores),
                    'activos': sensores_activos,
                    'inactivos': len(self.sensores) - sensores_activos
                },
                'controladores': {
                    'total': len(self.controladores),
                    'activos': controladores_activos,
                    'inactivos': len(self.controladores) - controladores_activos
                },
                'programaciones': {
                    'total': len(self.programaciones),
                    'activas': sum(1 for p in self.programaciones.values() if p.activa)
                },
                'riego_diario': {
                    'eventos': stats_diarias[0] or 0,
                    'minutos': stats_diarias[1] or 0,
                    'litros': stats_diarias[2] or 0
                },
                'riego_semanal': {
                    'eventos': stats_semanales[0] or 0,
                    'minutos': stats_semanales[1] or 0,
                    'litros': stats_semanales[2] or 0
                },
                'sistema': {
                    'activo': self.estado_sistema['activo'],
                    'modo_manual': self.estado_sistema['modo_manual'],
                    'ultima_actualizacion': self.estado_sistema['ultima_actualizacion']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def generar_reporte_riego(self) -> str:
        """Generar reporte del sistema de riego"""
        try:
            self.logger.info("Generando reporte del sistema de riego...")
            
            # Obtener estadísticas
            estadisticas = self.obtener_estadisticas_riego()
            
            # Evaluar condiciones actuales
            condiciones_actuales = self.evaluar_condiciones_riego()
            
            # Leer sensores
            lecturas_sensores = self.leer_sensores()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema de Riego Automatizado',
                'version': self.configuracion['version'],
                'configuracion_sistema': self.configuracion_sistema,
                'estadisticas': estadisticas,
                'condiciones_actuales': condiciones_actuales,
                'lecturas_sensores': lecturas_sensores,
                'sensores': [
                    {
                        'id': s.id,
                        'nombre': s.nombre,
                        'tipo': s.tipo,
                        'estado': s.estado,
                        'valor': s.valor,
                        'unidad': s.unidad,
                        'ultima_lectura': s.ultima_lectura
                    } for s in self.sensores.values()
                ],
                'controladores': [
                    {
                        'id': c.id,
                        'nombre': c.nombre,
                        'tipo': c.tipo,
                        'estado': c.estado,
                        'configuracion': c.configuracion
                    } for c in self.controladores.values()
                ],
                'programaciones': [
                    {
                        'id': p.id,
                        'nombre': p.nombre,
                        'controlador_id': p.controlador_id,
                        'horario_inicio': p.horario_inicio,
                        'duracion_minutos': p.duracion_minutos,
                        'activa': p.activa
                    } for p in self.programaciones.values()
                ],
                'funcionalidades_implementadas': [
                    'Sistema de sensores inteligentes',
                    'Controladores de riego automatizados',
                    'Programación flexible de riego',
                    'Evaluación automática de condiciones',
                    'Base de datos SQLite para almacenamiento',
                    'Sistema de logging estructurado',
                    'Estadísticas en tiempo real',
                    'Simulación de riego',
                    'Gestión de eventos',
                    'Monitoreo continuo'
                ],
                'tecnologias_utilizadas': [
                    'SQLite para base de datos',
                    'NumPy para cálculos',
                    'Pandas para análisis de datos',
                    'Flask para API REST',
                    'Logging estructurado',
                    'Simulación de hardware'
                ],
                'recomendaciones': [
                    'Integrar con sensores reales de humedad',
                    'Implementar controladores físicos',
                    'Agregar sistema de alertas por email/SMS',
                    'Implementar programación por zonas',
                    'Agregar análisis de eficiencia hídrica',
                    'Implementar backup automático',
                    'Agregar interfaz web para monitoreo',
                    'Implementar machine learning para optimización',
                    'Agregar integración con pronósticos meteorológicos',
                    'Implementar sistema de mantenimiento predictivo'
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"riego_automatizado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte del sistema de riego generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal del sistema de riego automatizado"""
    print("RIEGO AUTOMATIZADO METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Sistema de Riego Automatizado")
    print("=" * 80)
    
    try:
        # Crear sistema de riego
        riego_sistema = RiegoAutomatizadoMETGO()
        
        # Generar reporte
        print(f"\nGenerando reporte del sistema...")
        reporte = riego_sistema.generar_reporte_riego()
        
        if reporte:
            print(f"Reporte generado: {reporte}")
        else:
            print(f"Error generando reporte")
        
        # Mostrar información del sistema
        print(f"\nSistema de Riego Automatizado METGO 3D")
        print(f"Version: {riego_sistema.configuracion['version']}")
        print(f"Modo automatico: {riego_sistema.configuracion_sistema['modo_automatico']}")
        print(f"Intervalo de lectura: {riego_sistema.configuracion_sistema['intervalo_lectura']} segundos")
        
        print(f"\nSensores configurados:")
        for sensor_id, sensor in riego_sistema.sensores.items():
            print(f"   - {sensor.nombre} ({sensor.tipo}): {sensor.valor} {sensor.unidad}")
        
        print(f"\nControladores configurados:")
        for controlador_id, controlador in riego_sistema.controladores.items():
            print(f"   - {controlador.nombre} ({controlador.tipo}): {controlador.estado}")
        
        print(f"\nProgramaciones configuradas:")
        for programacion_id, programacion in riego_sistema.programaciones.items():
            print(f"   - {programacion.nombre}: {programacion.horario_inicio} ({programacion.duracion_minutos} min)")
        
        # Demostrar evaluación de condiciones
        print(f"\nEvaluando condiciones de riego...")
        condiciones = riego_sistema.evaluar_condiciones_riego()
        
        print(f"Debe regar: {condiciones.get('debe_regar', False)}")
        print(f"Duracion recomendada: {condiciones.get('duracion_minutos', 0)} minutos")
        print(f"Controladores a activar: {condiciones.get('controladores', [])}")
        print(f"Razon: {condiciones.get('razon', 'N/A')}")
        
        # Mostrar estadísticas
        estadisticas = riego_sistema.obtener_estadisticas_riego()
        if estadisticas:
            print(f"\nEstadisticas del sistema:")
            print(f"   Sensores activos: {estadisticas.get('sensores', {}).get('activos', 0)}")
            print(f"   Controladores activos: {estadisticas.get('controladores', {}).get('activos', 0)}")
            print(f"   Programaciones activas: {estadisticas.get('programaciones', {}).get('activas', 0)}")
            print(f"   Riego diario: {estadisticas.get('riego_diario', {}).get('litros', 0)} litros")
        
        return True
        
    except Exception as e:
        print(f"\nError en sistema de riego: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
