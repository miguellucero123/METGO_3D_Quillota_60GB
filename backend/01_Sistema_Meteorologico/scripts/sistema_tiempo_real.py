#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Tiempo Real METGO 3D
Características avanzadas de tiempo real para el sistema meteorológico
"""

import asyncio
import websockets
import json
import threading
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import queue
# import sseclient  # No necesario para esta implementación
import requests
from gestor_datos_meteorologicos import GestorDatosMeteorologicos

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SistemaTiempoReal:
    """Sistema de tiempo real para datos meteorológicos"""
    
    def __init__(self, gestor_datos: GestorDatosMeteorologicos):
        self.gestor_datos = gestor_datos
        self.websocket_server = None
        self.clients = set()
        self.running = False
        
        # Cola de notificaciones
        self.notification_queue = queue.Queue()
        
        # Configuración
        self.config = {
            'websocket_port': 8765,
            'update_interval': 30,  # segundos
            'max_clients': 50,
            'enable_alerts': True,
            'alert_thresholds': {
                'temperature_high': 35,
                'temperature_low': 5,
                'precipitation_heavy': 20,
                'wind_strong': 40,
                'humidity_extreme_high': 85,
                'humidity_extreme_low': 25
            }
        }
    
    async def start_websocket_server(self):
        """Iniciar servidor WebSocket para tiempo real"""
        try:
            self.websocket_server = await websockets.serve(
                self.handle_client,
                "localhost",
                self.config['websocket_port']
            )
            logger.info(f"Servidor WebSocket iniciado en puerto {self.config['websocket_port']}")
            
            # Iniciar loop de actualización
            await self.update_loop()
            
        except Exception as e:
            logger.error(f"Error iniciando servidor WebSocket: {e}")
    
    async def handle_client(self, websocket, path):
        """Manejar conexión de cliente WebSocket"""
        if len(self.clients) >= self.config['max_clients']:
            await websocket.close(code=1013, reason="Servidor lleno")
            return
        
        self.clients.add(websocket)
        client_ip = websocket.remote_address[0]
        logger.info(f"Cliente conectado desde {client_ip}")
        
        try:
            # Enviar datos iniciales
            await self.send_initial_data(websocket)
            
            # Mantener conexión activa
            await websocket.wait_closed()
            
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Cliente desconectado: {client_ip}")
        except Exception as e:
            logger.error(f"Error manejando cliente: {e}")
        finally:
            self.clients.discard(websocket)
    
    async def send_initial_data(self, websocket):
        """Enviar datos iniciales al cliente"""
        try:
            datos = self.gestor_datos.cargar_datos(1)  # Último dato
            
            if datos:
                mensaje = {
                    'type': 'initial_data',
                    'timestamp': datetime.now().isoformat(),
                    'data': datos[0]
                }
                
                await websocket.send(json.dumps(mensaje))
                
        except Exception as e:
            logger.error(f"Error enviando datos iniciales: {e}")
    
    async def update_loop(self):
        """Loop principal de actualización"""
        while self.running:
            try:
                # Actualizar datos
                await self.update_weather_data()
                
                # Verificar alertas
                if self.config['enable_alerts']:
                    await self.check_alerts()
                
                # Enviar actualizaciones a clientes
                await self.broadcast_updates()
                
                # Esperar intervalo
                await asyncio.sleep(self.config['update_interval'])
                
            except Exception as e:
                logger.error(f"Error en loop de actualización: {e}")
                await asyncio.sleep(5)  # Esperar antes de reintentar
    
    async def update_weather_data(self):
        """Actualizar datos meteorológicos"""
        try:
            # Intentar actualizar desde APIs
            if self.gestor_datos.actualizar_datos():
                logger.info("Datos meteorológicos actualizados")
            else:
                logger.warning("No se pudieron actualizar los datos")
                
        except Exception as e:
            logger.error(f"Error actualizando datos meteorológicos: {e}")
    
    async def check_alerts(self):
        """Verificar alertas meteorológicas"""
        try:
            datos = self.gestor_datos.cargar_datos(1)
            
            if not datos:
                return
            
            ultimo_dato = datos[0]
            alertas = []
            
            # Verificar umbrales de alerta
            thresholds = self.config['alert_thresholds']
            
            if ultimo_dato['temperatura_max'] > thresholds['temperature_high']:
                alertas.append({
                    'type': 'temperature_high',
                    'level': 'critical',
                    'message': f"Temperatura muy alta: {ultimo_dato['temperatura_max']:.1f}°C",
                    'value': ultimo_dato['temperatura_max']
                })
            
            if ultimo_dato['temperatura_min'] < thresholds['temperature_low']:
                alertas.append({
                    'type': 'temperature_low',
                    'level': 'critical',
                    'message': f"Temperatura muy baja: {ultimo_dato['temperatura_min']:.1f}°C",
                    'value': ultimo_dato['temperatura_min']
                })
            
            if ultimo_dato['precipitacion'] > thresholds['precipitation_heavy']:
                alertas.append({
                    'type': 'precipitation_heavy',
                    'level': 'warning',
                    'message': f"Lluvia intensa: {ultimo_dato['precipitacion']:.1f} mm",
                    'value': ultimo_dato['precipitacion']
                })
            
            if ultimo_dato['viento_velocidad'] > thresholds['wind_strong']:
                alertas.append({
                    'type': 'wind_strong',
                    'level': 'warning',
                    'message': f"Viento fuerte: {ultimo_dato['viento_velocidad']:.1f} km/h",
                    'value': ultimo_dato['viento_velocidad']
                })
            
            if ultimo_dato['humedad_relativa'] > thresholds['humidity_extreme_high']:
                alertas.append({
                    'type': 'humidity_high',
                    'level': 'info',
                    'message': f"Humedad muy alta: {ultimo_dato['humedad_relativa']:.1f}%",
                    'value': ultimo_dato['humedad_relativa']
                })
            
            if ultimo_dato['humedad_relativa'] < thresholds['humidity_extreme_low']:
                alertas.append({
                    'type': 'humidity_low',
                    'level': 'info',
                    'message': f"Humedad muy baja: {ultimo_dato['humedad_relativa']:.1f}%",
                    'value': ultimo_dato['humedad_relativa']
                })
            
            # Enviar alertas si las hay
            if alertas:
                await self.send_alerts(alertas)
                
        except Exception as e:
            logger.error(f"Error verificando alertas: {e}")
    
    async def send_alerts(self, alertas: List[Dict]):
        """Enviar alertas a clientes conectados"""
        try:
            mensaje = {
                'type': 'alerts',
                'timestamp': datetime.now().isoformat(),
                'alerts': alertas
            }
            
            await self.broadcast_message(mensaje)
            
            # También agregar a cola de notificaciones
            self.notification_queue.put(mensaje)
            
        except Exception as e:
            logger.error(f"Error enviando alertas: {e}")
    
    async def broadcast_updates(self):
        """Transmitir actualizaciones a todos los clientes"""
        try:
            datos = self.gestor_datos.cargar_datos(1)
            
            if not datos:
                return
            
            mensaje = {
                'type': 'update',
                'timestamp': datetime.now().isoformat(),
                'data': datos[0]
            }
            
            await self.broadcast_message(mensaje)
            
        except Exception as e:
            logger.error(f"Error transmitiendo actualizaciones: {e}")
    
    async def broadcast_message(self, message: Dict):
        """Transmitir mensaje a todos los clientes conectados"""
        if not self.clients:
            return
        
        message_str = json.dumps(message)
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Error enviando mensaje a cliente: {e}")
                disconnected_clients.add(client)
        
        # Remover clientes desconectados
        self.clients -= disconnected_clients
    
    def start(self):
        """Iniciar sistema de tiempo real"""
        self.running = True
        
        # Iniciar servidor WebSocket en hilo separado
        self.websocket_thread = threading.Thread(
            target=self._run_websocket_server,
            daemon=True
        )
        self.websocket_thread.start()
        
        logger.info("Sistema de tiempo real iniciado")
    
    def _run_websocket_server(self):
        """Ejecutar servidor WebSocket en hilo separado"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.start_websocket_server())
        except Exception as e:
            logger.error(f"Error ejecutando servidor WebSocket: {e}")
        finally:
            loop.close()
    
    def stop(self):
        """Detener sistema de tiempo real"""
        self.running = False
        
        # Cerrar todas las conexiones WebSocket
        if self.websocket_server:
            self.websocket_server.close()
        
        logger.info("Sistema de tiempo real detenido")
    
    def get_client_count(self) -> int:
        """Obtener número de clientes conectados"""
        return len(self.clients)
    
    def get_notifications(self) -> List[Dict]:
        """Obtener notificaciones pendientes"""
        notifications = []
        
        while not self.notification_queue.empty():
            try:
                notification = self.notification_queue.get_nowait()
                notifications.append(notification)
            except queue.Empty:
                break
        
        return notifications

