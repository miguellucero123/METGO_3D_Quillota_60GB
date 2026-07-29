#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests identidad S1 (store memoria)."""

from __future__ import annotations

import os

import pytest

os.environ["METGO_IDENTITY_STORE"] = "memory"
os.environ["METGO_JWT_SECRET"] = "test-secret-identity-s1"
os.environ["METGO_API_AUTH_REQUIRED"] = "1"
os.environ["METGO_SCRYPT_N"] = "1024"
os.environ["METGO_EMAIL_DEV"] = "1"

from api_rest.identity import identity_store, pii_crypto, validators
from api_rest.identity.plans_catalog import listar_planes


@pytest.fixture(autouse=True)
def _mem():
    identity_store.reset_memory()
    yield
    identity_store.reset_memory()


def _make_valid_rut():
    cuerpo = "76063552"
    s, m = 0, 2
    for c in reversed(cuerpo):
        s += int(c) * m
        m = 2 if m == 7 else m + 1
    resto = 11 - (s % 11)
    dv = "0" if resto == 11 else ("K" if resto == 10 else str(resto))
    return f"{cuerpo}-{dv}"


def _payload(**over):
    base = {
        "email": "ops.escondida@example.com",
        "password": "Segura1234",
        "password_confirm": "Segura1234",
        "nombres": "Maria",
        "apellidos": "Gonzalez",
        "telefono": "+56912345678",
        "razon_social": "Minera Escondida SpA",
        "rut": _make_valid_rut(),
        "sitio": "spati",
        "faena": "escondida",
        "consentimientos": {
            "almacenamiento_datos": True,
            "tos": True,
            "privacy": True,
            "veracidad": True,
        },
    }
    base.update(over)
    return base


def test_pii_roundtrip():
    token = pii_crypto.encrypt_pii("Juan Perez")
    assert token.startswith("v1.")
    assert "Juan" not in token
    assert pii_crypto.decrypt_pii(token) == "Juan Perez"


def test_password_scrypt():
    h = pii_crypto.hash_password("Segura1234")
    assert pii_crypto.verify_password("Segura1234", h)
    assert not pii_crypto.verify_password("otra", h)


def test_validate_requires_consent_and_rut():
    bad = _payload(consentimientos={}, rut="1-9")
    r = validators.validate_registro_payload(bad)
    assert r["ok"] is False
    assert "consentimientos" in r["errors"] or "rut" in r["errors"]


def test_register_isolated_by_faena():
    rut = _make_valid_rut()
    ok, _, info = identity_store.registrar_v2(
        _payload(rut=rut, email="a@mine.cl", faena="escondida")
    )
    assert ok and info["faena"] == "escondida"
    ok2, msg, _ = identity_store.registrar_v2(
        _payload(rut=rut, email="a@mine.cl", faena="escondida")
    )
    assert not ok2
    ok3, _, info3 = identity_store.registrar_v2(
        _payload(rut=rut, email="a@mine.cl", faena="los_bronces")
    )
    assert ok3 and info3["faena"] == "los_bronces"


def test_access_tabs_by_plan():
    access = identity_store.compute_access(
        sitio="spati", faena="escondida", plan_code="trial", sub_status="trialing"
    )
    assert access["tabs"]["panel"] is True
    assert access["tabs"]["dron"] is False
    access_pro = identity_store.compute_access(
        sitio="spati", faena="escondida", plan_code="pro", sub_status="active"
    )
    assert access_pro["tabs"]["umbrales"] is True


def test_planes_escalados_faena():
    base = listar_planes("spati", None)
    esc = listar_planes("spati", "escondida")
    p_base = next(p for p in base["planes"] if p["plan_code"] == "starter")
    p_esc = next(p for p in esc["planes"] if p["plan_code"] == "starter")
    assert p_esc["precio_mensual_clp"] > p_base["precio_mensual_clp"]


def test_api_validate_and_register():
    from api_rest.app import create_app

    app = create_app()
    client = app.test_client()
    body = _payload()
    r = client.post("/api/auth/validate-registro", json=body)
    assert r.status_code == 200
    assert r.get_json()["ok"] is True
    r2 = client.post("/api/auth/register-v2", json=body)
    assert r2.status_code == 201
    data = r2.get_json()
    assert data.get("verify_token")
    v = client.get(f"/api/auth/verify-email?token={data['verify_token']}")
    assert v.status_code == 200
    # login + checkout mock
    login = client.post(
        "/api/auth/login",
        json={
            "username": body["email"],
            "password": body["password"],
            "sitio": "spati",
            "faena": "escondida",
        },
    )
    assert login.status_code == 200
    token = login.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    chk = client.post(
        "/api/billing/checkout",
        json={"plan_code": "starter", "sitio": "spati", "faena": "escondida"},
        headers=headers,
    )
    assert chk.status_code == 200
    assert chk.get_json().get("applied") is True
    acc = client.get(
        "/api/auth/access?sitio=spati&faena=escondida&tab=dron",
        headers=headers,
    )
    assert acc.status_code == 200
    assert acc.get_json().get("tab_allowed") is True
    cuenta = client.get("/api/auth/cuenta?faena=escondida", headers=headers)
    assert cuenta.status_code == 200
    assert cuenta.get_json()["suscripcion"]["plan_code"] == "starter"
    planes = client.get("/api/public/planes?sitio=spati&faena=escondida")
    assert planes.status_code == 200
    assert len(planes.get_json()["planes"]) >= 3
    reglas = client.get("/api/public/faenas/escondida/reglas")
    assert reglas.status_code == 200
    assert reglas.get_json()["enlace"] == "/f/escondida/"


def test_access_tab_denied_returns_403():
    from api_rest.app import create_app

    app = create_app()
    client = app.test_client()
    body = _payload(email="trial.ops@example.com")
    reg = client.post("/api/auth/register-v2", json=body)
    assert reg.status_code == 201
    tok = reg.get_json()["verify_token"]
    assert client.get(f"/api/auth/verify-email?token={tok}").status_code == 200
    login = client.post(
        "/api/auth/login",
        json={
            "username": body["email"],
            "password": body["password"],
            "sitio": "spati",
            "faena": "escondida",
        },
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.get_json()['access_token']}"}
    # trial: umbrales bloqueado → 403 + payload tabs
    acc = client.get(
        "/api/auth/access?sitio=spati&faena=escondida&tab=umbrales",
        headers=headers,
    )
    assert acc.status_code == 403
    body_acc = acc.get_json()
    assert body_acc.get("tab_allowed") is False
    assert body_acc["tabs"]["panel"] is True
    assert body_acc["tabs"]["umbrales"] is False
