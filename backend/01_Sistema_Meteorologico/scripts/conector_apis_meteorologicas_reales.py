"""
CONECTOR DE APIs METEOROLÓGICAS REALES - METGO 3D QUILLOTA
Sistema para obtener datos meteorológicos en tiempo real de múltiples fuentes
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
import sqlite3
import os

class ConectorAPIsMeteorologicas:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_keys = self._cargar_api_keys()
        self.estaciones_quillota = self._configurar_estaciones_quillota()
        self.base_datos = "datos_meteorologicos_reales.db"
        self._inicializar_base_datos()
        
    def _cargar_api_keys(self) -> Dict:
        """Cargar claves API desde archivo de configuración"""
        api_keys_file = "api_keys_meteorologicas.json"
        
        # Claves por defecto (deben ser reemplazadas por las reales)
        default_keys = {
            "openweathermap": {
                "api_key": "YOUR_OPENWEATHERMAP_API_KEY",
                "base_url": "https://api.openweathermap.org/data/2.5",
                "activa": False
            },
            "accuweather": {
                "api_key": "YOUR_ACCUWEATHER_API_KEY", 
                "base_url": "https://dataservice.accuweather.com",
                "activa": False
            },
            "openmeteo": {
                "api_key": None,  # OpenMeteo es gratuito sin API key
                "base_url": "https://api.open-meteo.com/v1",
                "activa": True
            },
            "weatherapi": {
                "api_key": "YOUR_WEATHERAPI_API_KEY",
                "base_url": "https://api.weatherapi.com/v1",
                "activa": False
            }
        }
        
        if os.path.exists(api_keys_file):
            try:
                with open(api_keys_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error cargando API keys: {e}")
        
        # Crear archivo de configuración por defecto
        try:
            with open(api_keys_file, 'w') as f:
                json.dump(default_keys, f, indent=2)
            self.logger.info(f"Archivo de configuración creado: {api_keys_file}")
        except Exception as e:
            self.logger.error(f"Error creando archivo de configuración: {e}")
        
        return default_keys
    
    def _configurar_estaciones_quillota(self) -> Dict:
        """Configurar coordenadas de estaciones meteorológicas en Quillota"""
        return {
            "quillota_centro": {
                "nombre": "Quillota Centro",
                "lat": -32.8833,
                "lon": -71.2667,
                "altitud": 462,
                "sector": "centro_valle"
            },
            "la_cruz": {
                "nombre": "La Cruz", 
                "lat": -32.8167,
                "lon": -71.2167,
                "altitud": 380,
                "sector": "valle_bajo"
            },
            "nogueira": {
                "nombre": "Nogales",
                "lat": -32.9333, 
                "lon": -71.2167,
                "altitud": 520,
                "sector": "valle_medio"
            },
            "colliguay": {
                "nombre": "Colliguay",
                "lat": -32.9500,
                "lon": -71.1833,
                "altitud": 680,
                "sector": "valle_alto"
            },
            "hijuelas": {
                "nombre": "Hijuelas",
                "lat": -32.7833,
                "lon": -71.1500,
                "altitud": 420,
                "sector": "valle_bajo"
            },
            "calera": {
                "nombre": "La Calera",
                "lat": -32.7833,
                "lon": -71.2167,
                "altitud": 400,
                "sector": "valle_bajo"
            }
        }
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite para almacenar datos meteorológicos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Crear tabla para datos meteorológicos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datos_meteorologicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estacion TEXT NOT NULL,
                    fecha TIMESTAMP NOT NULL,
                    temperatura REAL,
                    temperatura_max REAL,
                    temperatura_min REAL,
                    precipitacion REAL,
                    humedad_relativa REAL,
                    presion_atmosferica REAL,
                    velocidad_viento REAL,
                    direccion_viento REAL,
                    nubosidad REAL,
                    radiacion_solar REAL,
                    punto_rocio REAL,
                    fuente_api TEXT,
                    calidad_datos TEXT DEFAULT 'buena',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear índices para optimizar consultas
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_estacion_fecha ON datos_meteorologicos(estacion, fecha)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_fecha ON datos_meteorologicos(fecha)')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Base de datos meteorológica inicializada")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def obtener_datos_openmeteo(self, estacion_id: str, dias: int = 7) -> Optional[Dict]:
        """Obtener datos de OpenMeteo (API gratuita)"""
        try:
            estacion = self.estaciones_quillota[estacion_id]
            api_config = self.api_keys["openmeteo"]
            
            if not api_config["activa"]:
                return None
            
            # Parámetros para la API
            params = {
                "latitude": estacion["lat"],
                "longitude": estacion["lon"],
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min", 
                    "precipitation_sum",
                    "relative_humidity_2m_mean",
                    "pressure_msl_mean",
                    "wind_speed_10m_max",
                    "wind_direction_10m_dominant",
                    "cloud_cover_mean",
                    "shortwave_radiation_sum",
                    "dew_point_2m_mean"
                ],
                "timezone": "America/Santiago",
                "past_days": dias
            }
            
            # Hacer petición a la API
            response = requests.get(api_config["base_url"] + "/forecast", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Procesar datos
            datos_procesados = self._procesar_datos_openmeteo(data, estacion_id)
            
            self.logger.info(f"Datos obtenidos de OpenMeteo para {estacion['nombre']}")
            return datos_procesados
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error de conexión con OpenMeteo: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error procesando datos de OpenMeteo: {e}")
            return None
    
    def obtener_datos_openmeteo_coordenadas(self, lat: float, lon: float, dias: int = 7) -> Optional[Dict]:
        """Obtener datos de OpenMeteo usando coordenadas directamente"""
        try:
            api_config = self.api_keys["openmeteo"]
            
            if not api_config["activa"]:
                return None
            
            # Parámetros para la API
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "precipitation",
                    "surface_pressure",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "cloud_cover",
                    "visibility",
                    "uv_index"
                ],
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min", 
                    "precipitation_sum",
                    "relative_humidity_2m_mean",
                    "pressure_msl_mean",
                    "wind_speed_10m_max",
                    "wind_direction_10m_dominant",
                    "cloud_cover_mean",
                    "shortwave_radiation_sum",
                    "dew_point_2m_mean"
                ],
                "timezone": "America/Santiago",
                "forecast_days": 1
            }
            
            # Hacer petición a la API
            response = requests.get(api_config["base_url"] + "/forecast", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Procesar datos
            datos_procesados = self._procesar_datos_openmeteo_coordenadas(data, lat, lon)
            
            self.logger.info(f"Datos obtenidos de OpenMeteo para coordenadas ({lat}, {lon})")
            return datos_procesados
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error de conexión con OpenMeteo: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error procesando datos de OpenMeteo: {e}")
            return None
    
    def _procesar_datos_openmeteo_coordenadas(self, data: Dict, lat: float, lon: float) -> Dict:
        """Procesar datos obtenidos de OpenMeteo usando coordenadas"""
        try:
            current = data.get("current", {})
            daily = data.get("daily", {})
            
            # Datos actuales
            datos_actuales = {
                "temperatura_actual": current.get("temperature_2m"),
                "humedad_relativa": current.get("relative_humidity_2m"),
                "precipitacion": current.get("precipitation", 0),
                "presion_atmosferica": current.get("surface_pressure"),
                "velocidad_viento": current.get("wind_speed_10m"),
                "direccion_viento": current.get("wind_direction_10m"),
                "nubosidad": current.get("cloud_cover"),
                "visibilidad": current.get("visibility"),
                "indice_uv": current.get("uv_index"),
                "coordenadas": {"lat": lat, "lon": lon},
                "fecha_actualizacion": datetime.now().isoformat()
            }
            
            # Calcular punto de rocío si hay temperatura y humedad
            if datos_actuales["temperatura_actual"] and datos_actuales["humedad_relativa"]:
                temp = datos_actuales["temperatura_actual"]
                humedad = datos_actuales["humedad_relativa"] / 100
                
                # Fórmula de Magnus para punto de rocío
                a = 17.27
                b = 237.7
                alpha = ((a * temp) / (b + temp)) + np.log(humedad)
                punto_rocio = (b * alpha) / (a - alpha)
                datos_actuales["punto_rocio"] = round(punto_rocio, 1)
            
            # Pronóstico 24h (si está disponible)
            pronostico_24h = None
            if daily.get("time") and len(daily["time"]) > 0:
                pronostico_24h = {
                    "temp_max": daily.get("temperature_2m_max", [None])[0],
                    "temp_min": daily.get("temperature_2m_min", [None])[0],
                    "precipitacion_total": daily.get("precipitation_sum", [0])[0],
                    "humedad_promedio": daily.get("relative_humidity_2m_mean", [None])[0],
                    "presion_promedio": daily.get("pressure_msl_mean", [None])[0],
                    "viento_max": daily.get("wind_speed_10m_max", [None])[0],
                    "nubosidad_promedio": daily.get("cloud_cover_mean", [None])[0],
                    "radiacion_solar": daily.get("shortwave_radiation_sum", [None])[0],
                    "probabilidad_lluvia": 0  # OpenMeteo no proporciona esto directamente
                }
                
                # Estimar probabilidad de lluvia basada en precipitación
                if pronostico_24h["precipitacion_total"] and pronostico_24h["precipitacion_total"] > 0:
                    pronostico_24h["probabilidad_lluvia"] = min(100, pronostico_24h["precipitacion_total"] * 20)
                
                # Condiciones generales basadas en temperatura y precipitación
                temp_max = pronostico_24h["temp_max"]
                temp_min = pronostico_24h["temp_min"]
                precipitacion = pronostico_24h["precipitacion_total"]
                
                if precipitacion and precipitacion > 5:
                    pronostico_24h["condiciones"] = "Lluvioso"
                elif temp_max and temp_max > 25:
                    pronostico_24h["condiciones"] = "Soleado y cálido"
                elif temp_min and temp_min < 5:
                    pronostico_24h["condiciones"] = "Frío"
                else:
                    pronostico_24h["condiciones"] = "Parcialmente nublado"
            
            datos_actuales["pronostico_24h"] = pronostico_24h
            
            # Generar alertas meteorológicas
            alertas = []
            
            # Alerta de helada
            if datos_actuales["temperatura_actual"] and datos_actuales["temperatura_actual"] < 2:
                alertas.append({
                    "tipo": "Helada",
                    "nivel": "critico",
                    "descripcion": f"Temperatura crítica: {datos_actuales['temperatura_actual']:.1f}°C. Riesgo de helada en cultivos sensibles."
                })
            elif datos_actuales["temperatura_actual"] and datos_actuales["temperatura_actual"] < 5:
                alertas.append({
                    "tipo": "Helada",
                    "nivel": "advertencia", 
                    "descripcion": f"Temperatura baja: {datos_actuales['temperatura_actual']:.1f}°C. Monitorear cultivos sensibles."
                })
            
            # Alerta de viento fuerte
            if datos_actuales["velocidad_viento"] and datos_actuales["velocidad_viento"] > 50:
                alertas.append({
                    "tipo": "Viento Fuerte",
                    "nivel": "advertencia",
                    "descripcion": f"Viento fuerte: {datos_actuales['velocidad_viento']:.1f} km/h. Posibles daños en cultivos."
                })
            
            # Alerta de alta humedad
            if datos_actuales["humedad_relativa"] and datos_actuales["humedad_relativa"] > 90:
                alertas.append({
                    "tipo": "Alta Humedad",
                    "nivel": "advertencia",
                    "descripcion": f"Humedad muy alta: {datos_actuales['humedad_relativa']:.1f}%. Riesgo de enfermedades fúngicas."
                })
            
            datos_actuales["alertas"] = alertas
            
            # Agregar información de la estación
            datos_actuales["estacion"] = f"coordenadas_{lat}_{lon}"
            datos_actuales["nombre_estacion"] = f"Estación ({lat:.4f}, {lon:.4f})"
            
            return datos_actuales
            
        except Exception as e:
            self.logger.error(f"Error procesando datos de OpenMeteo: {e}")
            return {"error": str(e)}
    
    def _procesar_datos_openmeteo(self, data: Dict, estacion_id: str) -> Dict:
        """Procesar datos obtenidos de OpenMeteo"""
        try:
            daily = data.get("daily", {})
            time_series = daily.get("time", [])
            
            if not time_series:
                return {"error": "No hay datos disponibles"}
            
            # Crear DataFrame con los datos
            df_data = {
                "fecha": pd.to_datetime(time_series),
                "temperatura_max": daily.get("temperature_2m_max", []),
                "temperatura_min": daily.get("temperature_2m_min", []),
                "precipitacion": daily.get("precipitation_sum", []),
                "humedad_relativa": daily.get("relative_humidity_2m_mean", []),
                "presion_atmosferica": daily.get("pressure_msl_mean", []),
                "velocidad_viento": daily.get("wind_speed_10m_max", []),
                "direccion_viento": daily.get("wind_direction_10m_dominant", []),
                "nubosidad": daily.get("cloud_cover_mean", []),
                "radiacion_solar": daily.get("shortwave_radiation_sum", []),
                "punto_rocio": daily.get("dew_point_2m_mean", [])
            }
            
            # Calcular temperatura promedio
            temp_max = np.array(df_data["temperatura_max"])
            temp_min = np.array(df_data["temperatura_min"])
            df_data["temperatura"] = (temp_max + temp_min) / 2
            
            # Crear DataFrame
            df = pd.DataFrame(df_data)
            
            # Agregar información de la estación
            df["estacion"] = estacion_id
            df["fuente_api"] = "openmeteo"
            df["calidad_datos"] = "buena"
            
            return {
                "estacion": estacion_id,
                "datos": df,
                "fuente": "openmeteo",
                "total_registros": len(df),
                "fecha_inicio": df["fecha"].min().isoformat(),
                "fecha_fin": df["fecha"].max().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando datos de OpenMeteo: {e}")
            return {"error": str(e)}
    
    def obtener_datos_openweathermap(self, estacion_id: str, dias: int = 7) -> Optional[Dict]:
        """Obtener datos de OpenWeatherMap"""
        try:
            estacion = self.estaciones_quillota[estacion_id]
            api_config = self.api_keys["openweathermap"]
            
            if not api_config["activa"] or not api_config["api_key"]:
                return None
            
            # OpenWeatherMap no tiene endpoint histórico gratuito, usar datos actuales
            params = {
                "lat": estacion["lat"],
                "lon": estacion["lon"],
                "appid": api_config["api_key"],
                "units": "metric",
                "lang": "es"
            }
            
            response = requests.get(
                api_config["base_url"] + "/weather", 
                params=params, 
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Procesar datos actuales
            datos_procesados = self._procesar_datos_openweathermap(data, estacion_id)
            
            self.logger.info(f"Datos obtenidos de OpenWeatherMap para {estacion['nombre']}")
            return datos_procesados
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error de conexión con OpenWeatherMap: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error procesando datos de OpenWeatherMap: {e}")
            return None
    
    def _procesar_datos_openweathermap(self, data: Dict, estacion_id: str) -> Dict:
        """Procesar datos obtenidos de OpenWeatherMap"""
        try:
            main = data.get("main", {})
            weather = data.get("weather", [{}])[0]
            wind = data.get("wind", {})
            clouds = data.get("clouds", {})
            
            # Crear DataFrame con datos actuales
            df_data = {
                "fecha": [datetime.now()],
                "temperatura": [main.get("temp")],
                "temperatura_max": [main.get("temp_max")],
                "temperatura_min": [main.get("temp_min")],
                "humedad_relativa": [main.get("humidity")],
                "presion_atmosferica": [main.get("pressure")],
                "velocidad_viento": [wind.get("speed", 0) * 3.6],  # Convertir m/s a km/h
                "direccion_viento": [wind.get("deg", 0)],
                "nubosidad": [clouds.get("all", 0)],
                "punto_rocio": [main.get("feels_like")],
                "estacion": [estacion_id],
                "fuente_api": ["openweathermap"],
                "calidad_datos": ["buena"]
            }
            
            # Agregar precipitación (si está disponible)
            if "rain" in data:
                df_data["precipitacion"] = [data["rain"].get("1h", 0)]
            else:
                df_data["precipitacion"] = [0]
            
            # Agregar radiación solar (no disponible en OpenWeatherMap básico)
            df_data["radiacion_solar"] = [None]
            
            df = pd.DataFrame(df_data)
            
            return {
                "estacion": estacion_id,
                "datos": df,
                "fuente": "openweathermap",
                "total_registros": len(df),
                "fecha_inicio": df["fecha"].min().isoformat(),
                "fecha_fin": df["fecha"].max().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando datos de OpenWeatherMap: {e}")
            return {"error": str(e)}
    
    def obtener_datos_todas_estaciones(self, dias: int = 7) -> Dict:
        """Obtener datos de todas las estaciones usando APIs disponibles"""
        resultados = {}
        datos_combinados = []
        
        for estacion_id in self.estaciones_quillota.keys():
            self.logger.info(f"Obteniendo datos para {estacion_id}")
            
            # Intentar OpenMeteo primero (más confiable y gratuito)
            datos = self.obtener_datos_openmeteo(estacion_id, dias)
            
            if datos and "error" not in datos:
                resultados[estacion_id] = datos
                datos_combinados.append(datos["datos"])
                
                # Guardar en base de datos
                self._guardar_datos_base_datos(datos["datos"])
            else:
                # Intentar OpenWeatherMap como respaldo
                datos = self.obtener_datos_openweathermap(estacion_id)
                
                if datos and "error" not in datos:
                    resultados[estacion_id] = datos
                    datos_combinados.append(datos["datos"])
                    
                    # Guardar en base de datos
                    self._guardar_datos_base_datos(datos["datos"])
                else:
                    self.logger.warning(f"No se pudieron obtener datos para {estacion_id}")
                    resultados[estacion_id] = {"error": "No hay datos disponibles"}
        
        # Combinar todos los datos
        if datos_combinados:
            df_combinado = pd.concat(datos_combinados, ignore_index=True)
            
            return {
                "estaciones": resultados,
                "datos_combinados": df_combinado,
                "total_estaciones": len(self.estaciones_quillota),
                "estaciones_exitosas": len([r for r in resultados.values() if "error" not in r]),
                "fecha_actualizacion": datetime.now().isoformat()
            }
        else:
            return {
                "estaciones": resultados,
                "error": "No se pudieron obtener datos de ninguna estación"
            }
    
    def _guardar_datos_base_datos(self, df: pd.DataFrame):
        """Guardar datos en la base de datos SQLite"""
        try:
            conn = sqlite3.connect(self.base_datos)
            
            # Preparar datos para inserción
            df_to_insert = df.copy()
            df_to_insert["created_at"] = datetime.now()
            
            # Insertar datos
            df_to_insert.to_sql("datos_meteorologicos", conn, if_exists="append", index=False)
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Datos guardados en base de datos: {len(df)} registros")
            
        except Exception as e:
            self.logger.error(f"Error guardando datos en base de datos: {e}")
    
    def obtener_datos_historicos(self, estacion_id: str, dias: int = 30) -> pd.DataFrame:
        """Obtener datos históricos de la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            
            # Consultar datos históricos
            query = '''
                SELECT * FROM datos_meteorologicos 
                WHERE estacion = ? 
                AND fecha >= datetime('now', '-{} days')
                ORDER BY fecha DESC
            '''.format(dias)
            
            df = pd.read_sql_query(query, conn, params=[estacion_id])
            conn.close()
            
            if not df.empty:
                df["fecha"] = pd.to_datetime(df["fecha"])
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos históricos: {e}")
            return pd.DataFrame()
    
    def obtener_resumen_estacion(self, estacion_id: str) -> Dict:
        """Obtener resumen de datos para una estación específica"""
        try:
            df = self.obtener_datos_historicos(estacion_id, 7)
            
            if df.empty:
                return {"error": "No hay datos disponibles"}
            
            estacion_info = self.estaciones_quillota[estacion_id]
            
            resumen = {
                "estacion": {
                    "id": estacion_id,
                    "nombre": estacion_info["nombre"],
                    "sector": estacion_info["sector"],
                    "altitud": estacion_info["altitud"]
                },
                "estadisticas": {
                    "total_registros": len(df),
                    "fecha_ultimo_dato": df["fecha"].max().isoformat() if not df.empty else None,
                    "temperatura_promedio": df["temperatura"].mean() if "temperatura" in df.columns else None,
                    "temperatura_maxima": df["temperatura_max"].max() if "temperatura_max" in df.columns else None,
                    "temperatura_minima": df["temperatura_min"].min() if "temperatura_min" in df.columns else None,
                    "precipitacion_total": df["precipitacion"].sum() if "precipitacion" in df.columns else None,
                    "humedad_promedio": df["humedad_relativa"].mean() if "humedad_relativa" in df.columns else None,
                    "presion_promedio": df["presion_atmosferica"].mean() if "presion_atmosferica" in df.columns else None,
                    "viento_promedio": df["velocidad_viento"].mean() if "velocidad_viento" in df.columns else None
                },
                "calidad_datos": {
                    "fuentes_utilizadas": df["fuente_api"].unique().tolist() if "fuente_api" in df.columns else [],
                    "registros_completos": len(df.dropna()) if not df.empty else 0,
                    "porcentaje_completitud": (len(df.dropna()) / len(df) * 100) if not df.empty else 0
                }
            }
            
            return resumen
            
        except Exception as e:
            self.logger.error(f"Error generando resumen de estación: {e}")
            return {"error": str(e)}
    
    def generar_datos_sinteticos_mejorados(self, estacion_id: str, dias: int = 7) -> pd.DataFrame:
        """Generar datos sintéticos mejorados basados en patrones reales de Quillota"""
        try:
            estacion = self.estaciones_quillota[estacion_id]
            
            # Generar fechas
            fechas = pd.date_range(end=datetime.now(), periods=dias, freq='D')
            
            # Factores de ajuste por altitud y sector
            factor_altitud = estacion["altitud"] / 462  # Quillota centro como referencia
            ajuste_temp = (estacion["altitud"] - 462) * -0.006  # Gradiente térmico
            
            # Datos base para Quillota
            datos_base = {
                "quillota_centro": {"temp_base": 18, "precip_base": 2, "humedad_base": 70},
                "la_cruz": {"temp_base": 19, "precip_base": 1.5, "humedad_base": 65},
                "nogueira": {"temp_base": 17, "precip_base": 2.5, "humedad_base": 75},
                "colliguay": {"temp_base": 15, "precip_base": 3, "humedad_base": 80},
                "hijuelas": {"temp_base": 18.5, "precip_base": 2, "humedad_base": 68},
                "calera": {"temp_base": 19.5, "precip_base": 1.8, "humedad_base": 67}
            }
            
            base = datos_base.get(estacion_id, datos_base["quillota_centro"])
            
            # Generar datos sintéticos con variabilidad realista
            datos = pd.DataFrame({
                "fecha": fechas,
                "temperatura": np.random.normal(base["temp_base"] + ajuste_temp, 3, dias),
                "temperatura_max": np.random.normal(base["temp_base"] + 8 + ajuste_temp, 4, dias),
                "temperatura_min": np.random.normal(base["temp_base"] - 5 + ajuste_temp, 3, dias),
                "precipitacion": np.maximum(np.random.exponential(base["precip_base"], dias), 0),
                "humedad_relativa": np.clip(np.random.normal(base["humedad_base"], 10, dias), 30, 95),
                "presion_atmosferica": np.random.normal(1015, 5, dias),
                "velocidad_viento": np.random.exponential(8, dias),
                "direccion_viento": np.random.uniform(0, 360, dias),
                "nubosidad": np.random.uniform(0, 100, dias),
                "radiacion_solar": np.random.normal(500, 100, dias),
                "punto_rocio": np.random.normal(base["temp_base"] - 5, 3, dias)
            })
            
            # Agregar información de la estación
            datos["estacion"] = estacion_id
            datos["fuente_api"] = "sintetico_mejorado"
            datos["calidad_datos"] = "sintetico"
            
            return datos
            
        except Exception as e:
            self.logger.error(f"Error generando datos sintéticos: {e}")
            return pd.DataFrame()
    
    def obtener_datos_completos_estacion(self, estacion_id: str, dias: int = 7, usar_sinteticos: bool = True) -> pd.DataFrame:
        """Obtener datos completos para una estación (reales + sintéticos si es necesario)"""
        try:
            # Intentar obtener datos reales primero
            datos_reales = self.obtener_datos_historicos(estacion_id, dias)
            
            if not datos_reales.empty and len(datos_reales) >= dias * 0.7:  # Al menos 70% de los datos
                self.logger.info(f"Datos reales obtenidos para {estacion_id}: {len(datos_reales)} registros")
                return datos_reales
            
            # Si no hay suficientes datos reales, generar sintéticos
            if usar_sinteticos:
                self.logger.info(f"Generando datos sintéticos para {estacion_id}")
                datos_sinteticos = self.generar_datos_sinteticos_mejorados(estacion_id, dias)
                
                # Combinar datos reales con sintéticos si hay algunos reales
                if not datos_reales.empty:
                    datos_completos = pd.concat([datos_reales, datos_sinteticos], ignore_index=True)
                    datos_completos = datos_completos.drop_duplicates(subset=["fecha"], keep="first")
                    datos_completos = datos_completos.sort_values("fecha")
                else:
                    datos_completos = datos_sinteticos
                
                return datos_completos
            
            return datos_reales
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos completos: {e}")
            return pd.DataFrame()

def main():
    """Función principal para probar el conector"""
    logging.basicConfig(level=logging.INFO)
    
    conector = ConectorAPIsMeteorologicas()
    
    print("=== CONECTOR DE APIs METEOROLÓGICAS REALES ===")
    print(f"Estaciones configuradas: {len(conector.estaciones_quillota)}")
    print(f"APIs disponibles: {len([api for api, config in conector.api_keys.items() if config.get('activa', False)])}")
    
    # Probar obtención de datos para una estación
    estacion_test = "quillota_centro"
    print(f"\nProbando obtención de datos para {estacion_test}...")
    
    datos = conector.obtener_datos_completos_estacion(estacion_test, dias=7)
    
    if not datos.empty:
        print(f"Datos obtenidos: {len(datos)} registros")
        print(f"Columnas: {list(datos.columns)}")
        print(f"Rango de fechas: {datos['fecha'].min()} a {datos['fecha'].max()}")
        print("\nPrimeras filas:")
        print(datos.head())
    else:
        print("No se pudieron obtener datos")

if __name__ == "__main__":
    main()
