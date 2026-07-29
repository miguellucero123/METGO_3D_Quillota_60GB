#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPATI — Ingesta Open-Meteo → serie 72 h × 15 min (288 intervalos)."""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

logger = logging.getLogger(__name__)

FORECAST_URL = (
    os.getenv("METGO_OPENMETEO_FORECAST_URL")
    or "https://api.open-meteo.com/v1/forecast"
).rstrip("/")
_API_KEY = (os.getenv("METGO_OPENMETEO_API_KEY") or os.getenv("OPENMETEO_API_KEY") or "").strip()
# Cortos: el endpoint SPA no puede colgarse 90s+ (Render + Open-Meteo 429).
_TIMEOUT = int(os.getenv("METGO_SPATI_NWP_TIMEOUT", "12"))
_RETRIES = int(os.getenv("METGO_SPATI_NWP_RETRIES", "2"))
_CACHE_TTL_S = int(os.getenv("METGO_SPATI_NWP_CACHE_TTL", str(45 * 60)))
_ALLOW_SYNTHETIC = os.getenv("METGO_SPATI_ALLOW_SYNTHETIC", "1").strip() not in ("0", "false", "no")

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
    "wind_speed_500hPa",
    "wind_direction_500hPa",
    "temperature_850hPa",
]

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

# Memoria proceso (última respuesta por site-key)
_LASTGOOD: dict[str, tuple[float, pd.DataFrame]] = {}


class NWPDataUnavailableError(RuntimeError):
    pass


def _runtime_cache_dir() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            d = p / "backend" / "08_Gestion_Datos" / "datos_runtime" / "spati_nwp"
            d.mkdir(parents=True, exist_ok=True)
            return d
    d = Path("spati_nwp_cache")
    d.mkdir(parents=True, exist_ok=True)
    return d


def _cache_key(lat: float, lon: float, days: int) -> str:
    return f"{round(lat, 4)}_{round(lon, 4)}_d{days}"


def _load_lastgood(key: str) -> pd.DataFrame | None:
    now = time.time()
    mem = _LASTGOOD.get(key)
    if mem and now - mem[0] <= _CACHE_TTL_S:
        return mem[1].copy()
    path = _runtime_cache_dir() / f"{key}.pkl"
    if not path.exists():
        return None
    try:
        age = now - path.stat().st_mtime
        if age > _CACHE_TTL_S * 2:
            return None
        df = pd.read_pickle(path)
        if isinstance(df, pd.DataFrame) and len(df) > 0:
            _LASTGOOD[key] = (now, df)
            return df.copy()
    except Exception as exc:
        logger.warning("SPATI NWP cache read: %s", exc)
    return None


def _save_lastgood(key: str, df: pd.DataFrame) -> None:
    _LASTGOOD[key] = (time.time(), df.copy())
    try:
        path = _runtime_cache_dir() / f"{key}.pkl"
        df.to_pickle(path)
    except Exception as exc:
        logger.warning("SPATI NWP cache write: %s", exc)


