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
    # Básico (starter): panel/ahora sí; dron es Pro+
    acc = client.get(
        "/api/auth/access?sitio=spati&faena=escondida&tab=panel",
        headers=headers,
    )
    assert acc.status_code == 200
    body_acc = acc.get_json()
    assert body_acc.get("tab_allowed") is True
    assert body_acc["tabs"]["panel"] is True
    assert body_acc["tabs"].get("ahora") is True
    assert body_acc["tabs"]["dron"] is False
    acc_ahora = client.get(
        "/api/auth/access?sitio=spati&faena=escondida&tab=ahora",
        headers=headers,
    )
    assert acc_ahora.status_code == 200
    assert acc_ahora.get_json().get("tab_allowed") is True
    acc_dron = client.get(
        "/api/auth/access?sitio=spati&faena=escondida&tab=dron",
        headers=headers,
    )
    assert acc_dron.status_code == 403
    assert acc_dron.get_json().get("tab_allowed") is False
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


def test_hub_faenas_solo_membresia():
    hub = identity_store.resolver_hub_faenas(
        email="ops@example.com",
        role="operador",
        sitio="spati",
        faena_jwt="quebrada_blanca",
        plan_code="starter",
    )
    assert hub["catalogo_completo"] is False
    assert hub["faenas"] == [{"slug": "quebrada_blanca"}]

    admin = identity_store.resolver_hub_faenas(
        email="admin",
        role="admin",
        sitio="spati",
        faena_jwt=None,
        plan_code="pro",
    )
    assert admin["catalogo_completo"] is True

    ent = identity_store.resolver_hub_faenas(
        email="big@example.com",
        role="operador",
        sitio="spati",
        faena_jwt="escondida",
        plan_code="enterprise",
    )
    assert ent["multi_faena"] is True


def test_ops_board_m10_forbidden_single_faena():
    """Trial con 1 faena no abre el board; service unitario sí arma filas."""
    from api_rest.app import create_app
    from api_rest.ops_board_service import construir_ops_board

    board = construir_ops_board(["escondida", "paipote"], refresh=False, incluir_observado=False)
    assert board["fase"] == "M10"
    assert board["n_faenas"] >= 1
    assert board["filas"][0]["faena_id"] in ("escondida", "paipote")

    app = create_app()
    client = app.test_client()
    body = _payload(email="board.single@example.com")
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
    r = client.get("/api/auth/ops-board", headers=headers)
    assert r.status_code == 403
    assert r.get_json().get("error") == "ops_board_requiere_multi_faena"


def test_ops_board_usa_paquete_mock(monkeypatch):
    """Cada faena recibe nivel desde paquete (no queda sin_dato por cupo live)."""
    from api_rest import ops_board_service as obs
    from api_rest import paquete_ambiental_service as pas

    def fake_pkg(fid, horas=24):
        return {
            "faena_id": fid,
            "generado_en": "2026-01-01T00:00:00",
            "actual": {"rafaga_10m_ms": 5.5, "viento_10m_ms": 3.0},
            "flags": {"nivel_global": "verde"},
            "operaciones": {
                "actividades": {
                    "izaje": {"nivel": "verde", "razones": []},
                    "caminos": {"nivel": "verde", "razones": []},
                    "botaderos": {"nivel": "amarillo", "razones": ["polvo"]},
                }
            },
            "fuente": {"meteo": "test"},
        }

    monkeypatch.setattr(pas, "_load_lastgood", lambda *a, **k: None)
    monkeypatch.setattr(pas, "construir_paquete_ambiental", fake_pkg)

    board = obs.construir_ops_board(
        ["andina", "candelaria", "collahuasi"],
        refresh=True,
        incluir_observado=False,
    )
    assert board["n_faenas"] == 3
    assert board["live_usados"] == 3
    for row in board["filas"]:
        assert row["nivel_global"] == "verde"
        assert row["izaje"]["nivel"] == "verde"
        assert row["rafaga_10m_ms"] == 5.5
        assert row["fuente_paquete"] in ("live", "degraded")


