#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pronóstico: fechas sintéticas y deduplicación por día."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths

metgo_paths.setup_paths("01_meteo", "05_api_rest")
_apis = metgo_paths.MODULE_PATHS["05_api_rest"]
if str(_apis) not in sys.path:
    sys.path.insert(0, str(_apis))

from datos_reales_openmeteo import OpenMeteoData
from api_rest import services

TZ = ZoneInfo("America/Santiago")


def test_sintetico_pronostico_desde_hoy_chile():
    om = OpenMeteoData()
    df = om._crear_datos_sinteticos("Quillota", 7, modo="pronostico")
    hoy = date.today()
    # TZ Chile; tolerancia ±1 día por medianoche UTC
    fechas = sorted({f.date() if hasattr(f, "date") else f for f in df["fecha"]})
    assert len(fechas) == 7
    assert fechas[0] >= hoy - timedelta(days=1)
    assert fechas[-1] >= hoy + timedelta(days=5)


def test_sintetico_historico_hacia_atras():
    om = OpenMeteoData()
    df = om._crear_datos_sinteticos("Quillota", 7, modo="historicos")
    hoy = date.today()
    fechas = sorted({f.date() if hasattr(f, "date") else f for f in df["fecha"]})
    assert len(fechas) == 7
    assert fechas[-1] <= hoy + timedelta(days=1)


def test_pronostico_meteo_respaldo_si_sin_datos(monkeypatch):
    """Sin DataFrame OpenMeteo, pronostico_meteo debe generar 7 días futuros."""

    monkeypatch.setattr(services, "_df_sin_prints", lambda *_a, **_k: None)

    out = services.pronostico_meteo("quillota", 7)
    assert out is None


def test_dedupe_pronostico_fallback_si_solo_pasado():
    hoy = services._hoy_chile()
    ayer = (date.fromisoformat(hoy) - timedelta(days=1)).isoformat()
    filas = [
        {"fecha": ayer, "temperatura_max": 20, "temperatura_min": 8},
        {"fecha": hoy, "temperatura_max": 21, "temperatura_min": 9},
    ]
    out = services._dedupe_pronostico_por_dia(filas, 7)
    assert len(out) >= 1
    assert out[-1]["fecha"] == hoy


@pytest.fixture
def api_client(monkeypatch):
    import os

    os.environ["METGO_API_AUTH_REQUIRED"] = "1"
    os.environ.setdefault("METGO_PASSWORD_ADMIN", "admin123")
    from api_rest.app import create_app

    return create_app().test_client()


def test_pronostico_api_con_respaldo_sintetico(api_client, monkeypatch):
    """Si OpenMeteo falla, /pronostico no debe devolver lista vacía."""

    def _falla(_estacion, tipo, dias):
        if tipo == "pronostico":
            return OpenMeteoData()._crear_datos_sinteticos(_estacion, dias, modo="pronostico")
        return None

    monkeypatch.setattr(services, "_df_sin_prints", _falla)

    r = api_client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    token = r.get_json()["access_token"]
    res = api_client.get(
        "/api/meteo/quillota/pronostico?dias=7",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 7
    hoy = services._hoy_chile()
    assert data[0]["fecha"] >= hoy
