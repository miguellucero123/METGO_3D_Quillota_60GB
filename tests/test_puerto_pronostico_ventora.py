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
    from api_rest.spati import mjo_index_service

    modelos = ["ecmwf_ifs025", "icon_seamless", "gfs_seamless"]
    # 5.0/6.0/7.0 m/s en los 3 modelos -> media = 6.0 m/s = 21.6 km/h
    vientos = {"ecmwf_ifs025": [5.0, 6.0], "icon_seamless": [6.0, 6.0], "gfs_seamless": [7.0, 6.0]}

    def fake_get_multimodelo(url, params=None, timeout=None):
        class R:
            status_code = 200

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
                hourly = {"time": ["2026-09-14T00:00", "2026-09-14T01:00"]}
                for m in modelos:
                    hourly[f"wind_speed_10m_{m}"] = vientos[m]
                    hourly[f"wind_direction_10m_{m}"] = [210, 215]
                    hourly[f"wind_gusts_10m_{m}"] = [7.0, 8.0]
                    hourly[f"visibility_{m}"] = [10000, 9000]
                    hourly[f"temperature_2m_{m}"] = [16.0, 15.5]
                    hourly[f"precipitation_{m}"] = [0.0, 0.5]
                return {"hourly": hourly}

        return R()

    monkeypatch.setattr(pps.requests, "get", fake_get_multimodelo)
    monkeypatch.setattr(
        mjo_index_service, "obtener_indice_mjo_real", lambda **kw: {"disponible": False}
    )
    monkeypatch.setattr(pps, "obtener_indice_mjo_real", lambda **kw: {"disponible": False})

    out = pps.generar_pronostico_puerto("iqq", hours=24)
    assert "error" not in out
    assert out["fuente"] == "openmeteo_multimodelo_marine"
    assert out["site_id"] == "iqq"
    assert out["modelos_utilizados"] == modelos
    assert len(out["hourly_states"]) == 2
    # media de 5,6,7 m/s = 6 m/s = 21.6 km/h
    assert out["hourly_states"][0]["wind_surface_kmh"] == pytest.approx(21.6, abs=0.1)
    assert out["hourly_states"][0]["wave_params"]["Hs"] == 1.2
    assert out["hourly_states"][0]["precipitacion"]["precipitacion_base_mm"] == 0.0
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

    def fake_gen(sitio_id, hours=72, longitud_cable_m=None):
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
