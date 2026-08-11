#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P2 KYC manual + sesión idle + KEK prev."""

from __future__ import annotations

import os
import time

import pytest

os.environ["METGO_IDENTITY_STORE"] = "memory"
os.environ["METGO_JWT_SECRET"] = "test-secret-kyc-p2-min-32-bytes!!!!!!"
os.environ["METGO_API_AUTH_REQUIRED"] = "1"
os.environ["METGO_SCRYPT_N"] = "1024"
os.environ["METGO_EMAIL_DEV"] = "1"
os.environ.pop("METGO_SESSION_IDLE_S", None)

from api_rest.identity import identity_store, pii_crypto
from api_rest.identity import session_store


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    identity_store.reset_memory()
    session_store.reset_for_tests()
    monkeypatch.setenv("METGO_KYC_GATE_PAID", "1")
    monkeypatch.delenv("METGO_SESSION_IDLE_S", raising=False)
    monkeypatch.delenv("METGO_PII_KEK_PREV", raising=False)
    yield
    identity_store.reset_memory()
    session_store.reset_for_tests()


def _rut():
    cuerpo = "76063552"
    s, m = 0, 2
    for c in reversed(cuerpo):
        s += int(c) * m
        m = 2 if m == 7 else m + 1
    r = 11 - (s % 11)
    dv = "0" if r == 11 else ("K" if r == 10 else str(r))
    return f"{cuerpo}-{dv}"


def _register():
    ok, _, out = identity_store.registrar_v2(
        {
            "email": "kyc@example.com",
            "password": "SecurePass1x",
            "password_confirm": "SecurePass1x",
            "nombres": "Ana Maria",
            "apellidos": "Perez Soto",
            "razon_social": "Org KYC SpA",
            "rut": _rut(),
            "sitio": "spati",
            "faena": "escondida",
            "consentimientos": {
                "almacenamiento_datos": True,
                "tos": True,
                "privacy": True,
                "veracidad": True,
            },
        },
        ip="127.0.0.1",
    )
    assert ok, out
    return out


def test_new_org_kyc_pending_and_gate_blocks_paid():
    out = _register()
    org_id = out["org_id"]
    kyc = identity_store.org_kyc(org_id)
    assert kyc["kyc_status"] == "pending"
    ok, msg = identity_store.assert_kyc_allows_paid_plan(org_id, "starter")
    assert ok is False
    assert "KYC" in (msg or "")


def test_verified_allows_paid_and_cuenta_includes_kyc():
    out = _register()
    org_id = out["org_id"]
    ok, msg, info = identity_store.set_org_kyc(
        org_id, "verified", notes="RUT OK", reviewed_by="ops@metgo"
    )
    assert ok, msg
    assert info["kyc_status"] == "verified"
    ok2, _ = identity_store.assert_kyc_allows_paid_plan(org_id, "pro")
    assert ok2 is True
    cuenta = identity_store.cuenta_resumen(
        email="kyc@example.com", org_id=org_id, sitio="spati", faena="escondida"
    )
    assert cuenta["kyc"]["kyc_status"] == "verified"


def test_gate_off_allows_paid_without_kyc(monkeypatch):
    monkeypatch.setenv("METGO_KYC_GATE_PAID", "0")
    out = _register()
    ok, _ = identity_store.assert_kyc_allows_paid_plan(out["org_id"], "starter")
    assert ok is True


def test_session_idle_expires(monkeypatch):
    monkeypatch.setenv("METGO_SESSION_IDLE_S", "1")
    session_store.register_session("user@x.com", "jti-1")
    assert session_store.is_session_active("user@x.com", "jti-1") is True
    # fuerza idle
    with session_store._lock:
        session_store._CURRENT["user@x.com"]["at"] = time.time() - 5
    assert session_store.is_session_active("user@x.com", "jti-1") is False


def test_pii_kek_prev_decrypt():
    os.environ["METGO_PII_KEK"] = "primary-kek-for-tests-32b!!!!"
    os.environ.pop("METGO_PII_KEK_PREV", None)
    enc = pii_crypto.encrypt_pii("dato-secreto")
    os.environ["METGO_PII_KEK_PREV"] = "primary-kek-for-tests-32b!!!!"
    os.environ["METGO_PII_KEK"] = "rotated-kek-for-tests-32bytes!!"
    assert pii_crypto.decrypt_pii(enc) == "dato-secreto"
    assert len(pii_crypto.kek_fingerprint()) == 12
