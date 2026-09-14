#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas defensivas de acceso VENTORA / SPATI (anti-bypass).

Objetivo: asegurar que registro, login y /auth/access no se puedan
eludir con token falso, claims elevados, tabs de plan superior o
email sin verificar. No incluye exploits ni payloads ofensivos.
"""

from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timedelta, timezone

import pytest

os.environ["METGO_IDENTITY_STORE"] = "memory"
os.environ["METGO_JWT_SECRET"] = "test-secret-ventora-access-min-32b!!"
os.environ["METGO_API_AUTH_REQUIRED"] = "1"
os.environ["METGO_SCRYPT_N"] = "1024"
os.environ["METGO_EMAIL_DEV"] = "1"
os.environ["METGO_RATE_LIMIT_ENABLED"] = "0"

from api_rest.identity import identity_store
from api_rest.identity.session_store import reset_for_tests as reset_sessions


@pytest.fixture(autouse=True)
def _reset_identity():
    identity_store.reset_memory()
    reset_sessions()
    yield
    identity_store.reset_memory()
    reset_sessions()


@pytest.fixture
def client():
    from api_rest.app import create_app

    return create_app().test_client()


def _rut_valido() -> str:
    cuerpo = "76123456"
    s, m = 0, 2
    for c in reversed(cuerpo):
        s += int(c) * m
        m = 2 if m == 7 else m + 1
    resto = 11 - (s % 11)
    dv = "0" if resto == 11 else ("K" if resto == 10 else str(resto))
    return f"{cuerpo}-{dv}"


def _registro_ventora(**over) -> dict:
    body = {
        "email": "ops.ventanas@puerto-demo.cl",
        "password": "SeguraPuerto1",
        "password_confirm": "SeguraPuerto1",
        "nombres": "Camila",
        "apellidos": "Rojas",
        "telefono": "+56987654321",
        "razon_social": "Terminal Ventanas SpA",
        "rut": _rut_valido(),
        "sitio": "spati",
        "producto": "ventora_mar",
        "spa": "ventora_mar",
        "faena": "ventanas_muelle",
        "consentimientos": {
            "almacenamiento_datos": True,
            "tos": True,
            "privacy": True,
            "veracidad": True,
        },
    }
    body.update(over)
    return body


def _registrar_y_login(client, email: str, faena: str = "ventanas_muelle"):
    body = _registro_ventora(email=email, faena=faena)
    reg = client.post("/api/auth/register-v2", json=body)
    assert reg.status_code == 201, reg.get_json()
    tok = reg.get_json()["verify_token"]
    assert client.get(f"/api/auth/verify-email?token={tok}").status_code == 200
    login = client.post(
        "/api/auth/login",
        json={
            "username": body["email"],
            "password": body["password"],
            "sitio": "spati",
            "faena": faena,
        },
    )
    assert login.status_code == 200, login.get_json()
    data = login.get_json()
    return body, data["access_token"], data.get("user") or {}


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


# ---------------------------------------------------------------------------
# Sin autenticación / token inválido
# ---------------------------------------------------------------------------


def test_access_sin_token_rechazado(client):
    r = client.get("/api/auth/access?sitio=spati&faena=ventanas_muelle&tab=panel")
    assert r.status_code == 401
    assert "token" in (r.get_json().get("error") or "").lower()


def test_access_bearer_vacio_rechazado(client):
    r = client.get(
        "/api/auth/access?sitio=spati&tab=panel",
        headers={"Authorization": "Bearer "},
    )
    assert r.status_code == 401


def test_access_token_basura_rechazado(client):
    r = client.get(
        "/api/auth/access?sitio=spati&faena=ventanas_muelle",
        headers={"Authorization": "Bearer no.es.un.jwt"},
    )
    assert r.status_code == 401


def test_access_jwt_firmado_con_secreto_ajeno_rechazado(client):
    """Token HS256 con otra clave no debe abrir /auth/access."""
    import jwt

    now = datetime.now(timezone.utc)
    forged = jwt.encode(
        {
            "sub": "hacker@evil.example",
            "role": "admin",
            "sitio": "spati",
            "faena": "ventanas_muelle",
            "plan_code": "enterprise",
            "sub_status": "active",
            "jti": "forged-jti-1",
            "iat": now,
            "exp": now + timedelta(hours=2),
        },
        "secreto-que-no-es-el-del-servidor!!!!!!!!!!!!",
        algorithm="HS256",
    )
    if isinstance(forged, bytes):
        forged = forged.decode("utf-8")
    r = client.get(
        "/api/auth/access?sitio=spati&faena=ventanas_muelle&tab=panel",
        headers={"Authorization": f"Bearer {forged}"},
    )
    assert r.status_code == 401


def test_access_jwt_payload_alterado_sin_reafirmar_rechazado(client):
    """Mutar claims del JWT rompe la firma → 401 (no privilege escalation)."""
    _, token, _ = _registrar_y_login(client, "firma.intacta@puerto-demo.cl")
    parts = token.split(".")
    assert len(parts) == 3
    pad = "=" * (-len(parts[1]) % 4)
    payload = json.loads(base64.urlsafe_b64decode(parts[1] + pad))
    payload["plan_code"] = "enterprise"
    payload["role"] = "admin"
    payload["sub_status"] = "active"
    tampered = f"{parts[0]}.{_b64url(json.dumps(payload, separators=(',', ':')).encode())}.{parts[2]}"
    r = client.get(
        "/api/auth/access?sitio=spati&faena=ventanas_muelle&tab=umbrales",
        headers={"Authorization": f"Bearer {tampered}"},
    )
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# Email / registro: no entrar sin verificación ni consentimientos
# ---------------------------------------------------------------------------


def test_login_bloqueado_sin_verificar_email(client):
    body = _registro_ventora(email="sin.verify@puerto-demo.cl")
    reg = client.post("/api/auth/register-v2", json=body)
    assert reg.status_code == 201
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


def test_verify_token_inventado_no_activa_cuenta(client):
    body = _registro_ventora(email="token.fake@puerto-demo.cl")
    assert client.post("/api/auth/register-v2", json=body).status_code == 201
    bad = client.get("/api/auth/verify-email?token=token-inventado-no-existe")
    assert bad.status_code == 400
    still = client.post(
        "/api/auth/login",
        json={
            "username": body["email"],
            "password": body["password"],
            "sitio": "spati",
            "faena": "ventanas_muelle",
        },
    )
    assert still.status_code == 403
    assert still.get_json().get("code") == "email_not_verified"


def test_registro_sin_consentimientos_rechazado(client):
    body = _registro_ventora(
        email="sin.consent@puerto-demo.cl",
        consentimientos={"tos": False, "privacy": False},
    )
    v = client.post("/api/auth/validate-registro", json=body)
    assert v.status_code == 400
    assert v.get_json().get("ok") is False
    r = client.post("/api/auth/register-v2", json=body)
    assert r.status_code == 400


def test_registro_password_debil_rechazado(client):
    body = _registro_ventora(
        email="pwd.weak@puerto-demo.cl",
        password="corta",
        password_confirm="corta",
    )
    v = client.post("/api/auth/validate-registro", json=body)
    assert v.status_code == 400
    errs = v.get_json().get("errors") or {}
    assert "password" in errs


def test_registro_nombre_placeholder_rechazado(client):
    body = _registro_ventora(
        email="fake.name@puerto-demo.cl",
        nombres="Test",
        apellidos="User",
    )
    v = client.post("/api/auth/validate-registro", json=body)
    assert v.status_code == 400
    assert v.get_json().get("ok") is False


# ---------------------------------------------------------------------------
# Autorización por plan: trial no abre tabs premium
# ---------------------------------------------------------------------------


def test_trial_ventora_panel_ok_umbrales_y_dron_403(client):
    _, token, _ = _registrar_y_login(client, "trial.tabs@puerto-demo.cl")
    h = {"Authorization": f"Bearer {token}"}

    panel = client.get(
        "/api/auth/access?sitio=spati&faena=ventanas_muelle&tab=panel",
        headers=h,
    )
    assert panel.status_code == 200
    assert panel.get_json().get("tab_allowed") is True

    for tab in ("umbrales", "dron"):
        acc = client.get(
            f"/api/auth/access?sitio=spati&faena=ventanas_muelle&tab={tab}",
            headers=h,
        )
        assert acc.status_code == 403, tab
        body = acc.get_json()
        assert body.get("tab_allowed") is False
        assert body["tabs"][tab] is False


def test_cuenta_y_ops_board_no_escalan_con_trial(client):
    """Usuario piloto de 1 faena: cuenta OK, ops-board multi-faena denegado."""
    _, token, _ = _registrar_y_login(client, "ops.deny@puerto-demo.cl")
    h = {"Authorization": f"Bearer {token}"}

    cuenta = client.get("/api/auth/cuenta?faena=ventanas_muelle", headers=h)
    assert cuenta.status_code == 200
    sub = (cuenta.get_json() or {}).get("suscripcion") or {}
    assert sub.get("plan_code") in ("trial", "preview")
    assert sub.get("status") in ("trialing", "active", "preview")

    board = client.get("/api/auth/ops-board", headers=h)
    assert board.status_code == 403
    assert board.get_json().get("error") == "ops_board_requiere_multi_faena"


def test_suscripcion_en_store_manda_sobre_claim_jwt_elevado(client):
    """Aunque el JWT diga enterprise, /access usa la suscripción real de la org."""
    import metgo_auth

    body, token, user = _registrar_y_login(client, "claim.elevate@puerto-demo.cl")
    org_id = user.get("org_id")
    assert org_id, "login debe devolver org_id de identidad comercial"

    forged = metgo_auth.crear_token_identidad(
        sub=body["email"],
        role="admin",
        sitio="spati",
        faena="ventanas_muelle",
        org_id=org_id,
        plan_code="enterprise",
        sub_status="active",
    )
    h = {"Authorization": f"Bearer {forged['access_token']}"}
    acc = client.get(
        "/api/auth/access?sitio=spati&faena=ventanas_muelle&tab=umbrales",
        headers=h,
    )
    # Trial real en store → umbrales sigue bloqueado (no confiar solo en JWT)
    assert acc.status_code == 403
    assert acc.get_json().get("tab_allowed") is False
    assert acc.get_json().get("plan_code") == "trial"


def test_hub_mis_faenas_no_lista_catalogo_ajeno(client):
    """Operador con 1 puerto no recibe catálogo completo de faenas."""
    _, token, _ = _registrar_y_login(client, "hub.limit@puerto-demo.cl", faena="iqq")
    hub = client.get(
        "/api/auth/mis-faenas",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert hub.status_code == 200
    data = hub.get_json()
    assert data.get("catalogo_completo") is False
    slugs = {str(f.get("slug") or f).lower() for f in (data.get("faenas") or [])}
    assert "iqq" in slugs
    # No debe exponer todo el catálogo minero/portuario
    assert len(slugs) <= 2


def test_password_incorrecto_no_revela_si_email_existe(client):
    body = _registro_ventora(email="enum.check@puerto-demo.cl")
    reg = client.post("/api/auth/register-v2", json=body)
    assert reg.status_code == 201
    tok = reg.get_json()["verify_token"]
    assert client.get(f"/api/auth/verify-email?token={tok}").status_code == 200

    bad = client.post(
        "/api/auth/login",
        json={
            "username": body["email"],
            "password": "ClaveIncorrecta9",
            "sitio": "spati",
            "faena": "ventanas_muelle",
        },
    )
    unknown = client.post(
        "/api/auth/login",
        json={
            "username": "noexiste@puerto-demo.cl",
            "password": "ClaveIncorrecta9",
            "sitio": "spati",
            "faena": "ventanas_muelle",
        },
    )
    assert bad.status_code == 401
    assert unknown.status_code == 401
