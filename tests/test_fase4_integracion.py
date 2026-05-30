#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests integración Fase 4 — módulos 01-08."""

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


def test_integracion_estado_publico(client):
    r = client.get("/api/integracion/estado")
    assert r.status_code == 200
    body = r.get_json()
    assert body.get("promedio_integracion", 0) >= 80
    assert len(body.get("modulos", [])) >= 10


def test_health_integracion(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.get_json()
    assert body.get("fase") in ("5", "7", "8", "9", "10")
    integracion = body.get("integracion") or {}
    assert "promedio_integracion" in integracion
    assert "scripts" not in integracion
    assert "deploy" not in integracion


def test_integracion_estado_sin_rutas_deploy(client):
    r = client.get("/api/integracion/estado")
    assert r.status_code == 200
    body = r.get_json()
    deploy = body.get("deploy") or {}
    assert "scripts" not in deploy
    assert "scripts_total" in deploy
    assert "fuentes_datos" not in body
    assert "documentacion" not in body


def test_agricola_avanzado_auth(client):
    login = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    tok = login.get_json()["access_token"]
    r = client.get(
        "/api/agricola/quillota/avanzado",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 200
    body = r.get_json()
    assert "error" not in body or body.get("analisis_heladas") is not None


def test_etl_status_public(client):
    r = client.get("/api/datos/etl/status")
    assert r.status_code == 200
    body = r.get_json()
    assert "ultimo" in body
    assert "fuentes" in body


def test_meteo_store_roundtrip():
    from api_rest.integracion.meteo_store import guardar_registros, leer_registros, _db_path
    import tempfile

    td = Path(tempfile.mkdtemp())
    db = td / "t.db"

    import api_rest.integracion.meteo_store as ms

    ms._db_path = lambda: db  # type: ignore
    n = guardar_registros(
        "quillota",
        [{"fecha": "2026-01-01", "temperatura_max": 25, "temperatura_min": 10, "humedad": 50, "precipitacion": 0, "viento": 5}],
    )
    assert n == 1
    rows = leer_registros("quillota", 7)
    assert len(rows) == 1
