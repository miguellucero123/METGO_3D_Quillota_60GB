#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Caché en disco para consultas OpenMeteo (TTL 15 min)."""

from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path
from typing import Any, Callable, TypeVar

import pandas as pd

T = TypeVar("T")

TTL_SECONDS = 900
_hits = 0
_misses = 0

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
    return {"cache_hits": _hits, "cache_misses": _misses}


def get_meteo_cached(
    estacion: str,
    tipo: str,
    dias: int,
    fetcher: Callable[[str, str, int], pd.DataFrame | None],
) -> pd.DataFrame | None:
    """Ejecuta fetcher con caché TTL (solo DataFrame no vacío)."""
    global _hits, _misses
    _ensure_cache()
    key = _cache_key(estacion, tipo, dias)

    if hasattr(_cache, "get"):
        entry = _cache.get(key, default=None)
        if entry is not None:
            df, stored_at = entry
            if time.time() - stored_at < TTL_SECONDS:
                _hits += 1
                return df.copy() if isinstance(df, pd.DataFrame) else df
        _misses += 1
        df = fetcher(estacion, tipo, dias)
        if df is not None and not df.empty:
            _cache.set(key, (df.copy(), time.time()), expire=TTL_SECONDS)
        return df

    # fallback dict sin diskcache
    entry = _cache.get(key) if isinstance(_cache, dict) else None
    if entry:
        df, stored_at = entry
        if time.time() - stored_at < TTL_SECONDS:
            _hits += 1
            return df.copy()
    _misses += 1
    df = fetcher(estacion, tipo, dias)
    if df is not None and not df.empty and isinstance(_cache, dict):
        _cache[key] = (df.copy(), time.time())
    return df
