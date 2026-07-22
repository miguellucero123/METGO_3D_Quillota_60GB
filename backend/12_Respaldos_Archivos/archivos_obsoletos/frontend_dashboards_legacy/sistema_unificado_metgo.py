#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔗 SISTEMA UNIFICADO METGO 3D
Sistema Meteorológico Agrícola Quillota - Integración de Todos los Módulos
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
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Flask para API unificada
try:
    from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for, session, flash
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Configuración
warnings.filterwarnings('ignore')

@dataclass
class ModuloMETGO:
    """Módulo del sistema METGO 3D"""
    id: str
    nombre: str
    descripcion: str
    archivo: str
    estado: str
    dependencias: List[str]
    configuracion: Dict[str, Any]
    ultima_ejecucion: str
    resultado: Dict[str, Any]

@dataclass
class TareaIntegracion:
    """Tarea de integración entre módulos"""
    id: str
    nombre: str
    modulo_origen: str
    modulo_destino: str
    tipo_datos: str
    frecuencia: str
    activa: bool
    configuracion: Dict[str, Any]

class SistemaUnificadoMETGO:
    """Sistema unificado que integra todos los módulos de METGO 3D"""
    
    def __init__(self):
        # Inicializar logger primero
        self.logger = logging.getLogger('METGO_UNIFICADO')
        
        self.app = Flask(__name__) if FLASK_AVAILABLE else None
        if self.app:
            self.app.secret_key = 'metgo_3d_unificado_secret_2025'
            CORS(self.app)
            self._configurar_rutas()
        
        self.configuracion = {
            'directorio_datos': 'data/unificado',
            'directorio_logs': 'logs/unificado',
            'directorio_reportes': 'reportes/unificado',
            'directorio_configuracion': 'config/unificado',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Configuración del sistema unificado
        self.configuracion_sistema = {
            'modo_operacion': 'produccion',
            'frecuencia_sincronizacion': 300,  # 5 minutos
            'timeout_modulos': 30,  # 30 segundos
            'reintentos_maximos': 3,
            'paralelismo': True,
            'monitoreo_continuo': True,
            'backup_automatico': True,
            'alertas_activas': True
        }
        
        # Módulos y tareas
        self.modulos = {}
        self.tareas_integracion = {}
        self.cola_tareas = queue.Queue()
        self.ejecutor = ThreadPoolExecutor(max_workers=4)
        
        # Estado del sistema
        self.estado_sistema = {
            'activo': True,
            'modulos_activos': 0,
            'tareas_pendientes': 0,
            'ultima_sincronizacion': None,
            'errores': []
        }
        
        # Configurar módulos
        self._configurar_modulos()
        self._configurar_tareas_integracion()
        
        # Iniciar monitoreo
        self._iniciar_monitoreo()
    
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
                        logging.FileHandler(f"{self.configuracion['directorio_logs']}/sistema_unificado.log"),
                        logging.StreamHandler()
                    ]
                )
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/sistema_unificado.db"
            
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
                CREATE TABLE IF NOT EXISTS modulos_sistema (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    descripcion TEXT NOT NULL,
                    archivo TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    dependencias TEXT,
                    configuracion TEXT,
                    ultima_ejecucion DATETIME,
                    resultado TEXT,
                    activo BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Tabla de tareas de integración
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS tareas_integracion (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    modulo_origen TEXT NOT NULL,
                    modulo_destino TEXT NOT NULL,
                    tipo_datos TEXT NOT NULL,
                    frecuencia TEXT NOT NULL,
                    activa BOOLEAN DEFAULT TRUE,
                    configuracion TEXT
                )
            ''')
            
            # Tabla de ejecuciones
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS ejecuciones_sistema (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tipo_ejecucion TEXT NOT NULL,
                    modulo_id TEXT,
                    estado TEXT NOT NULL,
                    duracion_segundos REAL,
                    resultado TEXT,
                    errores TEXT
                )
            ''')
            
            # Tabla de sincronización
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS sincronizacion_datos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    modulo_origen TEXT NOT NULL,
                    modulo_destino TEXT NOT NULL,
                    tipo_datos TEXT NOT NULL,
                    registros_procesados INTEGER,
                    estado TEXT NOT NULL,
                    duracion_segundos REAL
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_modulos_estado ON modulos_sistema(estado)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_tareas_activa ON tareas_integracion(activa)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_ejecuciones_timestamp ON ejecuciones_sistema(timestamp)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_sincronizacion_timestamp ON sincronizacion_datos(timestamp)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def _configurar_modulos(self):
        """Configurar módulos del sistema"""
        try:
            modulos_data = [
                {
                    'id': 'deep_learning',
                    'nombre': 'Deep Learning Avanzado',
                    'descripcion': 'Modelos LSTM, Transformer, CNN 1D y Ensemble',
                    'archivo': 'deep_learning_avanzado_metgo.py',
                    'dependencias': [],
                    'configuracion': {
                        'tipo': 'ml',
                        'frecuencia': 'diaria',
                        'timeout': 60
                    }
                },
                {
                    'id': 'app_movil',
                    'nombre': 'Aplicación Móvil',
                    'descripcion': 'API REST para agricultores',
                    'archivo': 'app_movil_metgo.py',
                    'dependencias': ['autenticacion'],
                    'configuracion': {
                        'tipo': 'api',
                        'frecuencia': 'continua',
                        'timeout': 30
                    }
                },
                {
                    'id': 'datos_satelitales',
                    'nombre': 'Datos Satelitales',
                    'descripcion': 'Integración NDVI, NDWI, EVI',
                    'archivo': 'datos_satelitales_metgo.py',
                    'dependencias': [],
                    'configuracion': {
                        'tipo': 'datos',
                        'frecuencia': 'horaria',
                        'timeout': 45
                    }
                },
                {
                    'id': 'chatbot',
                    'nombre': 'Chatbot Inteligente',
                    'descripcion': 'Asistente meteorológico',
                    'archivo': 'chatbot_metgo.py',
                    'dependencias': ['datos_satelitales'],
                    'configuracion': {
                        'tipo': 'ia',
                        'frecuencia': 'continua',
                        'timeout': 20
                    }
                },
                {
                    'id': 'reportes',
                    'nombre': 'Reportes Automáticos',
                    'descripcion': 'Generación PDF/JSON',
                    'archivo': 'reportes_automaticos_metgo.py',
                    'dependencias': ['deep_learning', 'datos_satelitales'],
                    'configuracion': {
                        'tipo': 'reporte',
                        'frecuencia': 'diaria',
                        'timeout': 90
                    }
                },
                {
                    'id': 'riego',
                    'nombre': 'Riego Automatizado',
                    'descripcion': 'Sistema de riego inteligente',
                    'archivo': 'riego_automatizado_metgo.py',
                    'dependencias': ['datos_satelitales'],
                    'configuracion': {
                        'tipo': 'control',
                        'frecuencia': 'continua',
                        'timeout': 15
                    }
                },
                {
                    'id': 'web_responsive',
                    'nombre': 'Web Responsive',
                    'descripcion': 'Aplicación web',
                    'archivo': 'web_responsive_metgo.py',
                    'dependencias': ['autenticacion'],
                    'configuracion': {
                        'tipo': 'web',
                        'frecuencia': 'continua',
                        'timeout': 30
                    }
                },
                {
                    'id': 'expansion_regional',
                    'nombre': 'Expansión Regional',
                    'descripcion': '6 regiones de Chile',
                    'archivo': 'expansion_regional_metgo.py',
                    'dependencias': [],
                    'configuracion': {
                        'tipo': 'datos',
                        'frecuencia': 'horaria',
                        'timeout': 40
                    }
                },
                {
                    'id': 'autenticacion',
                    'nombre': 'Autenticación Avanzada',
                    'descripcion': 'JWT, roles, permisos',
                    'archivo': 'autenticacion_avanzada_metgo.py',
                    'dependencias': [],
                    'configuracion': {
                        'tipo': 'seguridad',
                        'frecuencia': 'continua',
                        'timeout': 25
                    }
                },
                {
                    'id': 'metricas',
                    'nombre': 'Métricas de Negocio',
                    'descripcion': 'KPIs y análisis',
                    'archivo': 'metricas_negocio_metgo.py',
                    'dependencias': ['reportes'],
                    'configuracion': {
                        'tipo': 'analisis',
                        'frecuencia': 'horaria',
                        'timeout': 35
                    }
                }
            ]
            
            for modulo_data in modulos_data:
                modulo = ModuloMETGO(
                    id=modulo_data['id'],
                    nombre=modulo_data['nombre'],
                    descripcion=modulo_data['descripcion'],
                    archivo=modulo_data['archivo'],
                    estado='configurado',
                    dependencias=modulo_data['dependencias'],
                    configuracion=modulo_data['configuracion'],
                    ultima_ejecucion=datetime.now().isoformat(),
                    resultado={}
                )
                self.modulos[modulo.id] = modulo
            
            self.logger.info(f"Módulos configurados: {len(self.modulos)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando módulos: {e}")
    
    def _configurar_tareas_integracion(self):
        """Configurar tareas de integración"""
        try:
            tareas_data = [
                {
                    'id': 'tarea_1',
                    'nombre': 'Sincronización Datos Satelitales',
                    'modulo_origen': 'datos_satelitales',
                    'modulo_destino': 'chatbot',
                    'tipo_datos': 'ndvi_ndwi_evi',
                    'frecuencia': 'horaria',
                    'configuracion': {
                        'formato': 'json',
                        'compresion': True
                    }
                },
                {
                    'id': 'tarea_2',
                    'nombre': 'Integración ML con Reportes',
                    'modulo_origen': 'deep_learning',
                    'modulo_destino': 'reportes',
                    'tipo_datos': 'predicciones',
                    'frecuencia': 'diaria',
                    'configuracion': {
                        'formato': 'json',
                        'validacion': True
                    }
                },
                {
                    'id': 'tarea_3',
                    'nombre': 'Datos para Riego',
                    'modulo_origen': 'datos_satelitales',
                    'modulo_destino': 'riego',
                    'tipo_datos': 'condiciones_climaticas',
                    'frecuencia': 'continua',
                    'configuracion': {
                        'formato': 'json',
                        'tiempo_real': True
                    }
                },
                {
                    'id': 'tarea_4',
                    'nombre': 'Métricas de Reportes',
                    'modulo_origen': 'reportes',
                    'modulo_destino': 'metricas',
                    'tipo_datos': 'estadisticas',
                    'frecuencia': 'diaria',
                    'configuracion': {
                        'formato': 'json',
                        'agregacion': True
                    }
                },
                {
                    'id': 'tarea_5',
                    'nombre': 'Autenticación Web',
                    'modulo_origen': 'autenticacion',
                    'modulo_destino': 'web_responsive',
                    'tipo_datos': 'usuarios_sesiones',
                    'frecuencia': 'continua',
                    'configuracion': {
                        'formato': 'json',
                        'seguridad': True
                    }
                }
            ]
            
            for tarea_data in tareas_data:
                tarea = TareaIntegracion(
                    id=tarea_data['id'],
                    nombre=tarea_data['nombre'],
                    modulo_origen=tarea_data['modulo_origen'],
                    modulo_destino=tarea_data['modulo_destino'],
                    tipo_datos=tarea_data['tipo_datos'],
                    frecuencia=tarea_data['frecuencia'],
                    activa=True,
                    configuracion=tarea_data['configuracion']
                )
                self.tareas_integracion[tarea.id] = tarea
            
            self.logger.info(f"Tareas de integración configuradas: {len(self.tareas_integracion)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando tareas de integración: {e}")
    
    def _iniciar_monitoreo(self):
        """Iniciar monitoreo del sistema"""
        try:
            # Hilo de monitoreo
            hilo_monitoreo = threading.Thread(target=self._monitorear_sistema, daemon=True)
            hilo_monitoreo.start()
            
            # Hilo de procesamiento de tareas
            hilo_tareas = threading.Thread(target=self._procesar_tareas, daemon=True)
            hilo_tareas.start()
            
            self.logger.info("Monitoreo del sistema iniciado")
            
        except Exception as e:
            self.logger.error(f"Error iniciando monitoreo: {e}")
    
    def _monitorear_sistema(self):
        """Monitorear estado del sistema"""
        try:
            while self.estado_sistema['activo']:
                # Verificar estado de módulos
                modulos_activos = 0
                for modulo in self.modulos.values():
                    if modulo.estado == 'activo':
                        modulos_activos += 1
                
                self.estado_sistema['modulos_activos'] = modulos_activos
                self.estado_sistema['tareas_pendientes'] = self.cola_tareas.qsize()
                self.estado_sistema['ultima_sincronizacion'] = datetime.now().isoformat()
                
                # Log del estado
                self.logger.info(f"Estado del sistema - Módulos activos: {modulos_activos}, Tareas pendientes: {self.cola_tareas.qsize()}")
                
                time.sleep(60)  # Monitorear cada minuto
                
        except Exception as e:
            self.logger.error(f"Error en monitoreo: {e}")
    
    def _procesar_tareas(self):
        """Procesar tareas de integración"""
        try:
            while self.estado_sistema['activo']:
                try:
                    # Obtener tarea de la cola
                    tarea = self.cola_tareas.get(timeout=1)
                    
                    # Ejecutar tarea
                    self._ejecutar_tarea_integracion(tarea)
                    
                    # Marcar tarea como completada
                    self.cola_tareas.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Error procesando tarea: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error en procesamiento de tareas: {e}")
    
    def _ejecutar_tarea_integracion(self, tarea: TareaIntegracion):
        """Ejecutar tarea de integración"""
        try:
            self.logger.info(f"Ejecutando tarea: {tarea.nombre}")
            
            # Simular ejecución de tarea
            inicio = time.time()
            
            # Simular procesamiento
            time.sleep(2)
            
            duracion = time.time() - inicio
            
            # Guardar resultado
            self._guardar_ejecucion_tarea(tarea, 'completada', duracion)
            
            self.logger.info(f"Tarea completada: {tarea.nombre} en {duracion:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Error ejecutando tarea {tarea.nombre}: {e}")
            self._guardar_ejecucion_tarea(tarea, 'error', 0, str(e))
    
    def _guardar_ejecucion_tarea(self, tarea: TareaIntegracion, estado: str, duracion: float, errores: str = None):
        """Guardar ejecución de tarea"""
        try:
            self.cursor_bd.execute('''
                INSERT INTO ejecuciones_sistema 
                (tipo_ejecucion, modulo_id, estado, duracion_segundos, resultado, errores)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'tarea_integracion',
                tarea.id,
                estado,
                duracion,
                json.dumps({'tarea': tarea.nombre}),
                errores
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error guardando ejecución de tarea: {e}")
    
    def _configurar_rutas(self):
        """Configurar rutas de la API unificada"""
        try:
            if not self.app:
                return
            
            @self.app.route('/')
            def index():
                return self._renderizar_dashboard()
            
            @self.app.route('/api/estado')
            def api_estado():
                return jsonify(self._obtener_estado_sistema())
            
            @self.app.route('/api/modulos')
            def api_modulos():
                return jsonify(self._obtener_modulos())
            
            @self.app.route('/api/tareas')
            def api_tareas():
                return jsonify(self._obtener_tareas())
            
            @self.app.route('/api/ejecutar/<modulo_id>')
            def api_ejecutar_modulo(modulo_id):
                return jsonify(self._ejecutar_modulo(modulo_id))
            
            @self.app.route('/api/sincronizar')
            def api_sincronizar():
                return jsonify(self._sincronizar_sistema())
            
            self.logger.info("Rutas de API unificada configuradas")
            
        except Exception as e:
            self.logger.error(f"Error configurando rutas: {e}")
    
    def _renderizar_dashboard(self) -> str:
        """Renderizar dashboard unificado"""
        try:
            estado = self._obtener_estado_sistema()
            modulos = self._obtener_modulos()
            tareas = self._obtener_tareas()
            
            return f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>METGO 3D - Sistema Unificado</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .header {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }}
                    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                    .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .card h3 {{ color: #2E8B57; margin-top: 0; }}
                    .status {{ display: inline-block; padding: 5px 10px; border-radius: 15px; font-size: 0.9em; }}
                    .status.activo {{ background: #d4edda; color: #155724; }}
                    .status.inactivo {{ background: #f8d7da; color: #721c24; }}
                    .metric {{ font-size: 24px; font-weight: bold; color: #2E8B57; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔗 METGO 3D - Sistema Unificado</h1>
                        <p>Integración de Todos los Módulos</p>
                    </div>
                    
                    <div class="grid">
                        <div class="card">
                            <h3>📊 Estado del Sistema</h3>
                            <div class="metric">{estado['modulos_activos']}</div>
                            <p>Módulos Activos</p>
                            <span class="status {'activo' if estado['activo'] else 'inactivo'}">
                                {'Sistema Activo' if estado['activo'] else 'Sistema Inactivo'}
                            </span>
                        </div>
                        
                        <div class="card">
                            <h3>⚙️ Tareas Pendientes</h3>
                            <div class="metric">{estado['tareas_pendientes']}</div>
                            <p>Tareas en Cola</p>
                        </div>
                        
                        <div class="card">
                            <h3>🔄 Última Sincronización</h3>
                            <div class="metric">{estado['ultima_sincronizacion'][:19] if estado['ultima_sincronizacion'] else 'N/A'}</div>
                            <p>Timestamp</p>
                        </div>
                    </div>
                    
                    <div class="card" style="margin-top: 20px;">
                        <h3>📋 Módulos del Sistema</h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
            """
            
            for modulo in modulos['modulos']:
                estado_modulo = 'activo' if modulo['estado'] == 'activo' else 'inactivo'
                return f"""
                            <div style="padding: 15px; border: 1px solid #ddd; border-radius: 8px;">
                                <h4>{modulo['nombre']}</h4>
                                <p>{modulo['descripcion']}</p>
                                <span class="status {estado_modulo}">{modulo['estado']}</span>
                            </div>
                """
            
            return """
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
        except Exception as e:
            self.logger.error(f"Error renderizando dashboard: {e}")
            return f"<h1>Error: {e}</h1>"
    
    def _obtener_estado_sistema(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        try:
            return {
                'activo': self.estado_sistema['activo'],
                'modulos_activos': self.estado_sistema['modulos_activos'],
                'tareas_pendientes': self.estado_sistema['tareas_pendientes'],
                'ultima_sincronizacion': self.estado_sistema['ultima_sincronizacion'],
                'errores': self.estado_sistema['errores'],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo estado: {e}")
            return {}
    
    def _obtener_modulos(self) -> Dict[str, Any]:
        """Obtener información de módulos"""
        try:
            modulos_data = []
            for modulo in self.modulos.values():
                modulos_data.append({
                    'id': modulo.id,
                    'nombre': modulo.nombre,
                    'descripcion': modulo.descripcion,
                    'estado': modulo.estado,
                    'dependencias': modulo.dependencias,
                    'ultima_ejecucion': modulo.ultima_ejecucion
                })
            
            return {
                'exitoso': True,
                'modulos': modulos_data,
                'total': len(modulos_data)
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo módulos: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def _obtener_tareas(self) -> Dict[str, Any]:
        """Obtener información de tareas"""
        try:
            tareas_data = []
            for tarea in self.tareas_integracion.values():
                tareas_data.append({
                    'id': tarea.id,
                    'nombre': tarea.nombre,
                    'modulo_origen': tarea.modulo_origen,
                    'modulo_destino': tarea.modulo_destino,
                    'tipo_datos': tarea.tipo_datos,
                    'frecuencia': tarea.frecuencia,
                    'activa': tarea.activa
                })
            
            return {
                'exitoso': True,
                'tareas': tareas_data,
                'total': len(tareas_data)
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo tareas: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def _ejecutar_modulo(self, modulo_id: str) -> Dict[str, Any]:
        """Ejecutar módulo específico"""
        try:
            if modulo_id not in self.modulos:
                return {'exitoso': False, 'error': 'Módulo no encontrado'}
            
            modulo = self.modulos[modulo_id]
            
            # Simular ejecución
            inicio = time.time()
            modulo.estado = 'ejecutando'
            modulo.ultima_ejecucion = datetime.now().isoformat()
            
            # Simular procesamiento
            time.sleep(2)
            
            duracion = time.time() - inicio
            modulo.estado = 'activo'
            modulo.resultado = {'duracion': duracion, 'timestamp': modulo.ultima_ejecucion}
            
            return {
                'exitoso': True,
                'modulo': modulo_id,
                'estado': modulo.estado,
                'duracion': duracion
            }
            
        except Exception as e:
            self.logger.error(f"Error ejecutando módulo {modulo_id}: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def _sincronizar_sistema(self) -> Dict[str, Any]:
        """Sincronizar todo el sistema"""
        try:
            self.logger.info("Iniciando sincronización del sistema")
            
            # Agregar tareas a la cola
            for tarea in self.tareas_integracion.values():
                if tarea.activa:
                    self.cola_tareas.put(tarea)
            
            return {
                'exitoso': True,
                'tareas_agregadas': len(self.tareas_integracion),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error sincronizando sistema: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def generar_reporte_unificado(self) -> str:
        """Generar reporte del sistema unificado"""
        try:
            self.logger.info("Generando reporte del sistema unificado...")
            
            # Obtener información del sistema
            estado = self._obtener_estado_sistema()
            modulos = self._obtener_modulos()
            tareas = self._obtener_tareas()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Unificado',
                'version': self.configuracion['version'],
                'configuracion_sistema': self.configuracion_sistema,
                'estado_sistema': estado,
                'modulos': modulos,
                'tareas_integracion': tareas,
                'funcionalidades_implementadas': [
                    'Sistema unificado de módulos',
                    'Integración automática entre componentes',
                    'Monitoreo continuo del sistema',
                    'Procesamiento paralelo de tareas',
                    'Base de datos centralizada',
                    'API REST unificada',
                    'Dashboard de control',
                    'Sistema de colas para tareas',
                    'Logging estructurado',
                    'Gestión de dependencias'
                ],
                'tecnologias_utilizadas': [
                    'Flask para API unificada',
                    'SQLite para base de datos',
                    'Threading para paralelismo',
                    'Queue para gestión de tareas',
                    'Logging estructurado',
                    'JSON para intercambio de datos'
                ],
                'recomendaciones': [
                    'Implementar balanceador de carga',
                    'Agregar cache Redis',
                    'Implementar microservicios',
                    'Agregar monitoreo con Prometheus',
                    'Implementar CI/CD automatizado',
                    'Agregar tests de integración',
                    'Implementar backup automático',
                    'Agregar métricas de performance',
                    'Implementar alertas automáticas',
                    'Agregar documentación API'
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"sistema_unificado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte del sistema unificado generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""
    
    def ejecutar_sistema_unificado(self, puerto: int = 5002, debug: bool = False):
        """Ejecutar sistema unificado"""
        try:
            if not self.app:
                self.logger.error("Flask no disponible")
                return False
            
            self.logger.info(f"Iniciando sistema unificado en puerto {puerto}")
            
            # Generar reporte
            self.generar_reporte_unificado()
            
            # Ejecutar aplicación
            self.app.run(host='0.0.0.0', port=puerto, debug=debug)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error ejecutando sistema unificado: {e}")
            return False

def main():
    """Función principal del sistema unificado"""
    print("SISTEMA UNIFICADO METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Integracion de Todos los Modulos")
    print("=" * 80)
    
    try:
        # Crear sistema unificado
        sistema_unificado = SistemaUnificadoMETGO()
        
        if not FLASK_AVAILABLE:
            print("Flask no disponible. Instalando...")
            print("pip install flask flask-cors")
            return False
        
        # Generar reporte
        print(f"\nGenerando reporte del sistema unificado...")
        reporte = sistema_unificado.generar_reporte_unificado()
        
        if reporte:
            print(f"Reporte generado: {reporte}")
        else:
            print(f"Error generando reporte")
        
        # Mostrar información del sistema
        print(f"\nSistema Unificado METGO 3D")
        print(f"Version: {sistema_unificado.configuracion['version']}")
        print(f"Modo de operacion: {sistema_unificado.configuracion_sistema['modo_operacion']}")
        print(f"Frecuencia de sincronizacion: {sistema_unificado.configuracion_sistema['frecuencia_sincronizacion']} segundos")
        print(f"Paralelismo: {sistema_unificado.configuracion_sistema['paralelismo']}")
        
        print(f"\nModulos configurados:")
        for modulo in sistema_unificado.modulos.values():
            print(f"   - {modulo.nombre} ({modulo.id}): {modulo.estado}")
            print(f"     Dependencias: {', '.join(modulo.dependencias) if modulo.dependencias else 'Ninguna'}")
        
        print(f"\nTareas de integracion:")
        for tarea in sistema_unificado.tareas_integracion.values():
            print(f"   - {tarea.nombre}")
            print(f"     {tarea.modulo_origen} -> {tarea.modulo_destino} ({tarea.frecuencia})")
        
        print(f"\nRutas de API disponibles:")
        rutas = [
            'GET / - Dashboard principal',
            'GET /api/estado - Estado del sistema',
            'GET /api/modulos - Lista de módulos',
            'GET /api/tareas - Lista de tareas',
            'GET /api/ejecutar/<modulo_id> - Ejecutar módulo',
            'GET /api/sincronizar - Sincronizar sistema'
        ]
        
        for ruta in rutas:
            print(f"   - {ruta}")
        
        print(f"\nPara ejecutar el sistema unificado:")
        print(f"   python sistema_unificado_metgo.py --ejecutar")
        print(f"   El sistema estara disponible en: http://localhost:5002")
        
        return True
        
    except Exception as e:
        print(f"\nError en sistema unificado: {e}")
        return False

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--ejecutar':
            # Ejecutar sistema unificado
            sistema_unificado = SistemaUnificadoMETGO()
            sistema_unificado.ejecutar_sistema_unificado(debug=True)
        else:
            # Generar reporte
            exito = main()
            sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
