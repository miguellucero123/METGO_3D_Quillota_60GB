#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests endurecimiento seguridad (rate limit + turnstile skip)."""

from __future__ import annotations

import os

import pytest

os.environ["METGO_IDENTITY_STORE"] = "memory"
os.environ["METGO_JWT_SECRET"] = "test-secret-security-min-32-bytes!!!!"
os.environ["METGO_API_AUTH_REQUIRED"] = "1"
os.environ["METGO_SCRYPT_N"] = "1024"
os.environ["METGO_EMAIL_DEV"] = "1"
os.environ["METGO_RATE_LIMIT_ENABLED"] = "1"
os.environ.pop("METGO_TURNSTILE_SECRET", None)
os.environ.pop("METGO_TURNSTILE_REQUIRED", None)

from api_rest import security_hardening as sec
from api_rest.identity import identity_store


@pytest.fixture(autouse=True)
def _reset():
    identity_store.reset_memory()
    sec.reset_rate_limits()
    yield
    identity_store.reset_memory()
    sec.reset_rate_limits()


def test_rate_limit_blocks_after_limit():
    for _ in range(5):
        ok, _ = sec.check_rate_limit("t_bucket", limit=5, window_s=60, key="1.2.3.4")
        assert ok
    ok, meta = sec.check_rate_limit("t_bucket", limit=5, window_s=60, key="1.2.3.4")
    assert ok is False
    assert meta.get("limited") is True
    assert meta.get("retry_after_s", 0) >= 1


def test_turnstile_skipped_without_secret():
    ok, msg = sec.verify_turnstile("anything")
    assert ok is True
    assert "skip" in msg


def test_security_config_public():
    from api_rest.app import create_app

    client = create_app().test_client()
    r = client.get("/api/public/security-config")
    assert r.status_code == 200
    body = r.get_json()
    assert "turnstile" in body
    assert body["rate_limit_enabled"] is True


def test_login_rate_limit_http():
    from api_rest.app import create_app

    client = create_app().test_client()
    for _ in range(20):
        client.post(
            "/api/auth/login",
            json={"username": "x@y.z", "password": "wrong-password", "sitio": "spati"},
        )
    r = client.post(
        "/api/auth/login",
        json={"username": "x@y.z", "password": "wrong-password", "sitio": "spati"},
    )
    assert r.status_code == 429
    assert r.get_json().get("code") == "rate_limited"


def test_etl_retry_queue_requires_cron_when_set(monkeypatch):
    monkeypatch.setenv("CRON_SECRET", "test-cron")
    from api_rest.app import create_app

    client = create_app().test_client()
    denied = client.get("/api/public/datos/etl/retry-queue")
    assert denied.status_code == 403
    ok = client.get(
        "/api/public/datos/etl/retry-queue",
        headers={"X-Cron-Token": "test-cron"},
    )
    assert ok.status_code in (200, 503)
