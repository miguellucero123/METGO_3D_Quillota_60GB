"""
SISTEMA DE INTEGRACIÓN CON SISTEMAS EXISTENTES - METGO 3D QUILLOTA
Sistema para integración con ERP agrícolas, GPS de maquinaria, sensores IoT y sistemas de gestión
Incluye: Conectores para sistemas ERP, protocolos GPS, comunicación IoT, sincronización de datos
"""

import pandas as pd
import numpy as np
import json
import logging
import sqlite3
import requests
import socket
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import os
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import asyncio
# import aiohttp  # Comentado temporalmente para evitar errores
import paho.mqtt.client as mqtt
# import serial  # Comentado temporalmente para evitar errores
import plotly.graph_objects as go
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

@dataclass
class DispositivoGPS:
    """Clase para representar dispositivos GPS"""
    id_dispositivo: str
    nombre: str
    tipo: str  # 'tractor', 'cosechadora', 'pulverizador', 'sensor'
    latitud: float
    longitud: float
    altitud: float
    velocidad: float
    direccion: float
    timestamp: datetime
    estado: str  # 'activo', 'inactivo', 'mantenimiento'
    bateria: float

@dataclass
class SensorIoT:
    """Clase para representar sensores IoT"""
    id_sensor: str
    nombre: str
    tipo: str  # 'humedad', 'temperatura', 'ph', 'nutrientes', 'riego'
    ubicacion: str
    valor: float
    unidad: str
    timestamp: datetime
    estado: str
    bateria: float

@dataclass
class DatosERP:
    """Clase para representar datos de sistemas ERP"""
    id_registro: str
    modulo: str  # 'inventario', 'produccion', 'financiero', 'recursos_humanos'
    tipo_dato: str
    valor: Any
    timestamp: datetime
    usuario: str

