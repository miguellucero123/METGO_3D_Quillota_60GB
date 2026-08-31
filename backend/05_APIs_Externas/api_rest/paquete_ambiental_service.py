#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Paquete ambiental multi-faena (M1–M3).

Meteo + viento + serie nival + calidad del aire CAMS + flags operativos
(izaje / caminos / botaderos) para cualquier faena del catálogo.

Ante Open-Meteo 429/cooldown: no devolver None (503). Usa lastgood o
paquete degradado con aviso, igual que SPATI NWP.
"""

from __future__ import annotations

import logging
import math
import os
import time
from datetime import datetime, timedelta
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

logger = logging.getLogger(__name__)

TZ_CHILE = ZoneInfo("America/Santiago")
FORECAST_API = (
    os.getenv("METGO_OPENMETEO_FORECAST_URL") or "https://api.open-meteo.com/v1/forecast"
).rstrip("/")
AIR_API = "https://air-quality-api.open-meteo.com/v1/air-quality"
_TIMEOUT = int(os.getenv("METGO_OPENMETEO_TIMEOUT", "12"))
_API_KEY = (os.getenv("METGO_OPENMETEO_API_KEY") or os.getenv("OPENMETEO_API_KEY") or "").strip()
_ALLOW_DEGRADED = os.getenv("METGO_PAQUETE_ALLOW_DEGRADED", "1").strip() not in (
    "0",
    "false",
    "no",
)

_METEO_HOURLY = (
    "temperature_2m,relative_humidity_2m,precipitation,snowfall,"
    "pressure_msl,visibility,"
    "wind_speed_10m,wind_direction_10m,wind_gusts_10m,"
    "wind_speed_100m,wind_direction_100m,"
    "cloud_cover,weather_code"
)
_METEO_MIN = (
    "temperature_2m,precipitation,wind_speed_10m,wind_direction_10m,"
    "wind_gusts_10m,visibility,relative_humidity_2m"
)
_AIR_HOURLY = (
    "pm2_5,pm10,sulphur_dioxide,nitrogen_dioxide,ozone,carbon_monoxide,dust"
)

# Caché del último paquete OK por faena (memoria + disco para Render)
_LASTGOOD: dict[str, tuple[float, dict[str, Any]]] = {}


def _lastgood_ttl() -> int:
    try:
        from api_rest.integracion.openmeteo_ciclo import fetch_mode, segundos_hasta_proximo_ciclo

        if fetch_mode() == "ciclo":
            return max(300, segundos_hasta_proximo_ciclo())
    except Exception:
        pass
    return int(
        os.getenv("METGO_PAQUETE_CACHE_TTL")
        or os.getenv("METGO_OPENMETEO_CACHE_TTL")
        or str(3600)
    )


_LASTGOOD_TTL = _lastgood_ttl()


def _runtime_cache_dir():
    from pathlib import Path

    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            d = p / "backend" / "08_Gestion_Datos" / "datos_runtime" / "paquete_ambiental"
            d.mkdir(parents=True, exist_ok=True)
            return d
    d = Path("paquete_ambiental_cache")
    d.mkdir(parents=True, exist_ok=True)
    return d


def _disk_path(faena_id: str):
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in (faena_id or "x"))
    return _runtime_cache_dir() / f"{safe}.json"


def _openmeteo_cooldown() -> bool:
    try:
        from datos_reales_openmeteo import openmeteo_en_cooldown

        return bool(openmeteo_en_cooldown())
    except Exception:
        return False


def _mark_cooldown(seconds: int = 90) -> None:
    try:
        from datos_reales_openmeteo import marcar_openmeteo_cooldown

        marcar_openmeteo_cooldown(seconds)
    except Exception:
        pass


def _get(url: str, params: dict[str, Any]) -> dict[str, Any] | None:
    if _openmeteo_cooldown() and "open-meteo.com" in url:
        return None
    p = dict(params)
    if _API_KEY and "open-meteo.com" in url:
        p.setdefault("apikey", _API_KEY)
    try:
        r = requests.get(url, params=p, timeout=_TIMEOUT)
        if r.status_code == 429:
            _mark_cooldown(90)
            return None
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, dict) else None
    except Exception as exc:
        logger.warning("paquete_ambiental GET %s: %s", url.split("/")[2], exc)
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


def _save_lastgood(faena_id: str, data: dict[str, Any]) -> None:
    import json

    _LASTGOOD[faena_id] = (time.time(), data)
    try:
        slim = {
            k: v
            for k, v in data.items()
            if k not in ("serie_meteo", "serie_aire", "serie_nival")
        }
        # Mantener series cortas para board/ops (24 h máx en disco)
        for key in ("serie_meteo", "serie_aire", "serie_nival"):
            serie = data.get(key)
            if isinstance(serie, list):
                slim[key] = serie[:24]
        path = _disk_path(faena_id)
        path.write_text(json.dumps(slim, ensure_ascii=False, default=str), encoding="utf-8")
    except Exception as exc:
        logger.debug("paquete lastgood disk write %s: %s", faena_id, exc)


def _load_lastgood(faena_id: str, *, as_fallback: bool = False) -> dict[str, Any] | None:
    """Lee lastgood. as_fallback=True marca degradado (uso ante fallo Open-Meteo)."""
    import json

    now = time.time()
    hit = _LASTGOOD.get(faena_id)
    data = None
    ttl = _lastgood_ttl()
    if hit and now - hit[0] <= ttl:
        data = hit[1]
    else:
        try:
            path = _disk_path(faena_id)
            if path.exists():
                age = now - path.stat().st_mtime
                if age <= ttl * 2:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(data, dict) and data.get("faena_id"):
                        _LASTGOOD[faena_id] = (now, data)
        except Exception as exc:
            logger.debug("paquete lastgood disk read %s: %s", faena_id, exc)
            data = None
    if not data:
        return None
    out = dict(data)
    if as_fallback:
        out["degradado"] = True
        out["aviso"] = "Datos en caché (Open-Meteo no disponible). Reintente en unos minutos."
        fuente = dict(out.get("fuente") or {})
        fuente["tipo_dato"] = "lastgood"
        out["fuente"] = fuente
    return out


def _paquete_degradado(faena: dict[str, Any], horas: int) -> dict[str, Any]:
    """Snapshot estimado para no devolver 503 ante rate limit."""
    ahora = datetime.now(TZ_CHILE)
    alt = float(faena.get("altitud_m") or 2500)
    base_v = 4.0 + min(6.0, max(0.0, (alt - 1000) / 400.0))  # m/s
    serie_meteo: list[dict[str, Any]] = []
    for i in range(horas):
        t = ahora + timedelta(hours=i)
        hour = t.hour + t.minute / 60.0
        diurno = 0.8 * math.sin((hour - 6) / 24.0 * 2 * math.pi)
        v = max(1.5, base_v + diurno)
        serie_meteo.append(
            {
                "fecha_hora": t.isoformat(timespec="minutes"),
                "temperature_2m": round(10.0 - alt / 700.0 + diurno * 2, 1),
                "relative_humidity_2m": 35.0,
                "precipitation": 0.0,
                "snowfall": 0.0,
                "pressure_msl": round(1013.0 * math.exp(-alt / 8500.0), 1),
                "visibility": 20000.0,
                "wind_speed_10m": round(v, 2),
                "wind_direction_10m": (220 + i) % 360,
                "wind_gusts_10m": round(v * 1.35, 2),
                "wind_speed_100m": round(v * 1.18, 2),
                "wind_direction_100m": (225 + i) % 360,
                "cloud_cover": 40.0,
                "weather_code": 1,
            }
        )
    cur = serie_meteo[0]
    rafaga = cur["wind_gusts_10m"]
    vis = cur["visibility"]
    temp_act = cur["temperature_2m"]
    serie_nival = construir_serie_nival(serie_meteo)
    acum_24h_cm = 0.0
    if serie_nival:
        idx24 = min(23, len(serie_nival) - 1)
        acum_24h_cm = serie_nival[idx24]["acum_desde_inicio_cm"]

    actual = {
        "temperatura_c": temp_act,
        "humedad_relativa_pct": 35.0,
        "precipitacion_mm": 0.0,
        "snowfall_mm": 0.0,
        "presion_msl_hpa": cur["pressure_msl"],
        "visibilidad_m": vis,
        "nubosidad_pct": 40.0,
        "weather_code": 1,
        "viento_10m_ms": cur["wind_speed_10m"],
        "viento_10m_dir_deg": cur["wind_direction_10m"],
        "rafaga_10m_ms": rafaga,
        "viento_100m_ms": cur["wind_speed_100m"],
        "viento_100m_dir_deg": cur["wind_direction_100m"],
        "pm2_5": None,
        "pm10": None,
        "so2": None,
        "no2": None,
        "nox_proxy": None,
        "o3": None,
        "co": None,
        "dust": None,
        "icap": None,
        "nivel_icap": None,
    }
    umb = umbrales_efectivos()
    ops = evaluar_operaciones(
        rafaga_ms=rafaga,
        snowfall_hora_mm=0.0,
        acum_24h_cm=acum_24h_cm,
        visibilidad_m=vis,
        umbrales=umb,
    )
    flags = flags_desde_serie_y_actual(serie_nival, actual, ops)
    return {
        "faena_id": faena["id"],
        "nombre": faena.get("nombre"),
        "sitio": faena.get("sitio"),
        "lat": faena.get("lat"),
        "lon": faena.get("lon"),
        "altitud_m": faena.get("altitud_m"),
        "estaciones_area": faena.get("estaciones_area") or [],
        "capacidades": faena.get("capacidades") or [],
        "generado_en": ahora.isoformat(timespec="seconds"),
        "horizonte_horas": horas,
        "degradado": True,
        "aviso": (
            "Paquete estimado: Open-Meteo no respondió (rate limit/cooldown). "
            "No usar para decisión crítica hasta recuperar modelo."
        ),
        "fuente": {
            "meteo": "synthetic_degraded",
            "aire": None,
            "tipo_dato": "estimado",
        },
        "actual": actual,
        "nieve": {
            "snowfall_mm_acum_horizonte": 0.0,
            "snowfall_mm_acum_24h": 0.0,
            "acumulacion_proxy_cm": 0.0,
            "acumulacion_24h_cm": acum_24h_cm,
            "factor_conversion": "mm_agua→cm con factor T",
            "nota": "Sin dato nival real (modo degradado).",
        },
        "serie_nival": serie_nival,
        "operaciones": ops,
        "flags": flags,
        "serie_meteo": serie_meteo,
        "serie_aire": [],
    }


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
        
    # Short-circuit: Si hay caché válido y cubre el horizonte, evitar llamada a API
    # (Previene 429 Rate Limit de Open-Meteo).
    cached = _load_lastgood(faena_id, as_fallback=False)
    if cached and cached.get("horizonte_horas", 0) >= horas:
        logger.info("paquete_ambiental %s → servido desde caché fresco", faena_id)
        return cached

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
    fid = faena["id"]

    meteo = _get(
        FORECAST_API,
        {
            "latitude": lat,
            "longitude": lon,
            "hourly": _METEO_MIN,
            "current": _METEO_MIN,
            "timezone": "America/Santiago",
            "forecast_days": forecast_days,
            "wind_speed_unit": "ms",
        },
    )
    # Reintento con vars completas solo si el mínimo funcionó o no hay cooldown
    if meteo and not _openmeteo_cooldown():
        meteo_full = _get(
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
        if meteo_full:
            meteo = meteo_full

    aire = None
    if meteo and not _openmeteo_cooldown():
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
        cached = _load_lastgood(fid, as_fallback=True)
        if cached:
            logger.warning("paquete_ambiental %s → lastgood", fid)
            return cached
        if _ALLOW_DEGRADED:
            logger.warning("paquete_ambiental %s → degradado", fid)
            return _paquete_degradado(faena, horas)
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
    
    try:
        from api_rest.services import estado_maritimo
        maritimo = estado_maritimo(fid, dias=3)
    except Exception:
        maritimo = None

    out = {
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
        "maritimo": maritimo,
    }
    _save_lastgood(fid, out)
    return out
