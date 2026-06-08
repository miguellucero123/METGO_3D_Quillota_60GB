#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests comparación GFS/ECMWF OpenMeteo."""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
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

from api_rest.meteo_modelos_core import _concordancia, comparacion_gfs_ecmwf


def _mock_response(daily_time, daily_vals):
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = {
        "daily": {
            "time": daily_time,
            "temperature_2m_max": daily_vals,
        }
    }
    return mock


@patch("api_rest.meteo_modelos_core.requests.get")
def test_comparacion_gfs_ecmwf_openmeteo(mock_get):
    hoy = datetime.now(ZoneInfo("America/Santiago")).date()
    fechas = [(hoy + timedelta(days=i)).isoformat() for i in range(3)]
    mock_get.side_effect = [
        _mock_response(fechas, [22.0, 23.5, 21.0]),
        _mock_response(fechas, [21.5, 24.0, 20.5]),
    ]
    res = comparacion_gfs_ecmwf("quillota", "temperatura", 7)
    assert res["fuente"] == "openmeteo_multi_modelo"
    assert len(res["comparacion"]) == 3
    assert res["comparacion"][0]["gfs"] == 22.0
    assert res["comparacion"][0]["ecmwf"] == 21.5
    assert res["comparacion"][0]["concordancia"] in ("alta", "media", "baja")


def test_concordancia_umbrales():
    assert _concordancia(1.0, "temperatura") == "alta"
    assert _concordancia(5.0, "temperatura") == "baja"


def test_variable_invalida():
    with pytest.raises(ValueError):
        comparacion_gfs_ecmwf("quillota", "variable_inexistente")