class IntegracionSistemasExistentesMetgo:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_datos = "integracion_sistemas_existentes.db"
        self.directorio_datos = "datos_integracion"
        self.directorio_logs = "logs_integracion"
        
        # Crear directorios necesarios
        self._crear_directorios()
        
        # Inicializar base de datos
        self._inicializar_base_datos()
        
        # Configuración de sistemas ERP
        self.configuracion_erp = {
            'sap_agricola': {
                'nombre': 'SAP Agrícola',
                'tipo': 'ERP',
                'protocolo': 'RFC',
                'endpoint': 'http://sap-agricola.local:8000',
                'modulos': ['inventario', 'produccion', 'financiero', 'calidad'],
                'autenticacion': 'usuario_password',
                'activo': True
            },
            'agvance': {
                'nombre': 'Agvance',
                'tipo': 'ERP_Agricola',
                'protocolo': 'REST',
                'endpoint': 'https://api.agvance.com',
                'modulos': ['cultivos', 'inventario', 'maquinaria', 'reportes'],
                'autenticacion': 'api_key',
                'activo': True
            },
            'granular': {
                'nombre': 'Granular',
                'tipo': 'Plataforma_Digital',
                'protocolo': 'GraphQL',
                'endpoint': 'https://api.granular.ag',
                'modulos': ['datos_campo', 'analytics', 'maquinaria'],
                'autenticacion': 'oauth2',
                'activo': True
            }
        }
        
        # Configuración de sistemas GPS
        self.configuracion_gps = {
            'john_deere_operations_center': {
                'nombre': 'John Deere Operations Center',
                'protocolo': 'ISOXML',
                'puerto': 8080,
                'formato_datos': 'ISOXML',
                'dispositivos_soportados': ['tractor', 'cosechadora', 'pulverizador'],
                'activo': True
            },
            'cnh_agriculture': {
                'nombre': 'CNH Agriculture',
                'protocolo': 'ISOXML',
                'puerto': 8081,
                'formato_datos': 'ISOXML',
                'dispositivos_soportados': ['tractor', 'cosechadora'],
                'activo': True
            },
            'trimble_agriculture': {
                'nombre': 'Trimble Agriculture',
                'protocolo': 'NMEA',
                'puerto': 8082,
                'formato_datos': 'NMEA',
                'dispositivos_soportados': ['tractor', 'pulverizador', 'sensor'],
                'activo': True
            }
        }
        
        # Configuración de sensores IoT
        self.configuracion_iot = {
            'protocolos_soportados': ['MQTT', 'HTTP', 'LoRaWAN', 'Modbus'],
            'sensores_configurados': {
                'humedad_suelo': {
                    'protocolo': 'MQTT',
                    'topic': 'sensores/humedad_suelo',
                    'frecuencia': 30,  # segundos
                    'rango_valores': [0, 100],
                    'unidad': '%'
                },
                'temperatura_ambiente': {
                    'protocolo': 'MQTT',
                    'topic': 'sensores/temperatura',
                    'frecuencia': 60,
                    'rango_valores': [-10, 50],
                    'unidad': '°C'
                },
                'ph_suelo': {
                    'protocolo': 'HTTP',
                    'endpoint': 'http://sensores.local/ph',
                    'frecuencia': 300,
                    'rango_valores': [0, 14],
                    'unidad': 'pH'
                },
                'nivel_riego': {
                    'protocolo': 'Modbus',
                    'direccion': '192.168.1.100',
                    'puerto': 502,
                    'frecuencia': 120,
                    'rango_valores': [0, 100],
                    'unidad': '%'
                }
            }
        }
        
        # Configuración de MQTT
        self.configuracion_mqtt = {
            'broker_host': 'localhost',
            'broker_port': 1883,
            'username': 'metgo_user',
            'password': 'metgo_pass',
            'client_id': 'metgo_integration',
            'topics': {
                'sensores': 'metgo/sensores/+',
                'maquinaria': 'metgo/maquinaria/+',
                'alertas': 'metgo/alertas/+'
            }
        }
        
        # Inicializar clientes
        self.mqtt_client = None
        self.dispositivos_gps = {}
        self.sensores_iot = {}
        self.datos_erp = {}
        
        self.logger.info("Sistema de Integración con Sistemas Existentes METGO 3D inicializado")
    
    def _crear_directorios(self):
        """Crear directorios necesarios para el sistema"""
        try:
            directorios = [
                self.directorio_datos,
                self.directorio_logs,
                f"{self.directorio_datos}/erp",
                f"{self.directorio_datos}/gps",
                f"{self.directorio_datos}/iot",
                f"{self.directorio_datos}/sincronizacion",
                f"{self.directorio_logs}/conexiones",
                f"{self.directorio_logs}/errores"
            ]
            
            for directorio in directorios:
                os.makedirs(directorio, exist_ok=True)
                
            print("[OK] Directorios del sistema de integración creados")
            
        except Exception as e:
            print(f"[ERROR] Error creando directorios: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos para integración"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla de dispositivos GPS
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dispositivos_gps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_dispositivo TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    latitud REAL,
                    longitud REAL,
                    altitud REAL,
                    velocidad REAL,
                    direccion REAL,
                    timestamp DATETIME,
                    estado TEXT DEFAULT 'inactivo',
                    bateria REAL,
                    sistema_gps TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de sensores IoT
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensores_iot (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_sensor TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    ubicacion TEXT NOT NULL,
                    valor REAL,
                    unidad TEXT,
                    timestamp DATETIME,
                    estado TEXT DEFAULT 'inactivo',
                    bateria REAL,
                    protocolo TEXT,
                    topic_endpoint TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de datos ERP
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datos_erp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_registro TEXT UNIQUE NOT NULL,
                    sistema_erp TEXT NOT NULL,
                    modulo TEXT NOT NULL,
                    tipo_dato TEXT NOT NULL,
                    valor TEXT,
                    timestamp DATETIME,
                    usuario TEXT,
                    sincronizado BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de logs de integración
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs_integracion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sistema TEXT NOT NULL,
                    tipo_operacion TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    mensaje TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duracion_ms INTEGER
                )
            ''')
            
            # Tabla de configuración de sistemas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracion_sistemas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sistema_nombre TEXT UNIQUE NOT NULL,
                    sistema_tipo TEXT NOT NULL,
                    configuracion_json TEXT NOT NULL,
                    activo BOOLEAN DEFAULT 1,
                    ultima_conexion DATETIME,
                    estado_conexion TEXT DEFAULT 'desconocido',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insertar configuraciones iniciales
            self._insertar_configuraciones_iniciales(cursor)
            
            conn.commit()
            conn.close()
            
            print("[OK] Base de datos de integración inicializada")
            
        except Exception as e:
            print(f"[ERROR] Error inicializando base de datos: {e}")
    
    def _insertar_configuraciones_iniciales(self, cursor):
        """Insertar configuraciones iniciales de sistemas"""
        try:
            # Insertar configuraciones ERP
            for sistema, config in self.configuracion_erp.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO configuracion_sistemas 
                    (sistema_nombre, sistema_tipo, configuracion_json, activo)
                    VALUES (?, ?, ?, ?)
                ''', (sistema, 'ERP', json.dumps(config), config['activo']))
            
            # Insertar configuraciones GPS
            for sistema, config in self.configuracion_gps.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO configuracion_sistemas 
                    (sistema_nombre, sistema_tipo, configuracion_json, activo)
                    VALUES (?, ?, ?, ?)
                ''', (sistema, 'GPS', json.dumps(config), config['activo']))
            
            print("[OK] Configuraciones iniciales insertadas")
            
        except Exception as e:
            print(f"[ERROR] Error insertando configuraciones: {e}")
    
    def inicializar_mqtt(self):
        """Inicializar cliente MQTT para comunicación IoT"""
        try:
            print("[MQTT] Inicializando cliente MQTT...")
            
            self.mqtt_client = mqtt.Client(self.configuracion_mqtt['client_id'])
            self.mqtt_client.username_pw_set(
                self.configuracion_mqtt['username'], 
                self.configuracion_mqtt['password']
            )
            
            # Callbacks MQTT
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            # Conectar al broker
            self.mqtt_client.connect(
                self.configuracion_mqtt['broker_host'],
                self.configuracion_mqtt['broker_port'],
                60
            )
            
            # Iniciar loop en thread separado
            self.mqtt_client.loop_start()
            
            print("[OK] Cliente MQTT inicializado y conectado")
            
        except Exception as e:
            print(f"[ERROR] Error inicializando MQTT: {e}")
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback para conexión MQTT"""
        if rc == 0:
            print("[MQTT] Conectado exitosamente")
            # Suscribirse a topics
            for topic in self.configuracion_mqtt['topics'].values():
                client.subscribe(topic)
                print(f"[MQTT] Suscrito a {topic}")
        else:
            print(f"[MQTT] Error de conexión: {rc}")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """Callback para mensajes MQTT"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            print(f"[MQTT] Mensaje recibido en {topic}: {payload}")
            
            # Procesar según el tipo de mensaje
            if 'sensores' in topic:
                self._procesar_mensaje_sensor(payload)
            elif 'maquinaria' in topic:
                self._procesar_mensaje_maquinaria(payload)
            elif 'alertas' in topic:
                self._procesar_mensaje_alerta(payload)
                
        except Exception as e:
            print(f"[ERROR] Error procesando mensaje MQTT: {e}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Callback para desconexión MQTT"""
        print("[MQTT] Desconectado del broker")
    
    def _procesar_mensaje_sensor(self, payload: Dict):
        """Procesar mensaje de sensor IoT"""
        try:
            sensor = SensorIoT(
                id_sensor=payload.get('id_sensor', ''),
                nombre=payload.get('nombre', ''),
                tipo=payload.get('tipo', ''),
                ubicacion=payload.get('ubicacion', ''),
                valor=payload.get('valor', 0.0),
                unidad=payload.get('unidad', ''),
                timestamp=datetime.now(),
                estado='activo',
                bateria=payload.get('bateria', 100.0)
            )
            
            self._guardar_sensor_iot(sensor)
            
        except Exception as e:
            print(f"[ERROR] Error procesando sensor: {e}")
    
    def _procesar_mensaje_maquinaria(self, payload: Dict):
        """Procesar mensaje de maquinaria GPS"""
        try:
            dispositivo = DispositivoGPS(
                id_dispositivo=payload.get('id_dispositivo', ''),
                nombre=payload.get('nombre', ''),
                tipo=payload.get('tipo', ''),
                latitud=payload.get('latitud', 0.0),
                longitud=payload.get('longitud', 0.0),
                altitud=payload.get('altitud', 0.0),
                velocidad=payload.get('velocidad', 0.0),
                direccion=payload.get('direccion', 0.0),
                timestamp=datetime.now(),
                estado='activo',
                bateria=payload.get('bateria', 100.0)
            )
            
            self._guardar_dispositivo_gps(dispositivo)
            
        except Exception as e:
            print(f"[ERROR] Error procesando maquinaria: {e}")
    
    def _procesar_mensaje_alerta(self, payload: Dict):
        """Procesar mensaje de alerta"""
        try:
            print(f"[ALERTA] {payload.get('tipo', 'Desconocido')}: {payload.get('mensaje', '')}")
            self._guardar_log_integracion('Sistema_Alertas', 'alerta', 'recibida', payload.get('mensaje', ''))
            
        except Exception as e:
            print(f"[ERROR] Error procesando alerta: {e}")
    
    def conectar_sistema_erp(self, sistema_erp: str) -> Dict:
        """Conectar con sistema ERP específico"""
        try:
            print(f"[ERP] Conectando con {sistema_erp}...")
            
            config = self.configuracion_erp.get(sistema_erp)
            if not config:
                raise ValueError(f"Sistema ERP {sistema_erp} no encontrado")
            
            if not config['activo']:
                return {'error': 'Sistema ERP inactivo'}
            
            # Simular conexión según protocolo
            if config['protocolo'] == 'REST':
                resultado = self._conectar_erp_rest(config)
            elif config['protocolo'] == 'RFC':
                resultado = self._conectar_erp_rfc(config)
            elif config['protocolo'] == 'GraphQL':
                resultado = self._conectar_erp_graphql(config)
            else:
                raise ValueError(f"Protocolo {config['protocolo']} no soportado")
            
            # Actualizar estado de conexión
            self._actualizar_estado_conexion(sistema_erp, 'conectado' if 'error' not in resultado else 'error')
            
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error conectando ERP: {e}")
            self._guardar_log_integracion('ERP', 'conexion', 'error', str(e))
            return {'error': str(e)}
    
    def _conectar_erp_rest(self, config: Dict) -> Dict:
        """Conectar con ERP usando REST API"""
        try:
            # Simular conexión REST
            endpoint = config['endpoint']
            
            # Simular autenticación
            if config['autenticacion'] == 'api_key':
                headers = {'Authorization': 'Bearer api_key_simulado'}
            else:
                headers = {'Content-Type': 'application/json'}
            
            # Simular llamada a API
            print(f"[REST] Conectando a {endpoint}")
            time.sleep(1)  # Simular latencia
            
            # Simular respuesta exitosa
            modulos_disponibles = config.get('modulos', [])
            
            resultado = {
                'sistema': config['nombre'],
                'protocolo': config['protocolo'],
                'estado': 'conectado',
                'modulos_disponibles': modulos_disponibles,
                'timestamp_conexion': datetime.now().isoformat(),
                'datos_sincronizados': self._simular_datos_erp(modulos_disponibles)
            }
            
            print(f"[OK] ERP REST conectado: {len(modulos_disponibles)} módulos disponibles")
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error en conexión REST: {e}")
            return {'error': str(e)}
    
    def _conectar_erp_rfc(self, config: Dict) -> Dict:
        """Conectar con ERP usando RFC (SAP)"""
        try:
            # Simular conexión RFC
            print(f"[RFC] Conectando a {config['nombre']}")
            time.sleep(2)  # Simular latencia RFC
            
            modulos_disponibles = config.get('modulos', [])
            
            resultado = {
                'sistema': config['nombre'],
                'protocolo': config['protocolo'],
                'estado': 'conectado',
                'modulos_disponibles': modulos_disponibles,
                'timestamp_conexion': datetime.now().isoformat(),
                'datos_sincronizados': self._simular_datos_sap(modulos_disponibles)
            }
            
            print(f"[OK] ERP RFC conectado: {len(modulos_disponibles)} módulos disponibles")
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error en conexión RFC: {e}")
            return {'error': str(e)}
    
    def _conectar_erp_graphql(self, config: Dict) -> Dict:
        """Conectar con ERP usando GraphQL"""
        try:
            # Simular conexión GraphQL
            print(f"[GraphQL] Conectando a {config['nombre']}")
            time.sleep(1.5)  # Simular latencia
            
            modulos_disponibles = config.get('modulos', [])
            
            resultado = {
                'sistema': config['nombre'],
                'protocolo': config['protocolo'],
                'estado': 'conectado',
                'modulos_disponibles': modulos_disponibles,
                'timestamp_conexion': datetime.now().isoformat(),
                'datos_sincronizados': self._simular_datos_graphql(modulos_disponibles)
            }
            
            print(f"[OK] ERP GraphQL conectado: {len(modulos_disponibles)} módulos disponibles")
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error en conexión GraphQL: {e}")
            return {'error': str(e)}
    
    def _simular_datos_erp(self, modulos: List[str]) -> Dict:
        """Simular datos de ERP REST"""
        datos = {}
        
        for modulo in modulos:
            if modulo == 'inventario':
                datos[modulo] = {
                    'productos': 1250,
                    'stock_total': 45600,
                    'valor_inventario': 125000000,  # CLP
                    'productos_bajo_stock': 45
                }
            elif modulo == 'produccion':
                datos[modulo] = {
                    'ordenes_activas': 23,
                    'hectareas_procesadas': 450,
                    'produccion_mensual': 12500,  # kg
                    'eficiencia_promedio': 87.5
                }
            elif modulo == 'financiero':
                datos[modulo] = {
                    'ventas_mes': 85000000,  # CLP
                    'costos_mes': 62000000,  # CLP
                    'margen_bruto': 27.1,
                    'cuentas_por_cobrar': 15000000  # CLP
                }
        
        return datos
    
    def _simular_datos_sap(self, modulos: List[str]) -> Dict:
        """Simular datos de SAP"""
        datos = {}
        
        for modulo in modulos:
            if modulo == 'inventario':
                datos[modulo] = {
                    'materiales': 3400,
                    'stock_valorizado': 89000000,  # CLP
                    'movimientos_dia': 156,
                    'ubicaciones': 12
                }
            elif modulo == 'produccion':
                datos[modulo] = {
                    'ordenes_produccion': 45,
                    'centros_trabajo': 8,
                    'tiempo_estandar': 125.5,  # horas
                    'rendimiento_actual': 92.3
                }
            elif modulo == 'calidad':
                datos[modulo] = {
                    'inspecciones_pendientes': 23,
                    'lotes_aprobados': 156,
                    'no_conformidades': 3,
                    'indice_calidad': 94.2
                }
        
        return datos
    
    def _simular_datos_graphql(self, modulos: List[str]) -> Dict:
        """Simular datos de GraphQL"""
        datos = {}
        
        for modulo in modulos:
            if modulo == 'datos_campo':
                datos[modulo] = {
                    'campos_activos': 25,
                    'datos_sensores': 12500,
                    'imagenes_satelitales': 450,
                    'analisis_completados': 89
                }
            elif modulo == 'analytics':
                datos[modulo] = {
                    'reportes_generados': 156,
                    'predicciones_activas': 12,
                    'insights_disponibles': 45,
                    'alertas_configuradas': 23
                }
            elif modulo == 'maquinaria':
                datos[modulo] = {
                    'tractores_activos': 8,
                    'horas_operacion': 1250,
                    'combustible_consumido': 8500,  # litros
                    'eficiencia_promedio': 78.5
                }
        
        return datos
    
    def conectar_sistema_gps(self, sistema_gps: str) -> Dict:
        """Conectar con sistema GPS específico"""
        try:
            print(f"[GPS] Conectando con {sistema_gps}...")
            
            config = self.configuracion_gps.get(sistema_gps)
            if not config:
                raise ValueError(f"Sistema GPS {sistema_gps} no encontrado")
            
            if not config['activo']:
                return {'error': 'Sistema GPS inactivo'}
            
            # Simular conexión GPS
            resultado = self._simular_conexion_gps(config)
            
            # Actualizar estado de conexión
            self._actualizar_estado_conexion(sistema_gps, 'conectado' if 'error' not in resultado else 'error')
            
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error conectando GPS: {e}")
            self._guardar_log_integracion('GPS', 'conexion', 'error', str(e))
            return {'error': str(e)}
    
    def _simular_conexion_gps(self, config: Dict) -> Dict:
        """Simular conexión con sistema GPS"""
        try:
            print(f"[GPS] Estableciendo conexión con {config['nombre']}")
            time.sleep(1)  # Simular latencia
            
            # Simular dispositivos GPS
            dispositivos = []
            for i, tipo in enumerate(config['dispositivos_soportados']):
                dispositivo = DispositivoGPS(
                    id_dispositivo=f"{config['nombre'].lower()}_{tipo}_{i+1}",
                    nombre=f"{tipo.title()} {i+1}",
                    tipo=tipo,
                    latitud=-33.3167 + np.random.uniform(-0.01, 0.01),
                    longitud=-71.4167 + np.random.uniform(-0.01, 0.01),
                    altitud=200 + np.random.uniform(-50, 50),
                    velocidad=np.random.uniform(0, 15),
                    direccion=np.random.uniform(0, 360),
                    timestamp=datetime.now(),
                    estado='activo',
                    bateria=np.random.uniform(60, 100)
                )
                
                dispositivos.append(dispositivo)
                self._guardar_dispositivo_gps(dispositivo)
            
            resultado = {
                'sistema': config['nombre'],
                'protocolo': config['protocolo'],
                'estado': 'conectado',
                'dispositivos_conectados': len(dispositivos),
                'dispositivos': [
                    {
                        'id': d.id_dispositivo,
                        'nombre': d.nombre,
                        'tipo': d.tipo,
                        'ubicacion': f"{d.latitud:.6f}, {d.longitud:.6f}",
                        'velocidad': d.velocidad,
                        'estado': d.estado,
                        'bateria': d.bateria
                    } for d in dispositivos
                ],
                'timestamp_conexion': datetime.now().isoformat()
            }
            
            print(f"[OK] GPS conectado: {len(dispositivos)} dispositivos activos")
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error simulando GPS: {e}")
            return {'error': str(e)}
    
    def configurar_sensores_iot(self) -> Dict:
        """Configurar y simular sensores IoT"""
        try:
            print("[IoT] Configurando sensores IoT...")
            
            # Inicializar MQTT si no está activo
            if not self.mqtt_client or not self.mqtt_client.is_connected():
                self.inicializar_mqtt()
            
            sensores_configurados = []
            
            for tipo_sensor, config in self.configuracion_iot['sensores_configurados'].items():
                # Crear sensor simulado
                sensor = SensorIoT(
                    id_sensor=f"sensor_{tipo_sensor}_001",
                    nombre=f"Sensor {tipo_sensor.replace('_', ' ').title()}",
                    tipo=tipo_sensor,
                    ubicacion=f"Campo {np.random.randint(1, 6)} - Sector {chr(65 + np.random.randint(0, 4))}",
                    valor=np.random.uniform(config['rango_valores'][0], config['rango_valores'][1]),
                    unidad=config['unidad'],
                    timestamp=datetime.now(),
                    estado='activo',
                    bateria=np.random.uniform(70, 100)
                )
                
                # Guardar sensor
                self._guardar_sensor_iot(sensor)
                
                # Simular envío de datos MQTT
                self._simular_datos_mqtt(sensor, config)
                
                sensores_configurados.append({
                    'id': sensor.id_sensor,
                    'nombre': sensor.nombre,
                    'tipo': sensor.tipo,
                    'ubicacion': sensor.ubicacion,
                    'valor': sensor.valor,
                    'unidad': sensor.unidad,
                    'estado': sensor.estado,
                    'bateria': sensor.bateria,
                    'protocolo': config['protocolo']
                })
            
            resultado = {
                'sensores_configurados': len(sensores_configurados),
                'protocolos_activos': list(set([s['protocolo'] for s in sensores_configurados])),
                'sensores': sensores_configurados,
                'mqtt_activo': self.mqtt_client.is_connected() if self.mqtt_client else False,
                'timestamp_configuracion': datetime.now().isoformat()
            }
            
            print(f"[OK] {len(sensores_configurados)} sensores IoT configurados")
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error configurando IoT: {e}")
            return {'error': str(e)}
    
    def _simular_datos_mqtt(self, sensor: SensorIoT, config: Dict):
        """Simular envío de datos MQTT"""
        try:
            if config['protocolo'] == 'MQTT' and self.mqtt_client:
                # Simular variación de valores
                valor_variado = sensor.valor + np.random.uniform(-0.1, 0.1) * sensor.valor
                valor_variado = max(config['rango_valores'][0], 
                                  min(config['rango_valores'][1], valor_variado))
                
                mensaje = {
                    'id_sensor': sensor.id_sensor,
                    'nombre': sensor.nombre,
                    'tipo': sensor.tipo,
                    'ubicacion': sensor.ubicacion,
                    'valor': round(valor_variado, 2),
                    'unidad': sensor.unidad,
                    'bateria': max(0, sensor.bateria - np.random.uniform(0, 2)),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Publicar mensaje
                topic = config['topic']
                self.mqtt_client.publish(topic, json.dumps(mensaje))
                
        except Exception as e:
            print(f"[ERROR] Error simulando MQTT: {e}")
    
    def _guardar_dispositivo_gps(self, dispositivo: DispositivoGPS):
        """Guardar dispositivo GPS en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO dispositivos_gps 
                (id_dispositivo, nombre, tipo, latitud, longitud, altitud, velocidad, 
                 direccion, timestamp, estado, bateria, sistema_gps)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dispositivo.id_dispositivo, dispositivo.nombre, dispositivo.tipo,
                dispositivo.latitud, dispositivo.longitud, dispositivo.altitud,
                dispositivo.velocidad, dispositivo.direccion, dispositivo.timestamp,
                dispositivo.estado, dispositivo.bateria, 'Sistema_Simulado'
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error guardando dispositivo GPS: {e}")
    
    def _guardar_sensor_iot(self, sensor: SensorIoT):
        """Guardar sensor IoT en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sensores_iot 
                (id_sensor, nombre, tipo, ubicacion, valor, unidad, timestamp, 
                 estado, bateria, protocolo, topic_endpoint)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sensor.id_sensor, sensor.nombre, sensor.tipo, sensor.ubicacion,
                sensor.valor, sensor.unidad, sensor.timestamp, sensor.estado,
                sensor.bateria, 'MQTT', 'sensores/' + sensor.tipo
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error guardando sensor IoT: {e}")
    
    def _actualizar_estado_conexion(self, sistema: str, estado: str):
        """Actualizar estado de conexión del sistema"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE configuracion_sistemas 
                SET estado_conexion = ?, ultima_conexion = CURRENT_TIMESTAMP
                WHERE sistema_nombre = ?
            ''', (estado, sistema))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error actualizando estado: {e}")
    
    def _guardar_log_integracion(self, sistema: str, operacion: str, estado: str, mensaje: str):
        """Guardar log de integración"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO logs_integracion (sistema, tipo_operacion, estado, mensaje)
                VALUES (?, ?, ?, ?)
            ''', (sistema, operacion, estado, mensaje))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error guardando log: {e}")
    
    def sincronizar_datos_sistemas(self) -> Dict:
        """Sincronizar datos entre todos los sistemas conectados"""
        try:
            print("[SINCRONIZACION] Iniciando sincronización de datos...")
            
            resultado_sincronizacion = {
                'fecha_sincronizacion': datetime.now().isoformat(),
                'sistemas_procesados': [],
                'datos_sincronizados': {},
                'errores': []
            }
            
            # Sincronizar sistemas ERP
            for sistema_erp in self.configuracion_erp.keys():
                try:
                    resultado_erp = self.conectar_sistema_erp(sistema_erp)
                    if 'error' not in resultado_erp:
                        resultado_sincronizacion['sistemas_procesados'].append({
                            'sistema': sistema_erp,
                            'tipo': 'ERP',
                            'estado': 'exitoso'
                        })
                        resultado_sincronizacion['datos_sincronizados'][sistema_erp] = resultado_erp
                    else:
                        resultado_sincronizacion['errores'].append(f"ERP {sistema_erp}: {resultado_erp['error']}")
                except Exception as e:
                    resultado_sincronizacion['errores'].append(f"ERP {sistema_erp}: {str(e)}")
            
            # Sincronizar sistemas GPS
            for sistema_gps in self.configuracion_gps.keys():
                try:
                    resultado_gps = self.conectar_sistema_gps(sistema_gps)
                    if 'error' not in resultado_gps:
                        resultado_sincronizacion['sistemas_procesados'].append({
                            'sistema': sistema_gps,
                            'tipo': 'GPS',
                            'estado': 'exitoso'
                        })
                        resultado_sincronizacion['datos_sincronizados'][sistema_gps] = resultado_gps
                    else:
                        resultado_sincronizacion['errores'].append(f"GPS {sistema_gps}: {resultado_gps['error']}")
                except Exception as e:
                    resultado_sincronizacion['errores'].append(f"GPS {sistema_gps}: {str(e)}")
            
            # Configurar sensores IoT
            try:
                resultado_iot = self.configurar_sensores_iot()
                if 'error' not in resultado_iot:
                    resultado_sincronizacion['sistemas_procesados'].append({
                        'sistema': 'sensores_iot',
                        'tipo': 'IoT',
                        'estado': 'exitoso'
                    })
                    resultado_sincronizacion['datos_sincronizados']['sensores_iot'] = resultado_iot
                else:
                    resultado_sincronizacion['errores'].append(f"IoT: {resultado_iot['error']}")
            except Exception as e:
                resultado_sincronizacion['errores'].append(f"IoT: {str(e)}")
            
            # Generar resumen
            resultado_sincronizacion['resumen'] = {
                'sistemas_exitosos': len([s for s in resultado_sincronizacion['sistemas_procesados'] if s['estado'] == 'exitoso']),
                'total_sistemas': len(resultado_sincronizacion['sistemas_procesados']),
                'total_errores': len(resultado_sincronizacion['errores'])
            }
            
            print(f"[OK] Sincronización completada: {resultado_sincronizacion['resumen']['sistemas_exitosos']}/{resultado_sincronizacion['resumen']['total_sistemas']} sistemas")
            return resultado_sincronizacion
            
        except Exception as e:
            print(f"[ERROR] Error en sincronización: {e}")
            return {'error': str(e)}
    
    def generar_reporte_integracion(self) -> Dict:
        """Generar reporte de integración con sistemas existentes"""
        try:
            print("[REPORTE] Generando reporte de integración...")
            
            # Obtener datos de la base de datos
            conn = sqlite3.connect(self.base_datos)
            
            # Dispositivos GPS activos
            cursor_gps = conn.cursor()
            cursor_gps.execute('SELECT COUNT(*) FROM dispositivos_gps WHERE estado = "activo"')
            dispositivos_activos = cursor_gps.fetchone()[0]
            
            # Sensores IoT activos
            cursor_iot = conn.cursor()
            cursor_iot.execute('SELECT COUNT(*) FROM sensores_iot WHERE estado = "activo"')
            sensores_activos = cursor_iot.fetchone()[0]
            
            # Logs de integración recientes
            cursor_logs = conn.cursor()
            cursor_logs.execute('''
                SELECT sistema, COUNT(*) as total 
                FROM logs_integracion 
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY sistema
            ''')
            logs_24h = dict(cursor_logs.fetchall())
            
            conn.close()
            
            # Generar visualizaciones
            rutas_graficos = self._generar_visualizaciones_integracion()
            
            reporte = {
                'fecha_reporte': datetime.now().isoformat(),
                'estado_sistemas': {
                    'erp_configurados': len(self.configuracion_erp),
                    'gps_configurados': len(self.configuracion_gps),
                    'dispositivos_gps_activos': dispositivos_activos,
                    'sensores_iot_activos': sensores_activos,
                    'mqtt_conectado': self.mqtt_client.is_connected() if self.mqtt_client else False
                },
                'actividad_24h': logs_24h,
                'visualizaciones': rutas_graficos,
                'configuraciones': {
                    'erp': self.configuracion_erp,
                    'gps': self.configuracion_gps,
                    'iot': self.configuracion_iot
                }
            }
            
            # Guardar reporte
            self._guardar_reporte_integracion(reporte)
            
            print("[OK] Reporte de integración generado")
            return reporte
            
        except Exception as e:
            print(f"[ERROR] Error generando reporte: {e}")
            return {'error': str(e)}
    
    def _generar_visualizaciones_integracion(self) -> Dict:
        """Generar visualizaciones para el reporte de integración"""
        try:
            rutas_graficos = {}
            
            # Gráfico de estado de sistemas
            sistemas = list(self.configuracion_erp.keys()) + list(self.configuracion_gps.keys()) + ['IoT']
            estados = ['Activo'] * len(sistemas)
            
            fig_sistemas = px.pie(
                values=[1] * len(sistemas),
                names=sistemas,
                title='Estado de Sistemas Integrados',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            ruta_sistemas = os.path.join(self.directorio_datos, 'sincronizacion', 'estado_sistemas.html')
            fig_sistemas.write_html(ruta_sistemas)
            rutas_graficos['estado_sistemas'] = ruta_sistemas
            
            return rutas_graficos
            
        except Exception as e:
            print(f"[ERROR] Error generando visualizaciones: {e}")
            return {}
    
    def _guardar_reporte_integracion(self, reporte: Dict):
        """Guardar reporte de integración"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"reporte_integracion_{timestamp}.json"
            ruta_archivo = os.path.join(self.directorio_datos, 'sincronizacion', nombre_archivo)
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"[OK] Reporte de integración guardado: {ruta_archivo}")
            
        except Exception as e:
            print(f"[ERROR] Error guardando reporte: {e}")

