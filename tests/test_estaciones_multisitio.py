#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Multi-sitio: listar estaciones por ?sitio=."""

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


def test_catalogo_sitios():
    _setup_api()
    from api_rest.estaciones_catalogo import ESTACIONES_POR_SITIO, normalizar_sitio, slugs_de_sitio

    assert normalizar_sitio(None) == "quillota"
    assert normalizar_sitio("PAINE") == "paine"
    assert normalizar_sitio("desconocido") == "quillota"
    assert "quillota" in slugs_de_sitio("quillota")
    assert "base_torres" in slugs_de_sitio("paine")
    assert "base_torres" not in ESTACIONES_POR_SITIO["quillota"]


def test_listar_estaciones_por_sitio():
    _setup_api()
    from api_rest.services import listar_estaciones

    q = listar_estaciones(sitio="quillota")
    assert len(q) >= 5
    assert all(e.get("sitio") == "quillota" for e in q)
    assert any(e["id"] == "quillota" for e in q)

    p = listar_estaciones(sitio="paine")
    assert len(p) == 6
    assert all(e.get("sitio") == "paine" for e in p)
    assert any(e["id"] == "base_torres" and e.get("circuito") == "W" for e in p)


def test_api_public_estaciones_sitio():
    _setup_api()
    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/public/estaciones")
    assert r.status_code == 200
    body = r.get_json()
    assert isinstance(body, list)
    assert any(e.get("id") == "quillota" for e in body)

    r2 = c.get("/api/public/estaciones?sitio=paine")
    assert r2.status_code == 200
    paine = r2.get_json()
    assert len(paine) == 6
    assert all(e.get("sitio") == "paine" for e in paine)


def test_api_public_pronostico_paine():
    _setup_api()
    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/public/meteo/base_torres/pronostico?dias=3")
    # 200 con datos o 503 si OpenMeteo caído en CI — no 404
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        body = r.get_json()
        assert isinstance(body, list)
