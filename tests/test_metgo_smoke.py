#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke tests: layout por capas y API REST METGO."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths


def test_layout_capas_detectado():
    assert metgo_paths.LAYOUT_CAPAS is True
    assert (metgo_paths.BACKEND / "05_APIs_Externas").is_dir()
    assert (metgo_paths.FRONTEND / "vue").is_dir()
    assert (metgo_paths.SITE_WEB / "streamlit").is_dir()


def test_metgo_paths_helpers():
    assert metgo_paths.streamlit_dashboard_path("streamlit_app.py").parent.name == "dashboards"
    assert metgo_paths.site_web_streamlit_path("dashboard_web_publico.py").exists()
    assert metgo_paths.frontend_vue_dir().name == "vue"
    assert metgo_paths.frontend_app_movil_dir().name == "app_movil"


def test_api_health():
    metgo_paths.setup_paths("01_meteo", "05_api_rest")
    apis = metgo_paths.MODULE_PATHS["05_api_rest"]
    if str(apis) not in sys.path:
        sys.path.insert(0, str(apis))
    from api_rest.app import create_app

    app = create_app()
    c = app.test_client()
    r = c.get("/api/health")
    assert r.status_code == 200
    body = r.get_json()
    assert body.get("status") in ("ok", "degraded")


def test_api_public_estaciones():
    metgo_paths.setup_paths("01_meteo", "05_api_rest")
    apis = metgo_paths.MODULE_PATHS["05_api_rest"]
    if str(apis) not in sys.path:
        sys.path.insert(0, str(apis))
    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/public/estaciones")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_api_public_meteo_desconocida():
    metgo_paths.setup_paths("01_meteo", "05_api_rest")
    apis = metgo_paths.MODULE_PATHS["05_api_rest"]
    if str(apis) not in sys.path:
        sys.path.insert(0, str(apis))
    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/public/meteo/estacion_inexistente_xyz")
    assert r.status_code == 404
