#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests precipitación calibrada, heladas y alertas."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths

metgo_paths.setup_paths("01_meteo", "05_api_rest")
_apis = metgo_paths.MODULE_PATHS["05_api_rest"]
if str(_apis) not in sys.path:
    sys.path.insert(0, str(_apis))


@pytest.fixture
def client(tmp_path, monkeypatch):
    os.environ["METGO_API_AUTH_REQUIRED"] = "1"
    os.environ.setdefault("METGO_PASSWORD_ADMIN", "admin123")
    cfg = tmp_path / "alertas_config.json"
    cfg.write_text("[]", encoding="utf-8")
    monkeypatch.setattr("api_rest.alertas_config._store_path", lambda: cfg)
    from api_rest.app import create_app

    return create_app().test_client()


def _token(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    return r.get_json()["access_token"]


MOCK_PRON = [
    {
        "estacion_id": "quillota",
        "fecha": "2026-06-10",
        "precipitacion": 28.0,
        "temperatura_min": 3.0,
        "probabilidad_lluvia": 85,
    },
    {
        "estacion_id": "quillota",
        "fecha": "2026-06-11",
        "precipitacion": 5.0,
        "temperatura_min": 6.0,
        "probabilidad_lluvia": 40,
    },
]

MOCK_CAL = {
    "estacion_id": "quillota",
    "fechas": ["2026-06-10", "2026-06-11"],
    "precipitacion_calibrada": [25.0, 4.5],
    "precipitacion_p10": [18.0, 3.0],
    "precipitacion_p90": [32.0, 6.0],
    "datos": {"precipitacion": [28.0, 5.0], "pop": [85, 40]},
    "metadatos": {"calibrado": True, "tipo_dato": "pronostico_calibrado"},
    "alerta_lluvia_fuerte": True,
}


def test_pronostico_precipitacion_sin_fechas_futuras_en_historico():
    from api_rest import services

    hist = services.historico_meteo("quillota", 30)
    if hist:
        hoy = services._hoy_chile()
        for row in hist:
            assert str(row["fecha"])[:10] <= hoy


def test_calibracion_bias_aplicada():
    from api_rest.precipitacion_core import pronostico_precipitacion_calibrado

    with patch("api_rest.services.pronostico_meteo", return_value=MOCK_PRON):
        with patch("api_rest.services.historico_meteo", return_value=[]):
            out = pronostico_precipitacion_calibrado(
                "quillota",
                2,
                lambda e, d: MOCK_PRON,
                lambda e, d: [],
                lambda e: "Quillota",
            )
    assert out is not None
    assert out["metadatos"]["calibrado"] is True
    assert len(out["precipitacion_calibrada"]) == 2
    assert all(p >= 0 for p in out["precipitacion_calibrada"])


def test_alerta_lluvia_fuerte_activada():
    from api_rest.precipitacion_core import generar_alertas_precipitacion

    alertas = generar_alertas_precipitacion(
        "quillota",
        lambda eid, d=7: MOCK_CAL,
        "palto",
    )
    assert len(alertas) >= 1
    assert any(a["nivel_severidad"] == "rojo" for a in alertas)


def test_pronostico_heladas_estructura():
    from api_rest import services

    with patch("api_rest.services.pronostico_meteo", return_value=MOCK_PRON):
        data = services.pronostico_heladas("quillota", 7)
    assert "dias" in data
    assert data["tipo_dato"] == "pronostico"
    assert any(d["severidad"] in ("critico", "alto", "moderado", "bajo") for d in data["dias"])


def test_endpoint_precipitacion_calibrada(client):
    tok = _token(client)
    h = {"Authorization": f"Bearer {tok}"}
    with patch("api_rest.services.pronostico_precipitacion_calibrado", return_value=MOCK_CAL):
        r = client.get("/api/meteo/quillota/precipitacion-calibrada?dias=2", headers=h)
    assert r.status_code == 200
    body = r.get_json()
    assert body["precipitacion_calibrada"][0] == 25.0


def test_endpoint_alertas_precipitacion(client):
    tok = _token(client)
    h = {"Authorization": f"Bearer {tok}"}
    with patch(
        "api_rest.services.generar_alertas_precipitacion",
        return_value=[{"id": 1, "nivel_severidad": "rojo", "cultivo": "palto"}],
    ):
        r = client.get("/api/precip/quillota/alertas", headers=h)
    assert r.status_code == 200
    assert r.get_json()["resumen"]["rojas"] == 1


def test_endpoint_heladas(client):
    tok = _token(client)
    h = {"Authorization": f"Bearer {tok}"}
    with patch(
        "api_rest.services.pronostico_heladas",
        return_value={"estacion_id": "quillota", "dias": [], "alerta_activa": False},
    ):
        r = client.get("/api/meteo/quillota/heladas", headers=h)
    assert r.status_code == 200
