#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regresión: histórico no incluye fechas posteriores a hoy Chile."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths

metgo_paths.setup_paths("01_meteo", "05_api_rest")
_apis = metgo_paths.MODULE_PATHS["05_api_rest"]
if str(_apis) not in sys.path:
    sys.path.insert(0, str(_apis))

from api_rest import services


def test_dedupe_historico_excluye_fechas_futuras():
    hoy_str = services._hoy_chile()
    manana = (date.fromisoformat(hoy_str) + timedelta(days=1)).isoformat()
    ayer = (date.fromisoformat(hoy_str) - timedelta(days=1)).isoformat()
    filas = [
        {"fecha": ayer, "temperatura_max": 20, "fuente": "openmeteo_archive"},
        {"fecha": hoy_str, "temperatura_max": 21, "fuente": "openmeteo_archive"},
        {"fecha": manana, "temperatura_max": 99, "fuente": "openmeteo_archive"},
        {
            "fecha": (date.fromisoformat(hoy_str) + timedelta(days=5)).isoformat(),
            "temperatura_max": 88,
        },
    ]
    out = services._dedupe_historico_por_dia(filas, dias=30)
    fechas = [r["fecha"] for r in out]
    assert manana not in fechas
    assert all(f <= hoy_str for f in fechas)
    assert hoy_str in fechas
    assert ayer in fechas


def test_dedupe_historico_prefiere_real_sobre_sintetico():
    hoy_str = services._hoy_chile()
    filas = [
        {"fecha": hoy_str, "temperatura_max": 10, "fuente": "sintetico"},
        {"fecha": hoy_str, "temperatura_max": 22, "fuente": "openmeteo_archive"},
    ]
    out = services._dedupe_historico_por_dia(filas, dias=1)
    assert len(out) == 1
    assert out[0]["temperatura_max"] == 22
    assert "sintetico" not in str(out[0].get("fuente", "")).lower()
