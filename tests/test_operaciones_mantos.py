#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E8 Mantos Blancos: sitio minero, ventanas operacionales y alertas por turno."""

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


def test_sitio_mantos_blancos_registrado():
    _setup_api()
    from api_rest.estaciones_catalogo import listar_sitios, slugs_de_sitio

    mb = next(s for s in listar_sitios() if s["slug"] == "mantos_blancos")
    assert mb["dominio"] == "mineria"
    assert "operaciones" in mb["modules"]
    assert set(slugs_de_sitio("mantos_blancos")) == {
        "mb_rajo",
        "mb_campamento",
        "mb_chancado",
        "mb_ruta_acceso",
    }


def test_semaforo_helpers():
    _setup_api()
    from api_rest.operaciones_service import _nivel_directo, _nivel_inverso, _peor

    assert _nivel_directo(5, 10, 14) == "verde"
    assert _nivel_directo(11, 10, 14) == "amarillo"
    assert _nivel_directo(15, 10, 14) == "rojo"
    # invertido (visibilidad): menos = peor
    assert _nivel_inverso(8, 5, 2) == "verde"
    assert _nivel_inverso(4, 5, 2) == "amarillo"
    assert _nivel_inverso(1, 5, 2) == "rojo"
    assert _peor("verde", "rojo", "amarillo") == "rojo"
    assert _peor("verde", "verde") == "verde"


def test_evaluar_izaje():
    _setup_api()
    from api_rest.operaciones_service import _evaluar_izaje

    # Ráfaga extrema → rojo (grúa fuera de carta)
    assert _evaluar_izaje({"viento_racha": 18.0, "viento_sostenido": 6.0})["nivel"] == "rojo"
    # Condiciones suaves → verde
    assert _evaluar_izaje({"viento_racha": 6.0, "viento_sostenido": 4.0})["nivel"] == "verde"


def test_evaluar_tronadura_viento_bajo():
    _setup_api()
    from api_rest.operaciones_service import _evaluar_tronadura

    # Viento insuficiente → polvo estancado → al menos amarillo
    r = _evaluar_tronadura({"viento_sostenido": 0.8, "viento_racha": 2.0, "visibilidad": 10.0})
    assert r["nivel"] in ("amarillo", "rojo")
    # Viento fuerte → rojo (nube descontrolada)
    r2 = _evaluar_tronadura({"viento_sostenido": 15.0, "viento_racha": 18.0, "visibilidad": 10.0})
    assert r2["nivel"] == "rojo"


def test_evaluar_hora_global():
    _setup_api()
    from api_rest.operaciones_service import evaluar_hora

    reg = {
        "fecha_hora": "2026-07-24T10:00",
        "viento_sostenido": 15.0,
        "viento_racha": 20.0,
        "visibilidad": 0.5,
        "precipitacion": 0.0,
        "uv_index": 11.0,
    }
    ev = evaluar_hora(reg)
    assert ev["nivel_global"] == "rojo"
    assert set(ev["actividades"].keys()) == {
        "tronadura",
        "transporte",
        "izaje",
        "exposicion_uv",
    }
    assert ev["actividades"]["exposicion_uv"]["nivel"] == "rojo"


def test_umbrales_override_env(monkeypatch):
    _setup_api()
    from api_rest import operaciones_service

    monkeypatch.setenv(
        "METGO_OP_UMBRALES_JSON",
        '{"izaje": {"racha": [5.0, 8.0]}}',
    )
    umb = operaciones_service.obtener_umbrales("mantos_blancos")
    assert umb["izaje"]["racha"] == (5.0, 8.0)
    # override solo afecta izaje; tronadura conserva default
    assert umb["tronadura"]["viento_sostenido"] == (10.0, 14.0)

    # Con umbrales más estrictos, 7 m/s de ráfaga ya es amarillo
    r = operaciones_service._evaluar_izaje(
        {"viento_racha": 7.0, "viento_sostenido": 3.0}, umb
    )
    assert r["nivel"] == "amarillo"

    pub = operaciones_service.umbrales_publicos("mantos_blancos")
    assert pub["sitio"] == "mantos_blancos"
    assert pub["umbrales"]["izaje"]["racha"] == [5.0, 8.0]


def test_api_operaciones_endpoints():
    _setup_api()
    from api_rest.app import create_app

    c = create_app().test_client()

    r404 = c.get("/api/public/operaciones/no_existe/ventanas")
    assert r404.status_code == 404

    r = c.get("/api/public/operaciones/mb_rajo/ventanas?horas=24")
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        filas = r.get_json()
        assert isinstance(filas, list)
        if filas:
            assert "actividades" in filas[0]
            assert "nivel_global" in filas[0]
            assert "exposicion_uv" in filas[0]["actividades"]

    ra = c.get("/api/public/operaciones/alertas?sitio=mantos_blancos&turno=dia")
    assert ra.status_code in (200, 503)
    if ra.status_code == 200:
        body = ra.get_json()
        assert body["turno"] == "dia"
        assert "hay_bloqueo" in body
        assert "estaciones" in body
        assert "umbrales_aplicados" in body

    ru = c.get("/api/public/operaciones/umbrales?sitio=mantos_blancos")
    assert ru.status_code == 200
    umb = ru.get_json()
    assert "umbrales" in umb
    assert "izaje" in umb["umbrales"]


def test_faena_catalogo_mantos():
    _setup_api()
    from api_rest.faena_catalogo import get_faena, listar_faenas, estacion_ancla

    f = get_faena("mantos_blancos")
    assert f is not None
    assert f["estacion_ancla"] == "mb_rajo"
    assert estacion_ancla("mantos") == "mb_rajo"
    ids = {x["id"] for x in listar_faenas()}
    assert "paipote" in ids and "mantos_blancos" in ids


def test_api_faena_mantos_endpoints():
    _setup_api()
    from api_rest.app import create_app

    c = create_app().test_client()
    rl = c.get("/api/public/operaciones/faenas")
    assert rl.status_code == 200
    assert any(f["id"] == "mantos_blancos" for f in rl.get_json()["faenas"])

    r404 = c.get("/api/public/operaciones/faena/no_existe/paquete")
    assert r404.status_code == 404

    # Puede ser 200 o 503 según red Open-Meteo
    rv = c.get("/api/public/operaciones/faena/mantos_blancos/ventilacion?horizonte=horaria")
    assert rv.status_code in (200, 503)
    if rv.status_code == 200:
        body = rv.get_json()
        assert body.get("faena") == "mantos_blancos"
        assert body.get("estacion_id") == "mb_rajo"

    rs = c.get("/api/public/operaciones/faena/mantos_blancos/satelite?estacion=mb_rajo")
    assert rs.status_code in (200, 404, 503)
    if rs.status_code == 200:
        body = rs.get_json()
        assert "bandas" in body
        assert body.get("faena") == "mantos_blancos"


def test_airshed_mantos_bbox():
    _setup_api()
    from api_rest.airshed_model_service import BBOX_POR_SITIO, FUENTES_POR_SITIO, modelar_airshed

    assert "mantos_blancos" in BBOX_POR_SITIO
    assert any(f["id"] == "mb_rajo" for f in FUENTES_POR_SITIO["mantos_blancos"])
    out = modelar_airshed(sitio="mantos_blancos", nx=12, ny=12, frames=1)
    assert "error" not in out or out.get("error") != "sitio_desconocido"
    if "error" not in out:
        assert out["sitio"] == "mantos_blancos"
        assert out["bbox"]["south"] > -24
