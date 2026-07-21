#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Caché en disco para consultas OpenMeteo (TTL 15 min)."""

from __future__ import annotations

import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, TypeVar

import pandas as pd

T = TypeVar("T")

TTL_SECONDS = 900
# Edad máxima (segundos) del "último dato bueno" que se sirve cuando OpenMeteo falla.
# Por defecto 48 h: datos reales recientes, sin servir algo demasiado viejo.
LAST_GOOD_MAX_AGE = int(os.getenv("METGO_CACHE_LASTGOOD_MAX_AGE", str(48 * 3600)))
_hits = 0
_misses = 0
_lastgood_hits = 0

_CACHE_DIR: Path | None = None
_cache = None


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
    raw = f"{estacion}|{tipo}|{dias}"
    return hashlib.sha256(raw.encode()).hexdigest()


def cache_stats() -> dict[str, int]:
    return {
        "cache_hits": _hits,
        "cache_misses": _misses,
        "cache_lastgood_hits": _lastgood_hits,
    }


def _marcar_desde_cache(df: pd.DataFrame, stored_at: float) -> pd.DataFrame:
    """Copia el DataFrame etiquetando que proviene de caché (dato real, no en vivo)."""
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
            _cache.set(key, payload)  # sin expire -> persiste (último dato bueno)
    elif isinstance(_cache, dict):
        _cache[key] = payload


def _servir_lastgood(key: str) -> pd.DataFrame | None:
    """Devuelve el último dato bueno si existe y no supera la edad máxima."""
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
    """Ejecuta fetcher con caché TTL. Si OpenMeteo falla, sirve el último dato REAL
    almacenado (marcado con `desde_cache`) en vez de devolver None."""
    global _hits, _misses
    _ensure_cache()
    key = _cache_key(estacion, tipo, dias)

    entry = _leer_entry(key)
    if entry is not None:
        df, stored_at = entry
        if time.time() - stored_at < TTL_SECONDS:
            _hits += 1
            return df.copy() if isinstance(df, pd.DataFrame) else df

    _misses += 1
    df = fetcher(estacion, tipo, dias)
    if df is not None and not df.empty:
        payload = (df.copy(), time.time())
        _guardar_entry(key, payload, ttl=TTL_SECONDS)
        _guardar_entry(key + "|lastgood", payload)
        return df

    # OpenMeteo falló: servir el último dato real conocido (si existe y es reciente).
    return _servir_lastgood(key)


def get_json_cached(
    clave: str,
    fetcher: Callable[[], Any],
    es_valido: Callable[[Any], bool] | None = None,
    ttl: int = TTL_SECONDS,
) -> Any:
    """Caché TTL para payloads JSON (series horarias, etc.) con 'último dato bueno'.

    - `clave`: identificador estable (p.ej. "viento_horario|Quillota|7").
    - `es_valido`: valida el payload fresco antes de cachearlo (default: truthiness).
    - Si el fetcher falla o devuelve un payload inválido, sirve el último payload
      REAL cacheado (marcado con `desde_cache`) mientras no supere LAST_GOOD_MAX_AGE.
    """
    global _hits, _misses, _lastgood_hits
    _ensure_cache()
    key = "json|" + hashlib.sha256(clave.encode()).hexdigest()
    valida = es_valido or bool

    entry = _leer_entry(key)
    if entry is not None:
        payload, stored_at = entry
        if time.time() - stored_at < ttl:
            _hits += 1
            return payload

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