def _synthetic_df(lat: float, lon: float, *, alt_msnm: float | None = None) -> pd.DataFrame:
    """Serie degradada operativa cuando Open-Meteo no responde (429 / offline).

    No inventa alertas críticas: viento medio moderado + ráfagas suaves para
    que el panel no quede vacío. Flag nwp_fuente=synthetic_degraded.
    """
    import math

    t0 = pd.Timestamp.now(tz="UTC").floor("15min")
    idx = pd.date_range(t0, periods=288, freq="15min", tz="UTC")
    # Media climática simple por altitud
    alt = float(alt_msnm or 2500)
    base = 14.0 + min(16.0, max(0.0, (alt - 1000) / 200.0))
    rows = []
    for i, ts in enumerate(idx):
        # Ciclo diurno débil + variación suave
        hour = ts.hour + ts.minute / 60.0
        diurno = 3.0 * math.sin((hour - 6) / 24.0 * 2 * math.pi)
        onda = 2.0 * math.sin(i / 18.0)
        v10 = max(4.0, base + diurno + onda)
        v100 = v10 * 1.18
        gust = v10 * 1.35
        rows.append(
            {
                "valid_time": ts,
                "viento_modelo_10m": round(v10, 2),
                "viento_modelo_80m": round(v10 * 1.12, 2),
                "viento_modelo_100m": round(v100, 2),
                "rafaga_modelo_10m": round(gust, 2),
                "dir_modelo": (220 + i * 0.4) % 360,
                "dir_100m": (225 + i * 0.4) % 360,
                "temp_celsius": 8.0 - alt / 800.0 + diurno * 0.4,
                "presion_pa": max(55000.0, 101325.0 * math.exp(-alt / 8500.0)),
                "pressure_msl_pa": 101325.0,
                "rh_pct": 35.0,
                "precip_mmh": 0.0,
                "snowfall_mm": 0.0,
                "cloud_pct": 40.0,
                "visibilidad_m": 20000.0,
                "viento_500hpa_kt": None,
                "dir_500hpa": None,
                "temp_850hpa": None,
                "prob_rayos_pct": None,
            }
        )
    df = pd.DataFrame(rows).set_index("valid_time")
    df["run_timestamp"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    df.attrs["nwp_fuente"] = "synthetic_degraded"
    df.attrs["nwp_aviso"] = (
        "Pronóstico estimado (Open-Meteo no disponible / rate limit). "
        "No usar para decisión crítica hasta recuperar NWP."
    )
    return df


def _cooldown_restante() -> int:
    try:
        from datos_reales_openmeteo import openmeteo_cooldown_restante

        return int(openmeteo_cooldown_restante())
    except Exception:
        return 0


def _openmeteo_cooldown() -> bool:
    try:
        from datos_reales_openmeteo import openmeteo_en_cooldown

        return bool(openmeteo_en_cooldown())
    except Exception:
        return False


def _mark_cooldown(seconds: int = 120) -> None:
    try:
        from datos_reales_openmeteo import marcar_openmeteo_cooldown

        marcar_openmeteo_cooldown(seconds)
    except Exception:
        pass


class NWPIngestor:
    def __init__(self, modelo: str = "best_match"):
        self.modelo = modelo

    def fetch_forecast(
        self,
        lat: float,
        lon: float,
        forecast_days: int = 3,
        *,
        alt_msnm: float | None = None,
    ) -> pd.DataFrame:
        """Retorna DataFrame indexado UTC con ~288 filas (72 h × 15 min)."""
        days = max(3, min(int(forecast_days), 7))
        key = _cache_key(lat, lon, days)

        def _fallback(err: Exception | None) -> pd.DataFrame:
            cached = _load_lastgood(key)
            if cached is not None:
                logger.warning("SPATI NWP → lastgood (%s)", err)
                cached = cached.copy()
                cached.attrs["nwp_fuente"] = "lastgood_error"
                return cached
            if _ALLOW_SYNTHETIC:
                logger.warning("SPATI NWP → synthetic_degraded (%s)", err)
                return _synthetic_df(lat, lon, alt_msnm=alt_msnm)
            raise NWPDataUnavailableError(str(err or "sin datos Open-Meteo"))

        if _openmeteo_cooldown():
            cached = _load_lastgood(key)
            if cached is not None:
                logger.info("SPATI NWP cooldown → lastgood %s", key)
                cached = cached.copy()
                cached.attrs["nwp_fuente"] = "lastgood_cooldown"
                return cached
            rest = _cooldown_restante()
            if rest > 20:
                return _fallback(NWPDataUnavailableError(f"cooldown {rest}s"))
            # Espera corta y un intento mínimo
            time.sleep(min(rest + 0.5, 8))

        base: dict[str, Any] = {
            "latitude": lat,
            "longitude": lon,
            "forecast_days": days,
            "timezone": "UTC",
            "wind_speed_unit": "ms",
        }
        if _API_KEY:
            base["apikey"] = _API_KEY

        attempts: list[tuple[str | None, list[str]]] = [
            (None if self.modelo == "best_match" else self.modelo, _HOURLY_VARS_MIN),
            (None, _HOURLY_VARS_MIN),
        ]
        last_err: Exception | None = None
        data = None
        for model, vars_ in attempts:
            p = dict(base)
            p["hourly"] = ",".join(vars_)
            if model:
                p["models"] = model
            try:
                data = self._get_json(p)
                if data and data.get("hourly"):
                    break
            except NWPDataUnavailableError as exc:
                last_err = exc
                if "429" in str(exc):
                    _mark_cooldown(90)
                    time.sleep(2)
                    # un reintento mínimo tras breve espera
                    try:
                        data = self._get_json({**base, "hourly": ",".join(_HOURLY_VARS_MIN)})
                        if data and data.get("hourly"):
                            break
                    except Exception as exc2:
                        last_err = exc2
                    break
                logger.warning("NWP intento falló: %s", exc)
                data = None
            except Exception as exc:
                last_err = exc
                logger.warning("NWP intento falló: %s", exc)
                data = None

        if not data or not data.get("hourly"):
            return _fallback(last_err)

        df = self._hourly_to_df(data["hourly"])
        _save_lastgood(key, df)
        df.attrs["nwp_fuente"] = "openmeteo"
        return df

    def _hourly_to_df(self, hourly: dict[str, Any]) -> pd.DataFrame:
        times = hourly.get("time") or []
        rows = []
        for i, ts in enumerate(times):
            def _f(key: str, scale: float = 1.0, _i=i):
                serie = hourly.get(key) or []
                v = serie[_i] if _i < len(serie) else None
                if v is None:
                    return None
                return float(v) * scale

            v10 = _f("wind_speed_10m", 3.6)
            v80 = _f("wind_speed_80m", 3.6)
            v100 = _f("wind_speed_100m", 3.6)
            gust = _f("wind_gusts_10m", 3.6)
            p_raw = _f("surface_pressure", 1.0)
            if p_raw is not None and p_raw < 2000:
                p_pa = p_raw * 100.0
            else:
                p_pa = p_raw
            w500_ms = _f("wind_speed_500hPa", 1.0)
            w500_kt = (w500_ms * 1.94384) if w500_ms is not None else None
            p_msl = _f("pressure_msl", 1.0)
            if p_msl is not None and p_msl < 2000:
                p_msl = p_msl * 100.0

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
                    "pressure_msl_pa": p_msl,
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
        for col in list(df.columns):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.resample("15min").interpolate(method="time", limit_direction="both")
        t0 = df.index.min()
        t1 = t0 + pd.Timedelta(hours=72)
        df = df.loc[t0:t1].iloc[:288]
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
                    _mark_cooldown(180)
                    raise NWPDataUnavailableError("HTTP 429")
                if r.status_code >= 500 and intento < _RETRIES:
                    time.sleep(min(1.5**intento, 4))
                    continue
                raise NWPDataUnavailableError(f"HTTP {r.status_code}")
            except NWPDataUnavailableError:
                raise
            except Exception as exc:
                last = exc
                if intento < _RETRIES:
                    time.sleep(min(1.5**intento, 4))
        raise NWPDataUnavailableError(str(last or "fetch fallido"))
