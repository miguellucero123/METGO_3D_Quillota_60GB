#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ciclos Open-Meteo METGO: descargas de pronóstico/mapas en 00 UTC y 12 UTC.

Modo ``ciclo`` (default): fuera del cron 00/12 no se golpean APIs Open-Meteo
si ya hay dato del ciclo vigente (caché / last-good / store).
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Iterator

# Horas UTC de corrida operativa (NWP / Open-Meteo forecast cycle).
CICLOS_UTC: tuple[int, ...] = (0, 12)

_FORCE_FETCH = False


def fetch_mode() -> str:
    """``ciclo`` = solo refrescar en 00/12; ``ttl`` = caché por METGO_OPENMETEO_CACHE_TTL."""
    return (os.getenv("METGO_OPENMETEO_FETCH_MODE") or "ciclo").strip().lower()


def _now_utc(now: datetime | None = None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def ciclo_utc_vigente(now: datetime | None = None) -> str:
    """Último ciclo 00 o 12 UTC ya iniciado. Ej: ``2026-08-31T00`` / ``2026-08-31T12``."""
    n = _now_utc(now)
    if n.hour >= 12:
        return n.strftime("%Y-%m-%dT12")
    return n.strftime("%Y-%m-%dT00")


def datetime_ciclo_vigente(now: datetime | None = None) -> datetime:
    n = _now_utc(now)
    if n.hour >= 12:
        return n.replace(hour=12, minute=0, second=0, microsecond=0)
    return n.replace(hour=0, minute=0, second=0, microsecond=0)


def proximo_ciclo_utc(now: datetime | None = None) -> datetime:
    n = _now_utc(now)
    if n.hour < 12:
        return n.replace(hour=12, minute=0, second=0, microsecond=0)
    manana = n.date() + timedelta(days=1)
    return datetime(manana.year, manana.month, manana.day, 0, 0, 0, tzinfo=timezone.utc)


def segundos_hasta_proximo_ciclo(now: datetime | None = None) -> int:
    delta = proximo_ciclo_utc(now) - _now_utc(now)
    return max(60, int(delta.total_seconds()))


def en_ventana_cron(now: datetime | None = None, margen_min: int = 90) -> bool:
    """True cerca de 00 o 12 UTC (margen por defecto ±90 min del tick)."""
    n = _now_utc(now)
    minutos = n.hour * 60 + n.minute
    for h in CICLOS_UTC:
        centro = h * 60
        # Distancia circular en el día (00 cerca de medianoche).
        d = abs(minutos - centro)
        d = min(d, 24 * 60 - d)
        if d <= margen_min:
            return True
    return False


def force_fetch_activo() -> bool:
    return bool(_FORCE_FETCH)


def allow_live_openmeteo_fetch() -> bool:
    """Si False, cache_openmeteo / clientes deben servir last-good y no pegar a la API."""
    if force_fetch_activo():
        return True
    mode = fetch_mode()
    if mode in ("ttl", "libre", "live", "always"):
        return True
    # modo ciclo: permitir solo en ventana 00/12 (cron) o si no hay dato (lo decide el caché)
    return en_ventana_cron()


@contextmanager
def ciclo_sync_context(ciclo: str | None = None) -> Iterator[str]:
    """Marca la corrida ETL 00/12: fuerza descarga fresca de todas las variables."""
    global _FORCE_FETCH
    prev = _FORCE_FETCH
    _FORCE_FETCH = True
    label = ciclo or ciclo_utc_vigente()
    try:
        yield label
    finally:
        _FORCE_FETCH = prev


def ciclo_info(now: datetime | None = None) -> dict:
    n = _now_utc(now)
    return {
        "modo": fetch_mode(),
        "ciclo_utc": ciclo_utc_vigente(n),
        "proximo_ciclo_utc": proximo_ciclo_utc(n).strftime("%Y-%m-%dT%H"),
        "segundos_hasta_proximo": segundos_hasta_proximo_ciclo(n),
        "en_ventana_cron": en_ventana_cron(n),
        "force_fetch": force_fetch_activo(),
        "ciclos": list(CICLOS_UTC),
    }
