#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests: ensamble multi-modelo real de Open-Meteo (funciones puras, sin red)."""

from __future__ import annotations

import os

os.environ.setdefault("METGO_JWT_SECRET", "test-secret-multimodelo-min-32-bytes!!")

from api_rest.integracion import openmeteo_multimodelo as mm


def test_ensamble_variable_media_y_spread():
    hourly = {
        "time": ["t0", "t1"],
        "wind_speed_10m_ecmwf_ifs025": [10.0, 12.0],
        "wind_speed_10m_icon_seamless": [12.0, 12.0],
        "wind_speed_10m_gfs_seamless": [14.0, 12.0],
    }
    out = mm.ensamble_variable(hourly, "wind_speed_10m", ["ecmwf_ifs025", "icon_seamless", "gfs_seamless"])
    assert out["media"][0] == 12.0
    assert out["media"][1] == 12.0
    assert out["spread"][1] == 0.0
    assert out["spread"][0] > 0
    assert out["n_modelos"] == 3


def test_ensamble_variable_modelo_faltante_no_rompe():
    hourly = {"wind_speed_10m_ecmwf_ifs025": [5.0]}
    out = mm.ensamble_variable(hourly, "wind_speed_10m", ["ecmwf_ifs025", "icon_seamless"])
    assert out["media"] == [5.0]
    assert out["n_modelos"] == 1


def test_ensamble_variable_sin_datos():
    out = mm.ensamble_variable({}, "wind_speed_10m", ["ecmwf_ifs025"])
    assert out["media"] == []
    assert out["n_modelos"] == 0


def test_primer_modelo_disponible():
    hourly = {"wind_direction_10m_icon_seamless": [180, 190]}
    serie = mm.primer_modelo_disponible(hourly, "wind_direction_10m", ["ecmwf_ifs025", "icon_seamless"])
    assert serie == [180, 190]
    assert mm.primer_modelo_disponible({}, "wind_direction_10m", ["ecmwf_ifs025"]) is None


def test_fetch_multimodelo_error_http(monkeypatch):
    class FakeResp:
        status_code = 400
        text = "Invalid model"

    def fake_get(url, params=None, timeout=None):
        return FakeResp()

    monkeypatch.setattr(mm.requests, "get", fake_get)
    import pytest

    with pytest.raises(mm.MultiModeloNoDisponibleError):
        mm.fetch_multimodelo(-33.0, -71.0, hourly_vars=["wind_speed_10m"])
