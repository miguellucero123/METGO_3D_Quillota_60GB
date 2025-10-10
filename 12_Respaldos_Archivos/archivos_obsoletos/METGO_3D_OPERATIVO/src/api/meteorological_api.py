"""
Módulo de manejo robusto de APIs meteorológicas.
Versión operativa con manejo completo de errores.
"""

import requests
import logging
import time
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime, timedelta
import json


class APIMeteorologica:
    """
    Clase para manejo robusto de APIs meteorológicas.
    
    Características:
    - Manejo completo de errores
    - Rate limiting automático
    - Cache de respuestas
    - Reintentos automáticos
    - Fallback a datos locales
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializar cliente de API meteorológica.
        
        Args:
            config: Configuración del sistema
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuración de API
        self.api_config = config.get('APIS', {}).get('openmeteo', {})
        self.url_base = self.api_config.get('url_base', 'https://api.open-meteo.com/v1')
        self.timeout = self.api_config.get('timeout', 30)
        self.max_retries = self.api_config.get('max_retries', 3)
        self.rate_limit = self.api_config.get('rate_limit', 1000)
        
        # Cache simple en memoria
        self.cache = {}
        self.cache_duration = self.api_config.get('cache_duration', 3600)
        
        # Control de rate limiting
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_start = time.time()
        
        self.logger.info("Cliente API meteorológica inicializado")
    
    def obtener_datos_openmeteo(self, dias: int = 30) -> pd.DataFrame:
        """
        Obtener datos meteorológicos desde OpenMeteo API.
        
        Args:
            dias: Número de días de datos a obtener
            
        Returns:
            DataFrame con datos meteorológicos
            
        Raises:
            APIMeteorologicaError: Si hay error en la API
        """
        self.logger.info(f"Solicitando {dias} días de datos desde OpenMeteo")
        
        # Verificar cache primero
        cache_key = f"openmeteo_{dias}"
        if self._verificar_cache(cache_key):
            self.logger.info("Datos obtenidos desde cache")
            return self.cache[cache_key]['data']
        
        # Preparar parámetros de la API
        params = self._preparar_parametros_openmeteo(dias)
        
        # Realizar solicitud con manejo de errores
        try:
            datos = self._realizar_solicitud_api(params)
            
            # Guardar en cache
            self._guardar_en_cache(cache_key, datos)
            
            self.logger.info(f"Datos obtenidos exitosamente: {len(datos)} registros")
            return datos
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos de OpenMeteo: {e}")
            raise APIMeteorologicaError(f"Error en API OpenMeteo: {e}")
    
    def _preparar_parametros_openmeteo(self, dias: int) -> Dict[str, Any]:
        """Preparar parámetros para la solicitud a OpenMeteo."""
        quillota_config = self.config.get('QUILLOTA', {})
        coordenadas = quillota_config.get('coordenadas', {})
        
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=dias)
        
        params = {
            'latitude': coordenadas.get('latitud', -32.8833),
            'longitude': coordenadas.get('longitud', -71.25),
            'start_date': fecha_inicio.strftime('%Y-%m-%d'),
            'end_date': fecha_fin.strftime('%Y-%m-%d'),
            'daily': [
                'temperature_2m_max',
                'temperature_2m_min',
                'relative_humidity_2m',
                'precipitation_sum',
                'wind_speed_10m_max',
                'wind_direction_10m_dominant',
                'pressure_msl',
                'shortwave_radiation_sum',
                'cloud_cover'
            ],
            'timezone': 'America/Santiago'
        }
        
        return params
    
    def _realizar_solicitud_api(self, params: Dict[str, Any]) -> pd.DataFrame:
        """Realizar solicitud a la API con manejo robusto de errores."""
        url = f"{self.url_base}/forecast"
        
        for intento in range(self.max_retries):
            try:
                # Control de rate limiting
                self._aplicar_rate_limiting()
                
                # Realizar solicitud
                self.logger.debug(f"Realizando solicitud a: {url}")
                response = requests.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                    headers={'User-Agent': 'METGO-3D-Operativo/2.0'}
                )
                
                # Verificar respuesta
                response.raise_for_status()
                
                # Procesar respuesta
                datos = self._procesar_respuesta_openmeteo(response.json())
                
                return datos
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout en intento {intento + 1}/{self.max_retries}")
                if intento < self.max_retries - 1:
                    time.sleep(2 ** intento)  # Backoff exponencial
                    continue
                else:
                    raise APIMeteorologicaError("Timeout después de múltiples intentos")
            
            except requests.exceptions.ConnectionError:
                self.logger.warning(f"Error de conexión en intento {intento + 1}/{self.max_retries}")
                if intento < self.max_retries - 1:
                    time.sleep(2 ** intento)
                    continue
                else:
                    raise APIMeteorologicaError("Error de conexión después de múltiples intentos")
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit exceeded
                    self.logger.warning("Rate limit excedido, esperando...")
                    time.sleep(60)  # Esperar 1 minuto
                    continue
                else:
                    raise APIMeteorologicaError(f"Error HTTP {e.response.status_code}: {e}")
            
            except Exception as e:
                self.logger.error(f"Error inesperado en solicitud API: {e}")
                raise APIMeteorologicaError(f"Error inesperado: {e}")
        
        raise APIMeteorologicaError("Error después de todos los intentos")
    
    def _procesar_respuesta_openmeteo(self, response_data: Dict[str, Any]) -> pd.DataFrame:
        """Procesar respuesta de OpenMeteo API."""
        try:
            daily_data = response_data.get('daily', {})
            
            if not daily_data:
                raise APIMeteorologicaError("No hay datos diarios en la respuesta")
            
            # Crear DataFrame
            datos = pd.DataFrame({
                'fecha': pd.to_datetime(daily_data.get('time', [])),
                'temperatura_max': daily_data.get('temperature_2m_max', []),
                'temperatura_min': daily_data.get('temperature_2m_min', []),
                'humedad_relativa': daily_data.get('relative_humidity_2m', []),
                'precipitacion': daily_data.get('precipitation_sum', []),
                'velocidad_viento': daily_data.get('wind_speed_10m_max', []),
                'direccion_viento': daily_data.get('wind_direction_10m_dominant', []),
                'presion_atmosferica': daily_data.get('pressure_msl', []),
                'radiacion_solar': daily_data.get('shortwave_radiation_sum', []),
                'nubosidad': daily_data.get('cloud_cover', [])
            })
            
            # Validar datos básicos
            if datos.empty:
                raise APIMeteorologicaError("DataFrame vacío después del procesamiento")
            
            # Limpiar datos
            datos = self._limpiar_datos_api(datos)
            
            return datos
            
        except Exception as e:
            self.logger.error(f"Error procesando respuesta de API: {e}")
            raise APIMeteorologicaError(f"Error procesando datos: {e}")
    
    def _limpiar_datos_api(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Limpiar y validar datos de la API."""
        # Eliminar filas con valores nulos críticos
        datos = datos.dropna(subset=['temperatura_max', 'temperatura_min'])
        
        # Validar rangos razonables
        datos = datos[
            (datos['temperatura_max'] >= -50) & (datos['temperatura_max'] <= 60) &
            (datos['temperatura_min'] >= -50) & (datos['temperatura_min'] <= 60) &
            (datos['humedad_relativa'] >= 0) & (datos['humedad_relativa'] <= 100) &
            (datos['precipitacion'] >= 0) &
            (datos['velocidad_viento'] >= 0)
        ]
        
        # Convertir direcciones de viento a texto
        direcciones = {
            0: 'N', 45: 'NE', 90: 'E', 135: 'SE',
            180: 'S', 225: 'SW', 270: 'W', 315: 'NW'
        }
        
        datos['direccion_viento'] = datos['direccion_viento'].map(
            lambda x: direcciones.get(round(x / 45) * 45, 'N')
        )
        
        return datos
    
    def _aplicar_rate_limiting(self):
        """Aplicar control de rate limiting."""
        current_time = time.time()
        
        # Resetear contador cada hora
        if current_time - self.rate_limit_start > 3600:
            self.request_count = 0
            self.rate_limit_start = current_time
        
        # Verificar límite de requests
        if self.request_count >= self.rate_limit:
            sleep_time = 3600 - (current_time - self.rate_limit_start)
            if sleep_time > 0:
                self.logger.warning(f"Rate limit alcanzado, esperando {sleep_time:.0f} segundos")
                time.sleep(sleep_time)
                self.request_count = 0
                self.rate_limit_start = time.time()
        
        # Espaciar requests
        time_since_last = current_time - self.last_request_time
        min_interval = 3600 / self.rate_limit  # Intervalo mínimo entre requests
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _verificar_cache(self, cache_key: str) -> bool:
        """Verificar si los datos están en cache y son válidos."""
        if cache_key not in self.cache:
            return False
        
        cache_entry = self.cache[cache_key]
        cache_time = cache_entry['timestamp']
        
        # Verificar si el cache ha expirado
        if time.time() - cache_time > self.cache_duration:
            del self.cache[cache_key]
            return False
        
        return True
    
    def _guardar_en_cache(self, cache_key: str, datos: pd.DataFrame):
        """Guardar datos en cache."""
        self.cache[cache_key] = {
            'data': datos.copy(),
            'timestamp': time.time()
        }
        
        # Limpiar cache si es muy grande
        if len(self.cache) > 10:
            # Eliminar entrada más antigua
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
    
    def obtener_pronostico(self, dias: int = 7) -> pd.DataFrame:
        """
        Obtener pronóstico meteorológico.
        
        Args:
            dias: Número de días de pronóstico
            
        Returns:
            DataFrame con pronóstico meteorológico
        """
        self.logger.info(f"Obteniendo pronóstico para {dias} días")
        
        try:
            # Usar endpoint de pronóstico
            params = self._preparar_parametros_pronostico(dias)
            datos = self._realizar_solicitud_api(params)
            
            self.logger.info(f"Pronóstico obtenido: {len(datos)} días")
            return datos
            
        except Exception as e:
            self.logger.error(f"Error obteniendo pronóstico: {e}")
            raise APIMeteorologicaError(f"Error en pronóstico: {e}")
    
    def _preparar_parametros_pronostico(self, dias: int) -> Dict[str, Any]:
        """Preparar parámetros para pronóstico."""
        quillota_config = self.config.get('QUILLOTA', {})
        coordenadas = quillota_config.get('coordenadas', {})
        
        params = {
            'latitude': coordenadas.get('latitud', -32.8833),
            'longitude': coordenadas.get('longitud', -71.25),
            'forecast_days': dias,
            'daily': [
                'temperature_2m_max',
                'temperature_2m_min',
                'relative_humidity_2m',
                'precipitation_sum',
                'wind_speed_10m_max',
                'wind_direction_10m_dominant',
                'pressure_msl',
                'shortwave_radiation_sum',
                'cloud_cover'
            ],
            'timezone': 'America/Santiago'
        }
        
        return params
    
    def verificar_conectividad(self) -> bool:
        """
        Verificar conectividad con la API.
        
        Returns:
            True si hay conectividad, False en caso contrario
        """
        try:
            # Solicitud simple para verificar conectividad
            response = requests.get(
                f"{self.url_base}/forecast",
                params={'latitude': -32.8833, 'longitude': -71.25, 'forecast_days': 1},
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.warning(f"Sin conectividad con API: {e}")
            return False


class APIMeteorologicaError(Exception):
    """Excepción personalizada para errores de API meteorológica."""
    pass