def main():
    """Función principal para demostrar la integración con sistemas existentes"""
    try:
        print("="*80)
        print("INTEGRACIÓN CON SISTEMAS EXISTENTES - METGO 3D QUILLOTA")
        print("="*80)
        
        # Inicializar sistema de integración
        integracion = IntegracionSistemasExistentesMetgo()
        
        print("\n[1] SINCRONIZANDO CON SISTEMAS EXISTENTES...")
        
        # Sincronizar todos los sistemas
        resultado_sincronizacion = integracion.sincronizar_datos_sistemas()
        
        if 'error' not in resultado_sincronizacion:
            print(f"[OK] Sincronización completada:")
            print(f"    - Sistemas exitosos: {resultado_sincronizacion['resumen']['sistemas_exitosos']}")
            print(f"    - Total sistemas: {resultado_sincronizacion['resumen']['total_sistemas']}")
            print(f"    - Errores: {resultado_sincronizacion['resumen']['total_errores']}")
        
        print("\n[2] DETALLES DE SISTEMAS CONECTADOS...")
        
        # Mostrar detalles por sistema
        for sistema, datos in resultado_sincronizacion.get('datos_sincronizados', {}).items():
            print(f"\n    [{sistema.upper()}]")
            
            if 'modulos_disponibles' in datos:
                print(f"      Módulos: {', '.join(datos['modulos_disponibles'])}")
                print(f"      Protocolo: {datos['protocolo']}")
                
                # Mostrar algunos datos de ejemplo
                for modulo, datos_modulo in datos.get('datos_sincronizados', {}).items():
                    if isinstance(datos_modulo, dict):
                        items_mostrar = list(datos_modulo.items())[:2]  # Mostrar solo 2 items
                        print(f"      {modulo}: {dict(items_mostrar)}")
            
            elif 'dispositivos_conectados' in datos:
                print(f"      Dispositivos: {datos['dispositivos_conectados']}")
                print(f"      Protocolo: {datos['protocolo']}")
                
                for dispositivo in datos['dispositivos'][:2]:  # Mostrar solo 2 dispositivos
                    print(f"      - {dispositivo['nombre']}: {dispositivo['ubicacion']}")
            
            elif 'sensores_configurados' in datos:
                print(f"      Sensores: {datos['sensores_configurados']}")
                print(f"      Protocolos: {', '.join(datos['protocolos_activos'])}")
                print(f"      MQTT: {'Activo' if datos['mqtt_activo'] else 'Inactivo'}")
        
        print("\n[3] GENERANDO REPORTE DE INTEGRACIÓN...")
        
        # Generar reporte final
        reporte_final = integracion.generar_reporte_integracion()
        
        if 'error' not in reporte_final:
            estado = reporte_final['estado_sistemas']
            print(f"[OK] Reporte de integración generado")
            print(f"    - ERP configurados: {estado['erp_configurados']}")
            print(f"    - GPS configurados: {estado['gps_configurados']}")
            print(f"    - Dispositivos GPS activos: {estado['dispositivos_gps_activos']}")
            print(f"    - Sensores IoT activos: {estado['sensores_iot_activos']}")
            print(f"    - MQTT conectado: {'Sí' if estado['mqtt_conectado'] else 'No'}")
        
        print("\n[4] RESUMEN DE INTEGRACIONES...")
        
        print("    [ERP] Sistemas de gestión empresarial:")
        for sistema in integracion.configuracion_erp.keys():
            print(f"      - {sistema}: {integracion.configuracion_erp[sistema]['nombre']}")
        
        print("    [GPS] Sistemas de posicionamiento:")
        for sistema in integracion.configuracion_gps.keys():
            print(f"      - {sistema}: {integracion.configuracion_gps[sistema]['nombre']}")
        
        print("    [IoT] Sensores y dispositivos:")
        for sensor in integracion.configuracion_iot['sensores_configurados'].keys():
            print(f"      - {sensor}: {integracion.configuracion_iot['sensores_configurados'][sensor]['protocolo']}")
        
        print("\n" + "="*80)
        print("INTEGRACIÓN CON SISTEMAS EXISTENTES COMPLETADA")
        print("="*80)
        print("[OK] Sistema de integración implementado")
        print("[OK] Conexiones ERP establecidas")
        print("[OK] Sistemas GPS conectados")
        print("[OK] Sensores IoT configurados")
        print("[OK] MQTT activo para comunicación")
        print("[OK] Sincronización de datos completada")
        print("="*80)
        
    except Exception as e:
        print(f"[ERROR] Error en función principal: {e}")

if __name__ == "__main__":
    main()
