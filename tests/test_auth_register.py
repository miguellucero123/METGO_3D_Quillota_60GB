#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests registro JWT (Módulo 7)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths

metgo_paths.setup_paths("07_monitoreo", "05_api_rest")

import metgo_auth  # noqa: E402


def test_registrar_usuario_demo(tmp_path, monkeypatch):
    reg_file = tmp_path / "usuarios_registrados.json"
    monkeypatch.setattr(metgo_auth, "_registry_path", lambda: reg_file)
    monkeypatch.setenv("METGO_ALLOW_SELF_REGISTER", "1")

    ok, msg = metgo_auth.registrar_usuario("campo_norte", "secreto1", "a@b.cl")
    assert ok, msg
    assert metgo_auth.verificar_credenciales("campo_norte", "secreto1")
    assert not metgo_auth.verificar_credenciales("campo_norte", "mala")

    ok2, _ = metgo_auth.registrar_usuario("campo_norte", "otra", None)
    assert not ok2

    data = json.loads(reg_file.read_text(encoding="utf-8"))
    assert data["campo_norte"]["role"] == "lectura"


def test_usuario_o_contrasena_incorrectos():
    assert not metgo_auth.verificar_credenciales("admin", "mal")
