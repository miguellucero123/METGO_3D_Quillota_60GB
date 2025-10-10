#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 MONITOREO AVANZADO METGO 3D
Sistema Meteorológico Agrícola Quillota - Monitoreo Avanzado y Alertas
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
import psutil
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from dataclasses import dataclass, asdict
from enum import Enum
import yaml

# Configuración
warnings.filterwarnings('ignore')

class NivelAlerta(Enum):
    """Niveles de alerta"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class EstadoServicio(Enum):
    """Estados de servicios"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"

@dataclass
class Metrica:
    """Estructura de métrica"""
    nombre: str
    valor: float
    unidad: str
    timestamp: datetime
    tags: Dict[str, str] = None
    metadata: Dict[str, Any] = None

@dataclass
class Alerta:
    """Estructura de alerta"""
    id: str
    nivel: NivelAlerta
    mensaje: str
    timestamp: datetime
    servicio: str
    metrica: str
    valor: float
    umbral: float
    resuelta: bool = False
    metadata: Dict[str, Any] = None

@dataclass
class EstadoServicio:
    """Estado de un servicio"""
    nombre: str
    estado: EstadoServicio
    timestamp: datetime
    uptime: float
    latencia: float
    errores: int
    metadata: Dict[str, Any] = None

class MonitoreoAvanzadoMETGO:
    """Sistema de monitoreo avanzado para METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/monitoreo',
            'directorio_logs': 'logs/monitoreo',
            'directorio_config': 'config/monitoreo',
            'directorio_alertas': 'alertas',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Configuración de monitoreo
        self.configuracion_monitoreo = {
            'intervalo_metricas': 30,  # segundos
            'intervalo_servicios': 60,  # segundos
            'intervalo_alertas': 10,  # segundos
            'timeout_servicios': 30,  # segundos
            'max_reintentos': 3,
            'habilitar_notificaciones': True,
            'habilitar_alertas': True,
            'habilitar_metricas': True,
            'habilitar_servicios': True
        }
        
        # Estado del monitoreo
        self.estado_monitoreo = {
            'activo': False,
            'ultima_actualizacion': None,
            'metricas_colectadas': 0,
            'alertas_generadas': 0,
            'servicios_monitoreados': 0,
            'errores': []
        }
        
        # Colas de datos
        self.cola_metricas = queue.Queue()
        self.cola_alertas = queue.Queue()
        self.cola_servicios = queue.Queue()
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Configuración de alertas
        self.umbrales_alertas = {
            'cpu_uso': {'warning': 70, 'critical': 90},
            'memoria_uso': {'warning': 80, 'critical': 95},
            'disco_uso': {'warning': 85, 'critical': 95},
            'latencia_api': {'warning': 5, 'critical': 10},
            'errores_por_minuto': {'warning': 10, 'critical': 50},
            'temperatura': {'warning': 35, 'critical': 40},
            'humedad': {'warning': 90, 'critical': 95},
            'viento_velocidad': {'warning': 20, 'critical': 30}
        }
        
        # Servicios a monitorear
        self.servicios = {
            'api_principal': {'url': 'http://localhost:5000/health', 'timeout': 10},
            'api_meteorologia': {'url': 'http://localhost:5001/health', 'timeout': 10},
            'api_agricola': {'url': 'http://localhost:5002/health', 'timeout': 10},
            'api_alertas': {'url': 'http://localhost:5003/health', 'timeout': 10},
            'api_iot': {'url': 'http://localhost:5004/health', 'timeout': 10},
            'api_ml': {'url': 'http://localhost:5005/health', 'timeout': 10},
            'api_visualizacion': {'url': 'http://localhost:5006/health', 'timeout': 10},
            'api_reportes': {'url': 'http://localhost:5007/health', 'timeout': 10},
            'api_configuracion': {'url': 'http://localhost:5008/health', 'timeout': 10},
            'api_monitoreo': {'url': 'http://localhost:5009/health', 'timeout': 10},
            'dashboard': {'url': 'http://localhost:8050/health', 'timeout': 10},
            'postgres': {'url': 'http://localhost:5432', 'timeout': 5},
            'redis': {'url': 'http://localhost:6379', 'timeout': 5}
        }
        
        # Configuración de notificaciones
        self.configuracion_notificaciones = {
            'email': {
                'habilitado': True,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'usuario': 'metgo3d@example.com',
                'password': 'password',
                'destinatarios': ['admin@metgo3d.cl']
            },
            'slack': {
                'habilitado': False,
                'webhook_url': 'https://hooks.slack.com/services/...',
                'canal': '#metgo3d-alerts'
            },
            'webhook': {
                'habilitado': False,
                'url': 'https://api.example.com/webhook',
                'headers': {'Authorization': 'Bearer token'}
            }
        }
        
        # Hilos de monitoreo
        self.hilos_activos = []
        self.detener_hilos = threading.Event()
        
        # Cache de métricas
        self.cache_metricas = {}
        self.cache_alertas = {}
        self.cache_servicios = {}
    
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
                    logging.FileHandler(f"{self.configuracion['directorio_logs']}/monitoreo_avanzado.log"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('METGO_MONITOREO_AVANZADO')
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/monitoreo_avanzado.db"
            
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
            # Tabla de métricas
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS metricas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    valor REAL NOT NULL,
                    unidad TEXT,
                    timestamp DATETIME NOT NULL,
                    tags TEXT,
                    metadata TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de alertas
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS alertas (
                    id TEXT PRIMARY KEY,
                    nivel TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    servicio TEXT,
                    metrica TEXT,
                    valor REAL,
                    umbral REAL,
                    resuelta BOOLEAN DEFAULT FALSE,
                    metadata TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de servicios
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS servicios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    uptime REAL,
                    latencia REAL,
                    errores INTEGER,
                    metadata TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de eventos
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    nivel TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    metadata TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_metricas_timestamp ON metricas(timestamp)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_metricas_nombre ON metricas(nombre)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_alertas_timestamp ON alertas(timestamp)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_alertas_nivel ON alertas(nivel)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_alertas_resuelta ON alertas(resuelta)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_servicios_timestamp ON servicios(timestamp)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_servicios_estado ON servicios(estado)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_eventos_timestamp ON eventos(timestamp)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON eventos(tipo)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def recolectar_metricas_sistema(self) -> List[Metrica]:
        """Recolectar métricas del sistema"""
        try:
            metricas = []
            timestamp = datetime.now()
            
            # Métricas de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            metricas.append(Metrica(
                nombre='cpu_uso',
                valor=cpu_percent,
                unidad='%',
                timestamp=timestamp,
                tags={'tipo': 'sistema', 'componente': 'cpu'}
            ))
            
            # Métricas de memoria
            memoria = psutil.virtual_memory()
            metricas.append(Metrica(
                nombre='memoria_uso',
                valor=memoria.percent,
                unidad='%',
                timestamp=timestamp,
                tags={'tipo': 'sistema', 'componente': 'memoria'}
            ))
            
            # Métricas de disco
            disco = psutil.disk_usage('/')
            metricas.append(Metrica(
                nombre='disco_uso',
                valor=(disco.used / disco.total) * 100,
                unidad='%',
                timestamp=timestamp,
                tags={'tipo': 'sistema', 'componente': 'disco'}
            ))
            
            # Métricas de red
            red = psutil.net_io_counters()
            metricas.append(Metrica(
                nombre='red_bytes_enviados',
                valor=red.bytes_sent,
                unidad='bytes',
                timestamp=timestamp,
                tags={'tipo': 'sistema', 'componente': 'red'}
            ))
            
            metricas.append(Metrica(
                nombre='red_bytes_recibidos',
                valor=red.bytes_recv,
                unidad='bytes',
                timestamp=timestamp,
                tags={'tipo': 'sistema', 'componente': 'red'}
            ))
            
            # Métricas de procesos
            procesos = len(psutil.pids())
            metricas.append(Metrica(
                nombre='procesos_activos',
                valor=procesos,
                unidad='count',
                timestamp=timestamp,
                tags={'tipo': 'sistema', 'componente': 'procesos'}
            ))
            
            return metricas
            
        except Exception as e:
            self.logger.error(f"Error recolectando métricas del sistema: {e}")
            return []
    
    def recolectar_metricas_aplicacion(self) -> List[Metrica]:
        """Recolectar métricas de la aplicación"""
        try:
            metricas = []
            timestamp = datetime.now()
            
            # Métricas de Python
            import gc
            gc.collect()
            
            # Memoria de Python
            import sys
            memoria_python = sys.getsizeof(gc.get_objects())
            metricas.append(Metrica(
                nombre='python_memoria',
                valor=memoria_python,
                unidad='bytes',
                timestamp=timestamp,
                tags={'tipo': 'aplicacion', 'componente': 'python'}
            ))
            
            # Objetos en memoria
            objetos_gc = len(gc.get_objects())
            metricas.append(Metrica(
                nombre='python_objetos',
                valor=objetos_gc,
                unidad='count',
                timestamp=timestamp,
                tags={'tipo': 'aplicacion', 'componente': 'python'}
            ))
            
            # Métricas de threading
            hilos_activos = threading.active_count()
            metricas.append(Metrica(
                nombre='python_hilos',
                valor=hilos_activos,
                unidad='count',
                timestamp=timestamp,
                tags={'tipo': 'aplicacion', 'componente': 'threading'}
            ))
            
            return metricas
            
        except Exception as e:
            self.logger.error(f"Error recolectando métricas de aplicación: {e}")
            return []
    
    def monitorear_servicios(self) -> List[EstadoServicio]:
        """Monitorear estado de servicios"""
        try:
            estados = []
            timestamp = datetime.now()
            
            for nombre, config in self.servicios.items():
                try:
                    inicio = time.time()
                    
                    # Verificar servicio
                    if nombre in ['postgres', 'redis']:
                        # Servicios de base de datos
                        estado = self._verificar_servicio_db(nombre, config)
                    else:
                        # Servicios HTTP
                        estado = self._verificar_servicio_http(nombre, config)
                    
                    latencia = time.time() - inicio
                    
                    estado_servicio = EstadoServicio(
                        nombre=nombre,
                        estado=estado,
                        timestamp=timestamp,
                        uptime=0,  # Se calculará después
                        latencia=latencia,
                        errores=0,  # Se calculará después
                        metadata={'config': config}
                    )
                    
                    estados.append(estado_servicio)
                    
                except Exception as e:
                    self.logger.error(f"Error monitoreando servicio {nombre}: {e}")
                    
                    estado_servicio = EstadoServicio(
                        nombre=nombre,
                        estado=EstadoServicio.DOWN,
                        timestamp=timestamp,
                        uptime=0,
                        latencia=0,
                        errores=1,
                        metadata={'error': str(e)}
                    )
                    
                    estados.append(estado_servicio)
            
            return estados
            
        except Exception as e:
            self.logger.error(f"Error monitoreando servicios: {e}")
            return []
    
    def _verificar_servicio_http(self, nombre: str, config: Dict) -> EstadoServicio:
        """Verificar servicio HTTP"""
        try:
            response = requests.get(
                config['url'],
                timeout=config['timeout'],
                headers={'User-Agent': 'METGO3D-Monitor/2.0'}
            )
            
            if response.status_code == 200:
                return EstadoServicio.HEALTHY
            elif response.status_code in [500, 502, 503, 504]:
                return EstadoServicio.DEGRADED
            else:
                return EstadoServicio.DOWN
                
        except requests.exceptions.Timeout:
            return EstadoServicio.DOWN
        except requests.exceptions.ConnectionError:
            return EstadoServicio.DOWN
        except Exception:
            return EstadoServicio.UNKNOWN
    
    def _verificar_servicio_db(self, nombre: str, config: Dict) -> EstadoServicio:
        """Verificar servicio de base de datos"""
        try:
            if nombre == 'postgres':
                import psycopg2
                conn = psycopg2.connect(
                    host='localhost',
                    port=5432,
                    database='metgo3d',
                    user='metgo3d',
                    password='metgo3d_2024_secure',
                    connect_timeout=config['timeout']
                )
                conn.close()
                return EstadoServicio.HEALTHY
                
            elif nombre == 'redis':
                import redis
                r = redis.Redis(host='localhost', port=6379, socket_timeout=config['timeout'])
                r.ping()
                return EstadoServicio.HEALTHY
                
        except Exception:
            return EstadoServicio.DOWN
    
    def evaluar_alertas(self, metricas: List[Metrica]) -> List[Alerta]:
        """Evaluar alertas basadas en métricas"""
        try:
            alertas = []
            timestamp = datetime.now()
            
            for metrica in metricas:
                if metrica.nombre in self.umbrales_alertas:
                    umbrales = self.umbrales_alertas[metrica.nombre]
                    
                    # Evaluar umbrales
                    if metrica.valor >= umbrales.get('critical', float('inf')):
                        nivel = NivelAlerta.CRITICAL
                    elif metrica.valor >= umbrales.get('warning', float('inf')):
                        nivel = NivelAlerta.WARNING
                    else:
                        continue
                    
                    # Crear alerta
                    alerta = Alerta(
                        id=f"{metrica.nombre}_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                        nivel=nivel,
                        mensaje=f"{metrica.nombre} excede umbral: {metrica.valor:.2f} {metrica.unidad}",
                        timestamp=timestamp,
                        servicio='sistema',
                        metrica=metrica.nombre,
                        valor=metrica.valor,
                        umbral=umbrales.get('warning', umbrales.get('critical')),
                        metadata={'tags': metrica.tags}
                    )
                    
                    alertas.append(alerta)
            
            return alertas
            
        except Exception as e:
            self.logger.error(f"Error evaluando alertas: {e}")
            return []
    
    def guardar_metricas(self, metricas: List[Metrica]) -> bool:
        """Guardar métricas en la base de datos"""
        try:
            for metrica in metricas:
                self.cursor_bd.execute('''
                    INSERT INTO metricas 
                    (nombre, valor, unidad, timestamp, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    metrica.nombre,
                    metrica.valor,
                    metrica.unidad,
                    metrica.timestamp,
                    json.dumps(metrica.tags) if metrica.tags else None,
                    json.dumps(metrica.metadata) if metrica.metadata else None
                ))
            
            self.conexion_bd.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando métricas: {e}")
            return False
    
    def guardar_alertas(self, alertas: List[Alerta]) -> bool:
        """Guardar alertas en la base de datos"""
        try:
            for alerta in alertas:
                self.cursor_bd.execute('''
                    INSERT OR REPLACE INTO alertas 
                    (id, nivel, mensaje, timestamp, servicio, metrica, valor, umbral, resuelta, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alerta.id,
                    alerta.nivel.value,
                    alerta.mensaje,
                    alerta.timestamp,
                    alerta.servicio,
                    alerta.metrica,
                    alerta.valor,
                    alerta.umbral,
                    alerta.resuelta,
                    json.dumps(alerta.metadata) if alerta.metadata else None
                ))
            
            self.conexion_bd.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando alertas: {e}")
            return False
    
    def guardar_servicios(self, servicios: List[EstadoServicio]) -> bool:
        """Guardar estados de servicios en la base de datos"""
        try:
            for servicio in servicios:
                self.cursor_bd.execute('''
                    INSERT INTO servicios 
                    (nombre, estado, timestamp, uptime, latencia, errores, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    servicio.nombre,
                    servicio.estado.value,
                    servicio.timestamp,
                    servicio.uptime,
                    servicio.latencia,
                    servicio.errores,
                    json.dumps(servicio.metadata) if servicio.metadata else None
                ))
            
            self.conexion_bd.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando servicios: {e}")
            return False
    
    def enviar_notificaciones(self, alertas: List[Alerta]) -> bool:
        """Enviar notificaciones de alertas"""
        try:
            if not self.configuracion_notificaciones['email']['habilitado']:
                return True
            
            for alerta in alertas:
                if alerta.nivel in [NivelAlerta.WARNING, NivelAlerta.ERROR, NivelAlerta.CRITICAL]:
                    self._enviar_email(alerta)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error enviando notificaciones: {e}")
            return False
    
    def _enviar_email(self, alerta: Alerta) -> bool:
        """Enviar email de alerta"""
        try:
            config = self.configuracion_notificaciones['email']
            
            # Crear mensaje
            msg = MimeMultipart()
            msg['From'] = config['usuario']
            msg['To'] = ', '.join(config['destinatarios'])
            msg['Subject'] = f"METGO 3D - Alerta {alerta.nivel.value.upper()}"
            
            # Contenido del mensaje
            body = f"""
            Alerta del Sistema METGO 3D
            
            Nivel: {alerta.nivel.value.upper()}
            Servicio: {alerta.servicio}
            Métrica: {alerta.metrica}
            Valor: {alerta.valor} (Umbral: {alerta.umbral})
            Mensaje: {alerta.mensaje}
            Timestamp: {alerta.timestamp}
            
            Sistema Meteorológico Agrícola Quillota
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Enviar email
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['usuario'], config['password'])
            text = msg.as_string()
            server.sendmail(config['usuario'], config['destinatarios'], text)
            server.quit()
            
            self.logger.info(f"Email de alerta enviado: {alerta.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enviando email: {e}")
            return False
    
    def ejecutar_monitoreo_completo(self) -> Dict:
        """Ejecutar monitoreo completo"""
        try:
            self.logger.info("Iniciando monitoreo completo...")
            
            inicio = datetime.now()
            resultados = {
                'inicio': inicio.isoformat(),
                'metricas': [],
                'alertas': [],
                'servicios': [],
                'errores': []
            }
            
            # Recolectar métricas del sistema
            metricas_sistema = self.recolectar_metricas_sistema()
            resultados['metricas'].extend(metricas_sistema)
            
            # Recolectar métricas de aplicación
            metricas_aplicacion = self.recolectar_metricas_aplicacion()
            resultados['metricas'].extend(metricas_aplicacion)
            
            # Monitorear servicios
            servicios = self.monitorear_servicios()
            resultados['servicios'] = servicios
            
            # Evaluar alertas
            alertas = self.evaluar_alertas(resultados['metricas'])
            resultados['alertas'] = alertas
            
            # Guardar datos
            self.guardar_metricas(resultados['metricas'])
            self.guardar_alertas(alertas)
            self.guardar_servicios(servicios)
            
            # Enviar notificaciones
            if alertas:
                self.enviar_notificaciones(alertas)
            
            # Actualizar estado
            fin = datetime.now()
            self.estado_monitoreo['ultima_actualizacion'] = fin.isoformat()
            self.estado_monitoreo['metricas_colectadas'] += len(resultados['metricas'])
            self.estado_monitoreo['alertas_generadas'] += len(alertas)
            self.estado_monitoreo['servicios_monitoreados'] = len(servicios)
            
            resultados['fin'] = fin.isoformat()
            resultados['duracion'] = (fin - inicio).total_seconds()
            
            self.logger.info(f"Monitoreo completo ejecutado en {resultados['duracion']:.2f} segundos")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error ejecutando monitoreo completo: {e}")
            self.estado_monitoreo['errores'].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            })
            return {'error': str(e)}
    
    def iniciar_monitoreo_continuo(self) -> bool:
        """Iniciar monitoreo continuo"""
        try:
            self.logger.info("Iniciando monitoreo continuo...")
            
            self.estado_monitoreo['activo'] = True
            self.detener_hilos.clear()
            
            # Hilo de métricas
            hilo_metricas = threading.Thread(
                target=self._hilo_metricas,
                name="MonitoreoMetricas"
            )
            hilo_metricas.daemon = True
            hilo_metricas.start()
            self.hilos_activos.append(hilo_metricas)
            
            # Hilo de servicios
            hilo_servicios = threading.Thread(
                target=self._hilo_servicios,
                name="MonitoreoServicios"
            )
            hilo_servicios.daemon = True
            hilo_servicios.start()
            self.hilos_activos.append(hilo_servicios)
            
            # Hilo de alertas
            hilo_alertas = threading.Thread(
                target=self._hilo_alertas,
                name="MonitoreoAlertas"
            )
            hilo_alertas.daemon = True
            hilo_alertas.start()
            self.hilos_activos.append(hilo_alertas)
            
            self.logger.info("Monitoreo continuo iniciado")
            return True
            
        except Exception as e:
            self.logger.error(f"Error iniciando monitoreo continuo: {e}")
            return False
    
    def _hilo_metricas(self):
        """Hilo para recolectar métricas"""
        while not self.detener_hilos.is_set():
            try:
                if self.configuracion_monitoreo['habilitar_metricas']:
                    resultado = self.ejecutar_monitoreo_completo()
                    if 'error' not in resultado:
                        self.logger.debug("Métricas recolectadas correctamente")
                
                time.sleep(self.configuracion_monitoreo['intervalo_metricas'])
                
            except Exception as e:
                self.logger.error(f"Error en hilo de métricas: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    def _hilo_servicios(self):
        """Hilo para monitorear servicios"""
        while not self.detener_hilos.is_set():
            try:
                if self.configuracion_monitoreo['habilitar_servicios']:
                    servicios = self.monitorear_servicios()
                    self.guardar_servicios(servicios)
                    self.logger.debug("Servicios monitoreados correctamente")
                
                time.sleep(self.configuracion_monitoreo['intervalo_servicios'])
                
            except Exception as e:
                self.logger.error(f"Error en hilo de servicios: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    def _hilo_alertas(self):
        """Hilo para procesar alertas"""
        while not self.detener_hilos.is_set():
            try:
                if self.configuracion_monitoreo['habilitar_alertas']:
                    # Procesar alertas pendientes
                    self._procesar_alertas_pendientes()
                
                time.sleep(self.configuracion_monitoreo['intervalo_alertas'])
                
            except Exception as e:
                self.logger.error(f"Error en hilo de alertas: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    def _procesar_alertas_pendientes(self):
        """Procesar alertas pendientes"""
        try:
            # Obtener alertas no resueltas
            self.cursor_bd.execute('''
                SELECT * FROM alertas 
                WHERE resuelta = FALSE 
                AND timestamp > datetime('now', '-1 hour')
                ORDER BY timestamp DESC
            ''')
            
            alertas_pendientes = self.cursor_bd.fetchall()
            
            for alerta in alertas_pendientes:
                # Verificar si la alerta sigue siendo válida
                # Si no, marcarla como resuelta
                pass
                
        except Exception as e:
            self.logger.error(f"Error procesando alertas pendientes: {e}")
    
    def detener_monitoreo(self):
        """Detener monitoreo continuo"""
        try:
            self.logger.info("Deteniendo monitoreo continuo...")
            
            self.estado_monitoreo['activo'] = False
            self.detener_hilos.set()
            
            # Esperar a que terminen los hilos
            for hilo in self.hilos_activos:
                hilo.join(timeout=10)
            
            self.hilos_activos.clear()
            self.logger.info("Monitoreo continuo detenido")
            
        except Exception as e:
            self.logger.error(f"Error deteniendo monitoreo: {e}")
    
    def obtener_estadisticas(self) -> Dict:
        """Obtener estadísticas del monitoreo"""
        try:
            # Estadísticas de métricas
            self.cursor_bd.execute('SELECT COUNT(*) FROM metricas')
            total_metricas = self.cursor_bd.fetchone()[0]
            
            # Estadísticas de alertas
            self.cursor_bd.execute('SELECT COUNT(*) FROM alertas WHERE resuelta = FALSE')
            alertas_activas = self.cursor_bd.fetchone()[0]
            
            self.cursor_bd.execute('SELECT COUNT(*) FROM alertas')
            total_alertas = self.cursor_bd.fetchone()[0]
            
            # Estadísticas de servicios
            self.cursor_bd.execute('SELECT COUNT(*) FROM servicios')
            total_servicios = self.cursor_bd.fetchone()[0]
            
            return {
                'timestamp': datetime.now().isoformat(),
                'estado_monitoreo': self.estado_monitoreo,
                'estadisticas': {
                    'total_metricas': total_metricas,
                    'alertas_activas': alertas_activas,
                    'total_alertas': total_alertas,
                    'total_servicios': total_servicios
                },
                'configuracion': self.configuracion_monitoreo
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def generar_reporte_monitoreo(self) -> str:
        """Generar reporte de monitoreo"""
        try:
            self.logger.info("Generando reporte de monitoreo...")
            
            estadisticas = self.obtener_estadisticas()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Monitoreo Avanzado',
                'version': self.configuracion['version'],
                'resumen': {
                    'monitoreo_activo': self.estado_monitoreo['activo'],
                    'ultima_actualizacion': self.estado_monitoreo.get('ultima_actualizacion'),
                    'metricas_colectadas': self.estado_monitoreo['metricas_colectadas'],
                    'alertas_generadas': self.estado_monitoreo['alertas_generadas'],
                    'servicios_monitoreados': self.estado_monitoreo['servicios_monitoreados']
                },
                'estadisticas': estadisticas,
                'configuracion': self.configuracion_monitoreo,
                'recomendaciones': [
                    "Monitorear regularmente las métricas del sistema",
                    "Revisar alertas activas periódicamente",
                    "Mantener umbrales de alerta actualizados",
                    "Verificar estado de servicios críticos",
                    "Implementar notificaciones adicionales si es necesario"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"monitoreo_avanzado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte de monitoreo generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal del monitoreo avanzado"""
    print("📊 MONITOREO AVANZADO METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Monitoreo Avanzado y Alertas")
    print("=" * 80)
    
    try:
        # Crear monitoreo
        monitoreo = MonitoreoAvanzadoMETGO()
        
        # Ejecutar monitoreo completo
        print(f"\n📊 Ejecutando monitoreo completo...")
        resultados = monitoreo.ejecutar_monitoreo_completo()
        
        if 'error' in resultados:
            print(f"\n❌ Error en monitoreo: {resultados['error']}")
            return False
        
        # Mostrar resultados
        print(f"\n📈 Resultados del monitoreo:")
        print(f"   Métricas recolectadas: {len(resultados.get('metricas', []))}")
        print(f"   Alertas generadas: {len(resultados.get('alertas', []))}")
        print(f"   Servicios monitoreados: {len(resultados.get('servicios', []))}")
        print(f"   Duración: {resultados.get('duracion', 0):.2f} segundos")
        
        # Mostrar alertas
        if resultados.get('alertas'):
            print(f"\n🚨 Alertas generadas:")
            for alerta in resultados['alertas']:
                print(f"   - {alerta.nivel.value.upper()}: {alerta.mensaje}")
        
        # Mostrar servicios
        if resultados.get('servicios'):
            print(f"\n🔧 Estado de servicios:")
            for servicio in resultados['servicios']:
                print(f"   - {servicio.nombre}: {servicio.estado.value}")
        
        # Obtener estadísticas
        print(f"\n📊 Estadísticas del monitoreo:")
        estadisticas = monitoreo.obtener_estadisticas()
        if estadisticas:
            stats = estadisticas.get('estadisticas', {})
            print(f"   Total métricas: {stats.get('total_metricas', 0)}")
            print(f"   Alertas activas: {stats.get('alertas_activas', 0)}")
            print(f"   Total alertas: {stats.get('total_alertas', 0)}")
            print(f"   Total servicios: {stats.get('total_servicios', 0)}")
        
        # Generar reporte
        print(f"\n📋 Generando reporte...")
        reporte = monitoreo.generar_reporte_monitoreo()
        
        if reporte:
            print(f"\n✅ Monitoreo avanzado ejecutado exitosamente")
            print(f"📄 Reporte generado: {reporte}")
        else:
            print(f"\n⚠️ Error generando reporte")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en monitoreo avanzado: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
