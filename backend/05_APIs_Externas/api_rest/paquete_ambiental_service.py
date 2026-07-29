#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Paquete ambiental multi-faena (M1–M3).

Meteo + viento + serie nival + calidad del aire CAMS + flags operativos
(izaje / caminos / botaderos) para cualquier faena del catálogo.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests

from api_rest.aire_service import evaluar_icap
from api_rest.umbrales_faena_service import (
    construir_serie_nival,
    evaluar_operaciones,
    flags_desde_serie_y_actual,
    mm_agua_a_cm_nieve,
    umbrales_efectivos,
)

TZ_CHILE = ZoneInfo("America/Santiago")
FORECAST_API = "https://api.open-meteo.com/v1/forecast"
AIR_API = "https://air-quality-api.open-meteo.com/v1/air-quality"
_TIMEOUT = int(os.getenv("METGO_OPENMETEO_TIMEOUT", "25"))

_METEO_HOURLY = (
    "temperature_2m,relative_humidity_2m,precipitation,snowfall,"
    "pressure_msl,visibility,"
    "wind_speed_10m,wind_direction_10m,wind_gusts_10m,"
    "wind_speed_100m,wind_direction_100m,"
    "cloud_cover,weather_code"
)
_AIR_HOURLY = (
    "pm2_5,pm10,sulphur_dioxide,nitrogen_dioxide,ozone,carbon_monoxide,dust"
)


