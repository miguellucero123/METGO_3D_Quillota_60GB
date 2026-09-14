#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Flujo Izaje Mar (ventora_mar): validate → register → verify → login → access → puerto.

Pasos cubiertos (API, sin navegador):
  1. security-config / turnstile wiring (test local)
  2. validate-registro (producto ventora_mar + puerto)
  3. register-v2 (Turnstile mock OK)
  4. login bloqueado sin verificar email
  5. verify-email
  6. login OK
  7. /auth/access tab=panel
  8. /public/spati/{puerto}/puerto/pronostico (Open-Meteo mock)
"""

from __future__ import annotations

import os

import pytest

os.environ["METGO_IDENTITY_STORE"] = "memory"
os.environ["METGO_JWT_SECRET"] = "test-secret-izaje-mar-flow-min-32-bytes!"
os.environ["METGO_API_AUTH_REQUIRED"] = "1"
os.environ["METGO_SCRYPT_N"] = "1024"
os.environ["METGO_EMAIL_DEV"] = "1"
os.environ["METGO_RATE_LIMIT_ENABLED"] = "0"
os.environ["METGO_SPATI_ALLOW_SYNTHETIC"] = "1"
# Turnstile: NO setear aquí a nivel módulo — otros tests (p.ej. security_hardening)
# hacen pop() en import y pisan el entorno global en CI.

from api_rest.identity import identity_store
from api_rest.identity.session_store import reset_for_tests as reset_sessions


@pytest.fixture(autouse=True)
def _env_turnstile_y_reset(monkeypatch):
    monkeypatch.setenv("METGO_TURNSTILE_SECRET", "test-turnstile-secret")
    monkeypatch.setenv("METGO_TURNSTILE_SITE_KEY", "0x4AAAAAAE0mVDhC6afUBTSv")
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


def _payload(**over):
    body = {
        "email": "ops.izaje.mar.flow@example.com",
        "password": "SeguraPuerto1",
        "password_confirm": "SeguraPuerto1",
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
    body.update(over)
    return body


def test_paso1_security_config_turnstile(client):
    r = client.get("/api/public/security-config")
    assert r.status_code == 200
    ts = r.get_json()["turnstile"]
    assert ts["enabled"] is True
    assert ts["required"] is True
    assert ts["site_key"]


def test_paso2_validate_registro_izaje_mar(client):
    r = client.post("/api/auth/validate-registro", json=_payload())
    assert r.status_code == 200
    assert r.get_json()["ok"] is True


def test_pasos_3_a_8_flujo_completo(client, monkeypatch):
    from api_rest.spati import puerto_pronostico_service as pps

    monkeypatch.setattr(
        pps,
        "generar_pronostico_puerto",
        lambda sitio_id, hours=72: {
            "site_id": sitio_id,
            "fuente": "openmeteo_marine",
            "hourly_states": [
                {
                    "timestamp": "2026-09-14T12:00:00Z",
                    "wind_surface_kmh": 18.0,
                    "wave_params": {"Hs": 1.1, "Tp": 11.0},
                }
            ],
            "alerts": [],
            "forecast_period_hours": 1,
        },
    )

    body = _payload()

    # 3) register
    reg = client.post("/api/auth/register-v2", json=body)
    assert reg.status_code == 201, reg.get_json()
    data = reg.get_json()
    assert data.get("verify_token")
    assert data.get("email_verification_required") is True
    url = data.get("verify_url") or ""
    assert "ventora-izaje-mar.pages.dev" in url
    assert "/p/ventanas_muelle/verificar" in url or "/verificar" in url

    # 4) login sin verificar
    denied = client.post(
        "/api/auth/login",
        json={
            "username": body["email"],
            "password": body["password"],
            "sitio": "spati",
            "faena": "ventanas_muelle",
        },
    )
    assert denied.status_code == 403
    assert denied.get_json().get("code") == "email_not_verified"

    # 5) verify
    v = client.get(f"/api/auth/verify-email?token={data['verify_token']}")
    assert v.status_code == 200

    # 6) login OK
    login = client.post(
        "/api/auth/login",
        json={
            "username": body["email"],
            "password": body["password"],
            "sitio": "spati",
            "faena": "ventanas_muelle",
        },
    )
    assert login.status_code == 200, login.get_json()
    token = login.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 7) access panel
    acc = client.get(
        "/api/auth/access?sitio=spati&faena=ventanas_muelle&tab=panel",
        headers=headers,
    )
    assert acc.status_code == 200
    assert acc.get_json().get("tab_allowed") is True

    # 8) pronóstico puerto
    puerto = client.get("/api/public/spati/ventanas_muelle/puerto/pronostico")
    assert puerto.status_code == 200
    pj = puerto.get_json()
    assert pj.get("fuente") == "openmeteo_marine"
    assert pj.get("hourly_states")


def test_register_sin_turnstile_token_rechazado(client, monkeypatch):
    """Con Turnstile required, sin token → 400 captcha_failed."""
    from api_rest import security_hardening as sec

    # Restaurar verify real (fixture lo mockeó a OK); forzar fallo si vacío
    def realish(token=None, remoteip=None):
        if not (token or "").strip():
            return False, "Captcha requerido"
        return True, "ok"

    monkeypatch.setattr(sec, "verify_turnstile", realish)
    body = _payload()
    body.pop("turnstile_token", None)
    r = client.post("/api/auth/register-v2", json=body)
    assert r.status_code == 400
    assert r.get_json().get("code") == "captcha_failed"
