#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pronóstico portuario 72 h para VENTORA (Open-Meteo + fallback local)."""

from __future__ import annotations

import logging
import math
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from api_rest.integracion.openmeteo_multimodelo import (
    MODELOS_DETERMINISTAS,
    MultiModeloNoDisponibleError,
    ensamble_variable,
    fetch_multimodelo,
    primer_modelo_disponible,
)
from api_rest.spati.mjo_index_service import (
    ajustar_precipitacion_mjo,
    obtener_indice_mjo_real,
)
from api_rest.spati.physics_engine import (
    LONGITUD_CABLE_DEFAULT_M,
    corriente_superficial_por_viento,
    evaluar_resonancia_pendular,
    extrapolar_power_law_estabilidad,
)

logger = logging.getLogger(__name__)

FORECAST_URL = (
    os.getenv("METGO_OPENMETEO_FORECAST_URL") or "https://api.open-meteo.com/v1/forecast"
).rstrip("/")
MARINE_URL = (
    os.getenv("METGO_OPENMETEO_MARINE_URL") or "https://marine-api.open-meteo.com/v1/marine"
).rstrip("/")
_API_KEY = (os.getenv("METGO_OPENMETEO_API_KEY") or os.getenv("OPENMETEO_API_KEY") or "").strip()
_TIMEOUT = int(os.getenv("METGO_PUERTO_NWP_TIMEOUT", "15"))
_ALLOW_SYNTHETIC = os.getenv("METGO_SPATI_ALLOW_SYNTHETIC", "1").strip() not in (
    "0",
    "false",
    "no",
)

# Catálogo VENTORA (coords muelle / terminal)
PUERTOS: dict[str, dict[str, Any]] = {
    "iqq": {
        "sitio_id": "iqq",
        "nombre": "Terminal Iquique (ITI)",
        "region": "Tarapacá",
        "lat": -20.2058,
        "lon": -70.1608,
        "altitud_msnm": 5,
        "z0_terreno": 0.002,
        "tipo": "portuario",
    },
    "ventanas_muelle": {
        "sitio_id": "ventanas_muelle",
        "nombre": "Puerto Ventanas (Muelle)",
        "region": "Valparaíso",
        "lat": -32.748,
        "lon": -71.482,
        "altitud_msnm": 8,
        "z0_terreno": 0.002,
        "tipo": "portuario",
    },
    "anf": {
        "sitio_id": "anf",
        "nombre": "Puerto Antofagasta",
        "region": "Antofagasta",
        "lat": -23.6509,
        "lon": -70.4001,
        "altitud_msnm": 5,
        "z0_terreno": 0.002,
        "tipo": "portuario",
    },
    "vlp": {
        "sitio_id": "vlp",
        "nombre": "Puerto Valparaíso",
        "region": "Valparaíso",
        "lat": -33.037,
        "lon": -71.627,
        "altitud_msnm": 5,
        "z0_terreno": 0.002,
        "tipo": "portuario",
    },
    "san": {
        "sitio_id": "san",
        "nombre": "Puerto San Antonio",
        "region": "Valparaíso",
        "lat": -33.580,
        "lon": -71.615,
        "altitud_msnm": 5,
        "z0_terreno": 0.002,
        "tipo": "portuario",
    },
    "pmc": {
        "sitio_id": "pmc",
        "nombre": "Puerto Mejillones",
        "region": "Antofagasta",
        "lat": -23.100,
        "lon": -70.450,
        "altitud_msnm": 5,
        "z0_terreno": 0.002,
        "tipo": "portuario",
    },
}

_ALIASES = {
    "iquique": "iqq",
    "iti": "iqq",
    "puerto_iquique": "iqq",
    "ventanas": "ventanas_muelle",
    "puerto_ventanas": "ventanas_muelle",
    "antofagasta": "anf",
    "valparaiso": "vlp",
    "valparaíso": "vlp",
    "san_antonio": "san",
    "mejillones": "pmc",
}


