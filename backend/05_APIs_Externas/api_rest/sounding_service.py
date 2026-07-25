#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Soundings modelados por estación (Open-Meteo pressure levels) — proxy MetPy."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from api_rest.dispersion_service import FORECAST_API_BASE, _get_json, clasificar_inversion
from api_rest.estaciones_catalogo import COORDS, SLUG_A_NOMBRE
from api_rest.ventilacion_service import codigo_desde_indice, label_codigo

TZ_CHILE = ZoneInfo("America/Santiago")

_NIVELES = [1000, 975, 950, 925, 900, 850, 800, 700, 600, 500]


def _hourly_vars() -> list[str]:
    base = [
        "temperature_2m",
        "dew_point_2m",
        "surface_pressure",
        "wind_speed_10m",
        "wind_direction_10m",
        "boundary_layer_height",
    ]
    for p in _NIVELES:
        base.append(f"temperature_{p}hPa")
        base.append(f"relative_humidity_{p}hPa")
        base.append(f"wind_speed_{p}hPa")
        base.append(f"wind_direction_{p}hPa")
        base.append(f"geopotential_height_{p}hPa")
    return base


def _dewpoint_from_rh(t_c: float | None, rh: float | None) -> float | None:
    if t_c is None or rh is None or rh <= 0:
        return None
    # Magnus approx
    a, b = 17.27, 237.7
    rh = max(1.0, min(100.0, rh))
    gamma = (a * t_c / (b + t_c)) + math.log(rh / 100.0)
    return round((b * gamma) / (a - gamma), 2)


def _lapse_rate(t1: float, z1: float, t2: float, z2: float) -> float | None:
    dz = z2 - z1
    if abs(dz) < 10:
        return None
    return round((t1 - t2) / (dz / 1000.0), 2)  # °C/km


def sounding_estacion(estacion_id: str, horas: int = 24) -> dict[str, Any] | None:
    key = (estacion_id or "").strip().lower().replace("-", "_")
    coords = COORDS.get(key)
    if not coords or key not in SLUG_A_NOMBRE:
        return None

    horas = max(1, min(int(horas), 72))
    dias = min(7, (horas + 23) // 24 + 1)
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "hourly": ",".join(_hourly_vars()),
        "wind_speed_unit": "ms",
        "timezone": "America/Santiago",
        "forecast_days": dias,
    }
    data = _get_json(FORECAST_API_BASE, params)
    if not data:
        # Fallback subset
        params["hourly"] = ",".join(
            [
                "temperature_2m",
                "dew_point_2m",
                "surface_pressure",
                "wind_speed_10m",
                "wind_direction_10m",
                "temperature_925hPa",
                "temperature_850hPa",
                "temperature_700hPa",
                "temperature_500hPa",
                "relative_humidity_925hPa",
                "relative_humidity_850hPa",
                "wind_speed_850hPa",
                "wind_direction_850hPa",
            ]
        )
        data = _get_json(FORECAST_API_BASE, params)
    if not data:
        return None

    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    frames: list[dict[str, Any]] = []

    def val(name: str, i: int):
        serie = hourly.get(name) or []
        v = serie[i] if i < len(serie) else None
        return round(float(v), 2) if isinstance(v, (int, float)) else None

    for i, ts in enumerate(times[:horas]):
        t2 = val("temperature_2m", i)
        td2 = val("dew_point_2m", i)
        sp = val("surface_pressure", i)
        niveles: list[dict[str, Any]] = [
            {
                "pressure_hPa": round(sp, 1) if sp else 1013.0,
                "height_m": 2.0,
                "temp_c": t2,
                "dewpoint_c": td2,
                "wind_ms": val("wind_speed_10m", i),
                "wind_dir": val("wind_direction_10m", i),
                "origen": "superficie",
            }
        ]
        for p in _NIVELES:
            tc = val(f"temperature_{p}hPa", i)
            if tc is None:
                continue
            rh = val(f"relative_humidity_{p}hPa", i)
            gh = val(f"geopotential_height_{p}hPa", i)
            niveles.append(
                {
                    "pressure_hPa": p,
                    "height_m": gh,
                    "temp_c": tc,
                    "dewpoint_c": _dewpoint_from_rh(tc, rh),
                    "rh": rh,
                    "wind_ms": val(f"wind_speed_{p}hPa", i),
                    "wind_dir": val(f"wind_direction_{p}hPa", i),
                    "origen": "modelo",
                }
            )
        inv = clasificar_inversion(t2, val("temperature_925hPa", i), val("temperature_850hPa", i))
        # Lapse 925-700
        t925 = val("temperature_925hPa", i)
        t700 = val("temperature_700hPa", i)
        lapse = None
        if t925 is not None and t700 is not None:
            lapse = _lapse_rate(t925, 760, t700, 3000)

        # Estabilidad proxy → índice rough
        pbl = val("boundary_layer_height", i)
        viento = val("wind_speed_10m", i) or 1.0
        from api_rest.dispersion_service import indice_dispersion

        idx = indice_dispersion(
            viento,
            inv.get("inversion_intensidad"),
            "despejado",
            pbl,
        )
        codigo = codigo_desde_indice(idx.get("indice_dispersion"))
        frames.append(
            {
                "fecha_hora": ts,
                "niveles": niveles,
                "diagnostico": {
                    **inv,
                    "lapse_925_700_c_km": lapse,
                    "altura_capa_limite": pbl,
                    "indice_dispersion": idx.get("indice_dispersion"),
                    "ventilacion": codigo,
                    "ventilacion_label": label_codigo(codigo),
                },
            }
        )

    return {
        "estacion_id": key,
        "estacion_nombre": SLUG_A_NOMBRE.get(key, key),
        "lat": coords["lat"],
        "lon": coords["lon"],
        "fuente": "openmeteo_forecast_pressure_levels",
        "nota": "Sounding modelado (proxy MetPy); no es radiosondea observada.",
        "frames": frames,
        "generado": datetime.now(TZ_CHILE).isoformat(timespec="seconds"),
    }


def soundings_sitio(sitio: str = "copiapo") -> dict[str, Any]:
    from api_rest.estaciones_catalogo import ESTACIONES_POR_SITIO

    sitio = (sitio or "copiapo").strip().lower()
    slugs = ESTACIONES_POR_SITIO.get(sitio) or []
    resumen = []
    for slug in slugs:
        s = sounding_estacion(slug, horas=1)
        if not s or not s.get("frames"):
            resumen.append({"estacion_id": slug, "ok": False})
            continue
        f0 = s["frames"][0]
        resumen.append(
            {
                "estacion_id": slug,
                "nombre": s["estacion_nombre"],
                "ok": True,
                "fecha_hora": f0.get("fecha_hora"),
                "diagnostico": f0.get("diagnostico"),
                "n_niveles": len(f0.get("niveles") or []),
            }
        )
    return {"sitio": sitio, "estaciones": resumen}