def _get(url: str, params: dict[str, Any]) -> dict[str, Any] | None:
    try:
        r = requests.get(url, params=params, timeout=_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _num(v: Any, nd: int = 2) -> float | None:
    if v is None:
        return None
    try:
        return round(float(v), nd)
    except (TypeError, ValueError):
        return None


def _slice_hourly(hourly: dict[str, Any], horas: int) -> list[dict[str, Any]]:
    tiempos = hourly.get("time") or []
    if not tiempos:
        return []
    n = min(len(tiempos), max(1, horas))
    keys = [k for k in hourly.keys() if k != "time"]
    out: list[dict[str, Any]] = []
    for i in range(n):
        fila: dict[str, Any] = {"fecha_hora": tiempos[i]}
        for k in keys:
            serie = hourly.get(k) or []
            fila[k] = _num(serie[i] if i < len(serie) else None, 2)
        out.append(fila)
    return out


def _sum_snowfall_mm(serie: list[dict[str, Any]]) -> float:
    total = 0.0
    for f in serie:
        v = f.get("snowfall")
        if v is not None:
            total += float(v)
    return round(total, 2)


def construir_paquete_ambiental(
    faena_id: str,
    *,
    horas: int = 72,
) -> dict[str, Any] | None:
    """Arma snapshot + serie horaria meteo/aire/nival + flags M3."""
    from api_rest.faena_catalogo import get_faena

    faena = get_faena(faena_id)
    if not faena:
        return None
    lat = faena.get("lat")
    lon = faena.get("lon")
    if lat is None or lon is None:
        return {
            "faena_id": faena["id"],
            "nombre": faena.get("nombre"),
            "error": "sin_coordenadas",
            "fuente": "openmeteo",
        }

    horas = max(6, min(int(horas or 72), 168))
    forecast_days = max(1, min((horas + 23) // 24, 7))

    meteo = _get(
        FORECAST_API,
        {
            "latitude": lat,
            "longitude": lon,
            "hourly": _METEO_HOURLY,
            "current": _METEO_HOURLY,
            "timezone": "America/Santiago",
            "forecast_days": forecast_days,
            "wind_speed_unit": "ms",
        },
    )
    aire = _get(
        AIR_API,
        {
            "latitude": lat,
            "longitude": lon,
            "hourly": _AIR_HOURLY,
            "current": _AIR_HOURLY,
            "timezone": "America/Santiago",
            "forecast_days": min(forecast_days, 5),
        },
    )
    if not meteo:
        return None

    cur_m = meteo.get("current") or {}
    cur_a = (aire or {}).get("current") or {}
    serie_meteo = _slice_hourly(meteo.get("hourly") or {}, horas)
    serie_aire = _slice_hourly((aire or {}).get("hourly") or {}, horas) if aire else []
    serie_nival = construir_serie_nival(serie_meteo)

    snow_horizonte_mm = _sum_snowfall_mm(serie_meteo)
    snow_24_mm = _sum_snowfall_mm(serie_meteo[:24])
    temp_act = _num(cur_m.get("temperature_2m"), 1)
    acum_proxy_cm = mm_agua_a_cm_nieve(snow_horizonte_mm, temp_act)
    if serie_nival:
        idx24 = min(23, len(serie_nival) - 1)
        acum_24h_cm = serie_nival[idx24]["acum_desde_inicio_cm"]
    else:
        acum_24h_cm = mm_agua_a_cm_nieve(snow_24_mm, temp_act)

    pm25 = _num(cur_a.get("pm2_5"), 1)
    pm10 = _num(cur_a.get("pm10"), 1)
    icap = evaluar_icap(pm25, pm10)
    no2 = _num(cur_a.get("nitrogen_dioxide"), 1)
    so2 = _num(cur_a.get("sulphur_dioxide"), 1)
    snowfall_act = _num(cur_m.get("snowfall"), 2)
    rafaga = _num(cur_m.get("wind_gusts_10m"), 2)
    vis = _num(cur_m.get("visibility"), 0)

    actual = {
        "temperatura_c": temp_act,
        "humedad_relativa_pct": _num(cur_m.get("relative_humidity_2m"), 0),
        "precipitacion_mm": _num(cur_m.get("precipitation"), 2),
        "snowfall_mm": snowfall_act,
        "presion_msl_hpa": _num(cur_m.get("pressure_msl"), 1),
        "visibilidad_m": vis,
        "nubosidad_pct": _num(cur_m.get("cloud_cover"), 0),
        "weather_code": cur_m.get("weather_code"),
        "viento_10m_ms": _num(cur_m.get("wind_speed_10m"), 2),
        "viento_10m_dir_deg": _num(cur_m.get("wind_direction_10m"), 0),
        "rafaga_10m_ms": rafaga,
        "viento_100m_ms": _num(cur_m.get("wind_speed_100m"), 2),
        "viento_100m_dir_deg": _num(cur_m.get("wind_direction_100m"), 0),
        "pm2_5": pm25,
        "pm10": pm10,
        "so2": so2,
        "no2": no2,
        "nox_proxy": no2,
        "o3": _num(cur_a.get("ozone"), 1),
        "co": _num(cur_a.get("carbon_monoxide"), 1),
        "dust": _num(cur_a.get("dust"), 1),
        "icap": icap.get("icap"),
        "nivel_icap": icap.get("nivel"),
    }

    umb = umbrales_efectivos()
    ops = evaluar_operaciones(
        rafaga_ms=rafaga,
        snowfall_hora_mm=snowfall_act,
        acum_24h_cm=acum_24h_cm,
        visibilidad_m=vis,
        umbrales=umb,
    )
    flags = flags_desde_serie_y_actual(serie_nival, actual, ops)

    return {
        "faena_id": faena["id"],
        "nombre": faena.get("nombre"),
        "sitio": faena.get("sitio"),
        "lat": lat,
        "lon": lon,
        "altitud_m": faena.get("altitud_m"),
        "estaciones_area": faena.get("estaciones_area") or [],
        "capacidades": faena.get("capacidades") or [],
        "generado_en": datetime.now(TZ_CHILE).isoformat(timespec="seconds"),
        "horizonte_horas": horas,
        "fuente": {
            "meteo": "openmeteo_forecast",
            "aire": "openmeteo_cams" if aire else None,
            "tipo_dato": "modelo",
        },
        "actual": actual,
        "nieve": {
            "snowfall_mm_acum_horizonte": snow_horizonte_mm,
            "snowfall_mm_acum_24h": snow_24_mm,
            "acumulacion_proxy_cm": acum_proxy_cm,
            "acumulacion_24h_cm": acum_24h_cm,
            "factor_conversion": "mm_agua→cm con factor T (0.7/>0°C, 1.0, 1.2/<-10°C)",
            "nota": "Proxy M3 SWE→profundidad. Densidad real / sensores en M4–M5.",
        },
        "serie_nival": serie_nival,
        "operaciones": ops,
        "flags": flags,
        "serie_meteo": serie_meteo,
        "serie_aire": serie_aire,
    }
