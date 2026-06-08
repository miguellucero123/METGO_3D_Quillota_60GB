#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests vista agrícola: cronograma dinámico y slug vid."""

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


def _token(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    return r.get_json()["access_token"]


def test_cronograma_riego_sin_helada():
    from api_rest import services

    result = services.cronograma_riego("quillota", "palto")
    assert "cronograma" in result
    assert len(result["cronograma"]) > 0
    for dia in result["cronograma"]:
        assert "fecha" in dia
        assert "regar" in dia
        assert "mm_sugeridos" in dia
        assert "categoria" in dia
        assert dia["categoria"] in (
            "riego_normal",
            "riego_reducido",
            "lluvia_cubre",
            "suspender_riego_helada",
        )


def test_cronograma_no_usa_random():
    from api_rest import services

    r1 = services.cronograma_riego("quillota", "palto")
    r2 = services.cronograma_riego("quillota", "palto")
    assert r1["cronograma"] == r2["cronograma"]


def test_slug_vid_no_uva():
    from api_rest import services

    result_vid = services.cronograma_riego("quillota", "vid")
    assert result_vid["cultivo"] == "vid"
    with pytest.raises(ValueError):
        services.cronograma_riego("quillota", "uva")


def test_cronograma_endpoint_uva_400(client):
    token = _token(client)
    res = client.get(
        "/api/agricola/quillota/uva/cronograma",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400


def test_cronograma_endpoint_vid_200(client):
    token = _token(client)
    res = client.get(
        "/api/agricola/quillota/vid/cronograma",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["cultivo"] == "vid"
    assert len(data.get("cronograma", [])) >= 1
