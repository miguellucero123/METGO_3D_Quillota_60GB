#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests ventilación Paipote N/R/M + corridas + informe."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "backend" / "05_APIs_Externas"
if str(API) not in sys.path:
    sys.path.insert(0, str(API))


def test_codigo_ventilacion_umbrales():
    from api_rest.ventilacion_service import codigo_desde_indice, peor_codigo

    assert codigo_desde_indice(80) == "N"
    assert codigo_desde_indice(55) == "N"
    assert codigo_desde_indice(40) == "R"
    assert codigo_desde_indice(20) == "M"
    assert codigo_desde_indice(None) == "R"
    assert peor_codigo(["N", "R", "M"]) == "M"
    assert peor_codigo(["N", "N"]) == "N"


def test_corrida_vigente_06_18():
    from api_rest.ventilacion_service import corrida_vigente

    # Just after 06 UTC
    m = corrida_vigente(datetime(2026, 7, 25, 7, 0, tzinfo=timezone.utc))
    assert m["corrida_utc"] == "06"
    assert m["proxima_corrida_utc"] == "18"

    # Just after 18 UTC
    m2 = corrida_vigente(datetime(2026, 7, 25, 19, 0, tzinfo=timezone.utc))
    assert m2["corrida_utc"] == "18"
    assert m2["proxima_corrida_utc"] == "06"


def test_api_paipote_ventilacion_y_informe():
    from api_rest.app import create_app

    c = create_app().test_client()

    r = c.get("/api/public/operaciones/paipote/ventilacion?horizonte=horaria")
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        body = r.get_json()
        assert body["corrida_utc"] in ("06", "18")
        assert "filas" in body
        if body["filas"]:
            assert body["filas"][0]["ventilacion"] in ("N", "R", "M")

    rp = c.get("/api/public/operaciones/paipote/paquete")
    assert rp.status_code in (200, 503)

    rh = c.get("/api/public/operaciones/paipote/informe?formato=html")
    assert rh.status_code in (200, 503)
    if rh.status_code == 200:
        assert b"Paipote" in rh.data

    rpdf = c.get("/api/public/operaciones/paipote/informe?formato=pdf")
    assert rpdf.status_code in (200, 503)
    if rpdf.status_code == 200:
        assert rpdf.data[:4] == b"%PDF"


def test_api_sounding_paipote():
    from api_rest.app import create_app

    c = create_app().test_client()
    r404 = c.get("/api/public/aire/no_existe/sounding")
    assert r404.status_code == 404

    r = c.get("/api/public/aire/paipote/sounding?horas=2")
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        body = r.get_json()
        assert "frames" in body
        if body["frames"]:
            assert "niveles" in body["frames"][0]
            assert "diagnostico" in body["frames"][0]


def test_olas_calor_serie_sintetica():
    from api_rest.olas_calor_service import _eventos_desde_serie_sintetica

    # 4 días calurosos consecutivos en mayo
    serie = [
        ("2024-05-10", 25.0),
        ("2024-05-11", 26.0),
        ("2024-05-12", 27.0),
        ("2024-05-13", 26.5),
    ]
    ev = _eventos_desde_serie_sintetica(serie, p90=20.0, media=17.0)
    assert len(ev) == 1
    assert ev[0]["duracion_dias"] == 4
    assert ev[0]["intensidad"] in ("leve", "moderada", "fuerte")


def test_api_olas_calor_y_satelite():
    from api_rest.app import create_app

    c = create_app().test_client()
    r404 = c.get("/api/public/operaciones/paipote/olas-calor?estacion=no_existe")
    assert r404.status_code == 404

    # Puede ser 200 (con archive) o 503 (sin red / sin histórico)
    r = c.get("/api/public/operaciones/paipote/olas-calor?estacion=paipote&estacion_ano=otono&anios=3")
    assert r.status_code in (200, 503)

    rs = c.get("/api/public/operaciones/paipote/satelite?estacion=paipote")
    assert rs.status_code in (200, 404, 503)
    if rs.status_code == 200:
        body = rs.get_json()
        assert "bandas" in body
        assert "diagnostico" in body
        assert len(body["bandas"]) >= 1


def test_variables_conjunto_catalogo_y_api():
    from api_rest.variables_conjunto_service import catalogo_publico
    from api_rest.app import create_app

    cat = catalogo_publico()
    assert cat["version"] == 1
    assert len(cat["slots"]) >= 4

    c = create_app().test_client()
    r = c.get("/api/public/operaciones/conjunto/catalogo")
    assert r.status_code == 200
    assert "slots" in r.get_json()

    rj = c.get("/api/public/operaciones/paipote/conjunto?horas=24&series=temp_2m,viento")
    assert rj.status_code in (200, 503)
    if rj.status_code == 200:
        body = rj.get_json()
        assert "labels" in body
        assert "series" in body
        assert "temp_2m" in body["series"]
