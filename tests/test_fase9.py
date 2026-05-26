#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests Fase 9 — notificaciones multicanal."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths

metgo_paths.setup_paths("05_api_rest")
_apis = metgo_paths.MODULE_PATHS["05_api_rest"]
if str(_apis) not in sys.path:
    sys.path.insert(0, str(_apis))


@pytest.fixture
def client(tmp_path, monkeypatch):
    os.environ["METGO_API_AUTH_REQUIRED"] = "1"
    os.environ.setdefault("METGO_PASSWORD_ADMIN", "admin123")
    cfg = tmp_path / "notif.json"
    outbox = tmp_path / "outbox.jsonl"
    monkeypatch.setattr("api_rest.integracion.notificaciones._config_path", lambda: cfg)
    monkeypatch.setattr("api_rest.integracion.notificaciones._outbox_path", lambda: outbox)
    from api_rest.app import create_app

    return create_app().test_client()


def _token(client) -> str:
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    return r.get_json()["access_token"]


def test_notificaciones_status(client):
    h = {"Authorization": f"Bearer {_token(client)}"}
    r = client.get("/api/notificaciones/status", headers=h)
    assert r.status_code == 200
    body = r.get_json()
    assert "canal_recomendado" in body
    assert "outbox_pendientes" in body


def test_outbox_y_retry(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "api_rest.integracion.notificaciones._config_path",
        lambda: tmp_path / "n.json",
    )
    ob = tmp_path / "o.jsonl"
    monkeypatch.setattr("api_rest.integracion.notificaciones._outbox_path", lambda: ob)
    from api_rest.integracion import notificaciones

    notificaciones._encolar_outbox("a@test.com", "Asunto", "Cuerpo")
    items = notificaciones.listar_outbox(5)
    assert len(items) == 1
    r = notificaciones.reintentar_outbox()
    assert r.get("ok") is False or r.get("enviados", 0) == 0


def test_webhook_y_email(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "api_rest.integracion.notificaciones._config_path",
        lambda: tmp_path / "n.json",
    )
    monkeypatch.setattr(
        "api_rest.integracion.notificaciones._outbox_path",
        lambda: tmp_path / "o.jsonl",
    )
    from api_rest.integracion import notificaciones

    notificaciones.guardar_config(
        {"webhook_url": "https://example.com/hook", "email_habilitado": True}
    )
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        r = notificaciones.enviar_notificacion("hola webhook")
    assert r.get("ok") is True
    canales = [c.get("canal") for c in r.get("canales", [])]
    assert "webhook" in canales
    assert "email_outbox" in canales


def test_health_fase9(client):
    r = client.get("/api/health")
    assert r.get_json().get("fase") in ("9", "10")