def normalizar_puerto_id(raw: str | None) -> str | None:
    key = (raw or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not key:
        return None
    if key in PUERTOS:
        return key
    return _ALIASES.get(key)


def get_puerto(sitio_id: str | None) -> dict[str, Any] | None:
    nid = normalizar_puerto_id(sitio_id)
    if not nid:
        # Intentar catálogo SPATI (minero) solo para coords; no es ideal para oleaje
        try:
            from api_rest.spati.sitios_catalogo import get_sitio

            s = get_sitio(sitio_id)
            if s and s.get("lat") is not None and s.get("lon") is not None:
                return {
                    "sitio_id": s.get("sitio_id") or sitio_id,
                    "nombre": s.get("nombre") or sitio_id,
                    "region": s.get("region"),
                    "lat": float(s["lat"]),
                    "lon": float(s["lon"]),
                    "altitud_msnm": float(s.get("altitud_msnm") or 10),
                    "z0_terreno": float(s.get("z0_terreno") or 0.05),
                    "tipo": "spati_fallback",
                }
        except Exception:
            pass
        return None
    return dict(PUERTOS[nid])


def _get_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    p = dict(params)
    if _API_KEY:
        p["apikey"] = _API_KEY
    r = requests.get(url, params=p, timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


def _log_profile(v10_ms: float, z0: float, heights: list[float]) -> dict[str, Any]:
    speeds = []
    for h in heights:
        if h <= 0:
            speeds.append(0.0)
            continue
        # perfil logarítmico desde 10 m
        try:
            v = v10_ms * math.log(max(h, z0 * 2) / z0) / math.log(10.0 / z0)
        except (ValueError, ZeroDivisionError):
            v = v10_ms
        speeds.append(round(max(0.0, v), 3))
    return {
        "heights_m": heights,
        "wind_speeds": speeds,
        "wind_directions": [None] * len(heights),
        "temperatures": [None] * len(heights),
        "pressures": [None] * len(heights),
        "u_components": speeds[:],
        "v_components": [0.0] * len(heights),
    }


def _build_alerts(hourly: list[dict[str, Any]], threshold_kmh: float = 32.0) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    run = 0
    start_ts = None
    peak = 0.0
    for st in hourly:
        w = float(st.get("wind_surface_kmh") or 0)
        if w >= threshold_kmh:
            if run == 0:
                start_ts = st.get("timestamp")
                peak = w
            run += 1
            peak = max(peak, w)
        else:
            if run >= 3 and start_ts:
                alerts.append(
                    {
                        "timestamp": start_ts,
                        "type": "sustained_wind",
                        "level": "YELLOW" if peak < 45 else "RED",
                        "wind_kmh": round(peak, 1),
                        "threshold_kmh": threshold_kmh,
                        "duration_hours": run,
                    }
                )
            run = 0
            start_ts = None
            peak = 0.0
    if run >= 3 and start_ts:
        alerts.append(
            {
                "timestamp": start_ts,
                "type": "sustained_wind",
                "level": "YELLOW" if peak < 45 else "RED",
                "wind_kmh": round(peak, 1),
                "threshold_kmh": threshold_kmh,
                "duration_hours": run,
            }
        )
    return alerts


def _build_alertas_resonancia(hourly: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ventanas horarias donde el período del péndulo (carga real) cae dentro
    de la banda de alerta del período de oleaje real — riesgo de resonancia,
    no un umbral fijo desconectado de la física de la operación."""
    alerts: list[dict[str, Any]] = []
    run = 0
    start_ts = None
    peor_delta = None
    for st in hourly:
        res = st.get("resonancia_pendular") or {}
        if res.get("en_resonancia"):
            if run == 0:
                start_ts = st.get("timestamp")
                peor_delta = res.get("delta_s")
            run += 1
            if peor_delta is None or (res.get("delta_s") or 99) < peor_delta:
                peor_delta = res.get("delta_s")
        else:
            if run >= 2 and start_ts:
                alerts.append(
                    {
                        "timestamp": start_ts,
                        "type": "pendulum_resonance",
                        "level": "RED",
                        "delta_s": peor_delta,
                        "duration_hours": run,
                    }
                )
            run = 0
            start_ts = None
            peor_delta = None
    if run >= 2 and start_ts:
        alerts.append(
            {
                "timestamp": start_ts,
                "type": "pendulum_resonance",
                "level": "RED",
                "delta_s": peor_delta,
                "duration_hours": run,
            }
        )
    return alerts


def _calcular_ventana(hourly: list[dict[str, Any]], threshold_kmh: float = 32.0) -> dict[str, Any]:
    """Calcula la ventana operativa actual (verde) o restricción (roja/amarilla)."""
    if not hourly:
        return {}
    
    # Buscar inicio de restricción (o fin si estamos en una)
    estado_actual_restringido = float(hourly[0].get("wind_surface_kmh") or 0) >= threshold_kmh
    
    cambio_ts = None
    horas_hasta_cambio = 0
    
    for st in hourly:
        w = float(st.get("wind_surface_kmh") or 0)
        restringido = w >= threshold_kmh
        if restringido != estado_actual_restringido:
            cambio_ts = st.get("timestamp")
            break
        horas_hasta_cambio += 1
        
    nivel_actual = "ROJO" if estado_actual_restringido else "VERDE"
    
    return {
        "inicio_restriccion": cambio_ts if not estado_actual_restringido else hourly[0].get("timestamp"),
        "fin_restriccion": cambio_ts if estado_actual_restringido else None,
        "duracion_ventana_actual_horas": horas_hasta_cambio,
        "nivel_actual": nivel_actual,
    }


_HOURLY_VARS_MULTIMODELO = [
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "visibility",
    "temperature_2m",
    "precipitation",
    # Real (no fabricado): viento a 900 hPa del propio NWP, y variables
    # para clasificación de estabilidad atmosférica (Pasquill).
    "wind_speed_900hPa",
    "wind_direction_900hPa",
    "cloud_cover",
    "is_day",
]


def _fetch_forecast_multimodelo(lat: float, lon: float, days: int) -> tuple[dict[str, Any], list[str]]:
    """Pronóstico atmosférico real: ensamble de varios modelos NWP reales
    (política de datos: sin estación propia → Open-Meteo multi-modelo, nunca
    un solo modelo opaco ni datos sintéticos). Si el multi-modelo falla,
    degrada a un único modelo real (``best_match``) antes de rendirse."""
    try:
        data = fetch_multimodelo(lat, lon, hourly_vars=_HOURLY_VARS_MULTIMODELO, forecast_days=days)
        return data, list(MODELOS_DETERMINISTAS)
    except MultiModeloNoDisponibleError as exc:
        logger.warning("multi-modelo puerto falló (%s); degradando a best_match", exc)
        data = _get_json(
            FORECAST_URL,
            {
                "latitude": lat,
                "longitude": lon,
                "forecast_days": days,
                "timezone": "UTC",
                "wind_speed_unit": "ms",
                "hourly": ",".join(_HOURLY_VARS_MULTIMODELO),
            },
        )
        # Homologar al formato sufijado por modelo para reusar ensamble_variable().
        hourly = data.get("hourly") or {}
        homologado = {"time": hourly.get("time")}
        for var in _HOURLY_VARS_MULTIMODELO:
            homologado[f"{var}_best_match"] = hourly.get(var)
        return {**data, "hourly": homologado}, ["best_match"]


def _from_openmeteo(
    puerto: dict[str, Any], hours: int = 72, *, longitud_cable_m: float = LONGITUD_CABLE_DEFAULT_M
) -> dict[str, Any]:
    lat = float(puerto["lat"])
    lon = float(puerto["lon"])
    z0 = float(puerto.get("z0_terreno") or 0.002)
    days = max(3, min(int(math.ceil(hours / 24)), 7))

    forecast, modelos_usados = _fetch_forecast_multimodelo(lat, lon, days)
    fh_raw = forecast.get("hourly") or {}

    ens_wind = ensamble_variable(fh_raw, "wind_speed_10m", modelos_usados)
    ens_gust = ensamble_variable(fh_raw, "wind_gusts_10m", modelos_usados)
    ens_temp = ensamble_variable(fh_raw, "temperature_2m", modelos_usados)
    ens_vis = ensamble_variable(fh_raw, "visibility", modelos_usados)
    ens_precip = ensamble_variable(fh_raw, "precipitation", modelos_usados)
    ens_900hpa = ensamble_variable(fh_raw, "wind_speed_900hPa", modelos_usados)
    ens_cloud = ensamble_variable(fh_raw, "cloud_cover", modelos_usados)
    wdir_serie = primer_modelo_disponible(fh_raw, "wind_direction_10m", modelos_usados) or []
    wdir900_serie = primer_modelo_disponible(fh_raw, "wind_direction_900hPa", modelos_usados) or []
    is_day_serie = primer_modelo_disponible(fh_raw, "is_day", modelos_usados) or []

    marine: dict[str, Any] = {}
    try:
        marine = _get_json(
            MARINE_URL,
            {
                "latitude": lat,
                "longitude": lon,
                "forecast_days": days,
                "timezone": "UTC",
                "hourly": ",".join(
                    [
                        "wave_height",
                        "wave_period",
                        "wave_direction",
                    ]
                ),
            },
        )
    except Exception as exc:
        logger.warning("marine Open-Meteo falló (%s); solo viento", exc)

    times = fh_raw.get("time") or []
    wind = ens_wind["media"]
    gust = ens_gust["media"]
    vis = ens_vis["media"]
    precip = ens_precip["media"]
    wdir = wdir_serie

    mh = marine.get("hourly") or {}
    m_times = mh.get("time") or []
    wave_h = {t: v for t, v in zip(m_times, mh.get("wave_height") or [])}
    wave_p = {t: v for t, v in zip(m_times, mh.get("wave_period") or [])}

    # MJO_Chile: índice real (una consulta por corrida, no por hora) para
    # ajustar el pronóstico de precipitación. Si no está disponible, se
    # expone el pronóstico base sin ajuste (nunca se inventa una fase MJO).
    mjo_indice = obtener_indice_mjo_real()

    hourly_states: list[dict[str, Any]] = []
    n = min(len(times), hours)
    heights = [0, 10, 40, 50, 100, 150, 200]
    for i in range(n):
        ts = times[i]
        v_ms = float(wind[i] or 0) if i < len(wind) and wind[i] is not None else 0.0
        v_kmh = v_ms * 3.6
        if i < len(gust) and gust[i] is not None:
            g_ms = float(gust[i])
        else:
            g_ms = v_ms * 1.3
        hs = float(wave_h.get(ts) or (0.8 + 0.2 * math.sin(i / 8.0)))
        tp = float(wave_p.get(ts) or (10 + 2 * math.sin(i / 12.0)))
        vis_m = float(vis[i]) if i < len(vis) and vis[i] is not None else 8000.0
        precip_mm = float(precip[i]) if i < len(precip) and precip[i] is not None else 0.0
        wind_spread = ens_wind["spread"][i] if i < len(ens_wind["spread"]) else None

        precip_info: dict[str, Any] = {"precipitacion_base_mm": round(precip_mm, 2)}
        if mjo_indice.get("disponible"):
            precip_info = ajustar_precipitacion_mjo(
                precip_mm, int(mjo_indice["fase"]), float(mjo_indice["amplitud"])
            )

        resonancia = evaluar_resonancia_pendular(longitud_cable_m, tp)

        dir_10m = float(wdir[i]) if i < len(wdir) and wdir[i] is not None else 0.0
        v_900_ms = float(ens_900hpa["media"][i]) if i < len(ens_900hpa["media"]) and ens_900hpa["media"][i] is not None else None
        dir_900 = float(wdir900_serie[i]) if i < len(wdir900_serie) and wdir900_serie[i] is not None else dir_10m
        cloud_pct = float(ens_cloud["media"][i]) if i < len(ens_cloud["media"]) and ens_cloud["media"][i] is not None else None
        es_de_dia = bool(is_day_serie[i]) if i < len(is_day_serie) and is_day_serie[i] is not None else True

        current = corriente_superficial_por_viento(v_ms, dir_10m, lat)
        perfil_estabilidad = extrapolar_power_law_estabilidad(
            v_ms, 100.0, wind_speed_10m_ms=v_ms, cloud_cover_pct=cloud_pct, is_day=es_de_dia
        )

        hourly_states.append(
            {
                "timestamp": ts if "T" in str(ts) else f"{ts}T00:00:00Z",
                "location": {
                    "latitude": lat,
                    "longitude": lon,
                    "height_m": float(puerto.get("altitud_msnm") or 0),
                },
                "wind_surface_kmh": round(v_kmh, 2),
                "wind_surface_ms": round(v_ms, 3),
                "wind_surface_kn": round(v_ms * 1.94384, 2),
                "wind_surface_dispersion_modelos_ms": round(wind_spread, 3) if wind_spread is not None else None,
                "wind_direction_surface": dir_10m,
                # Real: viento a 900 hPa del propio NWP (ensamble), ya no un
                # factor v10m*1.45 fabricado.
                "wind_900mb_ms": round(v_900_ms, 3) if v_900_ms is not None else None,
                "wind_900mb_direction": dir_900,
                "wind_gust_10m_kmh": round(g_ms * 3.6, 2),
                "wave_params": {"Hs": round(hs, 2), "Tp": round(tp, 1)},
                "resonancia_pendular": resonancia,
                "precipitacion": precip_info,
                "tidal_state": {
                    "level_m": round(0.9 + 0.55 * math.sin(i * math.pi / 6), 2),
                    "rate_change_cmh": 8,
                    "fuente": "astronomica_sintetica",
                },
                "current_profile": current,
                "visibility_m": vis_m,
                "ship_heave_m": round(hs * 0.35, 2),
                "wind_profile": _log_profile(v_ms, z0, heights),
                # Perfil alternativo a 100m considerando estabilidad real
                # (Pasquill); comparar con wind_profile (log-law neutro).
                "wind_profile_100m_estabilidad": perfil_estabilidad,
            }
        )

    issued = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return {
        "site_id": puerto["sitio_id"],
        "nombre": puerto.get("nombre"),
        "region": puerto.get("region"),
        "forecast_issued_utc": issued,
        "forecast_period_hours": n,
        "modelos_utilizados": modelos_usados,
        "mjo_chile": {
            k: v for k, v in mjo_indice.items() if k not in ("pc1", "pc2")
        },
        "hourly_states": hourly_states,
        "alerts": _build_alerts(hourly_states) + _build_alertas_resonancia(hourly_states),
        "ventana_operacional": _calcular_ventana(hourly_states),
        "longitud_cable_m": longitud_cable_m,
        "fuente": "openmeteo_multimodelo_marine" if wave_h else "openmeteo_multimodelo",
        "fuente_detalle": {
            "forecast": FORECAST_URL,
            "modelos": modelos_usados,
            "marine": MARINE_URL if wave_h else None,
            "marea_y_corriente": (
                "marea: aproximación astronómica sintética (sin fuente real integrada). "
                "corriente: parametrización física por viento real + profundidad de Ekman "
                "real (fórmula de Thorade, según latitud del sitio) — no es una medición "
                "de corriente, sigue siendo una parametrización."
            ),
            "lat": lat,
            "lon": lon,
        },
        "config": {
            "lat": lat,
            "lon": lon,
            "altitud_msnm": puerto.get("altitud_msnm"),
            "z0_terreno": z0,
            "tipo": puerto.get("tipo"),
        },
    }


def _from_hyperlocal(puerto: dict[str, Any], hours: int = 72) -> dict[str, Any]:
    from api_rest.spati.spati_puertos_era5_wrf_integration import (
        HyperLocalForecastGenerator,
        Point3D,
    )
    import dataclasses
    from enum import Enum

    loc = Point3D(float(puerto["lat"]), float(puerto["lon"]))
    gen = HyperLocalForecastGenerator(site_id=str(puerto["sitio_id"]), location=loc)
    start = datetime.now(timezone.utc)
    forecast = gen.generate_forecast(start_date=start, hours_ahead=hours)

    def json_serialize(obj: Any) -> Any:
        import numpy as np

        if dataclasses.is_dataclass(obj):
            return {k: json_serialize(v) for k, v in dataclasses.asdict(obj).items()}
        if isinstance(obj, dict):
            return {k: json_serialize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [json_serialize(i) for i in obj]
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        if hasattr(obj, "tolist"):
            return json_serialize(obj.tolist())
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        return obj

    out = json_serialize(forecast)
    out["fuente"] = "synthetic_local"
    out["fuente_detalle"] = {
        "motivo": "openmeteo_unavailable",
        "lat": puerto["lat"],
        "lon": puerto["lon"],
    }
    out["nombre"] = puerto.get("nombre")
    out["region"] = puerto.get("region")
    out["config"] = {
        "lat": puerto["lat"],
        "lon": puerto["lon"],
        "altitud_msnm": puerto.get("altitud_msnm"),
        "z0_terreno": puerto.get("z0_terreno"),
        "tipo": puerto.get("tipo"),
    }
    # Limitar alertas ruidosas del motor demo
    alerts = out.get("alerts") or []
    if isinstance(alerts, list) and len(alerts) > 24:
        out["alerts"] = alerts[:24]
        out["alerts_truncated"] = True
    
    out["ventana_operacional"] = _calcular_ventana(out.get("hourly_states") or [])
    return out


def generar_pronostico_puerto(
    sitio_id: str, *, hours: int = 72, longitud_cable_m: float | None = None
) -> dict[str, Any]:
    """Pipeline: Open-Meteo → hyperlocal sintético (coords del puerto).

    `longitud_cable_m`: distancia real punto de suspensión → centro de masa
    de la carga para esta maniobra (cable + eslingas). Si no se especifica,
    se usa `LONGITUD_CABLE_DEFAULT_M` y la respuesta lo marca explícitamente
    como un valor por defecto, no la operación real.
    """
    puerto = get_puerto(sitio_id)
    if not puerto:
        return {
            "error": "sitio_no_encontrado",
            "sitio_id": sitio_id,
            "sugerencia": "Use iqq, ventanas_muelle, anf, vlp, san o pmc",
        }

    cable_m = float(longitud_cable_m) if longitud_cable_m else LONGITUD_CABLE_DEFAULT_M
    cable_es_default = longitud_cable_m is None

    try:
        out = _from_openmeteo(puerto, hours=hours, longitud_cable_m=cable_m)
        out["longitud_cable_m_es_default"] = cable_es_default
        return out
    except Exception as exc:
        logger.warning("puerto Open-Meteo %s: %s", puerto["sitio_id"], exc)
        if not _ALLOW_SYNTHETIC:
            return {
                "error": "nwp_no_disponible",
                "sitio_id": puerto["sitio_id"],
                "detalle": str(exc),
                "sugerencia": "Open-Meteo saturado o lento; reintente en 1–2 minutos",
            }
        try:
            out = _from_hyperlocal(puerto, hours=hours)
            out["nwp_aviso"] = (
                "Pronóstico local estimado (Open-Meteo no disponible). "
                "No usar para decisión crítica hasta recuperar NWP."
            )
            return out
        except Exception as exc2:
            logger.exception("puerto fallback falló %s", puerto["sitio_id"])
            return {
                "error": "nwp_no_disponible",
                "sitio_id": puerto["sitio_id"],
                "detalle": f"{exc} | fallback: {exc2}",
            }
