#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests Fase 7: MQTT bridge y cola ML."""

from __future__ import annotations

import json
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
    iot = tmp_path / "iot_lecturas.json"
    iot.write_text("[]", encoding="utf-8")
    queue = tmp_path / "ml_training_queue.json"
    queue.write_text(json.dumps({"jobs": [], "historial": []}), encoding="utf-8")
    monkeypatch.setattr("api_rest.iot_services._store_path", lambda: iot)
    monkeypatch.setattr("api_rest.integracion.ml_training_queue._queue_path", lambda: queue)
    from api_rest.app import create_app

    return create_app().test_client()


def _token(client, user: str = "admin", pwd: str = "admin123") -> str:
    r = client.post("/api/auth/login", json={"username": user, "password": pwd})
    assert r.status_code == 200
    return r.get_json()["access_token"]


def test_mqtt_status_public(client):
    r = client.get("/api/iot/mqtt/status")
    assert r.status_code == 200
    body = r.get_json()
    assert "estado" in body
    assert body.get("modo_mvp")


def test_mqtt_ingestar(client):
    tok = _token(client)
    h = {"Authorization": f"Bearer {tok}"}
    r = client.post(
        "/api/iot/mqtt/ingestar",
        headers=h,
        json={"topic": "metgo/quillota/temperatura", "payload": {"valor": 21.3}},
    )
    assert r.status_code == 201
    assert r.get_json().get("ok") is True
    lecturas = client.get("/api/iot/lecturas?estacion=quillota", headers=h)
    assert lecturas.status_code == 200
    assert any(x.get("fuente") == "mqtt" for x in lecturas.get_json())


def test_ml_train_queue(client):
    tok = _token(client)
    h = {"Authorization": f"Bearer {tok}"}
    r = client.post("/api/ml/train/queue", headers=h, json={"variables": ["temperatura_max"]})
    assert r.status_code == 201
    st = client.get("/api/ml/train/status", headers=h)
    assert st.status_code == 200
    assert st.get_json().get("pendientes", 0) >= 1


def test_health_fase7(client):
    r = client.get("/api/health")
    body = r.get_json()
    assert body.get("fase") in ("7", "8", "9", "10")
    assert "mqtt_bridge" in body.get("features", [])
