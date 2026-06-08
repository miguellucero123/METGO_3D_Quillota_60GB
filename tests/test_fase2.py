#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests Fase 2: RBAC, alertas config, comparativo, métricas."""

from __future__ import annotations

import os
import sys
from pathlib import Path

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
    os.environ.setdefault("METGO_PASSWORD_AGRONOMO", "agro123")
    os.environ.setdefault("METGO_PASSWORD_LECTOR", "lec123")
    cfg = tmp_path / "alertas_config.json"
    cfg.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(
        "api_rest.alertas_config._store_path",
        lambda: cfg,
    )
    from api_rest.app import create_app

    return create_app().test_client()


def _token(client, user: str, password: str) -> str:
    r = client.post("/api/auth/login", json={"username": user, "password": password})
    assert r.status_code == 200
    return r.get_json()["access_token"]


def test_login_roles(client):
    r = client.post("/api/auth/login", json={"username": "agronomo", "password": "agro123"})
    assert r.status_code == 200
    assert r.get_json()["user"]["role"] == "agronomo"


def test_lector_no_crear_alerta(client):
    tok = _token(client, "lector", "lec123")
    r = client.post(
        "/api/alertas/config",
        json={"estacion": "quillota", "variable": "viento", "operador": ">", "umbral": 50},
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 403


def test_admin_crud_alerta(client):
    tok = _token(client, "admin", "admin123")
    r = client.post(
        "/api/alertas/config",
        json={
            "estacion": "quillota",
            "variable": "temperatura_max",
            "operador": ">",
            "umbral": 99,
        },
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 201
    aid = r.get_json()["id"]
    r2 = client.get("/api/alertas/config", headers={"Authorization": f"Bearer {tok}"})
    assert r2.status_code == 200
    assert len(r2.get_json()) >= 1
    r3 = client.delete(
        f"/api/alertas/config/{aid}",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r3.status_code == 200


def test_comparativo_y_metricas(client):
    tok = _token(client, "admin", "admin123")
    h = {"Authorization": f"Bearer {tok}"}
    assert client.get("/api/meteo/comparativo", headers=h).status_code == 200
    body = client.get("/api/metricas/globales", headers=h).get_json()
    assert "estaciones_activas" in body
    assert "referencia_fecha" in body
    assert "detalle_estaciones" in body
    if body.get("estaciones_activas", 0) > 0:
        assert len(body["detalle_estaciones"]) == body["estaciones_activas"]


def test_resumen_meteo_tipo_dato():
    from api_rest import services

    data = services.resumen_meteo("quillota")
    if data:
        assert "tipo_dato" in data
        assert data["tipo_dato"] in ("observado", "pronostico")


def test_streamlit_iniciar_requiere_operador(client):
    tok_lector = _token(client, "lector", "lec123")
    r = client.post(
        "/api/servicios/streamlit/streamlit_principal/iniciar",
        headers={"Authorization": f"Bearer {tok_lector}"},
    )
    assert r.status_code == 403