def test_sesion_unica_invalida_token_anterior():
    """Segundo login invalida el JWT anterior (401 session_replaced)."""
    from api_rest.app import create_app
    from api_rest.identity.session_store import reset_for_tests

    reset_for_tests()
    app = create_app()
    client = app.test_client()
    body = _payload(email="session.kick@example.com")
    reg = client.post("/api/auth/register-v2", json=body)
    assert reg.status_code == 201
    tok = reg.get_json()["verify_token"]
    assert client.get(f"/api/auth/verify-email?token={tok}").status_code == 200

    login1 = client.post(
        "/api/auth/login",
        json={
            "username": body["email"],
            "password": body["password"],
            "sitio": "spati",
            "faena": "escondida",
        },
    )
    assert login1.status_code == 200
    token1 = login1.get_json()["access_token"]
    h1 = {"Authorization": f"Bearer {token1}"}
    assert client.get("/api/auth/me", headers=h1).status_code == 200

    login2 = client.post(
        "/api/auth/login",
        json={
            "username": body["email"],
            "password": body["password"],
            "sitio": "spati",
            "faena": "escondida",
        },
    )
    assert login2.status_code == 200
    token2 = login2.get_json()["access_token"]
    assert token1 != token2

    kicked = client.get("/api/auth/me", headers=h1)
    assert kicked.status_code == 401
    assert kicked.get_json().get("code") == "session_replaced"

    ok = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token2}"})
    assert ok.status_code == 200


def test_preview_hora_solo_ahora_y_panel_y_purge(monkeypatch):
    """Usuario preview: tabs limitados, expira y se elimina."""
    monkeypatch.setenv("METGO_ALLOW_PREVIEW", "1")
    monkeypatch.setenv("METGO_IDENTITY_STORE", "memory")
    from api_rest.app import create_app
    from api_rest.identity import identity_store
    from datetime import timedelta

    identity_store.reset_memory()
    app = create_app()
    client = app.test_client()

    r = client.post(
        "/api/auth/preview-hora",
        json={"faena": "escondida", "horas": 1, "label": "demo"},
    )
    assert r.status_code == 201, r.get_json()
    cred = r.get_json()
    assert cred["plan_code"] == "preview"
    assert set(cred["tabs"]) == {"ahora", "panel"}
    email = cred["email"]
    password = cred["password"]

    login = client.post(
        "/api/auth/login",
        json={"username": email, "password": password, "sitio": "spati", "faena": "escondida"},
    )
    assert login.status_code == 200
    token = login.get_json()["access_token"]
    assert login.get_json()["expires_in"] <= 3600
    headers = {"Authorization": f"Bearer {token}"}

    access = client.get(
        "/api/auth/access?sitio=spati&faena=escondida",
        headers=headers,
    )
    assert access.status_code == 200
    tabs = access.get_json()["tabs"]
    assert tabs.get("ahora") is True
    assert tabs.get("panel") is True
    assert tabs.get("ambiente") is False
    assert tabs.get("dron") is False
    assert tabs.get("umbrales") is False
    assert access.get_json().get("preview") is True

    # Expirar y bloquear login
    with identity_store._lock:
        for s in identity_store._MEM["suscripciones"]:
            if s.get("plan_code") == "preview":
                s["current_period_end"] = (
                    identity_store._utcnow() - timedelta(minutes=1)
                ).isoformat()

    denied = client.post(
        "/api/auth/login",
        json={"username": email, "password": password, "sitio": "spati", "faena": "escondida"},
    )
    assert denied.status_code == 403
    assert denied.get_json().get("code") == "subscription_expired"

    purged = client.post("/api/cron/identity/purge-preview")
    assert purged.status_code == 200
    assert purged.get_json()["purged"] >= 1


def test_reporte_mensual_html_publico():
    from api_rest.app import create_app

    app = create_app()
    client = app.test_client()
    r = client.get("/api/public/spati/escondida/reporte-mensual")
    assert r.status_code == 200
    assert "text/html" in (r.content_type or "")
    assert b"Reporte mensual" in r.data