class ClienteTiempoReal:
    """Cliente para conectar al sistema de tiempo real"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.websocket = None
        self.running = False
        self.callbacks = {
            'update': [],
            'alerts': [],
            'initial_data': []
        }
    
    async def connect(self):
        """Conectar al servidor WebSocket"""
        try:
            uri = f"ws://{self.host}:{self.port}"
            self.websocket = await websockets.connect(uri)
            self.running = True
            
            logger.info(f"Conectado al servidor WebSocket: {uri}")
            
            # Iniciar loop de recepción
            await self.receive_loop()
            
        except Exception as e:
            logger.error(f"Error conectando al servidor: {e}")
    
    async def receive_loop(self):
        """Loop de recepción de mensajes"""
        try:
            while self.running:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                await self.handle_message(data)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("Conexión cerrada por el servidor")
        except Exception as e:
            logger.error(f"Error en loop de recepción: {e}")
    
    async def handle_message(self, data: Dict):
        """Manejar mensaje recibido"""
        message_type = data.get('type')
        
        if message_type in self.callbacks:
            for callback in self.callbacks[message_type]:
                try:
                    await callback(data)
                except Exception as e:
                    logger.error(f"Error en callback: {e}")
    
    def on_update(self, callback):
        """Registrar callback para actualizaciones"""
        self.callbacks['update'].append(callback)
    
    def on_alert(self, callback):
        """Registrar callback para alertas"""
        self.callbacks['alerts'].append(callback)
    
    def on_initial_data(self, callback):
        """Registrar callback para datos iniciales"""
        self.callbacks['initial_data'].append(callback)
    
    async def disconnect(self):
        """Desconectar del servidor"""
        self.running = False
        
        if self.websocket:
            await self.websocket.close()
        
        logger.info("Desconectado del servidor WebSocket")

# Función de utilidad para iniciar el sistema
def iniciar_sistema_tiempo_real(gestor_datos: GestorDatosMeteorologicos) -> SistemaTiempoReal:
    """Iniciar sistema de tiempo real"""
    sistema = SistemaTiempoReal(gestor_datos)
    sistema.start()
    return sistema

if __name__ == "__main__":
    # Prueba del sistema de tiempo real
    print("=== Prueba del Sistema de Tiempo Real ===")
    
    # Crear gestor de datos
    gestor = GestorDatosMeteorologicos()
    
    # Iniciar sistema de tiempo real
    sistema = iniciar_sistema_tiempo_real(gestor)
    
    try:
        print("Sistema de tiempo real ejecutándose...")
        print("Presiona Ctrl+C para detener")
        
        while True:
            time.sleep(1)
            clientes = sistema.get_client_count()
            if clientes > 0:
                print(f"Clientes conectados: {clientes}")
            
    except KeyboardInterrupt:
        print("\nDeteniendo sistema...")
        sistema.stop()
        gestor.detener_actualizacion_automatica()
        print("Sistema detenido correctamente")
