#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPATI — Ingesta Open-Meteo → serie 72 h × 15 min (288 intervalos)."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import requests

logger = logging.getLogger(__name__)

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
_TIMEOUT = 45
_RETRIES = 3

# DECISIÓN: minutely_15 si está disponible; si no, hourly + resample 15 min.
_HOURLY_VARS = [
    "wind_speed_10m",
    "wind_speed_80m",
    "wind_speed_100m",
    "wind_direction_10m",
    "wind_direction_100m",
    "wind_gusts_10m",
    "temperature_2m",
    "surface_pressure",
    "pressure_msl",
    "relative_humidity_2m",
    "precipitation",
    "snowfall",
    "cloud_cover",
    "visibility",
    # Alta montaña: onda de montaña / lapse rate
    "wind_speed_500hPa",
    "wind_direction_500hPa",
    "temperature_850hPa",
]

# Subconjunto si el modelo rechaza variables de presión
_HOURLY_VARS_MIN = [
    "wind_speed_10m",
    "wind_speed_100m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "temperature_2m",
    "surface_pressure",
    "relative_humidity_2m",
    "precipitation",
    "visibility",
]


class NWPDataUnavailableError(RuntimeError):
    pass


class NWPIngestor:
    def __init__(self, modelo: str = "best_match"):
        self.modelo = modelo

    def fetch_forecast(self, lat: float, lon: float, forecast_days: int = 3) -> pd.DataFrame:
        """Retorna DataFrame indexado UTC con 288 filas (72 h × 15 min)."""
        base = {
            "latitude": lat,
            "longitude": lon,
            "forecast_days": max(3, min(int(forecast_days), 7)),
            "timezone": "UTC",
            "wind_speed_unit": "ms",
        }
        # Intentos: vars completas → mínimas; best_match → icon → gfs
        modelos = [self.modelo, "icon_seamless", "gfs_seamless", "best_match"]
        var_sets = [_HOURLY_VARS, _HOURLY_VARS_MIN]
        seen: set[tuple[str, int]] = set()
        last_err: Exception | None = None
        data = None
        for vi, vars_ in enumerate(var_sets):
            for m in modelos:
                key = (m, vi)
                if key in seen:
                    continue
                seen.add(key)
                p = dict(base)
                p["hourly"] = ",".join(vars_)
                if m and m != "best_match":
                    p["models"] = m
                try:
                    data = self._get_json(p)
                    if data and data.get("hourly"):
                        break
                except Exception as exc:
                    last_err = exc
                    logger.warning("NWP modelo %s (vars#%s) falló: %s", m, vi, exc)
                    data = None
            if data and data.get("hourly"):
                break
        if not data or not data.get("hourly"):
            raise NWPDataUnavailableError(str(last_err or "sin datos Open-Meteo"))

        hourly = data["hourly"]
        times = hourly.get("time") or []
        rows = []
        for i, ts in enumerate(times):
            def _f(key: str, scale: float = 1.0):
                serie = hourly.get(key) or []
                v = serie[i] if i < len(serie) else None
                if v is None:
                    return None
                return float(v) * scale

            # m/s → km/h
            v10 = _f("wind_speed_10m", 3.6)
            v80 = _f("wind_speed_80m", 3.6)
            v100 = _f("wind_speed_100m", 3.6)
            gust = _f("wind_gusts_10m", 3.6)
            # hPa → Pa (Open-Meteo surface_pressure suele venir en hPa)
            p_raw = _f("surface_pressure", 1.0)
            if p_raw is not None and p_raw < 2000:
                p_pa = p_raw * 100.0
            else:
                p_pa = p_raw
            # wind_speed_500hPa: m/s → nudos (1 m/s ≈ 1.94384 kt)
            w500_ms = _f("wind_speed_500hPa", 1.0)
            w500_kt = (w500_ms * 1.94384) if w500_ms is not None else None

            rows.append(
                {
                    "valid_time": pd.Timestamp(ts, tz="UTC"),
                    "viento_modelo_10m": v10,
                    "viento_modelo_80m": v80,
                    "viento_modelo_100m": v100,
                    "rafaga_modelo_10m": gust,
                    "dir_modelo": _f("wind_direction_10m"),
                    "dir_100m": _f("wind_direction_100m"),
                    "temp_celsius": _f("temperature_2m"),
                    "presion_pa": p_pa,
                    "pressure_msl_pa": (
                        (lambda x: x * 100.0 if x is not None and x < 2000 else x)(
                            _f("pressure_msl", 1.0)
                        )
                    ),
                    "rh_pct": _f("relative_humidity_2m"),
                    "precip_mmh": _f("precipitation"),
                    "snowfall_mm": _f("snowfall"),
                    "cloud_pct": _f("cloud_cover"),
                    "visibilidad_m": _f("visibility"),
                    "viento_500hpa_kt": w500_kt,
                    "dir_500hpa": _f("wind_direction_500hPa"),
                    "temp_850hpa": _f("temperature_850hPa"),
                    "prob_rayos_pct": None,
                }
            )

        df = pd.DataFrame(rows).set_index("valid_time").sort_index()
        # Resample a 15 min
        df = df.resample("15min").interpolate(method="time")
        # Exactamente 72 h desde ahora (o desde primer timestamp)
        t0 = df.index.min()
        t1 = t0 + pd.Timedelta(hours=72)
        df = df.loc[t0:t1]
        # Asegurar 288 filas (puede haber 289 por borde inclusivo)
        df = df.iloc[:288]
        if len(df) < 280:
            logger.warning("Serie NWP corta: %s filas", len(df))
        df["run_timestamp"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        return df

    def _get_json(self, params: dict[str, Any]) -> dict[str, Any]:
        last: Exception | None = None
        for intento in range(1, _RETRIES + 1):
            try:
                r = requests.get(FORECAST_URL, params=params, timeout=_TIMEOUT)
                if r.status_code == 200:
                    return r.json()
                if r.status_code == 429:
                    time.sleep(min(4**intento, 30))
                    continue
                if r.status_code >= 500 and intento < _RETRIES:
                    time.sleep(min(2**intento, 16))
                    continue
                raise NWPDataUnavailableError(f"HTTP {r.status_code}")
            except NWPDataUnavailableError:
                raise
            except Exception as exc:
                last = exc
                if intento < _RETRIES:
                    time.sleep(min(2**intento, 16))
        raise NWPDataUnavailableError(str(last or "fetch fallido"))
