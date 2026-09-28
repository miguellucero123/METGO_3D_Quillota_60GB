#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ingesta multi-modelo real de Open-Meteo (ECMWF, ICON, GFS) para METGO.

Política de datos del sistema: **solo datos reales**. Cuando no hay una
estación meteorológica propia disponible para una variable/sitio, el sistema
debe recurrir a Open-Meteo pidiendo explícitamente varios modelos NWP reales
en una sola llamada (parámetro ``models=``) y combinarlos en un ensamble
simple (media + dispersión entre modelos), en vez de depender de un único
modelo "best_match" opaco o de datos sintéticos/simulados.

Modelos verificados en vivo contra la API pública el 2026-09-15
(``https://api.open-meteo.com/v1/forecast?...&models=ecmwf_ifs025,icon_seamless,gfs_seamless``):
cada variable vuelve sufijada por modelo, p. ej. ``precipitation_ecmwf_ifs025``.
"""

from __future__ import annotations

import logging
import os
import statistics
from typing import Any

import requests

logger = logging.getLogger(__name__)

_API_KEY = (os.getenv("METGO_OPENMETEO_API_KEY") or os.getenv("OPENMETEO_API_KEY") or "").strip()
# Uso comercial (servicio pagado a clientes): la API key de Open-Meteo solo es
# válida en los hosts ``customer-*``; el host público es solo no comercial.
FORECAST_URL = (
    os.getenv("METGO_OPENMETEO_FORECAST_URL")
    or (
        "https://customer-api.open-meteo.com/v1/forecast"
        if _API_KEY
        else "https://api.open-meteo.com/v1/forecast"
    )
).rstrip("/")
_TIMEOUT = int(os.getenv("METGO_OPENMETEO_MULTIMODEL_TIMEOUT", "15"))
_RETRIES = int(os.getenv("METGO_OPENMETEO_MULTIMODEL_RETRIES", "2"))

# Modelos deterministas reales usados por defecto para el ensamble simple.
# Editable vía env sin tocar código (ej. agregar "gem_seamless").
MODELOS_DETERMINISTAS: list[str] = [
    m.strip()
    for m in (
        os.getenv("METGO_OPENMETEO_MODELOS") or "ecmwf_ifs025,icon_seamless,gfs_seamless"
    ).split(",")
    if m.strip()
]

ENSEMBLE_URL = (
    os.getenv("METGO_OPENMETEO_ENSEMBLE_URL") or "https://ensemble-api.open-meteo.com/v1/ensemble"
).rstrip("/")


class MultiModeloNoDisponibleError(RuntimeError):
    """Open-Meteo multi-modelo no respondió; el caller debe degradar de forma honesta."""


def fetch_multimodelo(
    lat: float,
    lon: float,
    *,
    hourly_vars: list[str],
    forecast_days: int = 3,
    modelos: list[str] | None = None,
    past_days: int = 0,
) -> dict[str, Any]:
    """Una sola llamada real a Open-Meteo con varios modelos NWP (``models=a,b,c``).

    Retorna el JSON crudo de Open-Meteo. Cada variable de ``hourly_vars`` vuelve
    como ``<variable>_<modelo>`` por cada modelo solicitado.
    """
    modelos = modelos or MODELOS_DETERMINISTAS
    params: dict[str, Any] = {
        "latitude": lat,
        "longitude": lon,
        "forecast_days": max(1, min(int(forecast_days), 7)),
        "timezone": "UTC",
        "wind_speed_unit": "ms",
        "hourly": ",".join(hourly_vars),
        "models": ",".join(modelos),
    }
    if past_days:
        params["past_days"] = max(0, min(int(past_days), 7))
    if _API_KEY:
        params["apikey"] = _API_KEY

    last_err: Exception | None = None
    for intento in range(1, _RETRIES + 1):
        try:
            r = requests.get(FORECAST_URL, params=params, timeout=_TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                if not data.get("hourly"):
                    raise MultiModeloNoDisponibleError("respuesta sin 'hourly'")
                return data
            if r.status_code >= 500 and intento < _RETRIES:
                continue
            raise MultiModeloNoDisponibleError(f"HTTP {r.status_code}: {r.text[:200]}")
        except MultiModeloNoDisponibleError:
            raise
        except Exception as exc:  # requests.RequestException, timeout, json error, etc.
            last_err = exc
    raise MultiModeloNoDisponibleError(str(last_err or "fetch multi-modelo fallido"))


def ensamble_variable(
    hourly: dict[str, Any], variable: str, modelos: list[str] | None = None
) -> dict[str, Any]:
    """Combina ``<variable>_<modelo>`` de varios modelos reales en media + dispersión.

    ``spread`` es la desviación estándar entre modelos por paso horario: un
    proxy real de incertidumbre entre modelos NWP reales, no un valor inventado.
    Úsese solo para magnitudes escalares (viento, precipitación, temperatura);
    NO promediar variables circulares (dirección de viento) con esta función.
    """
    modelos = modelos or MODELOS_DETERMINISTAS
    series_por_modelo: dict[str, list[float | None]] = {}
    n = 0
    for modelo in modelos:
        serie = hourly.get(f"{variable}_{modelo}")
        if serie is None:
            continue
        series_por_modelo[modelo] = serie
        n = max(n, len(serie))

    media: list[float | None] = []
    spread: list[float | None] = []
    for i in range(n):
        vals = [
            float(s[i])
            for s in series_por_modelo.values()
            if i < len(s) and s[i] is not None
        ]
        if not vals:
            media.append(None)
            spread.append(None)
            continue
        media.append(sum(vals) / len(vals))
        spread.append(statistics.pstdev(vals) if len(vals) > 1 else 0.0)

    return {
        "media": media,
        "spread": spread,
        "n_modelos": len(series_por_modelo),
        "modelos": series_por_modelo,
    }


def primer_modelo_disponible(
    hourly: dict[str, Any], variable: str, modelos: list[str] | None = None
) -> list[float | None] | None:
    """Serie del primer modelo real disponible para una variable circular (ej. dirección)."""
    modelos = modelos or MODELOS_DETERMINISTAS
    for modelo in modelos:
        serie = hourly.get(f"{variable}_{modelo}")
        if serie is not None:
            return serie
    return None
