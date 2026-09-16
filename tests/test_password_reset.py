#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recuperación de contraseña: solicitar-reset -> resetear-password -> login."""

from __future__ import annotations

import os

import pytest

os.environ["METGO_IDENTITY_STORE"] = "memory"
os.environ["METGO_JWT_SECRET"] = "test-secret-password-reset-min-32-bytes!"
os.environ["METGO_API_AUTH_REQUIRED"] = "1"
os.environ["METGO_SCRYPT_N"] = "1024"
os.environ["METGO_EMAIL_DEV"] = "1"
os.environ["METGO_RATE_LIMIT_ENABLED"] = "0"

from api_rest.identity import identity_store
from api_rest.identity.session_store import reset_for_tests as reset_sessions


@pytest.fixture(autouse=True)
def _env_y_reset(monkeypatch):
    monkeypatch.setenv("METGO_TURNSTILE_SECRET", "test-turnstile-secret")
    monkeypatch.setenv("METGO_TURNSTILE_REQUIRED", "1")
    monkeypatch.setenv("METGO_IDENTITY_STORE", "memory")
    monkeypatch.setenv("METGO_EMAIL_DEV", "1")
    monkeypatch.setenv("METGO_RATE_LIMIT_ENABLED", "0")
    identity_store.reset_memory()
    reset_sessions()
    yield
    identity_store.reset_memory()
    reset_sessions()


@pytest.fixture
def client(monkeypatch):
    from api_rest import security_hardening as sec

    monkeypatch.setattr(sec, "verify_turnstile", lambda *a, **k: (True, "test_ok"))
    from api_rest.app import create_app

    return create_app().test_client()


def _registrar_y_verificar(client, email="reset.flow@example.com", password="ClaveVieja1"):
    body = {
        "email": email,
        "password": password,
        "password_confirm": password,
        "nombres": "Camila",
        "apellidos": "Rojas",
        "telefono": "+56987654321",
        "razon_social": "Terminal Demo SpA",
        "sitio": "spati",
        "producto": "ventora_mar",
        "spa": "ventora_mar",
        "faena": "ventanas_muelle",
        "turnstile_token": "test-token",
        "consentimientos": {
            "almacenamiento_datos": True,
            "tos": True,
            "privacy": True,
            "veracidad": True,
        },
    }
    reg = client.post("/api/auth/register-v2", json=body)
    assert reg.status_code == 201, reg.get_json()
    token = reg.get_json()["verify_token"]
    v = client.get(f"/api/auth/verify-email?token={token}")
    assert v.status_code == 200, v.get_json()
    return email


def test_solicitar_reset_email_inexistente_responde_generico(client):
    r = client.post("/api/auth/solicitar-reset", json={"email": "no.existe@example.com"})
    assert r.status_code == 200
    assert "reset_token" not in r.get_json()


def test_solicitar_reset_email_existente_devuelve_token_en_dev(client):
    email = _registrar_y_verificar(client)
    r = client.post(
        "/api/auth/solicitar-reset",
        json={"email": email, "sitio": "spati", "faena": "ventanas_muelle"},
    )
    assert r.status_code == 200
    body = r.get_json()
    assert body.get("reset_token")


def test_flujo_completo_reset_y_login(client):
    email = _registrar_y_verificar(client, password="ClaveVieja1")
    r = client.post(
        "/api/auth/solicitar-reset",
        json={"email": email, "sitio": "spati", "faena": "ventanas_muelle"},
    )
    token = r.get_json()["reset_token"]

    reset = client.post(
        "/api/auth/resetear-password", json={"token": token, "password": "ClaveNueva2"}
    )
    assert reset.status_code == 200, reset.get_json()

    # Token de un solo uso
    reuse = client.post(
        "/api/auth/resetear-password", json={"token": token, "password": "OtraClave3"}
    )
    assert reuse.status_code == 400

    login = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": "ClaveNueva2",
            "sitio": "spati",
            "faena": "ventanas_muelle",
        },
    )
    assert login.status_code == 200, login.get_json()


def test_resetear_password_corta_rechazada(client):
    email = _registrar_y_verificar(client)
    r = client.post("/api/auth/solicitar-reset", json={"email": email})
    token = r.get_json()["reset_token"]
    reset = client.post("/api/auth/resetear-password", json={"token": token, "password": "abc"})
    assert reset.status_code == 400


def test_resetear_password_token_invalido(client):
    r = client.post(
        "/api/auth/resetear-password", json={"token": "token-inventado", "password": "ClaveNueva2"}
    )
    assert r.status_code == 400
