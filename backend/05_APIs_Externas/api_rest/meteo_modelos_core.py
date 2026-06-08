#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comparación GFS vs ECMWF vía OpenMeteo (multi-modelo)."""

from __future__ import annotations

import logging
from datetime import datetime
from functools import lru_cache
from typing import Any
from zoneinfo import ZoneInfo

import requests

from api_rest.meteo_avanzado_core import COORDS_ESTACIONES, validar_estacion

logger = logging.getLogger(__name__)

TZ = ZoneInfo("America/Santiago")
API_BASE = "https://api.open-meteo.com/v1/forecast"

MODELOS = {
    "gfs": "gfs_seamless",
    "ecmwf": "ecmwf_ifs04",
}

CAMPOS_DAILY = {
    "temperatura": "temperature_2m_max",
    "temperatura_max": "temperature_2m_max",
    "temperatura_min": "temperature_2m_min",
    "humedad": "relative_humidity_2m_max",
    "precipitacion": "precipitation_sum",
    "nubosidad": "cloud_cover_mean",
    "viento_velocidad": "wind_speed_10m_max",
}

UMBRALES_CONCORDANCIA = {
    "temperatura": 2.0,
    "temperatura_max": 2.0,
    "temperatura_min": 2.0,
    "humedad": 10.0,
    "precipitacion": 3.0,
    "nubosidad": 15.0,
    "viento_velocidad": 3.0,
}


def _concordancia(diff: float, variable: str) -> str:
    umbral = UMBRALES_CONCORDANCIA.get(variable, 3.0)
    if diff <= umbral * 0.5:
        return "alta"
    if diff <= umbral:
        return "media"
    return "baja"


@lru_cache(maxsize=64)
def _pronostico_modelo(
    lat: float, lon: float, modelo_slug: str, campo_daily: str, dias: int
) -> tuple[tuple[str, ...], tuple[float, ...]]:
    """Serie diaria (fecha ISO, valor) para un modelo OpenMeteo."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": campo_daily,
        "models": modelo_slug,
        "forecast_days": min(dias, 16),
        "timezone": "America/Santiago",
    }
    try:
        resp = requests.get(API_BASE, params=params, timeout=20)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        logger.warning("OpenMeteo modelo %s: %s", modelo_slug, exc)
        return (), ()

    daily = payload.get("daily") or {}
    times = daily.get("time") or []
    vals = daily.get(campo_daily) or []
    hoy = datetime.now(TZ).date().isoformat()
    filas: list[tuple[str, float]] = []
    for i, t in enumerate(times):
        if i >= len(vals) or vals[i] is None:
            continue
        dia = str(t)[:10]
        if dia < hoy:
            continue
        filas.append((dia, round(float(vals[i]), 2)))
    filas.sort(key=lambda x: x[0])
    filas = filas[:dias]
    if not filas:
        return (), ()
    fechas, valores = zip(*filas)
    return fechas, valores


def comparacion_gfs_ecmwf(
    estacion_id: str, variable: str, dias: int = 7
) -> dict[str, Any]:
    """Compara pronóstico GFS y ECMWF para una variable diaria."""
    validar_estacion(estacion_id)
    slug = estacion_id.lower()
    coords = COORDS_ESTACIONES[slug]
    campo = CAMPOS_DAILY.get(variable)
    if not campo:
        raise ValueError(f"Variable no soportada para comparación: {variable}")

    gfs_fechas, gfs_vals = _pronostico_modelo(
        coords["lat"], coords["lon"], MODELOS["gfs"], campo, dias
    )
    ecmwf_fechas, ecmwf_vals = _pronostico_modelo(
        coords["lat"], coords["lon"], MODELOS["ecmwf"], campo, dias
    )

    gfs_map = dict(zip(gfs_fechas, gfs_vals))
    ecmwf_map = dict(zip(ecmwf_fechas, ecmwf_vals))
    fechas = sorted(set(gfs_map) | set(ecmwf_map))[:dias]

    comparacion: list[dict[str, Any]] = []
    fuente = "openmeteo_multi_modelo"
    nota = None

    if not fechas:
        fuente = "aproximacion"
        nota = "OpenMeteo no respondió; sin datos multi-modelo"
        return {
            "estacion_id": estacion_id,
            "variable": variable,
            "comparacion": comparacion,
            "fuente": fuente,
            "modelos": MODELOS,
            "nota": nota,
        }

    for fecha in fechas:
        gfs = gfs_map.get(fecha)
        ecmwf = ecmwf_map.get(fecha)
        if gfs is None and ecmwf is None:
            continue
        if gfs is None:
            gfs = ecmwf
        if ecmwf is None:
            ecmwf = gfs
        diff = round(abs(gfs - ecmwf), 2)
        comparacion.append(
            {
                "fecha": fecha,
                "gfs": gfs,
                "ecmwf": ecmwf,
                "diferencia": diff,
                "concordancia": _concordancia(diff, variable),
            }
        )

    if len(gfs_fechas) < 2 or len(ecmwf_fechas) < 2:
        nota = "Uno de los modelos devolvió pocos días; valores parciales"

    return {
        "estacion_id": estacion_id,
        "variable": variable,
        "comparacion": comparacion,
        "fuente": fuente,
        "modelos": {
            "gfs": MODELOS["gfs"],
            "ecmwf": MODELOS["ecmwf"],
        },
        "nota": nota,
    }
