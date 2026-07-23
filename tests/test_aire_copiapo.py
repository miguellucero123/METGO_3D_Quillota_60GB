#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E7 Copiapó: sitio, ICAP y endpoints de calidad del aire."""

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


def test_sitio_copiapo_registrado():
    _setup_api()
    from api_rest.estaciones_catalogo import listar_sitios, slugs_de_sitio

    copiapo = next(s for s in listar_sitios() if s["slug"] == "copiapo")
    assert copiapo["dominio"] == "aire"
    assert "aire" in copiapo["modules"]
    assert set(slugs_de_sitio("copiapo")) == {
        "copiapo_centro",
        "paipote",
        "tierra_amarilla",
    }


def test_icap_pm25_tramos():
    _setup_api()
    from api_rest.aire_service import icap_pm25

    assert icap_pm25(0) == 0
    assert icap_pm25(50) == 100  # norma 24 h PM2.5
    assert icap_pm25(80) == 200  # inicio Alerta
    assert icap_pm25(110) == 300  # inicio Preemergencia
    assert icap_pm25(170) == 500  # inicio Emergencia
    assert icap_pm25(25) == 50  # tramo lineal Bueno
    assert icap_pm25(None) is None


def test_icap_pm10_tramos():
    _setup_api()
    from api_rest.aire_service import icap_pm10

    assert icap_pm10(150) == 100
    assert icap_pm10(195) == 200
    assert icap_pm10(240) == 300
    assert icap_pm10(330) == 500
    assert icap_pm10(75) == 50


def test_evaluar_icap_contaminante_rector():
    _setup_api()
    from api_rest.aire_service import evaluar_icap

    # PM2.5 manda (80 µg/m³ → 200) frente a PM10 leve
    r = evaluar_icap(pm25=80, pm10=75)
    assert r["contaminante_rector"] == "pm2_5"
    assert r["icap"] == 200
    assert r["nivel"] == "alerta"
    assert r["recomendaciones"]

    # Sin datos
    vacio = evaluar_icap(None, None)
    assert vacio["icap"] is None
    assert vacio["nivel"] is None

    # Bueno
    ok = evaluar_icap(10, 30)
    assert ok["nivel"] == "bueno"


def test_api_public_aire_endpoints():
    _setup_api()
    from api_rest.app import create_app

    c = create_app().test_client()

    r404 = c.get("/api/public/aire/estacion_inexistente")
    assert r404.status_code == 404

    # 200 con datos o 503 si CAMS caído en CI — nunca 404 para estación válida
    r = c.get("/api/public/aire/copiapo_centro")
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        body = r.get_json()
        assert body["estacion_id"] == "copiapo_centro"
        assert "icap" in body and "recomendaciones" in body

    rp = c.get("/api/public/aire/copiapo_centro/pronostico?dias=3")
    assert rp.status_code in (200, 503)
    if rp.status_code == 200:
        dias = rp.get_json()
        assert isinstance(dias, list)
        assert all("icap" in d for d in dias)
