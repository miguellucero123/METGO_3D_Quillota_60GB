#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests Fase 3: IoT, ML, tenants, observabilidad."""

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
    os.environ.setdefault("METGO_PASSWORD_LECTOR", "lec123")
    iot = tmp_path / "iot_lecturas.json"
    iot.write_text("[]", encoding="utf-8")
    monkeypatch.setattr("api_rest.iot_services._store_path", lambda: iot)
    from api_rest.app import create_app

    return create_app().test_client()


def _token(client, user: str, pwd: str) -> str:
    r = client.post("/api/auth/login", json={"username": user, "password": pwd})
    assert r.status_code == 200
    return r.get_json()["access_token"]


def test_health_fase3(client):
    r = client.get("/api/health")
    body = r.get_json()
    assert body.get("fase") in ("3", "4", "5", "7", "8", "9", "10")
    assert "iot" in body.get("features", [])


def test_iot_lecturas(client):
    tok = _token(client, "admin", "admin123")
    h = {"Authorization": f"Bearer {tok}"}
    assert client.get("/api/iot/sensores", headers=h).status_code == 200
    r = client.get("/api/iot/lecturas", headers=h)
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_ml_modelos(client):
    tok = _token(client, "admin", "admin123")
    r = client.get("/api/ml/modelos", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_tenant_en_jwt(client):
    tok = _token(client, "lector", "lec123")
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {tok}"}).get_json()
    assert me.get("tenant") == "quillota"
    tm = client.get("/api/tenants/me", headers={"Authorization": f"Bearer {tok}"}).get_json()
    assert tm.get("tenant_id") == "quillota"
