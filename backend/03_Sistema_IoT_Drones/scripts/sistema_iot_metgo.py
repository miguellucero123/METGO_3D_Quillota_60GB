#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 SISTEMA IoT PARA METGO 3D
Sistema Meteorológico Agrícola Quillota - Internet de las Cosas
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
import socket
import struct
import random

# IoT y Comunicaciones
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Configuración
warnings.filterwarnings('ignore')

class SensorIoT:
    """Clase para simular sensores IoT"""
    
    def __init__(self, sensor_id: str, tipo: str, ubicacion: Dict, configuracion: Dict):
        self.sensor_id = sensor_id
        self.tipo = tipo
        self.ubicacion = ubicacion
        self.configuracion = configuracion
        self.estado = 'activo'
        self.ultima_lectura = None
        self.lecturas = []
        self.bateria = 100.0
        self.senal = 85.0
        
    def leer_sensor(self) -> Dict:
        """Simular lectura del sensor"""
        try:
            timestamp = datetime.now()
            
            # Generar datos según el tipo de sensor
            if self.tipo == 'temperatura':
                valor = 15 + 10 * np.sin(2 * np.pi * timestamp.hour / 24) + random.gauss(0, 2)
            elif self.tipo == 'humedad':
                valor = 60 + 20 * np.sin(2 * np.pi * timestamp.hour / 24) + random.gauss(0, 5)
                valor = max(0, min(100, valor))
            elif self.tipo == 'precipitacion':
                valor = random.exponential(0.5) if random.random() > 0.9 else 0
            elif self.tipo == 'viento_velocidad':
                valor = random.gamma(2, 2)
            elif self.tipo == 'viento_direccion':
                valor = random.uniform(0, 360)
            elif self.tipo == 'presion':
                valor = 1013 + random.gauss(0, 10)
            elif self.tipo == 'radiacion_solar':
                valor = max(0, 800 * np.sin(np.pi * timestamp.hour / 24) + random.gauss(0, 50))
            else:
                valor = random.uniform(0, 100)
            
            # Crear lectura
            lectura = {
                'sensor_id': self.sensor_id,
                'tipo': self.tipo,
                'timestamp': timestamp.isoformat(),
                'valor': round(valor, 2),
                'unidad': self.configuracion.get('unidad', 'N/A'),
                'ubicacion': self.ubicacion,
                'bateria': round(self.bateria, 1),
                'senal': round(self.senal, 1),
                'estado': self.estado
            }
            
            # Actualizar estado del sensor
            self.ultima_lectura = lectura
            self.lecturas.append(lectura)
            
            # Simular consumo de batería
            self.bateria -= 0.01
            if self.bateria < 0:
                self.bateria = 0
                self.estado = 'bateria_baja'
            
            # Simular variación de señal
            self.senal += random.gauss(0, 2)
            self.senal = max(0, min(100, self.senal))
            
            return lectura
            
        except Exception as e:
            print(f"Error leyendo sensor {self.sensor_id}: {e}")
            return {}
    
    def obtener_estado(self) -> Dict:
        """Obtener estado del sensor"""
        return {
            'sensor_id': self.sensor_id,
            'tipo': self.tipo,
            'estado': self.estado,
            'bateria': self.bateria,
            'senal': self.senal,
            'ultima_lectura': self.ultima_lectura,
            'total_lecturas': len(self.lecturas)
        }

class GatewayIoT:
    """Gateway para comunicación IoT"""
    
    def __init__(self, gateway_id: str, configuracion: Dict):
        self.gateway_id = gateway_id
        self.configuracion = configuracion
        self.sensores = {}
        self.conexiones = {}
        self.estado = 'activo'
        self.ultima_comunicacion = None
        
    def agregar_sensor(self, sensor: SensorIoT):
        """Agregar sensor al gateway"""
        self.sensores[sensor.sensor_id] = sensor
        print(f"✅ Sensor {sensor.sensor_id} agregado al gateway {self.gateway_id}")
    
    def leer_todos_los_sensores(self) -> List[Dict]:
        """Leer todos los sensores conectados"""
        lecturas = []
        for sensor in self.sensores.values():
            try:
                lectura = sensor.leer_sensor()
                if lectura:
                    lecturas.append(lectura)
            except Exception as e:
                print(f"Error leyendo sensor {sensor.sensor_id}: {e}")
        
        self.ultima_comunicacion = datetime.now()
        return lecturas
    
    def obtener_estado_gateway(self) -> Dict:
        """Obtener estado del gateway"""
        return {
            'gateway_id': self.gateway_id,
            'estado': self.estado,
            'total_sensores': len(self.sensores),
            'ultima_comunicacion': self.ultima_comunicacion.isoformat() if self.ultima_comunicacion else None,
            'sensores': {sensor_id: sensor.obtener_estado() for sensor_id, sensor in self.sensores.items()}
        }

