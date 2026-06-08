#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests para el endpoint de rosa de vientos horaria."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

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


def _mock_response_hourly(time, dirs, speeds, status_code: int = 200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = {
        "hourly": {
            "time": time,
            "wind_direction_10m": dirs,
            "wind_speed_10m": speeds,
        }
    }
    return mock


@patch("datos_reales_openmeteo.requests.get")
def test_obtener_viento_horario_pronostico_filtra_dias(mock_get):
    time = [
        "2026-06-03T00:00",
        "2026-06-03T01:00",
        "2026-06-04T00:00",  # debe excluirse para dias=1
    ]
    dirs = [10, 100, 200]
    speeds = [1.0, 2.0, 3.0]
    mock_get.return_value = _mock_response_hourly(time, dirs, speeds)

    om = OpenMeteoData()
    res = om.obtener_viento_horario_pronostico("Quillota", dias=1)
    assert res["unidad"] == "m/s"
    assert res["direcciones"] == [10.0, 100.0]
    assert res["velocidades"] == [1.0, 2.0]


@patch("datos_reales_openmeteo.requests.get")
def test_obtener_viento_horario_pronostico_sin_datos(mock_get):
    mock_get.return_value = _mock_response_hourly([], [], [])
    om = OpenMeteoData()
    res = om.obtener_viento_horario_pronostico("Quillota", dias=1)
    assert res["direcciones"] == []
    assert res["velocidades"] == []


@patch("datos_reales_openmeteo.requests.get")
def test_obtener_viento_horario_pronostico_error(mock_get):
    mock_get.return_value = _mock_response_hourly([], [], [], status_code=500)
    om = OpenMeteoData()
    res = om.obtener_viento_horario_pronostico("Quillota", dias=1)
    assert res["direcciones"] == []
    assert res["velocidades"] == []

