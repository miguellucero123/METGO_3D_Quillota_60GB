#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilidades comunes dashboards Streamlit meteorológicos (8502, 8506, …)."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def hoy_chile() -> str:
    return datetime.now(ZoneInfo("America/Santiago")).date().isoformat()


def dia_iso(val) -> str:
    return str(val or "")[:10]


def filtrar_historico_hasta_hoy(filas: list[dict]) -> list[dict]:
    hoy = hoy_chile()
    return [r for r in filas if dia_iso(r.get("fecha")) and dia_iso(r.get("fecha")) <= hoy]


def filtrar_pronostico_desde_hoy(filas: list[dict]) -> list[dict]:
    hoy = hoy_chile()
    return [r for r in filas if dia_iso(r.get("fecha")) and dia_iso(r.get("fecha")) >= hoy]


def nubosidad_estimada(humedad: float) -> float:
    """Estimación determinística (OpenMeteo diario no trae nubosidad en MVP)."""
    return round(min(100.0, max(0.0, humedad * 0.9)), 1)


def probabilidad_niebla(humedad: float) -> float:
    if humedad <= 75:
        return 0.0
    return round(min(100.0, max(0.0, (humedad - 75) * 2.5)), 1)
