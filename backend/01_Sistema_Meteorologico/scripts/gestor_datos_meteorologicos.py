#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de Datos Meteorológicos Avanzado METGO 3D
Sistema robusto para gestión de datos meteorológicos
"""

import sqlite3
import json
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import os
import logging
from typing import Dict, List, Optional, Tuple
import threading
import time

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gestor_datos_meteorologicos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GestorDatosMeteorologicos:
    """Gestor avanzado de datos meteorológicos con múltiples fuentes"""
    
    def __init__(self, config_path: str = "scripts/api_keys_meteorologicas.json"):
        self.config_path = config_path
        self.db_path = "scripts/datos_meteorologicos.db"
        self.backup_path = "scripts/backups/"
        self.logs_path = "logs/"
        
        # Configuración
        self.config = self._cargar_configuracion()
        
        # Cache de datos
        self.cache_datos = {}
        self.ultima_actualizacion = None
        
        # Threading para actualizaciones automáticas
        self.thread_actualizacion = None
        self.actualizacion_activa = False
        
        # Inicializar sistema
        self._inicializar_sistema()
    
    def _cargar_configuracion(self) -> Dict:
        """Cargar configuración desde archivo JSON"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info("Configuración cargada exitosamente")
                return config
            else:
                logger.warning("Archivo de configuración no encontrado, usando configuración por defecto")
                return self._configuracion_por_defecto()
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return self._configuracion_por_defecto()
    
    def _configuracion_por_defecto(self) -> Dict:
        """Configuración por defecto del sistema"""
        return {
            "openweathermap_key": "",
            "openmeteo_enabled": True,
            "actualizacion_automatica": True,
            "intervalo_actualizacion": 900,  # 15 minutos
            "backup_automatico": True,
            "max_registros": 10000,
            "coordenadas": {
                "lat": -32.8833,
                "lon": -71.2500,
                "ciudad": "Quillota",
                "pais": "Chile"
            }
        }
    
    def _inicializar_sistema(self):
        """Inicializar sistema de gestión de datos"""
        try:
            # Crear directorios necesarios
            os.makedirs(self.backup_path, exist_ok=True)
            os.makedirs(self.logs_path, exist_ok=True)
            
            # Inicializar base de datos
            self._inicializar_base_datos()
            
            # Iniciar actualización automática si está habilitada
            if self.config.get("actualizacion_automatica", True):
                self._iniciar_actualizacion_automatica()
            
            logger.info("Sistema de gestión de datos inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando sistema: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Crear tabla principal de datos meteorológicos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datos_meteorologicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha DATETIME NOT NULL,
                    temperatura_max REAL,
                    temperatura_min REAL,
                    temperatura_promedio REAL,
                    precipitacion REAL,
                    humedad_relativa REAL,
                    presion_atmosferica REAL,
                    viento_velocidad REAL,
                    viento_direccion TEXT,
                    cobertura_nubosa REAL,
                    indice_uv REAL,
                    punto_rocio REAL,
                    visibilidad REAL,
                    fuente TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(fecha)
                )
            ''')
            
            # Crear tabla de configuración
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracion_sistema (
                    clave TEXT PRIMARY KEY,
                    valor TEXT,
                    descripcion TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear tabla de logs de actualización
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs_actualizacion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha DATETIME,
                    fuente TEXT,
                    registros_agregados INTEGER,
                    estado TEXT,
                    mensaje TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insertar configuración inicial si no existe
            configs_iniciales = [
                ("ultima_actualizacion", "", "Última fecha de actualización de datos"),
                ("total_registros", "0", "Total de registros en la base de datos"),
                ("version_sistema", "2.0", "Versión del sistema de gestión de datos")
            ]
            
            for clave, valor, descripcion in configs_iniciales:
                cursor.execute('''
                    INSERT OR IGNORE INTO configuracion_sistema (clave, valor, descripcion)
                    VALUES (?, ?, ?)
                ''', (clave, valor, descripcion))
            
            conn.commit()
            conn.close()
            
            logger.info("Base de datos inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
    
    def cargar_datos(self, limite: int = 100) -> List[Dict]:
        """Cargar datos meteorológicos desde múltiples fuentes"""
        datos = []
        
        try:
            # 1. Intentar cargar desde base de datos local
            datos = self._cargar_desde_base_datos(limite)
            
            # 2. Si no hay datos locales, intentar APIs externas
            if not datos:
                logger.info("No hay datos locales, intentando cargar desde APIs")
                datos = self._cargar_desde_apis()
                
                # Guardar datos obtenidos de APIs
                if datos:
                    self._guardar_datos_en_db(datos)
            
            # 3. Si todo falla, generar datos demo
            if not datos:
                logger.warning("No se pudieron obtener datos reales, generando datos demo")
                datos = self._generar_datos_demo()
            
            # Actualizar cache
            self.cache_datos = datos
            self.ultima_actualizacion = datetime.now()
            
            logger.info(f"Datos cargados exitosamente: {len(datos)} registros")
            return datos
            
        except Exception as e:
            logger.error(f"Error cargando datos: {e}")
            return self._generar_datos_demo()
    
    def _cargar_desde_base_datos(self, limite: int) -> List[Dict]:
        """Cargar datos desde base de datos local"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT fecha, temperatura_max, temperatura_min, temperatura_promedio,
                       precipitacion, humedad_relativa, presion_atmosferica,
                       viento_velocidad, viento_direccion, cobertura_nubosa,
                       indice_uv, punto_rocio, visibilidad, fuente
                FROM datos_meteorologicos
                ORDER BY fecha DESC
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(limite,))
            conn.close()
            
            if not df.empty:
                return df.to_dict('records')
            
            return []
            
        except Exception as e:
            logger.error(f"Error cargando desde base de datos: {e}")
            return []
    
    def _cargar_desde_apis(self) -> List[Dict]:
        """Cargar datos desde APIs meteorológicas externas"""
        datos = []
        
        # Intentar OpenMeteo primero (gratuita)
        if self.config.get("openmeteo_enabled", True):
            datos = self._cargar_openmeteo()
        
        # Si no hay datos y hay API key, intentar OpenWeatherMap
        if not datos and self.config.get("openweathermap_key"):
            datos = self._cargar_openweathermap()
        
        return datos
    
    def _cargar_openmeteo(self) -> List[Dict]:
        """Cargar datos desde OpenMeteo API"""
        try:
            lat = self.config["coordenadas"]["lat"]
            lon = self.config["coordenadas"]["lon"]
            
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'hourly': 'temperature_2m,precipitation,relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m,cloud_cover,uv_index',
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
                'timezone': 'America/Santiago',
                'forecast_days': 7
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            datos = []
            
            # Procesar datos diarios
            for i in range(len(data['daily']['time'])):
                datos.append({
                    'fecha': data['daily']['time'][i],
                    'temperatura_max': data['daily']['temperature_2m_max'][i],
                    'temperatura_min': data['daily']['temperature_2m_min'][i],
                    'temperatura_promedio': (data['daily']['temperature_2m_max'][i] + data['daily']['temperature_2m_min'][i]) / 2,
                    'precipitacion': data['daily']['precipitation_sum'][i],
                    'humedad_relativa': data['hourly']['relative_humidity_2m'][i*24] if i*24 < len(data['hourly']['relative_humidity_2m']) else 60,
                    'presion_atmosferica': data['hourly']['pressure_msl'][i*24] if i*24 < len(data['hourly']['pressure_msl']) else 1013,
                    'viento_velocidad': data['hourly']['wind_speed_10m'][i*24] * 3.6 if i*24 < len(data['hourly']['wind_speed_10m']) else 10,
                    'viento_direccion': self._convertir_direccion_viento(data['hourly']['wind_direction_10m'][i*24]) if i*24 < len(data['hourly']['wind_direction_10m']) else 'N',
                    'cobertura_nubosa': data['hourly']['cloud_cover'][i*24] if i*24 < len(data['hourly']['cloud_cover']) else 50,
                    'indice_uv': data['hourly']['uv_index'][i*24] if i*24 < len(data['hourly']['uv_index']) else 5,
                    'punto_rocio': 0,  # Calcular después
                    'visibilidad': 15,  # Valor por defecto
                    'fuente': 'OpenMeteo'
                })
            
            logger.info(f"Datos cargados desde OpenMeteo: {len(datos)} registros")
            return datos
            
        except Exception as e:
            logger.error(f"Error cargando desde OpenMeteo: {e}")
            return []
    
    def _cargar_openweathermap(self, api_key: str) -> List[Dict]:
        """Cargar datos desde OpenWeatherMap API"""
        try:
            lat = self.config["coordenadas"]["lat"]
            lon = self.config["coordenadas"]["lon"]
            
            url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric',
                'lang': 'es'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            datos = []
            
            for item in data['list'][:40]:  # Próximos 5 días
                datos.append({
                    'fecha': item['dt_txt'],
                    'temperatura_max': item['main']['temp_max'],
                    'temperatura_min': item['main']['temp_min'],
                    'temperatura_promedio': item['main']['temp'],
                    'precipitacion': item.get('rain', {}).get('3h', 0),
                    'humedad_relativa': item['main']['humidity'],
                    'presion_atmosferica': item['main']['pressure'],
                    'viento_velocidad': item['wind']['speed'] * 3.6,  # m/s to km/h
                    'viento_direccion': self._convertir_direccion_viento(item['wind']['deg']),
                    'cobertura_nubosa': item['clouds']['all'],
                    'indice_uv': 5,  # Valor por defecto
                    'punto_rocio': 0,  # Calcular después
                    'visibilidad': item.get('visibility', 10000) / 1000,  # m to km
                    'fuente': 'OpenWeatherMap'
                })
            
            logger.info(f"Datos cargados desde OpenWeatherMap: {len(datos)} registros")
            return datos
            
        except Exception as e:
            logger.error(f"Error cargando desde OpenWeatherMap: {e}")
            return []
    
    def _convertir_direccion_viento(self, grados: float) -> str:
        """Convertir grados a dirección cardinal"""
        direcciones = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        index = int((grados + 22.5) / 45) % 8
        return direcciones[index]
    
    def _generar_datos_demo(self) -> List[Dict]:
        """Generar datos de demostración realistas para Quillota"""
        np.random.seed(42)
        
        fechas = pd.date_range(start='2025-01-01', end='2025-01-30', freq='D')
        datos = []
        
        for i, fecha in enumerate(fechas):
            # Variación estacional para Quillota
            dia_año = fecha.timetuple().tm_yday
            temp_base = 18 + 8 * np.sin(2 * np.pi * dia_año / 365)
            
            temp_max = temp_base + np.random.normal(8, 3)
            temp_min = temp_base - np.random.normal(5, 2)
            temp_promedio = (temp_max + temp_min) / 2
            
            # Precipitación estacional
            prob_precip = 0.4 if fecha.month in [5, 6, 7, 8] else 0.1
            precipitacion = np.random.exponential(8) if np.random.random() < prob_precip else 0
            
            humedad = np.random.normal(75, 15)
            presion = np.random.normal(1013, 15)
            viento_velocidad = np.random.exponential(12)
            viento_direccion = np.random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
            cobertura_nubosa = np.random.normal(45, 25)
            indice_uv = np.random.normal(6, 2)
            
            datos.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'temperatura_max': round(temp_max, 1),
                'temperatura_min': round(temp_min, 1),
                'temperatura_promedio': round(temp_promedio, 1),
                'precipitacion': round(max(0, precipitacion), 1),
                'humedad_relativa': round(max(0, min(100, humedad)), 1),
                'presion_atmosferica': round(presion, 1),
                'viento_velocidad': round(max(0, viento_velocidad), 1),
                'viento_direccion': viento_direccion,
                'cobertura_nubosa': round(max(0, min(100, cobertura_nubosa)), 1),
                'indice_uv': round(max(0, min(11, indice_uv)), 1),
                'punto_rocio': round(temp_promedio - (100 - humedad) / 5, 1),
                'visibilidad': round(np.random.normal(15, 5), 1),
                'fuente': 'Demo'
            })
        
        logger.info(f"Datos demo generados: {len(datos)} registros")
        return datos
    
    def _guardar_datos_en_db(self, datos: List[Dict]):
        """Guardar datos en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            registros_agregados = 0
            
            for dato in datos:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO datos_meteorologicos 
                        (fecha, temperatura_max, temperatura_min, temperatura_promedio,
                         precipitacion, humedad_relativa, presion_atmosferica,
                         viento_velocidad, viento_direccion, cobertura_nubosa,
                         indice_uv, punto_rocio, visibilidad, fuente)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        dato['fecha'], dato['temperatura_max'], dato['temperatura_min'],
                        dato['temperatura_promedio'], dato['precipitacion'],
                        dato['humedad_relativa'], dato['presion_atmosferica'],
                        dato['viento_velocidad'], dato['viento_direccion'],
                        dato['cobertura_nubosa'], dato['indice_uv'],
                        dato['punto_rocio'], dato['visibilidad'], dato['fuente']
                    ))
                    registros_agregados += 1
                    
                except Exception as e:
                    logger.error(f"Error insertando registro: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            # Log de actualización
            self._registrar_log_actualizacion(
                datetime.now(), "API", registros_agregados, "Exitoso", 
                f"Se agregaron {registros_agregados} registros"
            )
            
            logger.info(f"Datos guardados en base de datos: {registros_agregados} registros")
            
        except Exception as e:
            logger.error(f"Error guardando datos: {e}")
    
    def _registrar_log_actualizacion(self, fecha: datetime, fuente: str, 
                                   registros: int, estado: str, mensaje: str):
        """Registrar log de actualización"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO logs_actualizacion 
                (fecha, fuente, registros_agregados, estado, mensaje)
                VALUES (?, ?, ?, ?, ?)
            ''', (fecha, fuente, registros, estado, mensaje))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error registrando log: {e}")
    
    def actualizar_datos(self) -> bool:
        """Forzar actualización de datos"""
        try:
            logger.info("Iniciando actualización manual de datos")
            
            # Cargar datos desde APIs
            datos_nuevos = self._cargar_desde_apis()
            
            if datos_nuevos:
                # Guardar en base de datos
                self._guardar_datos_en_db(datos_nuevos)
                
                # Actualizar cache
                self.cache_datos = datos_nuevos
                self.ultima_actualizacion = datetime.now()
                
                logger.info("Actualización manual completada exitosamente")
                return True
            else:
                logger.warning("No se pudieron obtener datos nuevos")
                return False
                
        except Exception as e:
            logger.error(f"Error en actualización manual: {e}")
            return False
    
    def _iniciar_actualizacion_automatica(self):
        """Iniciar actualización automática en hilo separado"""
        if not self.actualizacion_activa:
            self.actualizacion_activa = True
            self.thread_actualizacion = threading.Thread(
                target=self._loop_actualizacion_automatica,
                daemon=True
            )
            self.thread_actualizacion.start()
            logger.info("Actualización automática iniciada")
    
    def _loop_actualizacion_automatica(self):
        """Loop de actualización automática"""
        intervalo = self.config.get("intervalo_actualizacion", 900)  # 15 minutos
        
        while self.actualizacion_activa:
            try:
                time.sleep(intervalo)
                
                if self.actualizacion_activa:
                    logger.info("Ejecutando actualización automática")
                    self.actualizar_datos()
                    
            except Exception as e:
                logger.error(f"Error en actualización automática: {e}")
    
    def detener_actualizacion_automatica(self):
        """Detener actualización automática"""
        self.actualizacion_activa = False
        if self.thread_actualizacion:
            self.thread_actualizacion.join(timeout=5)
        logger.info("Actualización automática detenida")
    
    def obtener_estadisticas(self) -> Dict:
        """Obtener estadísticas del sistema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total de registros
            cursor.execute("SELECT COUNT(*) FROM datos_meteorologicos")
            total_registros = cursor.fetchone()[0]
            
            # Última actualización
            cursor.execute("""
                SELECT MAX(created_at) FROM datos_meteorologicos
            """)
            ultima_actualizacion = cursor.fetchone()[0]
            
            # Registros por fuente
            cursor.execute("""
                SELECT fuente, COUNT(*) FROM datos_meteorologicos 
                GROUP BY fuente
            """)
            registros_por_fuente = dict(cursor.fetchall())
            
            # Últimos logs
            cursor.execute("""
                SELECT fecha, fuente, estado, mensaje 
                FROM logs_actualizacion 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            ultimos_logs = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_registros': total_registros,
                'ultima_actualizacion': ultima_actualizacion,
                'registros_por_fuente': registros_por_fuente,
                'ultimos_logs': ultimos_logs,
                'actualizacion_automatica_activa': self.actualizacion_activa,
                'configuracion': self.config
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def limpiar_datos_antiguos(self, dias_antiguedad: int = 365):
        """Limpiar datos más antiguos que el límite especificado"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            fecha_limite = (datetime.now() - timedelta(days=dias_antiguedad)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                DELETE FROM datos_meteorologicos 
                WHERE fecha < ?
            """, (fecha_limite,))
            
            registros_eliminados = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Datos antiguos eliminados: {registros_eliminados} registros")
            return registros_eliminados
            
        except Exception as e:
            logger.error(f"Error limpiando datos antiguos: {e}")
            return 0
    
    def crear_backup(self) -> str:
        """Crear backup de la base de datos"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{self.backup_path}datos_meteorologicos_backup_{timestamp}.db"
            
            # Copiar archivo de base de datos
            import shutil
            shutil.copy2(self.db_path, backup_file)
            
            logger.info(f"Backup creado: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return ""
    
    def __del__(self):
        """Destructor - detener actualización automática"""
        self.detener_actualizacion_automatica()

# Función de utilidad para uso directo
def obtener_gestor_datos() -> GestorDatosMeteorologicos:
    """Obtener instancia del gestor de datos"""
    return GestorDatosMeteorologicos()

if __name__ == "__main__":
    # Prueba del sistema
    gestor = GestorDatosMeteorologicos()
    
    print("=== Prueba del Gestor de Datos Meteorológicos ===")
    
    # Cargar datos
    datos = gestor.cargar_datos(10)
    print(f"Datos cargados: {len(datos)} registros")
    
    # Mostrar estadísticas
    stats = gestor.obtener_estadisticas()
    print(f"Total de registros en BD: {stats.get('total_registros', 0)}")
    print(f"Última actualización: {stats.get('ultima_actualizacion', 'N/A')}")
    
    # Detener sistema
    gestor.detener_actualizacion_automatica()
    print("Sistema detenido correctamente")
