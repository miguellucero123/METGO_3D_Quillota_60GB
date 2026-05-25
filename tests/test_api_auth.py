#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests API: health, login JWT, auth en meteo."""

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
def client():
    os.environ["METGO_API_AUTH_REQUIRED"] = "1"
    os.environ.setdefault("METGO_PASSWORD_ADMIN", "admin123")
    from api_rest.app import create_app

    return create_app().test_client()


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.get_json()
    assert body.get("status") in ("ok", "degraded")
    assert "version" in body
    assert "uptime_s" in body


def test_login_demo(client):
    r = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("access_token") or data.get("token")


def test_meteo_sin_auth(client):
    r = client.get("/api/meteo/quillota")
    assert r.status_code == 401


def test_openapi_and_docs(client):
    assert client.get("/api/openapi.json").status_code == 200
    assert client.get("/api/docs").status_code == 200
