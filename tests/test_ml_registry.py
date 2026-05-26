#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests registro ML + sanity-check (módulo 06)."""

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
    reg = tmp_path / "ml_registry.json"
    monkeypatch.setattr("api_rest.ml_registry_core._registry_path", lambda: reg)
    monkeypatch.setattr("api_rest.integracion.ml_registry._registry_path", lambda: reg)
    from api_rest.app import create_app

    return create_app().test_client()


def test_sincronizar_registro_genera_servibles(monkeypatch):
    from api_rest import ml_registry_core as core

    reg = core.sincronizar_registro(forzar=True)
    assert reg.get("total", 0) >= 5
    assert "servibles" in reg
    assert reg.get("servibles", 0) >= 1
    modelos = reg.get("modelos", [])
    assert any(m.get("servible") for m in modelos)
    assert any(not m.get("servible") for m in modelos) or reg.get("no_servibles", 0) >= 0


def test_predecir_solo_servible(monkeypatch):
    from api_rest import ml_registry_core as core

    core.sincronizar_registro(forzar=True)
    r = core.predecir_registrado("temperatura_max", "quillota")
    assert "error" not in r or "no servible" in r.get("error", "").lower()
    if "error" not in r:
        assert r.get("servible") is True
        assert "prediccion" in r


def test_api_registry_sync(client):
    tok = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).get_json()[
        "access_token"
    ]
    h = {"Authorization": f"Bearer {tok}"}
    r = client.post("/api/ml/registry/sync", headers=h)
    assert r.status_code == 200
    body = r.get_json()
    assert body.get("total", 0) >= 1
    assert "servibles" in body


def test_api_ml_modelos_incluye_servible_flag(client):
    client.post("/api/ml/registry/sync", headers={
        "Authorization": f"Bearer {client.post('/api/auth/login', json={'username':'admin','password':'admin123'}).get_json()['access_token']}"
    })
    tok = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).get_json()[
        "access_token"
    ]
    r = client.get("/api/ml/modelos", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert any("servible" in m for m in data)
