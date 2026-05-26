#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests integración Fase 5 — grado ~100%."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths

metgo_paths.setup_paths("01_meteo", "05_api_rest", "02_agricola")
_apis = metgo_paths.MODULE_PATHS["05_api_rest"]
if str(_apis) not in sys.path:
    sys.path.insert(0, str(_apis))


@pytest.fixture
def client(tmp_path, monkeypatch):
    os.environ["METGO_API_AUTH_REQUIRED"] = "1"
    os.environ.setdefault("METGO_PASSWORD_ADMIN", "admin123")
    db = tmp_path / "meteo_historico.db"
    monkeypatch.setattr("api_rest.integracion.meteo_store._db_path", lambda: db)
    hist = tmp_path / "alertas_historial.json"
    hist.write_text("[]", encoding="utf-8")
    monkeypatch.setattr("api_rest.integracion.alertas_store._path", lambda: hist)
    from api_rest.app import create_app

    return create_app().test_client()


def _token(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    return r.get_json()["access_token"]


def test_integracion_promedio_alto(client):
    r = client.get("/api/integracion/estado")
    assert r.status_code == 200
    body = r.get_json()
    assert body.get("fase") in ("5", "7", "8", "9", "10")
    assert body.get("promedio_integracion", 0) >= 85
    assert body.get("integracion_completa") in (True, False)
    for m in body.get("modulos", []):
        assert "checks" in m
        assert m["porcentaje"] >= 0


def test_health_fase5(client):
    r = client.get("/api/health")
    assert r.get_json().get("fase") in ("5", "7", "8", "9", "10")


def test_endpoints_fase5(client):
    tok = _token(client)
    h = {"Authorization": f"Bearer {tok}"}
    assert client.get("/api/agricola/cultivos", headers=h).status_code == 200
    assert client.get("/api/agricola/quillota/riego", headers=h).status_code == 200
    assert client.get("/api/datos/fuentes", headers=h).status_code == 200
    assert client.get("/api/iot/drones", headers=h).status_code == 200
    assert client.get("/api/ml/registry", headers=h).status_code == 200
    assert client.get("/api/testing/resumen").status_code == 200
    assert client.get("/api/deploy/info").status_code == 200
    assert client.get("/api/docs/indice").status_code == 200
    assert client.get("/api/modulos/streamlit/cobertura").status_code == 200


def test_streamlit_cobertura_completa(client):
    r = client.get("/api/modulos/streamlit/cobertura")
    assert r.get_json().get("cobertura_pct", 0) >= 90


def test_capabilities_eval():
    from api_rest.integracion.capabilities import evaluar_todos

    mods = evaluar_todos()
    assert len(mods) == 12
    assert all(m["checks_total"] > 0 for m in mods)
