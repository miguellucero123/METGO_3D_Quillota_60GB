#!/usr/bin/env python3
"""
Sistema METGO - Datos Reales OpenMeteo
Autor: Sistema METGO
Fecha: 2025-10-10
"""

import os
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
import time
import warnings
warnings.filterwarnings('ignore')

TZ_CHILE = ZoneInfo('America/Santiago')

DAILY_VARS_HISTORICO = [
    'temperature_2m_max',
    'temperature_2m_min',
    'temperature_2m_mean',
    'relative_humidity_2m_max',
    'precipitation_sum',
    'wind_speed_10m_max',
    'pressure_msl_mean',
    'cloud_cover_mean',
    'shortwave_radiation_sum',
    'wind_direction_10m_dominant',
    'et0_fao_evapotranspiration',
]

ARCHIVE_API_BASE = 'https://archive-api.open-meteo.com/v1/archive'

# Nombres OpenMeteo en self.estaciones (sin tilde en algunos casos)
_ALIASES_ESTACION = {
    'Viña del Mar': 'Vina del Mar',
    'Valparaíso': 'Valparaiso',
}


class OpenMeteoData:
    """Clase para obtener datos reales de OpenMeteo API"""
    
    def __init__(self):
        self.api_base = 'https://api.open-meteo.com/v1'
        # En Render (plan free) la salida a OpenMeteo puede ser lenta o intermitente;
        # timeout y reintentos configurables por entorno para reducir fallos transitorios.
        self.timeout = int(os.getenv('METGO_OPENMETEO_TIMEOUT', '25'))
        self.max_retries = int(os.getenv('METGO_OPENMETEO_RETRIES', '3'))
        
        # Coordenadas de las estaciones METGO (multi-sitio)
        self.estaciones = {
            'Quillota': {'lat': -32.8833, 'lon': -71.25},
            'Santiago': {'lat': -33.4489, 'lon': -70.6693},
            'Valparaiso': {'lat': -33.0458, 'lon': -71.6197},
            'Vina del Mar': {'lat': -33.0153, 'lon': -71.5508},
            'Casablanca': {'lat': -33.3167, 'lon': -71.4167},
            'Los Nogales': {'lat': -32.9333, 'lon': -71.2167},
            'Hijuelas': {'lat': -32.8000, 'lon': -71.1333},
            'Limache': {'lat': -33.0167, 'lon': -71.2667},
            'Olmue': {'lat': -33.0000, 'lon': -71.2167},
            # Torres del Paine (sitio=paine)
            'Base Torres': {'lat': -50.9417, 'lon': -72.9667},
            'Glaciar Grey': {'lat': -51.0, 'lon': -73.23},
            'Valle del Frances': {'lat': -50.9667, 'lon': -73.0833},
            'Paine Grande': {'lat': -50.9500, 'lon': -73.1167},
            'Campamento Italiano': {'lat': -50.9583, 'lon': -73.0667},
            'Los Cuernos': {'lat': -50.9750, 'lon': -73.0500},
            # Copiapó (sitio=copiapo, calidad del aire E7)
            'Copiapo Centro': {'lat': -27.3668, 'lon': -70.3323},
            'Paipote': {'lat': -27.4064, 'lon': -70.2853},
            'Tierra Amarilla': {'lat': -27.4667, 'lon': -70.2667},
            # Sitio plantilla E6 (ficticio)
            'Demo Norte': {'lat': -33.30, 'lon': -71.40},
            'Demo Sur': {'lat': -33.34, 'lon': -71.44},
        }
    
    def _get_json(self, url, params, intentos=None, timeout=None):
        """GET a OpenMeteo con reintentos y backoff exponencial.

        Devuelve (status_code, json|None). status_code=0 indica error de red.
        Reintenta ante 429/5xx y errores de red (típicos en Render free).
        """
        intentos = intentos or self.max_retries
        timeout = timeout or self.timeout
        ultimo_error = None
        for intento in range(1, intentos + 1):
            try:
                response = requests.get(url, params=params, timeout=timeout)
                if response.status_code == 200:
                    return 200, response.json()
                if response.status_code in (429, 500, 502, 503, 504) and intento < intentos:
                    time.sleep(min(2 ** intento, 8))
                    continue
                print(f"ERROR - OpenMeteo HTTP {response.status_code} (intento {intento}/{intentos})")
                return response.status_code, None
            except Exception as e:
                ultimo_error = e
                if intento < intentos:
                    time.sleep(min(2 ** intento, 8))
                    continue
        if ultimo_error:
            print(f"ERROR - Error de red OpenMeteo tras {intentos} intentos: {ultimo_error}")
        return 0, None

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
                'daily': DAILY_VARS_HISTORICO,
                'hourly': ['visibility', 'cloud_cover'],
                'timezone': 'America/Santiago',
                'past_days': min(dias, 92),  # Máximo 92 días hacia atrás
                'forecast_days': 0,
            }
            
            print(f" Conectando con OpenMeteo API...")
            status, data = self._get_json(url, params)

            if status == 200 and data:
                return self._procesar_datos_openmeteo(data, estacion)
            print(f"ERROR - No se obtuvieron historicos (status {status})")
            return None

        except Exception as e:
            print(f"ERROR - Error conectando con OpenMeteo: {e}")
            return None

    def _resolver_estacion(self, estacion):
        key = _ALIASES_ESTACION.get(estacion, estacion)
        if key not in self.estaciones:
            print(f"ERROR - Estación {estacion} no encontrada")
            return None
        return key

    def _rango_archive_chile(self, anios: int) -> tuple[date, date]:
        hoy = datetime.now(TZ_CHILE).date()
        end_date = hoy - timedelta(days=1)
        anios = max(1, int(anios))
        try:
            start_date = end_date.replace(year=end_date.year - anios)
        except ValueError:
            start_date = end_date.replace(year=end_date.year - anios, day=28)
        if start_date > end_date:
            start_date = end_date - timedelta(days=365 * anios)
        return start_date, end_date

    def _chunks_anuales(self, start_date: date, end_date: date) -> list[tuple[date, date]]:
        chunks: list[tuple[date, date]] = []
        year = start_date.year
        while year <= end_date.year:
            chunk_start = start_date if year == start_date.year else date(year, 1, 1)
            chunk_end = end_date if year == end_date.year else date(year, 12, 31)
            if chunk_start <= chunk_end:
                chunks.append((chunk_start, chunk_end))
            year += 1
        return chunks

    def _fetch_archive_chunk(self, coords: dict, start_date: date, end_date: date) -> dict | None:
        params = {
            'latitude': coords['lat'],
            'longitude': coords['lon'],
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'daily': DAILY_VARS_HISTORICO,
            'timezone': 'America/Santiago',
        }
        status, data = self._get_json(ARCHIVE_API_BASE, params, timeout=60)
        if status == 200 and data:
            return data
        print(
            f"ERROR - Archive OpenMeteo {start_date}..{end_date} (status {status})"
        )
        return None

    def obtener_datos_archive(self, estacion='Quillota', anios=5):
        """Históricos diarios ERA5 vía OpenMeteo Archive (hasta ayer, Chile)."""
        estacion_key = self._resolver_estacion(estacion)
        if not estacion_key:
            return None

        anios = max(1, int(anios))
        print(f"Obteniendo archive OpenMeteo para {estacion_key} ({anios} años)")

        coords = self.estaciones[estacion_key]
        start_date, end_date = self._rango_archive_chile(anios)
        chunks = self._chunks_anuales(start_date, end_date)

        frames: list[pd.DataFrame] = []
        for c_start, c_end in chunks:
            print(f" Archive {c_start.isoformat()} → {c_end.isoformat()}...")
            raw = self._fetch_archive_chunk(coords, c_start, c_end)
            if not raw:
                continue
            df_chunk = self._procesar_datos_openmeteo(raw, estacion_key)
            if df_chunk is not None and not df_chunk.empty:
                frames.append(df_chunk)

        if not frames:
            print("ERROR - Sin datos archive")
            return None

        df = pd.concat(frames, ignore_index=True)
        df = df.drop_duplicates(subset=['fecha'], keep='last').sort_values('fecha')
        df['fuente_datos'] = 'openmeteo_archive'
        df['estacion'] = estacion_key
        print(f"OK - Archive consolidado: {len(df)} días ({start_date} .. {end_date})")
        return df
    
    def obtener_datos_pronostico(self, estacion='Quillota', dias=16):
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
                    'precipitation_probability_max',
                    'cloud_cover_mean',
                    'shortwave_radiation_sum',
                    'wind_direction_10m_dominant',
                    'et0_fao_evapotranspiration',
                ],
                'hourly': ['visibility', 'cloud_cover'],
                'timezone': 'America/Santiago',
                'forecast_days': min(dias, 16)  # Máximo 16 días de pronóstico
            }
            
            print(f" Obteniendo pronóstico de OpenMeteo...")
            status, data = self._get_json(url, params)

            if status == 200 and data:
                df = self._procesar_datos_openmeteo(data, estacion)
                if df is not None and not df.empty:
                    df['fuente_datos'] = 'openmeteo_pronostico'
                    return df
                print('WARN - OpenMeteo 200 sin filas válidas')
                return None
            print(f"ERROR - No se obtuvo pronostico (status {status})")
            return None

        except Exception as e:
            print(f"ERROR - Error obteniendo pronóstico: {e}")
            return None

    def obtener_viento_horario_pronostico(self, estacion='Quillota', dias=7):
        """Obtiene pronóstico horario de viento (dirección y velocidad).

        Devuelve arrays paralelos para graficar una rosa de vientos más fina.
        """
        if estacion not in self.estaciones:
            return {
                "estacion": estacion,
                "direcciones": [],
                "velocidades": [],
                "unidad": "m/s",
                "fuente_datos": "openmeteo_pronostico_hourly",
            }

        coords = self.estaciones[estacion]
        dias = max(1, int(dias))

        try:
            url = f"{self.api_base}/forecast"
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "hourly": ["wind_speed_10m", "wind_direction_10m"],
                "timezone": "America/Santiago",
                "forecast_days": min(dias, 16),  # OpenMeteo máximo razonable
            }

            status, data = self._get_json(url, params)
            if status != 200 or not data:
                return {
                    "estacion": estacion,
                    "direcciones": [],
                    "velocidades": [],
                    "unidad": "m/s",
                    "fuente_datos": "openmeteo_pronostico_hourly",
                }

            hourly = data.get("hourly") or {}
            times = hourly.get("time") or []
            dirs = hourly.get("wind_direction_10m") or []
            speeds = hourly.get("wind_speed_10m") or []

            if not times:
                return {
                    "estacion": estacion,
                    "direcciones": [],
                    "velocidades": [],
                    "unidad": "m/s",
                    "fuente_datos": "openmeteo_pronostico_hourly",
                }

            start_date = pd.to_datetime(times[0]).date()
            end_date = (pd.to_datetime(times[0]).date() + timedelta(days=dias))

            out_dirs: list[float] = []
            out_speeds: list[float] = []
            for i, t in enumerate(times):
                if i >= len(dirs) or i >= len(speeds):
                    break
                ts = pd.to_datetime(t)
                if ts.date() < start_date or ts.date() >= end_date:
                    continue
                dval = dirs[i]
                sval = speeds[i]
                if dval is None or sval is None:
                    continue
                out_dirs.append(round(float(dval), 1))
                out_speeds.append(round(float(sval), 2))

            return {
                "estacion": estacion,
                "direcciones": out_dirs,
                "velocidades": out_speeds,
                "unidad": "m/s",
                "fuente_datos": "openmeteo_pronostico_hourly",
            }
        except Exception:
            # Importante: evitamos caer en datos sintéticos con aleatoriedad aquí.
            return {
                "estacion": estacion,
                "direcciones": [],
                "velocidades": [],
                "unidad": "m/s",
                "fuente_datos": "openmeteo_pronostico_hourly",
            }

    def obtener_serie_helada_madrugada(self, estacion="Quillota", dias=7):
        """Serie horaria nocturna/madrugada para identificación de helada.

        Incluye T°, HR, viento y nubosidad; agrega ventana crítica 03–06 h
        (hora típica de mínima radiativa en el valle).
        """
        vacio = {
            "estacion": estacion,
            "horas": [],
            "puntos": [],
            "madrugada": [],
            "fuente_datos": "openmeteo_helada_hourly",
        }
        if estacion not in self.estaciones:
            return vacio

        coords = self.estaciones[estacion]
        dias = max(1, min(int(dias), 16))
        try:
            url = f"{self.api_base}/forecast"
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "hourly": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "wind_speed_10m",
                    "cloud_cover",
                    "dew_point_2m",
                ],
                "timezone": "America/Santiago",
                "forecast_days": dias,
            }
            status, data = self._get_json(url, params)
            if status != 200 or not data:
                return vacio
            hourly = data.get("hourly") or {}
            times = hourly.get("time") or []
            temps = hourly.get("temperature_2m") or []
            hrs = hourly.get("relative_humidity_2m") or []
            winds = hourly.get("wind_speed_10m") or []
            clouds = hourly.get("cloud_cover") or []
            dews = hourly.get("dew_point_2m") or []
            if not times:
                return vacio

            puntos: list[dict] = []
            madrugada: list[dict] = []
            horas: list[str] = []
            for i, t in enumerate(times):
                ts = pd.to_datetime(t)
                hora = int(ts.hour)
                punto = {
                    "fecha_hora": str(t),
                    "fecha": ts.date().isoformat(),
                    "hora": hora,
                    "temperatura": round(float(temps[i]), 1) if i < len(temps) and temps[i] is not None else None,
                    "humedad": round(float(hrs[i]), 1) if i < len(hrs) and hrs[i] is not None else None,
                    "viento": round(float(winds[i]), 2) if i < len(winds) and winds[i] is not None else None,
                    "cobertura_nubosa": round(float(clouds[i]), 1)
                    if i < len(clouds) and clouds[i] is not None
                    else None,
                    "punto_rocio": round(float(dews[i]), 1) if i < len(dews) and dews[i] is not None else None,
                    "ventana_critica": 3 <= hora <= 6,
                }
                puntos.append(punto)
                horas.append(str(t))
                if punto["ventana_critica"]:
                    madrugada.append(punto)

            # Resumen diario: mínima en ventana 03–06
            por_dia: dict[str, list[dict]] = {}
            for p in madrugada:
                por_dia.setdefault(p["fecha"], []).append(p)
            resumen_diario = []
            for fecha, pts in sorted(por_dia.items()):
                temps_ok = [p["temperatura"] for p in pts if p["temperatura"] is not None]
                if not temps_ok:
                    continue
                tmin = min(temps_ok)
                resumen_diario.append(
                    {
                        "fecha": fecha,
                        "temperatura_min_madrugada": tmin,
                        "helada_observada_ventana": tmin <= 0.0,
                        "horas": pts,
                    }
                )

            return {
                "estacion": estacion,
                "horas": horas,
                "puntos": puntos,
                "madrugada": madrugada,
                "resumen_diario": resumen_diario,
                "unidad_temp": "C",
                "unidad_viento": "m/s",
                "fuente_datos": "openmeteo_helada_hourly",
            }
        except Exception:
            return vacio

    def obtener_precipitacion_horaria_3h(self, estacion='Quillota', dias=7):
        """Pronóstico de precipitación en ventanas de 3 h (suma mm + PoP máx)."""
        vacio = {
            "estacion": estacion,
            "resolucion": "3h",
            "fechas": [],
            "precipitacion": [],
            "pop": [],
            "unidad": "mm",
            "fuente_datos": "openmeteo_hourly_3h",
        }
        if estacion not in self.estaciones:
            return vacio

        coords = self.estaciones[estacion]
        dias = max(1, min(int(dias), 16))

        try:
            url = f"{self.api_base}/forecast"
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "hourly": ["precipitation", "precipitation_probability"],
                "timezone": "America/Santiago",
                "forecast_days": dias,
            }
            status, data = self._get_json(url, params)
            if status != 200 or not data:
                return self._precip_3h_desde_diario(estacion, dias)

            hourly = data.get("hourly") or {}
            times = hourly.get("time") or []
            prec = hourly.get("precipitation") or []
            pops = hourly.get("precipitation_probability") or []
            if not times:
                return self._precip_3h_desde_diario(estacion, dias)

            hoy = datetime.now(TZ_CHILE).replace(minute=0, second=0, microsecond=0)
            fechas_out: list[str] = []
            precip_out: list[float] = []
            pop_out: list[float] = []

            i = 0
            n = len(times)
            while i < n:
                chunk_times = times[i : i + 3]
                if len(chunk_times) < 3 and i > 0:
                    break
                ts0 = pd.to_datetime(chunk_times[0])
                if ts0.tzinfo is None:
                    ts0 = ts0.tz_localize("America/Santiago")
                else:
                    ts0 = ts0.tz_convert("America/Santiago")
                if ts0 < hoy - timedelta(hours=3):
                    i += 3
                    continue
                limite = hoy + timedelta(days=dias)
                if ts0 >= limite:
                    break
                mm = 0.0
                pop_max = 0.0
                for j in range(3):
                    idx = i + j
                    if idx >= n:
                        break
                    pval = prec[idx] if idx < len(prec) else 0
                    popv = pops[idx] if idx < len(pops) else 0
                    mm += float(pval or 0)
                    pop_max = max(pop_max, float(popv or 0))
                fechas_out.append(ts0.strftime("%Y-%m-%dT%H:%M"))
                precip_out.append(round(mm, 2))
                pop_out.append(round(pop_max, 0))
                i += 3

            if not fechas_out:
                return self._precip_3h_desde_diario(estacion, dias)

            return {
                "estacion": estacion,
                "resolucion": "3h",
                "fechas": fechas_out,
                "precipitacion": precip_out,
                "pop": pop_out,
                "unidad": "mm",
                "fuente_datos": "openmeteo_hourly_3h",
            }
        except Exception:
            return self._precip_3h_desde_diario(estacion, dias)

    def _precip_3h_desde_diario(self, estacion, dias):
        """Respaldo determinista: reparte mm diarios del pronóstico en 8 bloques de 3 h."""
        df = self.obtener_datos_pronostico(estacion, dias)
        vacio = {
            "estacion": estacion,
            "resolucion": "3h",
            "fechas": [],
            "precipitacion": [],
            "pop": [],
            "unidad": "mm",
            "fuente_datos": "pronostico_diario_repartido_3h",
        }
        if df is None or df.empty:
            return vacio
        hoy = datetime.now(TZ_CHILE).date()
        fechas_out: list[str] = []
        precip_out: list[float] = []
        pop_out: list[float] = []
        for _, row in df.sort_values("fecha").iterrows():
            dia = row["fecha"]
            if hasattr(dia, "date"):
                d = dia.date() if hasattr(dia, "tzinfo") and dia.tzinfo else pd.Timestamp(dia).date()
            else:
                d = pd.to_datetime(dia).date()
            if d < hoy:
                continue
            if d >= hoy + timedelta(days=dias):
                break
            mm_dia = float(row.get("precipitacion") or 0)
            pop_d = float(row.get("probabilidad_lluvia") or row.get("pop") or 0)
            por_bloque = round(mm_dia / 8.0, 2) if mm_dia else 0.0
            for h in range(0, 24, 3):
                fechas_out.append(f"{d.isoformat()}T{h:02d}:00")
                precip_out.append(por_bloque)
                pop_out.append(round(pop_d, 0))
        return {
            "estacion": estacion,
            "resolucion": "3h",
            "fechas": fechas_out,
            "precipitacion": precip_out,
            "pop": pop_out,
            "unidad": "mm",
            "fuente_datos": "pronostico_diario_repartido_3h",
        }
    
    def _visibilidad_diaria_desde_hourly(self, data):
        """Agrega visibilidad mínima diaria (km) y mínima 3–6 AM desde hourly OpenMeteo."""
        stats = {}
        hourly = data.get('hourly') or {}
        times = hourly.get('time') or []
        vis_list = hourly.get('visibility') or []
        for i, t in enumerate(times):
            if i >= len(vis_list) or vis_list[i] is None:
                continue
            ts = pd.to_datetime(t)
            km = float(vis_list[i]) / 1000.0
            key = ts.normalize()
            if key not in stats:
                madrugada = km if 3 <= ts.hour <= 6 else None
                stats[key] = {'min': km, 'madrugada': madrugada}
            else:
                stats[key]['min'] = min(stats[key]['min'], km)
                if 3 <= ts.hour <= 6:
                    prev = stats[key].get('madrugada')
                    stats[key]['madrugada'] = km if prev is None else min(prev, km)
        return stats

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
            vis_stats = self._visibilidad_diaria_desde_hourly(data)

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
                    
                    if 'precipitation_probability_max' in daily_data:
                        registro['probabilidad_lluvia'] = daily_data.get('precipitation_probability_max', [None]*len(times))[i]
                    if 'cloud_cover_mean' in daily_data:
                        registro['cobertura_nubosa'] = daily_data.get('cloud_cover_mean', [None]*len(times))[i]
                    if 'shortwave_radiation_sum' in daily_data:
                        registro['radiacion_solar_sum'] = daily_data.get('shortwave_radiation_sum', [None]*len(times))[i]
                    if 'wind_direction_10m_dominant' in daily_data:
                        registro['direccion_viento'] = daily_data.get('wind_direction_10m_dominant', [None]*len(times))[i]
                    if 'et0_fao_evapotranspiration' in daily_data:
                        registro['evapotranspiracion'] = daily_data.get('et0_fao_evapotranspiration', [None]*len(times))[i]
                        
                    # Lógica de Heladas y Niebla
                    tmin = registro['temperatura_min']
                    registro['helada'] = True if (tmin is not None and tmin <= 0) else False
                    registro['niebla'] = False
                    
                    vkey = pd.to_datetime(fecha_str).normalize()
                    if vkey in vis_stats:
                        vis = round(vis_stats[vkey]['min'], 2)
                        registro['visibilidad'] = vis
                        if vis < 1.0: # menos de 1 km
                            registro['niebla'] = True
                        mad = vis_stats[vkey].get('madrugada')
                        if mad is not None:
                            registro['visibilidad_madrugada'] = round(mad, 2)
                            if mad < 1.0:
                                registro['niebla'] = True

                    # Solo agregar si tiene al menos temperatura
                    if registro['temperatura_max'] is not None:
                        registros.append(registro)
                        
                except Exception as e:
                    print(f"WARN - Error procesando {fecha_str}: {e}")
                    continue
            
            if registros:
                df = pd.DataFrame(registros)
                
                # Convertir a numérico
                cols_numericas = [
                    'temperatura_max', 'temperatura_min', 'temperatura_promedio',
                    'humedad_relativa', 'precipitacion', 'velocidad_viento',
                    'presion_atmosferica', 'cobertura_nubosa', 'radiacion_solar_sum',
                    'direccion_viento', 'probabilidad_lluvia', 'visibilidad', 'visibilidad_madrugada',
                    'evapotranspiracion'
                ]
                
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
    
    def _crear_datos_sinteticos(self, estacion, dias, modo='historicos'):
        """Crea datos sintéticos como respaldo.

        modo='historicos' → ventana hacia atrás (≤ hoy Chile).
        modo='pronostico' → hoy y días futuros (evita pronóstico vacío en API).
        """
        print(f" Creando datos sintéticos ({modo}) para {estacion} ({dias} días)")
        
        if estacion not in self.estaciones:
            estacion = 'Quillota'
        
        registros = []
        hoy = datetime.now(TZ_CHILE).date()
        if modo == 'pronostico':
            fecha_inicio = hoy
        else:
            fecha_inicio = hoy - timedelta(days=max(dias - 1, 0))
        
        # Parámetros base según la estación
        params_base = self._obtener_parametros_estacion(estacion)
        
        for i in range(dias):
            dia = fecha_inicio + timedelta(days=i)
            fecha = datetime.combine(dia, datetime.min.time(), tzinfo=TZ_CHILE)
            
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
            },
            'Los Nogales': {
                'temp_base': 15.5, 'temp_amplitud': 7, 'temp_variacion': 2.5, 'temp_diferencia': 6,
                'humedad_base': 68, 'precip_base': 2.0, 'viento_base': 3.5, 'presion_base': 1013.00
            },
            'Hijuelas': {
                'temp_base': 17.0, 'temp_amplitud': 8, 'temp_variacion': 3, 'temp_diferencia': 7,
                'humedad_base': 62, 'precip_base': 1.8, 'viento_base': 4.0, 'presion_base': 1012.50
            },
            'Limache': {
                'temp_base': 15.0, 'temp_amplitud': 6, 'temp_variacion': 2.5, 'temp_diferencia': 6,
                'humedad_base': 78, 'precip_base': 2.5, 'viento_base': 5.0, 'presion_base': 1012.00
            },
            'Olmue': {
                'temp_base': 16.5, 'temp_amplitud': 7.5, 'temp_variacion': 3, 'temp_diferencia': 7,
                'humedad_base': 72, 'precip_base': 2.2, 'viento_base': 4.2, 'presion_base': 1013.50
            },
        }
        
        return parametros.get(estacion, parametros['Quillota'])
    
    def verificar_conexion(self, timeout_sec=10):
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

            status, _ = self._get_json(url, params, timeout=timeout_sec)

            if status == 200:
                print("OK - Conexión con OpenMeteo exitosa")
                return True
            print(f"ERROR - Error de conexión: {status}")
            return False

        except Exception as e:
            print(f"ERROR - Error de conectividad: {e}")
            return False

# Función principal para usar en los dashboards
def obtener_datos_archive_openmeteo(estacion='Quillota', anios=5):
    """Helper módulo: histórico largo OpenMeteo Archive."""
    return OpenMeteoData().obtener_datos_archive(estacion, anios)


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
