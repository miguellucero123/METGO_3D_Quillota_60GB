#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Multi-sitio: catálogo de sitios (E6)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths


def _setup_api():
    metgo_paths.setup_paths("01_meteo", "05_api_rest")
    apis = metgo_paths.MODULE_PATHS["05_api_rest"]
    if str(apis) not in sys.path:
        sys.path.insert(0, str(apis))


def test_listar_sitios_catalogo():
    _setup_api()
    from api_rest.estaciones_catalogo import listar_sitios

    todos = listar_sitios()
    slugs = {s["slug"] for s in todos}
    assert {"quillota", "paine", "demo"} <= slugs
    demo = next(s for s in todos if s["slug"] == "demo")
    assert demo["estado"] == "plantilla"
    assert "demo_norte" in demo["estaciones"]

    sin_plantilla = listar_sitios(incluir_plantilla=False)
    assert all(s["slug"] != "demo" for s in sin_plantilla)


def test_api_public_sitios():
    _setup_api()
    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/public/sitios")
    assert r.status_code == 200
    body = r.get_json()
    assert isinstance(body, list)
    assert any(s.get("slug") == "paine" for s in body)


def test_api_public_estaciones_demo():
    _setup_api()
    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/public/estaciones?sitio=demo")
    assert r.status_code == 200
    demo = r.get_json()
    assert len(demo) == 2
    assert all(e.get("sitio") == "demo" for e in demo)
    assert {e["id"] for e in demo} == {"demo_norte", "demo_sur"}
