#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests E10 — health sitios, métricas, contract OpenAPI smoke."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths

metgo_paths.setup_paths("05_api_rest")
_apis = metgo_paths.MODULE_PATHS["05_api_rest"]
if str(_apis) not in sys.path:
    sys.path.insert(0, str(_apis))


@pytest.fixture
def client():
    os.environ["METGO_API_AUTH_REQUIRED"] = "1"
    os.environ.setdefault("METGO_PASSWORD_ADMIN", "admin123")
    os.environ["METGO_METRICS_PUBLIC"] = "1"
    from api_rest.app import create_app

    return create_app().test_client()


def test_metrics_public(client):
    r = client.get("/api/metrics")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "metgo_uptime_seconds" in body
    assert "metgo_http_request_duration_ms" in body


def test_metrics_json(client):
    r = client.get("/api/metrics?format=json")
    assert r.status_code == 200
    assert "uptime_s" in r.get_json()


def test_mqtt_tls_config():
    from api_rest.integracion import mqtt_bridge

    os.environ["METGO_MQTT_TLS"] = "1"
    cfg = mqtt_bridge.mqtt_config()
    assert cfg["tls"] is True
    assert cfg["port"] == 8883
    del os.environ["METGO_MQTT_TLS"]


def test_health_fase10(client):
    assert client.get("/api/health").get_json().get("fase") == "10"


def test_health_sitios(client):
    r = client.get("/api/health/sitios")
    assert r.status_code == 200
    body = r.get_json()
    assert body.get("fase") == "E10"
    assert "sitios" in body
    slugs = {s["sitio"] for s in body["sitios"]}
    assert "quillota" in slugs and "copiapo" in slugs
    assert "demo" not in slugs


def test_health_sitio_copiapo(client):
    r = client.get("/api/health/sitios?sitio=copiapo")
    assert r.status_code == 200
    body = r.get_json()
    assert body["sitio"] == "copiapo"
    assert "aire" in body.get("frescura", {})


def test_openapi_contract_paths_exist():
    """Contract smoke: paths críticos del OpenAPI están en el archivo."""
    path = ROOT / "backend" / "05_APIs_Externas" / "api_rest" / "openapi.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    paths = doc.get("paths") or {}
    for required in (
        "/api/health",
        "/api/health/sitios",
        "/api/metrics",
        "/api/auth/login",
        "/api/public/sitios",
        "/api/me/preferencias",
    ):
        assert required in paths, f"Falta path OpenAPI: {required}"


def test_openapi_json_servido(client):
    r = client.get("/api/openapi.json")
    assert r.status_code == 200
    paths = (r.get_json() or {}).get("paths") or {}
    assert "/api/health/sitios" in paths or "/api/health" in paths
