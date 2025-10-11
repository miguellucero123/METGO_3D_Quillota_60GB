#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONECTOR APIs AVANZADAS - METGO 3D
Conectores para APIs externas y servicios web avanzados
"""

import os
import json
import time
import requests
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import hashlib
import hmac
import base64
from urllib.parse import urlencode

class ConectorAPIsAvanzadas:
    """Conector para APIs avanzadas del sistema METGO 3D"""
    
    def __init__(self):
        self.logger = logging.getLogger('APIS_AVANZADAS_CONNECTOR')
        self.db_path = 'data/apis_avanzadas.db'
        self.config_path = 'config/apis_config.json'
        
        # Configuracion de APIs
        self.apis_config = {
            'openweather': {
                'base_url': 'https://api.openweathermap.org/data/2.5',
                'api_key': os.getenv('OPENWEATHER_API_KEY', 'demo_key'),
                'endpoints': {
                    'current': '/weather',
                    'forecast': '/forecast',
                    'historical': '/onecall/timemachine'
                }
            },
            'openmeteo': {
                'base_url': 'https://api.open-meteo.com/v1',
                'api_key': None,
                'endpoints': {
                    'current': '/forecast',
                    'historical': '/forecast'
                }
            },
            'nasa': {
                'base_url': 'https://api.nasa.gov',
                'api_key': os.getenv('NASA_API_KEY', 'demo_key'),
                'endpoints': {
                    'earth_imagery': '/planetary/earth/imagery',
                    'asteroids': '/neo/rest/v1/feed'
                }
            },
            'google_maps': {
                'base_url': 'https://maps.googleapis.com/maps/api',
                'api_key': os.getenv('GOOGLE_MAPS_API_KEY', 'demo_key'),
                'endpoints': {
                    'geocoding': '/geocode/json',
                    'elevation': '/elevation/json'
                }
            }
        }
        
        # Inicializar base de datos
        self._inicializar_db()
    
    def _inicializar_db(self):
        """Inicializar base de datos de APIs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla de llamadas a APIs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS llamadas_api (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    api_name TEXT,
                    endpoint TEXT,
                    status_code INTEGER,
                    response_time_ms REAL,
                    success BOOLEAN,
                    error_message TEXT
                )
            ''')
            
            # Tabla de datos de APIs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datos_api (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    api_name TEXT,
                    data_type TEXT,
                    data_json TEXT,
                    processed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error inicializando DB de APIs: {e}")
    
    def _hacer_llamada_api(self, api_name: str, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Hacer llamada a una API externa"""
        try:
            if api_name not in self.apis_config:
                return {'error': f'API {api_name} no configurada'}
            
            config = self.apis_config[api_name]
            url = f"{config['base_url']}{config['endpoints'][endpoint]}"
            
            # Agregar API key si existe
            if config['api_key']:
                params = params or {}
                params['appid'] = config['api_key']
            
            # Hacer llamada
            start_time = time.time()
            response = requests.get(url, params=params, timeout=30)
            response_time = (time.time() - start_time) * 1000
            
            # Guardar en base de datos
            self._guardar_llamada_api(api_name, endpoint, response.status_code, response_time, response.status_code == 200)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json(),
                    'response_time_ms': response_time,
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'response_time_ms': response_time,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            self.logger.error(f"Error llamando API {api_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _guardar_llamada_api(self, api_name: str, endpoint: str, status_code: int, response_time: float, success: bool):
        """Guardar llamada a API en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO llamadas_api (api_name, endpoint, status_code, response_time_ms, success)
                VALUES (?, ?, ?, ?, ?)
            ''', (api_name, endpoint, status_code, response_time, success))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error guardando llamada API: {e}")
    
    def obtener_datos_openweather(self, lat: float = -32.8833, lon: float = -71.25) -> Dict[str, Any]:
        """Obtener datos de OpenWeather API"""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'units': 'metric',
                'lang': 'es'
            }
            
            resultado = self._hacer_llamada_api('openweather', 'current', params)
            
            if resultado['success']:
                # Procesar datos
                datos = resultado['data']
                datos_procesados = {
                    'temperatura': datos['main']['temp'],
                    'humedad': datos['main']['humidity'],
                    'presion': datos['main']['pressure'],
                    'descripcion': datos['weather'][0]['description'],
                    'viento_velocidad': datos['wind']['speed'],
                    'viento_direccion': datos['wind'].get('deg', 0),
                    'nubosidad': datos['clouds']['all'],
                    'visibilidad': datos.get('visibility', 0),
                    'timestamp': datetime.now().isoformat(),
                    'fuente': 'OpenWeather'
                }
                
                # Guardar datos procesados
                self._guardar_datos_api('openweather', 'current_weather', datos_procesados)
                
                return datos_procesados
            else:
                return resultado
                
        except Exception as e:
            self.logger.error(f"Error obteniendo datos OpenWeather: {e}")
            return {'error': str(e)}
    
    def obtener_datos_nasa_earth(self, lat: float = -32.8833, lon: float = -71.25) -> Dict[str, Any]:
        """Obtener datos de NASA Earth API"""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'dim': 0.1
            }
            
            resultado = self._hacer_llamada_api('nasa', 'earth_imagery', params)
            
            if resultado['success']:
                datos = resultado['data']
                datos_procesados = {
                    'url_imagen': datos['url'],
                    'fecha': datos['date'],
                    'coordenadas': {'lat': lat, 'lon': lon},
                    'timestamp': datetime.now().isoformat(),
                    'fuente': 'NASA Earth'
                }
                
                # Guardar datos procesados
                self._guardar_datos_api('nasa', 'earth_imagery', datos_procesados)
                
                return datos_procesados
            else:
                return resultado
                
        except Exception as e:
            self.logger.error(f"Error obteniendo datos NASA Earth: {e}")
            return {'error': str(e)}
    
    def obtener_elevacion_google_maps(self, lat: float = -32.8833, lon: float = -71.25) -> Dict[str, Any]:
        """Obtener elevacion de Google Maps API"""
        try:
            params = {
                'locations': f"{lat},{lon}",
                'key': self.apis_config['google_maps']['api_key']
            }
            
            resultado = self._hacer_llamada_api('google_maps', 'elevation', params)
            
            if resultado['success']:
                datos = resultado['data']
                if 'results' in datos and len(datos['results']) > 0:
                    elevacion = datos['results'][0]['elevation']
                    datos_procesados = {
                        'elevacion': elevacion,
                        'coordenadas': {'lat': lat, 'lon': lon},
                        'timestamp': datetime.now().isoformat(),
                        'fuente': 'Google Maps'
                    }
                    
                    # Guardar datos procesados
                    self._guardar_datos_api('google_maps', 'elevation', datos_procesados)
                    
                    return datos_procesados
                else:
                    return {'error': 'No se encontraron datos de elevacion'}
            else:
                return resultado
                
        except Exception as e:
            self.logger.error(f"Error obteniendo elevacion Google Maps: {e}")
            return {'error': str(e)}
    
    def _guardar_datos_api(self, api_name: str, data_type: str, data: Dict[str, Any]):
        """Guardar datos de API en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO datos_api (api_name, data_type, data_json)
                VALUES (?, ?, ?)
            ''', (api_name, data_type, json.dumps(data, ensure_ascii=False)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error guardando datos API: {e}")
    
    def obtener_estadisticas_apis(self) -> Dict[str, Any]:
        """Obtener estadisticas de uso de APIs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Estadisticas de llamadas
            cursor.execute('''
                SELECT 
                    api_name,
                    COUNT(*) as total_llamadas,
                    AVG(response_time_ms) as tiempo_promedio,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as llamadas_exitosas,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as llamadas_fallidas
                FROM llamadas_api 
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY api_name
            ''')
            
            stats_llamadas = cursor.fetchall()
            
            # Estadisticas de datos
            cursor.execute('''
                SELECT 
                    api_name,
                    data_type,
                    COUNT(*) as total_datos
                FROM datos_api 
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY api_name, data_type
            ''')
            
            stats_datos = cursor.fetchall()
            
            conn.close()
            
            return {
                'llamadas_por_api': [
                    {
                        'api': row[0],
                        'total_llamadas': row[1],
                        'tiempo_promedio_ms': round(row[2] or 0, 2),
                        'exitosas': row[3],
                        'fallidas': row[4]
                    }
                    for row in stats_llamadas
                ],
                'datos_por_api': [
                    {
                        'api': row[0],
                        'tipo_dato': row[1],
                        'total_datos': row[2]
                    }
                    for row in stats_datos
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadisticas APIs: {e}")
            return {'error': str(e)}
    
    def verificar_estado_apis(self) -> Dict[str, Any]:
        """Verificar estado de todas las APIs configuradas"""
        try:
            estado_apis = {}
            
            for api_name, config in self.apis_config.items():
                # Verificar si tiene API key
                tiene_key = config['api_key'] is not None and config['api_key'] != 'demo_key'
                
                # Hacer llamada de prueba
                if api_name == 'openweather':
                    resultado = self.obtener_datos_openweather()
                elif api_name == 'nasa':
                    resultado = self.obtener_datos_nasa_earth()
                elif api_name == 'google_maps':
                    resultado = self.obtener_elevacion_google_maps()
                else:
                    resultado = {'error': 'API no implementada'}
                
                estado_apis[api_name] = {
                    'configurada': tiene_key,
                    'disponible': 'error' not in resultado,
                    'ultima_respuesta': resultado.get('timestamp', None),
                    'error': resultado.get('error', None)
                }
            
            return estado_apis
            
        except Exception as e:
            self.logger.error(f"Error verificando estado APIs: {e}")
            return {'error': str(e)}

def main():
    """Funcion principal para probar conector de APIs avanzadas"""
    print("CONECTOR APIs AVANZADAS - METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Version 2.0")
    print("=" * 70)
    
    try:
        # Probar conector de APIs
        print("\n1. Probando Conector de APIs Avanzadas...")
        conector_apis = ConectorAPIsAvanzadas()
        
        # Verificar estado de APIs
        estado = conector_apis.verificar_estado_apis()
        print("   Estado de APIs:")
        for api, info in estado.items():
            print(f"   - {api}: {'OK' if info.get('disponible') else 'ERROR'}")
        
        # Obtener datos de OpenWeather
        print("\n2. Probando OpenWeather API...")
        datos_ow = conector_apis.obtener_datos_openweather()
        if 'error' not in datos_ow:
            print(f"   Temperatura: {datos_ow.get('temperatura', 'N/A')}°C")
            print(f"   Humedad: {datos_ow.get('humedad', 'N/A')}%")
        else:
            print(f"   Error: {datos_ow.get('error', 'Error desconocido')}")
        
        # Obtener estadisticas
        print("\n3. Obteniendo estadisticas...")
        stats = conector_apis.obtener_estadisticas_apis()
        print(f"   APIs con datos: {len(stats.get('llamadas_por_api', []))}")
        
        print("\nConector de APIs Avanzadas probado exitosamente")
        return True
        
    except Exception as e:
        print(f"\nError probando conector APIs: {e}")
        return False

if __name__ == "__main__":
    main()
