#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R1: en production no aceptar clave anon/publishable de Supabase."""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GD = ROOT / "backend" / "08_Gestion_Datos"
if str(GD) not in sys.path:
    sys.path.insert(0, str(GD))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _jwt_role(role: str) -> str:
    header = (
        base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').rstrip(b"=").decode()
    )
    payload = (
        base64.urlsafe_b64encode(json.dumps({"role": role, "iss": "test"}).encode())
        .rstrip(b"=")
        .decode()
    )
    return f"{header}.{payload}.sig"


def _reload_client(monkeypatch):
    """Evita que load_dotenv() reponga valores del .env local."""
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)
    import importlib

    import supabase_db.client as client

    return importlib.reload(client)


def test_prod_rejects_anon_jwt(monkeypatch):
    monkeypatch.setenv("METGO_ENV", "production")
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", _jwt_role("anon"))
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "")
    monkeypatch.setenv("METGO_SUPABASE_KEY", "")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "")

    client = _reload_client(monkeypatch)
    try:
        client._resolve_supabase_creds()
        assert False, "debía rechazar anon en production"
    except RuntimeError as exc:
        assert "anon" in str(exc).lower() or "publishable" in str(exc).lower()


def test_prod_accepts_service_jwt(monkeypatch):
    monkeypatch.setenv("METGO_ENV", "production")
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", _jwt_role("service_role"))
    monkeypatch.setenv("SUPABASE_ANON_KEY", "")

    client = _reload_client(monkeypatch)
    url, key = client._resolve_supabase_creds()
    assert url and key
    assert client._looks_like_anon_key(key) is False


def test_prod_ignores_anon_env_fallback(monkeypatch):
    monkeypatch.setenv("METGO_ENV", "production")
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "")
    monkeypatch.setenv("METGO_SUPABASE_KEY", "")
    monkeypatch.setenv("SUPABASE_ANON_KEY", _jwt_role("anon"))

    client = _reload_client(monkeypatch)
    url, key = client._resolve_supabase_creds()
    assert url
    assert key is None


def test_dev_allows_anon_fallback(monkeypatch):
    monkeypatch.setenv("METGO_ENV", "development")
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "")
    monkeypatch.setenv("METGO_SUPABASE_KEY", "")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "sb_publishable_test")

    client = _reload_client(monkeypatch)
    url, key = client._resolve_supabase_creds()
    assert url and key == "sb_publishable_test"
