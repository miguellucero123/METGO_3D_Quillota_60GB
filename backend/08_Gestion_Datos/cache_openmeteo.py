#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Caché en disco para consultas OpenMeteo.

Modo ciclo (default ``METGO_OPENMETEO_FETCH_MODE=ciclo``):
  claves incluyen el ciclo 00/12 UTC; TTL hasta el próximo ciclo;
  fuera de ventana 00/12 no se llama a la API si hay last-good.

Modo ``ttl``: refresco por ``METGO_OPENMETEO_CACHE_TTL`` (default 1 h).
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, TypeVar

import pandas as pd

T = TypeVar("T")

# Default 1 h en modo ttl. Para 30 min: METGO_OPENMETEO_CACHE_TTL=1800
_DEFAULT_TTL = 3600

# Edad máxima del "último dato bueno" si OpenMeteo falla (default 48 h).
LAST_GOOD_MAX_AGE = int(os.getenv("METGO_CACHE_LASTGOOD_MAX_AGE", str(48 * 3600)))
_hits = 0
_misses = 0
_lastgood_hits = 0

_CACHE_DIR: Path | None = None
_cache = None

# Compat: imports antiguos usan TTL_SECONDS
TTL_SECONDS = _DEFAULT_TTL


def get_ttl_seconds() -> int:
    """TTL efectivo: en modo ciclo, hasta el próximo 00/12 UTC; si no, env."""
    try:
        from api_rest.integracion.openmeteo_ciclo import fetch_mode, segundos_hasta_proximo_ciclo

        if fetch_mode() == "ciclo":
            return max(300, segundos_hasta_proximo_ciclo())
    except Exception:
        pass
    try:
        return max(300, int(os.getenv("METGO_OPENMETEO_CACHE_TTL", str(_DEFAULT_TTL))))
    except ValueError:
        return _DEFAULT_TTL


def _ciclo_suffix() -> str:
    try:
        from api_rest.integracion.openmeteo_ciclo import ciclo_utc_vigente

        return ciclo_utc_vigente()
    except Exception:
        return "na"


def _may_live_fetch() -> bool:
    """False = servir last-good y no pegar a Open-Meteo (modo ciclo fuera de 00/12)."""
    try:
        from api_rest.integracion.openmeteo_ciclo import (
            allow_live_openmeteo_fetch,
            force_fetch_activo,
        )

        if force_fetch_activo():
            return True
        return allow_live_openmeteo_fetch()
    except Exception:
        return True


def _repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            return p
    return Path(__file__).resolve().parents[2]


def _ensure_cache():
    global _CACHE_DIR, _cache
    if _cache is not None:
        return
    root = _repo_root()
    _CACHE_DIR = root / "metgo" / "cache" / "openmeteo"
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        import diskcache

        _cache = diskcache.Cache(str(_CACHE_DIR))
    except ImportError:
        _cache = {}


def _cache_key(estacion: str, tipo: str, dias: int) -> str:
    raw = f"{estacion}|{tipo}|{dias}|{_ciclo_suffix()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def cache_stats() -> dict[str, int | str]:
    return {
        "cache_hits": _hits,
        "cache_misses": _misses,
        "cache_lastgood_hits": _lastgood_hits,
        "cache_ttl_s": get_ttl_seconds(),
        "ciclo_utc": _ciclo_suffix(),
    }


def lastgood_freshest_age_s(estacion: str = "Quillota", tipo: str = "diarios", dias: int = 7) -> int | None:
    """Edad en segundos del last-good más reciente para una clave típica, o None."""
    _ensure_cache()
    key = _cache_key(estacion, tipo, dias) + "|lastgood"
    entry = _leer_entry(key)
    if not entry:
        return None
    try:
        _df, stored_at = entry
        age = int(max(0, time.time() - float(stored_at)))
        if age > LAST_GOOD_MAX_AGE:
            return None
        return age
    except Exception:
        return None


def has_usable_lastgood(max_age_s: int | None = None) -> bool:
    """True si hay last-good fresco para Quillota (health / degradación)."""
    age = lastgood_freshest_age_s()
    if age is None:
        return False
    limit = LAST_GOOD_MAX_AGE if max_age_s is None else max_age_s
    return age <= limit


def _marcar_desde_cache(df: pd.DataFrame, stored_at: float) -> pd.DataFrame:
    out = df.copy()
    out["desde_cache"] = True
    out["cache_edad_horas"] = round(max(0.0, (time.time() - stored_at)) / 3600.0, 1)
    return out


