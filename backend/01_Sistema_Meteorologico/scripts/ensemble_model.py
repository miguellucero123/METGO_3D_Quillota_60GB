import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class EnsembleMeteorologico:
    """
    Motor estadístico multi-modelo.
    Descarga predicciones de varios Modelos de Circulación Global (GCMs)
    para calcular consenso, medianas, probabilidades e incertidumbre.
    """
    
    def __init__(self, lat=-32.88, lon=-71.25):
        self.lat = lat
        self.lon = lon
        # Utilizamos 5 modelos globales de altísima calidad
        self.modelos = ['ecmwf_ifs04', 'gfs_seamless', 'icon_seamless']
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def obtener_ensemble_diario(self, dias=7):
        """Descarga el ensamble para variables diarias"""
        print(f"[ENSEMBLE] Consultando {len(self.modelos)} modelos numéricos para Quillota...")
        params = {
            'latitude': self.lat,
            'longitude': self.lon,
            'daily': ['precipitation_sum', 'temperature_2m_min', 'temperature_2m_max'],
            'timezone': 'America/Santiago',
            'forecast_days': dias,
            'models': ','.join(self.modelos)
        }
        
        ultimo_error = None
        for intento in range(1, 4):
            try:
                response = requests.get(self.base_url, params=params, timeout=20)
                response.raise_for_status()
                datos = response.json()
                return self._procesar_estadisticas_diarias(datos)
            except Exception as e:
                ultimo_error = e
                if intento < 3:
                    time.sleep(min(2 ** intento, 8))
        print(f"[ERROR] Fallo en la extracción del Ensemble tras 3 intentos: {ultimo_error}")
        return None

    def _procesar_estadisticas_diarias(self, datos_crudos):
        """Procesa los arrays de los diferentes modelos en un dataframe estadístico"""
        fechas = datos_crudos['daily']['time']
        resultados = []
        
        for i, fecha in enumerate(fechas):
            # Extraer vectores de todos los modelos para este día
            precip_vector = []
            tmin_vector = []
            
            for modelo in self.modelos:
                key_precip = f"precipitation_sum_{modelo}"
                key_tmin = f"temperature_2m_min_{modelo}"
                
                # Manejar fallos donde algún modelo no reporte ese día
                if key_precip in datos_crudos['daily'] and datos_crudos['daily'][key_precip][i] is not None:
                    precip_vector.append(datos_crudos['daily'][key_precip][i])
                if key_tmin in datos_crudos['daily'] and datos_crudos['daily'][key_tmin][i] is not None:
                    tmin_vector.append(datos_crudos['daily'][key_tmin][i])
            
            # Matemáticas del Ensemble
            precip_arr = np.array(precip_vector)
            tmin_arr = np.array(tmin_vector)
            
            if len(precip_arr) == 0:
                continue
                
            # Probabilidad de lluvia (consenso > 0.5mm)
            modelos_con_lluvia = np.sum(precip_arr > 0.5)
            probabilidad = (modelos_con_lluvia / len(precip_arr)) * 100
            
            # Estadísticas Lluvia
            mediana_precip = np.median(precip_arr)
            rango_min_precip = np.min(precip_arr)
            rango_max_precip = np.max(precip_arr)
            # Best Match: Media de los valores quitando los extremos (outliers)
            best_match_precip = np.percentile(precip_arr, 75) if mediana_precip > 5 else mediana_precip
            
            # Estadísticas Temperatura y Heladas
            mediana_tmin = np.median(tmin_arr) if len(tmin_arr) > 0 else None
            
            # Evaluación Termodinámica de Heladas
            tipo_helada = "Ninguna"
            alerta_helada = False
            if mediana_tmin is not None and mediana_tmin <= 2.5: # Umbral preventivo
                alerta_helada = True
                # Simulamos lógica termodinámica (requeriría rocío y viento horario para exactitud total)
                if mediana_tmin < 0:
                    tipo_helada = "Helada Radiativa (Alta Severidad)"
                else:
                    tipo_helada = "Riesgo de Helada en Suelo"
            
            resultados.append({
                'fecha': fecha,
                'precipitacion': {
                    'mediana': round(mediana_precip, 1),
                    'best_match': round(best_match_precip, 1),
                    'minimo': round(rango_min_precip, 1),
                    'maximo': round(rango_max_precip, 1),
                    'probabilidad': round(probabilidad, 0)
                },
                'temperatura': {
                    'min_mediana': round(mediana_tmin, 1) if mediana_tmin is not None else None,
                    'alerta_helada': alerta_helada,
                    'tipo_helada': tipo_helada
                }
            })
            
        return resultados

if __name__ == "__main__":
    motor = EnsembleMeteorologico()
    datos = motor.obtener_ensemble_diario(dias=7)
    import json
    print(json.dumps(datos, indent=2))
