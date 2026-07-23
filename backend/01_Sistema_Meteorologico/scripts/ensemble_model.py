import os
import time
import requests
import numpy as np

class EnsembleMeteorologico:
    """
    Motor estadístico multi-modelo.
    Descarga predicciones de varios Modelos de Circulación Global (GCMs)
    para calcular consenso, medianas, probabilidades e incertidumbre.
    """

    def __init__(self, lat=-32.88, lon=-71.25):
        self.lat = lat
        self.lon = lon
        # Modelos globales disponibles en OpenMeteo (forecast multi-model)
        self.modelos = ['ecmwf_ifs04', 'gfs_seamless', 'icon_seamless']
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.timeout = int(os.getenv('METGO_OPENMETEO_TIMEOUT', '25'))
        self.max_retries = int(os.getenv('METGO_OPENMETEO_RETRIES', '3'))

    def _get_json(self, params):
        """GET con reintentos ante 429/5xx y errores de red (típico en Render free)."""
        ultimo_error = None
        for intento in range(1, self.max_retries + 1):
            try:
                response = requests.get(self.base_url, params=params, timeout=self.timeout)
                if response.status_code == 200:
                    return response.json()
                if response.status_code in (429, 500, 502, 503, 504) and intento < self.max_retries:
                    time.sleep(min(2 ** intento, 8))
                    continue
                ultimo_error = RuntimeError(f"OpenMeteo HTTP {response.status_code}")
            except Exception as e:
                ultimo_error = e
                if intento < self.max_retries:
                    time.sleep(min(2 ** intento, 8))
                    continue
        if ultimo_error:
            print(f"[ERROR] Ensemble OpenMeteo tras {self.max_retries} intentos: {ultimo_error}")
        return None

    def obtener_ensemble_diario(self, dias=7):
        """Descarga el ensamble para variables diarias.

        1) Intenta multi-modelo en una sola petición.
        2) Si falla (frecuente desde Render), consulta cada modelo por separado
           y fusiona las series.
        """
        print(f"[ENSEMBLE] Consultando {len(self.modelos)} modelos numéricos para Quillota...")
        daily_vars = ['precipitation_sum', 'temperature_2m_min', 'temperature_2m_max']
        params = {
            'latitude': self.lat,
            'longitude': self.lon,
            'daily': daily_vars,
            'timezone': 'America/Santiago',
            'forecast_days': dias,
            'models': ','.join(self.modelos),
        }

        datos = self._get_json(params)
        if datos and 'daily' in datos:
            return self._procesar_estadisticas_diarias(datos)

        print("[ENSEMBLE] Multi-modelo falló; reintentando modelo por modelo...")
        fusion = self._obtener_por_modelo(dias, daily_vars)
        if fusion is None:
            return None
        return self._procesar_estadisticas_diarias(fusion)

    def _obtener_por_modelo(self, dias, daily_vars):
        """Consulta cada GCM por separado y arma el payload multi-modelo."""
        fusion_daily = {'time': None}
        ok = 0
        for modelo in self.modelos:
            params = {
                'latitude': self.lat,
                'longitude': self.lon,
                'daily': daily_vars,
                'timezone': 'America/Santiago',
                'forecast_days': dias,
                'models': modelo,
            }
            datos = self._get_json(params)
            if not datos or 'daily' not in datos:
                continue
            daily = datos['daily']
            if fusion_daily['time'] is None:
                fusion_daily['time'] = daily.get('time')
            for var in daily_vars:
                # OpenMeteo: con un solo modelo la clave puede venir sin sufijo o con él
                series = daily.get(f"{var}_{modelo}", daily.get(var))
                if series is not None:
                    fusion_daily[f"{var}_{modelo}"] = series
            ok += 1

        if ok == 0 or not fusion_daily.get('time'):
            return None
        return {'daily': fusion_daily}

    def _procesar_estadisticas_diarias(self, datos_crudos):
        """Procesa los arrays de los diferentes modelos en un dataframe estadístico"""
        fechas = datos_crudos['daily']['time']
        resultados = []

        for i, fecha in enumerate(fechas):
            precip_vector = []
            tmin_vector = []

            for modelo in self.modelos:
                key_precip = f"precipitation_sum_{modelo}"
                key_tmin = f"temperature_2m_min_{modelo}"

                if key_precip in datos_crudos['daily'] and datos_crudos['daily'][key_precip][i] is not None:
                    precip_vector.append(datos_crudos['daily'][key_precip][i])
                if key_tmin in datos_crudos['daily'] and datos_crudos['daily'][key_tmin][i] is not None:
                    tmin_vector.append(datos_crudos['daily'][key_tmin][i])

            precip_arr = np.array(precip_vector)
            tmin_arr = np.array(tmin_vector)

            if len(precip_arr) == 0:
                continue

            modelos_con_lluvia = np.sum(precip_arr > 0.5)
            probabilidad = (modelos_con_lluvia / len(precip_arr)) * 100

            mediana_precip = np.median(precip_arr)
            rango_min_precip = np.min(precip_arr)
            rango_max_precip = np.max(precip_arr)
            best_match_precip = np.percentile(precip_arr, 75) if mediana_precip > 5 else mediana_precip

            mediana_tmin = np.median(tmin_arr) if len(tmin_arr) > 0 else None

            tipo_helada = "Ninguna"
            alerta_helada = False
            if mediana_tmin is not None and mediana_tmin <= 2.5:
                alerta_helada = True
                if mediana_tmin < 0:
                    tipo_helada = "Helada Radiativa (Alta Severidad)"
                else:
                    tipo_helada = "Riesgo de Helada en Suelo"

            resultados.append({
                'fecha': fecha,
                'precipitacion': {
                    'mediana': round(float(mediana_precip), 1),
                    'best_match': round(float(best_match_precip), 1),
                    'minimo': round(float(rango_min_precip), 1),
                    'maximo': round(float(rango_max_precip), 1),
                    'probabilidad': round(float(probabilidad), 0)
                },
                'temperatura': {
                    'min_mediana': round(float(mediana_tmin), 1) if mediana_tmin is not None else None,
                    'alerta_helada': alerta_helada,
                    'tipo_helada': tipo_helada
                }
            })

        return resultados if resultados else None

if __name__ == "__main__":
    motor = EnsembleMeteorologico()
    datos = motor.obtener_ensemble_diario(dias=7)
    import json
    print(json.dumps(datos, indent=2))
