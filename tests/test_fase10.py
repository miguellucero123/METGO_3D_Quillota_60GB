#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests Fase 10."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

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
    assert "metgo_uptime_seconds" in r.get_data(as_text=True)


def test_mqtt_tls_config():
    from api_rest.integracion import mqtt_bridge

    os.environ["METGO_MQTT_TLS"] = "1"
    cfg = mqtt_bridge.mqtt_config()
    assert cfg["tls"] is True
    assert cfg["port"] == 8883
    del os.environ["METGO_MQTT_TLS"]


def test_health_fase10(client):
    assert client.get("/api/health").get_json().get("fase") == "10"
