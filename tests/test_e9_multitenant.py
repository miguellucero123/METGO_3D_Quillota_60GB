#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E9 multi-tenant: claim sitio, aislamiento y preferencias."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths


def _setup():
    metgo_paths.setup_paths("01_meteo", "05_api_rest")
    apis = metgo_paths.MODULE_PATHS["05_api_rest"]
    if str(apis) not in sys.path:
        sys.path.insert(0, str(apis))


@pytest.fixture
def client():
    _setup()
    os.environ["METGO_API_AUTH_REQUIRED"] = "1"
    os.environ.setdefault("METGO_PASSWORD_ADMIN", "admin123")
    os.environ.setdefault("METGO_PASSWORD_METGO", "metgo2025")
    from api_rest.app import create_app

    return create_app().test_client()


def test_sitio_de_usuario_membresia():
    _setup()
    from api_rest.sitios_auth import sitio_de_usuario, sitio_permitido, resolver_sitio_login

    assert sitio_de_usuario("admin") is None
    assert sitio_de_usuario("metgo") == "quillota"
    assert sitio_permitido(None, "copiapo") is True
    assert sitio_permitido("quillota", "copiapo") is False
    assert sitio_permitido("quillota", "quillota") is True

    sitio, err = resolver_sitio_login("metgo", "mantos_blancos")
    assert err is not None and sitio is None

    sitio, err = resolver_sitio_login("metgo", None)
    assert err is None and sitio == "quillota"

    sitio, err = resolver_sitio_login("admin", "copiapo")
    assert err is None and sitio == "copiapo"


def test_login_incluye_sitio(client):
    r = client.post("/api/auth/login", json={"username": "metgo", "password": "metgo2025"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["user"]["sitio"] == "quillota"
    assert body["user"]["tenant"] == "quillota"

    me = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me.status_code == 200
    assert me.get_json()["sitio"] == "quillota"


def test_login_sitio_no_autorizado(client):
    r = client.post(
        "/api/auth/login",
        json={"username": "metgo", "password": "metgo2025", "sitio": "mantos_blancos"},
    )
    assert r.status_code == 403


def test_admin_puede_scoped_sitio(client):
    r = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123", "sitio": "copiapo"},
    )
    assert r.status_code == 200
    assert r.get_json()["user"]["sitio"] == "copiapo"


def test_public_sitios_auth(client):
    r = client.get("/api/public/sitios-auth")
    assert r.status_code == 200
    slugs = {s["slug"] for s in r.get_json()}
    assert "quillota" in slugs and "copiapo" in slugs and "mantos_blancos" in slugs
    assert "demo" not in slugs


def test_preferencias_requiere_auth(client):
    assert client.get("/api/me/preferencias").status_code == 401
    login = client.post("/api/auth/login", json={"username": "metgo", "password": "metgo2025"})
    token = login.get_json()["access_token"]
    r = client.get(
        "/api/me/preferencias?sitio=quillota",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.get_json()
    assert body["sitio"] == "quillota"
    assert "prefs" in body and "favorites" in body

    # Otro sitio → 403
    r403 = client.get(
        "/api/me/preferencias?sitio=mantos_blancos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r403.status_code == 403


def test_estaciones_filtradas_por_sitio(client):
    login = client.post("/api/auth/login", json={"username": "metgo", "password": "metgo2025"})
    token = login.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sitios = client.get("/api/sitios", headers=headers)
    assert sitios.status_code == 200
    slugs = {s["slug"] for s in sitios.get_json()}
    assert slugs == {"quillota"}

    est = client.get("/api/estaciones?sitio=copiapo", headers=headers)
    assert est.status_code == 403

    est_ok = client.get("/api/estaciones", headers=headers)
    assert est_ok.status_code == 200
    ids = {e["id"] for e in est_ok.get_json()}
    assert "quillota" in ids
    assert "copiapo_centro" not in ids


def test_meteo_estacion_otro_sitio_403(client):
    login = client.post("/api/auth/login", json={"username": "metgo", "password": "metgo2025"})
    token = login.get_json()["access_token"]
    r = client.get(
        "/api/meteo/base_torres",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_aire_jwt_estacion_otro_sitio_403(client):
    login = client.post("/api/auth/login", json={"username": "metgo", "password": "metgo2025"})
    token = login.get_json()["access_token"]
    r = client.get(
        "/api/aire/copiapo_centro",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_login_sitio_copiapo(client):
    r = client.post(
        "/api/auth/login",
        json={"username": "copiapo", "password": "copiapo123", "sitio": "copiapo"},
    )
    assert r.status_code == 200
    assert r.get_json()["user"]["sitio"] == "copiapo"

    blocked = client.post(
        "/api/auth/login",
        json={"username": "copiapo", "password": "copiapo123", "sitio": "quillota"},
    )
    assert blocked.status_code == 403


def test_login_sitio_mantos(client):
    r = client.post(
        "/api/auth/login",
        json={"username": "mantos", "password": "mantos123", "sitio": "mantos_blancos"},
    )
    assert r.status_code == 200
    assert r.get_json()["user"]["sitio"] == "mantos_blancos"

    # No puede pedir Quillota
    blocked = client.post(
        "/api/auth/login",
        json={"username": "mantos", "password": "mantos123", "sitio": "quillota"},
    )
    assert blocked.status_code == 403
