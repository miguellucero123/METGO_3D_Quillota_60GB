#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests P1: pronóstico portuario VENTORA (Open-Meteo + fallback)."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("METGO_IDENTITY_STORE", "memory")
os.environ.setdefault("METGO_JWT_SECRET", "test-secret-puerto-p1-min-32-bytes!!!!")
os.environ.setdefault("METGO_SPATI_ALLOW_SYNTHETIC", "1")

from api_rest.spati import puerto_pronostico_service as pps


def test_normalizar_y_get_puerto():
    assert pps.normalizar_puerto_id("IQQ") == "iqq"
    assert pps.normalizar_puerto_id("puerto_ventanas") == "ventanas_muelle"
    p = pps.get_puerto("ventanas_muelle")
    assert p is not None
    assert p["lat"] == pytest.approx(-32.748, abs=1e-3)
    assert pps.get_puerto("mina_inventada_xyz") is None


def test_pronostico_openmeteo_mock(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        class R:
            def raise_for_status(self):
                return None

            def json(self):
                if "marine" in url:
                    return {
                        "hourly": {
                            "time": ["2026-09-14T00:00", "2026-09-14T01:00"],
                            "wave_height": [1.2, 1.4],
                            "wave_period": [11.0, 12.0],
                            "wave_direction": [220, 225],
                        }
                    }
                return {
                    "hourly": {
                        "time": ["2026-09-14T00:00", "2026-09-14T01:00"],
                        "wind_speed_10m": [5.0, 6.0],
                        "wind_direction_10m": [210, 215],
                        "wind_gusts_10m": [7.0, 8.0],
                        "visibility": [10000, 9000],
                        "temperature_2m": [16.0, 15.5],
                    }
                }

        return R()

    monkeypatch.setattr(pps.requests, "get", fake_get)
    out = pps.generar_pronostico_puerto("iqq", hours=24)
    assert "error" not in out
    assert out["fuente"] == "openmeteo_marine"
    assert out["site_id"] == "iqq"
    assert len(out["hourly_states"]) == 2
    assert out["hourly_states"][0]["wind_surface_kmh"] == pytest.approx(18.0, abs=0.1)
    assert out["hourly_states"][0]["wave_params"]["Hs"] == 1.2
    assert out["config"]["lat"] == pytest.approx(-20.2058, abs=1e-3)


def test_pronostico_fallback_synthetic(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("openmeteo down")

    monkeypatch.setattr(pps, "_from_openmeteo", boom)
    out = pps.generar_pronostico_puerto("ventanas_muelle", hours=24)
    assert "error" not in out
    assert out["fuente"] == "synthetic_local"
    assert out["config"]["lat"] == pytest.approx(-32.748, abs=1e-3)
    assert len(out["hourly_states"]) >= 1
    assert out.get("nwp_aviso")


def test_puerto_desconocido():
    out = pps.generar_pronostico_puerto("no_existe_xyz")
    assert out["error"] == "sitio_no_encontrado"


def test_http_route_404(monkeypatch):
    from api_rest.app import create_app

    client = create_app().test_client()
    r = client.get("/api/public/spati/puerto_falso_xyz/puerto/pronostico")
    assert r.status_code == 404


def test_http_route_ok_mocked(monkeypatch):
    from api_rest.app import create_app

    def fake_gen(sitio_id, hours=72):
        return {
            "site_id": sitio_id,
            "fuente": "openmeteo",
            "hourly_states": [{"timestamp": "2026-09-14T00:00:00Z", "wind_surface_kmh": 12}],
            "alerts": [],
            "forecast_period_hours": 1,
        }

    monkeypatch.setattr(pps, "generar_pronostico_puerto", fake_gen)
    # Re-bind route import path used inside view
    import api_rest.spati.puerto_pronostico_service as mod

    monkeypatch.setattr(mod, "generar_pronostico_puerto", fake_gen)
    client = create_app().test_client()
    r = client.get("/api/public/spati/ventanas_muelle/puerto/pronostico")
    assert r.status_code == 200
    assert r.get_json()["fuente"] == "openmeteo"
