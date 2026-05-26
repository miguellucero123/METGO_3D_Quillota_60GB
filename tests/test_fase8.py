#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests Fase 8: workers y entrenamiento ML ligero."""

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
    queue = tmp_path / "ml_training_queue.json"
    queue.write_text(json.dumps({"jobs": [], "historial": []}), encoding="utf-8")
    hb = tmp_path / "hb"
    hb.mkdir(exist_ok=True)
    monkeypatch.setattr("api_rest.integracion.ml_training_queue._queue_path", lambda: queue)
    monkeypatch.setattr("api_rest.integracion.workers_status._runtime_dir", lambda: hb)
    from api_rest.app import create_app

    return create_app().test_client()


def _token(client) -> str:
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    return r.get_json()["access_token"]


def test_workers_status_public(client):
    r = client.get("/api/workers/status")
    assert r.status_code == 200
    body = r.get_json()
    assert "mqtt_listener" in body
    assert "ml_training" in body


def test_ml_train_queue_modo_train(client):
    tok = _token(client)
    h = {"Authorization": f"Bearer {tok}"}
    r = client.post(
        "/api/ml/train/queue",
        headers=h,
        json={"modo": "train", "variables": ["temperatura_max"]},
    )
    assert r.status_code == 201
    assert r.get_json().get("modo") == "train"


def test_health_fase8(client):
    r = client.get("/api/health")
    body = r.get_json()
    assert body.get("fase") in ("8", "9", "10")
    assert "ml_train_runner" in body.get("features", [])


def test_ml_train_runner_unit(tmp_path, monkeypatch):
    out = tmp_path / "quillota"
    out.mkdir()
    monkeypatch.setattr("api_rest.integracion.ml_train_runner._quillota_dir", lambda: out)
    monkeypatch.setattr(
        "api_rest.integracion.ml_train_runner._filas_desde_meteo",
        lambda *a, **k: [],
    )
    from api_rest.integracion import ml_registry

    monkeypatch.setattr(ml_registry, "sincronizar_registro", lambda: {"total": 1, "servibles": 1})
    from api_rest.integracion.ml_train_runner import entrenar_quillota

    res = entrenar_quillota(variables=["temperatura_max"])
    assert res.get("ok") is True
    assert res.get("origen_datos") == "sintetico"
    assert (out / "modelo_temperatura_max.joblib").is_file()