class SistemaIoTMETGO:
    """Sistema IoT principal para METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/iot',
            'directorio_logs': 'logs/iot',
            'directorio_config': 'config/iot',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Configuración de red
        self.configuracion_red = {
            'mqtt_broker': 'localhost',
            'mqtt_port': 1883,
            'mqtt_topic': 'metgo3d/sensores',
            'http_port': 8080,
            'udp_port': 9999
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Inicializar componentes
        self.gateways = {}
        self.sensores = {}
        self.datos_iot = []
        self.estadisticas = {}
        
        # Configurar MQTT
        if MQTT_AVAILABLE:
            self._configurar_mqtt()
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        try:
            for directorio in self.configuracion.values():
                if isinstance(directorio, str) and '/' in directorio:
                    Path(directorio).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")
    
    def _configurar_mqtt(self):
        """Configurar cliente MQTT"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            print("✅ Cliente MQTT configurado")
        except Exception as e:
            print(f"Error configurando MQTT: {e}")
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback de conexión MQTT"""
        if rc == 0:
            print("✅ Conectado al broker MQTT")
            client.subscribe(self.configuracion_red['mqtt_topic'])
        else:
            print(f"❌ Error conectando al broker MQTT: {rc}")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """Callback de mensaje MQTT"""
        try:
            mensaje = json.loads(msg.payload.decode())
            self.procesar_mensaje_iot(mensaje)
        except Exception as e:
            print(f"Error procesando mensaje MQTT: {e}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Callback de desconexión MQTT"""
        print("⚠️ Desconectado del broker MQTT")
    
    def crear_red_sensores(self, configuracion_red: Dict) -> bool:
        """Crear red de sensores IoT"""
        try:
            print("🌐 Creando red de sensores IoT...")
            
            # Ubicaciones en Quillota
            ubicaciones_quillota = [
                {'nombre': 'Centro', 'latitud': -32.8833, 'longitud': -71.2333, 'altitud': 127},
                {'nombre': 'Norte', 'latitud': -32.8500, 'longitud': -71.2000, 'altitud': 150},
                {'nombre': 'Sur', 'latitud': -32.9200, 'longitud': -71.2500, 'altitud': 100},
                {'nombre': 'Este', 'latitud': -32.8800, 'longitud': -71.1800, 'altitud': 200},
                {'nombre': 'Oeste', 'latitud': -32.8900, 'longitud': -71.2800, 'altitud': 80}
            ]
            
            # Tipos de sensores
            tipos_sensores = [
                {'tipo': 'temperatura', 'unidad': '°C', 'frecuencia': 60},
                {'tipo': 'humedad', 'unidad': '%', 'frecuencia': 60},
                {'tipo': 'precipitacion', 'unidad': 'mm', 'frecuencia': 300},
                {'tipo': 'viento_velocidad', 'unidad': 'm/s', 'frecuencia': 30},
                {'tipo': 'viento_direccion', 'unidad': '°', 'frecuencia': 30},
                {'tipo': 'presion', 'unidad': 'hPa', 'frecuencia': 60},
                {'tipo': 'radiacion_solar', 'unidad': 'W/m²', 'frecuencia': 300}
            ]
            
            # Crear gateways
            for i, ubicacion in enumerate(ubicaciones_quillota):
                gateway_id = f"gateway_{ubicacion['nombre'].lower()}"
                gateway = GatewayIoT(gateway_id, {
                    'ubicacion': ubicacion,
                    'frecuencia_comunicacion': 60
                })
                
                # Crear sensores para cada gateway
                for j, tipo_sensor in enumerate(tipos_sensores):
                    sensor_id = f"{gateway_id}_sensor_{tipo_sensor['tipo']}"
                    sensor = SensorIoT(
                        sensor_id=sensor_id,
                        tipo=tipo_sensor['tipo'],
                        ubicacion=ubicacion,
                        configuracion=tipo_sensor
                    )
                    
                    gateway.agregar_sensor(sensor)
                    self.sensores[sensor_id] = sensor
                
                self.gateways[gateway_id] = gateway
            
            print(f"✅ Red de sensores creada: {len(self.gateways)} gateways, {len(self.sensores)} sensores")
            return True
            
        except Exception as e:
            print(f"Error creando red de sensores: {e}")
            return False
    
    def iniciar_monitoreo_iot(self, duracion_minutos: int = 60) -> bool:
        """Iniciar monitoreo de sensores IoT"""
        try:
            print(f"🚀 Iniciando monitoreo IoT por {duracion_minutos} minutos...")
            
            inicio = datetime.now()
            fin = inicio + timedelta(minutes=duracion_minutos)
            
            while datetime.now() < fin:
                # Leer todos los sensores
                for gateway in self.gateways.values():
                    lecturas = gateway.leer_todos_los_sensores()
                    self.datos_iot.extend(lecturas)
                
                # Procesar datos
                self.procesar_datos_iot()
                
                # Esperar antes de la siguiente lectura
                time.sleep(60)  # 1 minuto
            
            print("✅ Monitoreo IoT completado")
            return True
            
        except Exception as e:
            print(f"Error en monitoreo IoT: {e}")
            return False
    
    def procesar_datos_iot(self) -> bool:
        """Procesar datos de sensores IoT"""
        try:
            if not self.datos_iot:
                return False
            
            # Convertir a DataFrame
            df = pd.DataFrame(self.datos_iot)
            
            # Agregar timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Calcular estadísticas
            self.estadisticas = {
                'total_lecturas': len(df),
                'sensores_activos': df['sensor_id'].nunique(),
                'tipos_sensores': df['tipo'].nunique(),
                'rango_temporal': {
                    'inicio': df.index.min().isoformat(),
                    'fin': df.index.max().isoformat()
                },
                'estadisticas_por_tipo': {}
            }
            
            # Estadísticas por tipo de sensor
            for tipo in df['tipo'].unique():
                datos_tipo = df[df['tipo'] == tipo]['valor']
                self.estadisticas['estadisticas_por_tipo'][tipo] = {
                    'count': len(datos_tipo),
                    'mean': round(datos_tipo.mean(), 2),
                    'std': round(datos_tipo.std(), 2),
                    'min': round(datos_tipo.min(), 2),
                    'max': round(datos_tipo.max(), 2)
                }
            
            # Guardar datos
            self.guardar_datos_iot(df)
            
            print(f"✅ Datos IoT procesados: {len(df)} lecturas")
            return True
            
        except Exception as e:
            print(f"Error procesando datos IoT: {e}")
            return False
    
    def guardar_datos_iot(self, df: pd.DataFrame) -> bool:
        """Guardar datos IoT"""
        try:
            # Guardar como CSV
            archivo_csv = f"{self.configuracion['directorio_datos']}/datos_iot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(archivo_csv)
            
            # Guardar como JSON
            archivo_json = f"{self.configuracion['directorio_datos']}/datos_iot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            df.reset_index().to_json(archivo_json, orient='records', date_format='iso')
            
            print(f"✅ Datos IoT guardados: {archivo_csv}")
            return True
            
        except Exception as e:
            print(f"Error guardando datos IoT: {e}")
            return False
    
    def procesar_mensaje_iot(self, mensaje: Dict) -> bool:
        """Procesar mensaje de sensor IoT"""
        try:
            # Validar mensaje
            if not self.validar_mensaje_iot(mensaje):
                return False
            
            # Agregar a datos
            self.datos_iot.append(mensaje)
            
            # Procesar en tiempo real
            self.procesar_datos_iot()
            
            return True
            
        except Exception as e:
            print(f"Error procesando mensaje IoT: {e}")
            return False
    
    def validar_mensaje_iot(self, mensaje: Dict) -> bool:
        """Validar mensaje de sensor IoT"""
        try:
            campos_requeridos = ['sensor_id', 'tipo', 'timestamp', 'valor']
            
            for campo in campos_requeridos:
                if campo not in mensaje:
                    print(f"Campo requerido faltante: {campo}")
                    return False
            
            # Validar tipos de datos
            if not isinstance(mensaje['valor'], (int, float)):
                print("Valor debe ser numérico")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error validando mensaje IoT: {e}")
            return False
    
    def conectar_mqtt(self) -> bool:
        """Conectar al broker MQTT"""
        try:
            if not MQTT_AVAILABLE:
                print("⚠️ MQTT no disponible")
                return False
            
            self.mqtt_client.connect(
                self.configuracion_red['mqtt_broker'],
                self.configuracion_red['mqtt_port'],
                60
            )
            
            self.mqtt_client.loop_start()
            print("✅ Conectado al broker MQTT")
            return True
            
        except Exception as e:
            print(f"Error conectando MQTT: {e}")
            return False
    
    def desconectar_mqtt(self) -> bool:
        """Desconectar del broker MQTT"""
        try:
            if MQTT_AVAILABLE and hasattr(self, 'mqtt_client'):
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
                print("✅ Desconectado del broker MQTT")
            
            return True
            
        except Exception as e:
            print(f"Error desconectando MQTT: {e}")
            return False
    
    def publicar_datos_iot(self, datos: List[Dict]) -> bool:
        """Publicar datos IoT via MQTT"""
        try:
            if not MQTT_AVAILABLE:
                print("⚠️ MQTT no disponible")
                return False
            
            for dato in datos:
                mensaje = json.dumps(dato)
                self.mqtt_client.publish(
                    self.configuracion_red['mqtt_topic'],
                    mensaje
                )
            
            print(f"✅ {len(datos)} mensajes publicados via MQTT")
            return True
            
        except Exception as e:
            print(f"Error publicando datos MQTT: {e}")
            return False
    
    def obtener_estado_sistema_iot(self) -> Dict:
        """Obtener estado del sistema IoT"""
        try:
            estado = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D IoT',
                'version': self.configuracion['version'],
                'gateways': len(self.gateways),
                'sensores': len(self.sensores),
                'total_lecturas': len(self.datos_iot),
                'estadisticas': self.estadisticas,
                'estado_gateways': {}
            }
            
            # Estado de gateways
            for gateway_id, gateway in self.gateways.items():
                estado['estado_gateways'][gateway_id] = gateway.obtener_estado_gateway()
            
            return estado
            
        except Exception as e:
            print(f"Error obteniendo estado del sistema: {e}")
            return {}
    
    def generar_reporte_iot(self) -> str:
        """Generar reporte del sistema IoT"""
        try:
            print("📋 Generando reporte del sistema IoT...")
            
            estado = self.obtener_estado_sistema_iot()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema IoT',
                'version': self.configuracion['version'],
                'resumen': {
                    'gateways_activos': len(self.gateways),
                    'sensores_activos': len(self.sensores),
                    'total_lecturas': len(self.datos_iot),
                    'tiempo_operacion': 'N/A'
                },
                'estado_sistema': estado,
                'recomendaciones': [
                    "Monitorear el estado de batería de los sensores",
                    "Verificar la calidad de la señal de comunicación",
                    "Implementar alertas automáticas para fallos de sensores",
                    "Optimizar la frecuencia de lectura según las necesidades"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"sistema_iot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Reporte IoT generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            print(f"Error generando reporte IoT: {e}")
            return ""

def main():
    """Función principal del sistema IoT"""
    print("🌐 SISTEMA IoT PARA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Internet de las Cosas")
    print("=" * 80)
    
    try:
        # Crear sistema IoT
        sistema_iot = SistemaIoTMETGO()
        
        # Crear red de sensores
        print("\n🌐 Creando red de sensores...")
        if not sistema_iot.crear_red_sensores({}):
            print("❌ Error creando red de sensores")
            return False
        
        # Iniciar monitoreo
        print("\n🚀 Iniciando monitoreo IoT...")
        if not sistema_iot.iniciar_monitoreo_iot(duracion_minutos=5):
            print("❌ Error en monitoreo IoT")
            return False
        
        # Generar reporte
        print("\n📋 Generando reporte...")
        reporte = sistema_iot.generar_reporte_iot()
        
        if reporte:
            print(f"\n✅ Sistema IoT completado exitosamente")
            print(f"📄 Reporte generado: {reporte}")
        else:
            print("\n⚠️ Error generando reporte")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en sistema IoT: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

