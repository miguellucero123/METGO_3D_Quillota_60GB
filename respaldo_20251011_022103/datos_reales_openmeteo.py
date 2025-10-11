#!/usr/bin/env python3
"""
Sistema METGO - Datos Reales OpenMeteo
Autor: Sistema METGO
Fecha: 2025-10-10
"""

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

class OpenMeteoData:
    """Clase para obtener datos reales de OpenMeteo API"""
    
    def __init__(self):
        self.api_base = 'https://api.open-meteo.com/v1'
        self.timeout = 30
        self.max_retries = 3
        
        # Coordenadas de las estaciones METGO
        self.estaciones = {
            'Quillota': {'lat': -32.8833, 'lon': -71.25},
            'Santiago': {'lat': -33.4489, 'lon': -70.6693},
            'Valparaiso': {'lat': -33.0458, 'lon': -71.6197},
            'Vina del Mar': {'lat': -33.0153, 'lon': -71.5508},
            'Casablanca': {'lat': -33.3167, 'lon': -71.4167},
            'Los Nogales': {'lat': -32.9333, 'lon': -71.2167},
            'Hijuelas': {'lat': -32.8000, 'lon': -71.1333},
            'Limache': {'lat': -33.0167, 'lon': -71.2667},
            'Olmue': {'lat': -33.0000, 'lon': -71.2167}
        }
    
    def obtener_datos_historicos(self, estacion='Quillota', dias=30):
        """Obtiene datos históricos de OpenMeteo"""
        print(f"Obteniendo datos historicos para {estacion} ({dias} dias)")
        
        if estacion not in self.estaciones:
            print(f"ERROR - Estación {estacion} no encontrada")
            return None
        
        coords = self.estaciones[estacion]
        
        try:
            # Usar API de forecast con past_days
            url = f"{self.api_base}/forecast"
            
            params = {
                'latitude': coords['lat'],
                'longitude': coords['lon'],
                'daily': [
                    'temperature_2m_max',
                    'temperature_2m_min',
                    'temperature_2m_mean',
                    'relative_humidity_2m_max',
                    'precipitation_sum',
                    'wind_speed_10m_max',
                    'pressure_msl_mean'
                ],
                'timezone': 'America/Santiago',
                'past_days': min(dias, 92),  # Máximo 92 días hacia atrás
                'forecast_days': 7
            }
            
            print(f" Conectando con OpenMeteo API...")
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return self._procesar_datos_openmeteo(data, estacion)
            else:
                print(f"ERROR - Error HTTP {response.status_code}")
                return self._crear_datos_sinteticos(estacion, dias)
                
        except Exception as e:
            print(f"ERROR - Error conectando con OpenMeteo: {e}")
            return self._crear_datos_sinteticos(estacion, dias)
    
    def obtener_datos_pronostico(self, estacion='Quillota', dias=7):
        """Obtiene datos de pronóstico de OpenMeteo"""
        print(f" Obteniendo pronóstico para {estacion} ({dias} días)")
        
        if estacion not in self.estaciones:
            print(f"ERROR - Estación {estacion} no encontrada")
            return None
        
        coords = self.estaciones[estacion]
        
        try:
            url = f"{self.api_base}/forecast"
            
            params = {
                'latitude': coords['lat'],
                'longitude': coords['lon'],
                'daily': [
                    'temperature_2m_max',
                    'temperature_2m_min',
                    'temperature_2m_mean',
                    'relative_humidity_2m_max',
                    'precipitation_sum',
                    'wind_speed_10m_max',
                    'pressure_msl_mean',
                    'precipitation_probability_max'
                ],
                'timezone': 'America/Santiago',
                'forecast_days': min(dias, 16)  # Máximo 16 días de pronóstico
            }
            
            print(f" Obteniendo pronóstico de OpenMeteo...")
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                df = self._procesar_datos_openmeteo(data, estacion)
                if df is not None:
                    df['fuente_datos'] = 'openmeteo_pronostico'
                return df
            else:
                print(f"ERROR - Error HTTP {response.status_code}")
                return self._crear_datos_sinteticos(estacion, dias)
                
        except Exception as e:
            print(f"ERROR - Error obteniendo pronóstico: {e}")
            return self._crear_datos_sinteticos(estacion, dias)
    
    def _procesar_datos_openmeteo(self, data, estacion):
        """Procesa los datos recibidos de OpenMeteo"""
        try:
            if 'daily' not in data:
                print("ERROR - Formato de respuesta inesperado")
                return None
            
            daily_data = data['daily']
            times = daily_data.get('time', [])
            
            if not times:
                print("ERROR - Sin datos de tiempo")
                return None
            
            print(f"OK - Datos recibidos: {len(times)} días")
            
            registros = []
            for i, fecha_str in enumerate(times):
                try:
                    fecha = pd.to_datetime(fecha_str)
                    
                    registro = {
                        'fecha': fecha,
                        'temperatura_max': daily_data.get('temperature_2m_max', [None]*len(times))[i],
                        'temperatura_min': daily_data.get('temperature_2m_min', [None]*len(times))[i], 
                        'temperatura_promedio': daily_data.get('temperature_2m_mean', [None]*len(times))[i],
                        'humedad_relativa': daily_data.get('relative_humidity_2m_max', [None]*len(times))[i],
                        'precipitacion': daily_data.get('precipitation_sum', [0]*len(times))[i],
                        'velocidad_viento': daily_data.get('wind_speed_10m_max', [None]*len(times))[i],
                        'presion_atmosferica': daily_data.get('pressure_msl_mean', [None]*len(times))[i],
                        'fuente_datos': 'openmeteo_real'
                    }
                    
                    # Agregar probabilidad de precipitación si está disponible
                    if 'precipitation_probability_max' in daily_data:
                        registro['probabilidad_lluvia'] = daily_data.get('precipitation_probability_max', [None]*len(times))[i]
                    
                    # Solo agregar si tiene al menos temperatura
                    if registro['temperatura_max'] is not None:
                        registros.append(registro)
                        
                except Exception as e:
                    print(f"WARN - Error procesando {fecha_str}: {e}")
                    continue
            
            if registros:
                df = pd.DataFrame(registros)
                
                # Convertir a numérico
                cols_numericas = ['temperatura_max', 'temperatura_min', 'temperatura_promedio',
                                'humedad_relativa', 'precipitacion', 'velocidad_viento', 
                                'presion_atmosferica']
                
                for col in cols_numericas:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Agregar información de estación
                df['estacion'] = estacion
                
                print(f"OK - Datos OpenMeteo procesados: {len(df)} registros válidos")
                print(f"    Temperatura: {df['temperatura_max'].min():.1f}°C - {df['temperatura_max'].max():.1f}°C")
                print(f"    Precipitación: {df['precipitacion'].sum():.1f}mm")
                
                return df
            else:
                print("ERROR - No se pudieron procesar datos de OpenMeteo")
                return None
                
        except Exception as e:
            print(f"ERROR - Error procesando datos OpenMeteo: {e}")
            return None
    
    def _crear_datos_sinteticos(self, estacion, dias):
        """Crea datos sintéticos como respaldo"""
        print(f" Creando datos sintéticos para {estacion} ({dias} días)")
        
        if estacion not in self.estaciones:
            estacion = 'Quillota'
        
        registros = []
        fecha_inicio = datetime.now() - timedelta(days=dias)
        
        # Parámetros base según la estación
        params_base = self._obtener_parametros_estacion(estacion)
        
        for i in range(dias):
            fecha = fecha_inicio + timedelta(days=i)
            
            # Estacionalidad (hemisferio sur)
            dia_año = fecha.timetuple().tm_yday
            factor_estacional = np.cos(2 * np.pi * (dia_año - 15) / 365)
            
            # Temperatura base con estacionalidad
            temp_base = params_base['temp_base'] + params_base['temp_amplitud'] * factor_estacional
            
            # Variación diaria
            variacion = np.random.normal(0, params_base['temp_variacion'])
            
            # Temperaturas
            temp_max = temp_base + params_base['temp_diferencia'] + variacion
            temp_min = temp_base - params_base['temp_diferencia'] + variacion * 0.7
            
            # Otras variables
            humedad = max(20, min(100, params_base['humedad_base'] - (temp_base - 15) * 2 + np.random.normal(0, 10)))
            precipitacion = max(0, np.random.exponential(params_base['precip_base']) if np.random.random() < 0.1 else 0)
            viento = max(0, np.random.gamma(2, params_base['viento_base']))
            presion = params_base['presion_base'] + np.random.normal(0, 10)
            
            registro = {
                'fecha': fecha,
                'temperatura_max': round(temp_max, 1),
                'temperatura_min': round(temp_min, 1),
                'temperatura_promedio': round((temp_max + temp_min) / 2, 1),
                'humedad_relativa': round(humedad, 1),
                'precipitacion': round(precipitacion, 1),
                'velocidad_viento': round(viento, 1),
                'presion_atmosferica': round(presion, 1),
                'estacion': estacion,
                'fuente_datos': 'sintetico_respaldo'
            }
            
            registros.append(registro)
        
        df = pd.DataFrame(registros)
        print(f"OK - Datos sintéticos creados: {len(df)} registros")
        return df
    
    def _obtener_parametros_estacion(self, estacion):
        """Obtiene parámetros específicos para cada estación"""
        parametros = {
            'Quillota': {
                'temp_base': 16.5, 'temp_amplitud': 8, 'temp_variacion': 3, 'temp_diferencia': 7,
                'humedad_base': 70, 'precip_base': 2, 'viento_base': 4, 'presion_base': 1013.25
            },
            'Santiago': {
                'temp_base': 17.0, 'temp_amplitud': 9, 'temp_variacion': 4, 'temp_diferencia': 8,
                'humedad_base': 60, 'precip_base': 1.5, 'viento_base': 3, 'presion_base': 1015.00
            },
            'Valparaíso': {
                'temp_base': 15.5, 'temp_amplitud': 6, 'temp_variacion': 2.5, 'temp_diferencia': 6,
                'humedad_base': 80, 'precip_base': 2.5, 'viento_base': 6, 'presion_base': 1012.50
            },
            'Viña del Mar': {
                'temp_base': 15.0, 'temp_amplitud': 5, 'temp_variacion': 2, 'temp_diferencia': 5,
                'humedad_base': 85, 'precip_base': 3, 'viento_base': 5, 'presion_base': 1012.00
            },
            'Casablanca': {
                'temp_base': 14.0, 'temp_amplitud': 7, 'temp_variacion': 3.5, 'temp_diferencia': 8,
                'humedad_base': 75, 'precip_base': 2.2, 'viento_base': 4.5, 'presion_base': 1014.00
            }
        }
        
        return parametros.get(estacion, parametros['Quillota'])
    
    def verificar_conexion(self):
        """Verifica la conectividad con OpenMeteo"""
        print(" Verificando conectividad con OpenMeteo...")
        
        try:
            url = f"{self.api_base}/forecast"
            params = {
                'latitude': -32.8833,
                'longitude': -71.25,
                'daily': 'temperature_2m_max',
                'forecast_days': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                print("OK - Conexión con OpenMeteo exitosa")
                return True
            else:
                print(f"ERROR - Error de conexión: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"ERROR - Error de conectividad: {e}")
            return False

# Función principal para usar en los dashboards
def obtener_datos_meteorologicos_reales(estacion='Quillota', tipo='historicos', dias=30):
    """
    Función principal para obtener datos meteorológicos reales
    
    Args:
        estacion (str): Nombre de la estación
        tipo (str): 'historicos' o 'pronostico'
        dias (int): Número de días a obtener
    
    Returns:
        pandas.DataFrame: Datos meteorológicos
    """
    openmeteo = OpenMeteoData()
    
    if tipo == 'historicos':
        return openmeteo.obtener_datos_historicos(estacion, dias)
    elif tipo == 'pronostico':
        return openmeteo.obtener_datos_pronostico(estacion, dias)
    else:
        print(f"ERROR - Tipo no válido: {tipo}")
        return None

# Función de verificación
def verificar_datos_reales():
    """Verifica la disponibilidad de datos reales"""
    openmeteo = OpenMeteoData()
    
    print("=" * 60)
    print("VERIFICACION DE DATOS REALES OPENMETEO")
    print("=" * 60)
    
    # Verificar conectividad
    conexion_ok = openmeteo.verificar_conexion()
    
    if conexion_ok:
        print("\n Probando obtención de datos...")
        
        # Probar con Quillota
        datos = openmeteo.obtener_datos_historicos('Quillota', 7)
        
        if datos is not None:
            print(f"\nOK - Datos reales disponibles:")
            print(f"    Registros: {len(datos)}")
            print(f"    Temperatura promedio: {datos['temperatura_promedio'].mean():.1f}°C")
            print(f"    Precipitación total: {datos['precipitacion'].sum():.1f}mm")
            print(f"    Estación: {datos['estacion'].iloc[0]}")
            return True
        else:
            print("\nERROR - No se pudieron obtener datos reales")
            return False
    else:
        print("\nERROR - Sin conexión a OpenMeteo")
        return False

if __name__ == "__main__":
    # Ejecutar verificación
    verificar_datos_reales()