def _leer_entry(key: str):
    if hasattr(_cache, "get"):
        return _cache.get(key, default=None)
    if isinstance(_cache, dict):
        return _cache.get(key)
    return None


def _guardar_entry(key: str, payload, ttl: int | None = None) -> None:
    if hasattr(_cache, "set"):
        if ttl:
            _cache.set(key, payload, expire=ttl)
        else:
            _cache.set(key, payload)
    elif isinstance(_cache, dict):
        _cache[key] = payload


def _servir_lastgood(key: str) -> pd.DataFrame | None:
    global _lastgood_hits
    entry = _leer_entry(key + "|lastgood")
    if not entry:
        return None
    df, stored_at = entry
    if not isinstance(df, pd.DataFrame) or df.empty:
        return None
    if time.time() - stored_at > LAST_GOOD_MAX_AGE:
        return None
    _lastgood_hits += 1
    return _marcar_desde_cache(df, stored_at)


def get_meteo_cached(
    estacion: str,
    tipo: str,
    dias: int,
    fetcher: Callable[[str, str, int], pd.DataFrame | None],
) -> pd.DataFrame | None:
    """Fetcher con caché por ciclo 00/12 (o TTL). Si falla OpenMeteo, sirve last-good."""
    global _hits, _misses, TTL_SECONDS
    _ensure_cache()
    ttl = get_ttl_seconds()
    TTL_SECONDS = ttl
    key = _cache_key(estacion, tipo, dias)

    entry = _leer_entry(key)
    if entry is not None:
        df, stored_at = entry
        if time.time() - stored_at < ttl:
            _hits += 1
            return df.copy() if isinstance(df, pd.DataFrame) else df

    en_cooldown = False
    try:
        from datos_reales_openmeteo import openmeteo_en_cooldown

        en_cooldown = bool(openmeteo_en_cooldown())
    except ImportError:
        pass

    if en_cooldown or not _may_live_fetch():
        lg = _servir_lastgood(key)
        if lg is not None:
            return lg
        # Bootstrap: sin last-good, permitir una descarga aunque estemos fuera de ciclo.
        if en_cooldown:
            _misses += 1
            return None

    _misses += 1
    df = fetcher(estacion, tipo, dias)
    if df is not None and not df.empty:
        payload = (df.copy(), time.time())
        _guardar_entry(key, payload, ttl=ttl)
        _guardar_entry(key + "|lastgood", payload)
        return df

    return _servir_lastgood(key)


def get_json_cached(
    clave: str,
    fetcher: Callable[[], Any],
    es_valido: Callable[[Any], bool] | None = None,
    ttl: int | None = None,
) -> Any:
    """Caché TTL/ciclo para payloads JSON con last-good (mapas, aire, series)."""
    global _hits, _misses, _lastgood_hits, TTL_SECONDS
    _ensure_cache()
    if ttl is None:
        ttl = get_ttl_seconds()
    TTL_SECONDS = get_ttl_seconds()
    clave_ciclo = f"{clave}|{_ciclo_suffix()}"
    key = "json|" + hashlib.sha256(clave_ciclo.encode()).hexdigest()
    valida = es_valido or bool

    entry = _leer_entry(key)
    if entry is not None:
        payload, stored_at = entry
        if time.time() - stored_at < ttl:
            _hits += 1
            return payload

    if not _may_live_fetch():
        lg = _leer_entry(key + "|lastgood")
        if lg:
            old_payload, stored_at = lg
            if time.time() - stored_at <= LAST_GOOD_MAX_AGE and valida(old_payload):
                _lastgood_hits += 1
                if isinstance(old_payload, dict):
                    out = dict(old_payload)
                    out["desde_cache"] = True
                    out["cache_edad_horas"] = round((time.time() - stored_at) / 3600.0, 1)
                    return out
                return old_payload
        # sin last-good → bootstrap con fetch abajo

    _misses += 1
    try:
        payload = fetcher()
    except Exception:
        payload = None

    if payload is not None and valida(payload):
        blob = (payload, time.time())
        _guardar_entry(key, blob, ttl=ttl)
        _guardar_entry(key + "|lastgood", blob)
        return payload

    lg = _leer_entry(key + "|lastgood")
    if lg:
        old_payload, stored_at = lg
        if time.time() - stored_at <= LAST_GOOD_MAX_AGE and valida(old_payload):
            _lastgood_hits += 1
            if isinstance(old_payload, dict):
                out = dict(old_payload)
                out["desde_cache"] = True
                out["cache_edad_horas"] = round((time.time() - stored_at) / 3600.0, 1)
                return out
            return old_payload
    return payload
