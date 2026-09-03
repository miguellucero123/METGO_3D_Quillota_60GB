#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests R6/R8/R9 — retención, export y olvido (memoria)."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("METGO_JWT_SECRET", "test-secret-compliance-min-32-bytes!!")
os.environ.setdefault("METGO_ENV", "development")
os.environ["METGO_IDENTITY_STORE"] = "memory"


def _setup():
    import metgo_paths

    metgo_paths.setup_paths("05_api_rest")
    apis = metgo_paths.MODULE_PATHS["05_api_rest"]
    if str(apis) not in sys.path:
        sys.path.insert(0, str(apis))


def test_export_and_delete_memory():
    _setup()
    from api_rest.identity import identity_store, pii_crypto

    identity_store._MEM["usuarios_app"].clear()
    identity_store._MEM["consentimientos"].clear()
    identity_store._MEM["audit_auth"].clear()
    identity_store._MEM["suscripciones"].clear()

    uid = "11111111-1111-1111-1111-111111111111"
    identity_store._MEM["usuarios_app"].append(
        {
            "id": uid,
            "email_norm": "titular@metgo3d.com",
            "nombres_enc": pii_crypto.encrypt_pii("Ana"),
            "apellidos_enc": pii_crypto.encrypt_pii("Pérez"),
            "telefono_enc": pii_crypto.encrypt_pii("+56911111111"),
            "sitio": "quillota",
            "faena": None,
            "role": "operador",
            "status": "active",
            "org_id": None,
            "password_hash": pii_crypto.hash_password("x"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    identity_store._MEM["consentimientos"].append(
        {
            "usuario_id": uid,
            "tipo": "privacy",
            "version": "1",
            "accepted_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    identity_store._MEM["audit_auth"].append(
        {
            "usuario_id": uid,
            "evento": "login",
            "ip_hash": "abc",
            "sitio": "quillota",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    data, msg = identity_store.export_user_data("titular@metgo3d.com")
    assert msg == "ok" and data
    assert data["usuarios"][0]["nombres"] == "Ana"
    assert data["consentimientos"]

    ok, dmsg = identity_store.delete_user_data("titular@metgo3d.com")
    assert ok, dmsg
    u = identity_store._MEM["usuarios_app"][0]
    assert u["status"] == "deleted"
    assert u["email_norm"].startswith("deleted_")
    assert identity_store._MEM["audit_auth"][0].get("ip_hash") is None


def test_purge_audit_retention_memory():
    _setup()
    from api_rest.identity import identity_store
    from api_rest.identity.compliance_retention import purge_audit_auth

    identity_store._MEM["audit_auth"] = [
        {
            "evento": "old",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=800)).isoformat(),
        },
        {
            "evento": "new",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    ]
    res = purge_audit_auth(dry_run=False)
    assert res["ok"] is True
    assert res["deleted"] == 1
    assert len(identity_store._MEM["audit_auth"]) == 1
    assert identity_store._MEM["audit_auth"][0]["evento"] == "new"


def test_api_export_requires_auth():
    _setup()
    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/auth/me/export")
    assert r.status_code in (401, 403)
