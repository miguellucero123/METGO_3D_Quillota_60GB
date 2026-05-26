#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests notificaciones — email corporativo."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths

metgo_paths.setup_paths("05_api_rest")
_apis = metgo_paths.MODULE_PATHS["05_api_rest"]
if str(_apis) not in sys.path:
    sys.path.insert(0, str(_apis))


def test_email_corporativo_default(monkeypatch, tmp_path):
    monkeypatch.delenv("METGO_NOTIFY_EMAIL", raising=False)
    monkeypatch.setattr(
        "api_rest.integracion.notificaciones._config_path",
        lambda: tmp_path / "notif.json",
    )
    monkeypatch.setattr(
        "api_rest.integracion.notificaciones._outbox_path",
        lambda: tmp_path / "outbox.jsonl",
    )
    from api_rest.integracion import notificaciones

    cfg = notificaciones.leer_config()
    assert cfg["email_destino"] == "miguel.lucero@metgo3d.com"
    r = notificaciones.enviar_prueba("test unitario")
    assert r.get("ok") is True
    canales = r.get("canales") or []
    destinos = [c.get("destino") for c in canales if c.get("destino")]
    assert "miguel.lucero@metgo3d.com" in destinos or any(
        c.get("canal") == "email_outbox" for c in canales
    )
