#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M1 minería multi-faena: catálogo SPATI + paquete-ambiental + informe."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths


def _setup_api():
    metgo_paths.setup_paths("01_meteo", "05_api_rest")
    apis = metgo_paths.MODULE_PATHS["05_api_rest"]
    if str(apis) not in sys.path:
        sys.path.insert(0, str(apis))


def test_faena_catalogo_incluye_spati():
    _setup_api()
    from api_rest.faena_catalogo import get_faena, listar_faenas, estacion_ancla

    assert estacion_ancla("mantos") == "mb_rajo"
    ids = {x["id"] for x in listar_faenas()}
    assert "paipote" in ids and "mantos_blancos" in ids
    assert "escondida" in ids

    esc = get_faena("escondida")
    assert esc is not None
    assert esc["origen"] == "spati"
    assert esc["lat"] is not None and esc["lon"] is not None
    assert len(esc["estaciones_area"]) == 4
    assert "paquete_ambiental" in esc["capacidades"]

    solo = {x["id"] for x in listar_faenas(incluir_izaje=False)}
    assert "paipote" in solo and "escondida" not in solo


def test_estaciones_area_mantos_ids():
    _setup_api()
    from api_rest.faena_catalogo import get_faena, estaciones_area_faena

    f = get_faena("mantos_blancos")
    ids = {e["id"] for e in f["estaciones_area"]}
    assert "mb_rajo" in ids and "mb_campamento" in ids
    assert estaciones_area_faena("mantos")[0]["rol"] in (
        "rajo",
        "campamento",
        "chancado",
        "ruta",
        "botadero",
    )


def test_sync_estaciones_area_sin_supabase(monkeypatch):
    _setup_api()
    from api_rest.integracion import estaciones_area_store

    monkeypatch.setattr(estaciones_area_store, "_client", lambda: None)
    out = estaciones_area_store.sincronizar_desde_catalogo(solo_faena="escondida")
    assert out["puntos"] == 0
    assert out["supabase"] is False
    assert out["faenas"] == 1


def test_api_estaciones_area_endpoint():
    _setup_api()
    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/public/operaciones/faena/escondida/estaciones-area")
    assert r.status_code == 200
    body = r.get_json()
    assert body["faena_id"] == "escondida"
    assert body["n"] >= 4
    assert any(e["rol"] == "rajo" for e in body["estaciones_area"])


def test_modelo_vs_observado_m5():
    _setup_api()
    from api_rest.modelo_vs_observado_service import (
        _metricas_pares,
        reporte_modelo_vs_observado,
    )

    m = _metricas_pares(
        [
            {"fecha": "2026-07-20", "cams_pm10": 40.0, "sinca_pm10": 30.0},
            {"fecha": "2026-07-21", "cams_pm10": 50.0, "sinca_pm10": 40.0},
        ],
        ("pm10",),
    )
    assert m["pm10"]["sesgo_medio"] == 10.0

    rep = reporte_modelo_vs_observado("paipote", dias=7)
    assert rep is not None
    assert rep["faena_id"] == "paipote"
    assert rep["tipo_dato_observado"] == "observado"
    assert rep["estado"] in ("ok", "parcial", "sin_observado")
    assert "aire" in rep and "meteo" in rep and "iot" in rep

    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/public/operaciones/faena/paipote/modelo-vs-observado?dias=7")
    assert r.status_code == 200
    assert r.get_json()["tipo_dato_modelo"] == "modelo"


def test_umbrales_m3_evaluacion():
    _setup_api()
    from api_rest.umbrales_faena_service import (
        construir_serie_nival,
        evaluar_operaciones,
        mm_agua_a_cm_nieve,
    )

    assert mm_agua_a_cm_nieve(10, -15) == 12.0
    assert mm_agua_a_cm_nieve(10, 2) == 7.0

    verde = evaluar_operaciones(
        rafaga_ms=3.0,
        snowfall_hora_mm=0.0,
        acum_24h_cm=0.5,
        visibilidad_m=8000,
    )
    assert verde["nivel_global"] == "verde"

    rojo = evaluar_operaciones(
        rafaga_ms=12.0,
        snowfall_hora_mm=2.0,
        acum_24h_cm=20.0,
        visibilidad_m=100,
    )
    assert rojo["nivel_global"] == "rojo"
    assert rojo["actividades"]["izaje"]["nivel"] == "rojo"

    serie = construir_serie_nival(
        [
            {"fecha_hora": "2026-07-28T00:00", "snowfall": 1.0, "temperature_2m": -5},
            {"fecha_hora": "2026-07-28T01:00", "snowfall": 0.5, "temperature_2m": -5},
        ]
    )
    assert len(serie) == 2
    assert serie[1]["acum_desde_inicio_cm"] == 1.5
    assert serie[0]["flag_nieve"] is True


def test_informe_resumen_horizonte():
    _setup_api()
    from api_rest.informe_faena_service import resumen_horizonte, _tramos_3h

    pkg = {
        "serie_meteo": [
            {
                "fecha_hora": f"2026-07-28T{h:02d}:00",
                "wind_speed_10m": 5 + h * 0.1,
                "wind_gusts_10m": 8,
                "temperature_2m": 10,
                "visibility": 10000,
                "snowfall": 0.1 if h < 3 else 0,
            }
            for h in range(6)
        ],
        "serie_aire": [
            {"fecha_hora": f"2026-07-28T{h:02d}:00", "pm2_5": 12, "pm10": 20, "sulphur_dioxide": 1, "nitrogen_dioxide": 2}
            for h in range(6)
        ],
    }
    r = resumen_horizonte(pkg)
    assert r["n_horas_meteo"] == 6
    assert r["snowfall_mm_suma"] == 0.3
    assert r["viento_10m_ms"]["max"] is not None
    tr = _tramos_3h(pkg["serie_meteo"], pkg["serie_aire"], n=2)
    assert len(tr) == 2
    assert tr[0]["viento_ms"] is not None


def test_api_paquete_ambiental_y_informe_mock():
    _setup_api()
    from api_rest.app import create_app

    fake = {
        "faena_id": "escondida",
        "nombre": "Escondida",
        "lat": -24.27,
        "lon": -69.07,
        "estaciones_area": [],
        "capacidades": ["izaje", "paquete_ambiental"],
        "generado_en": "2026-07-28T12:00:00-04:00",
        "horizonte_horas": 72,
        "fuente": {"meteo": "openmeteo_forecast", "aire": "openmeteo_cams", "tipo_dato": "modelo"},
        "actual": {
            "temperatura_c": 5.0,
            "humedad_relativa_pct": 40,
            "precipitacion_mm": 0,
            "snowfall_mm": 0.1,
            "viento_10m_ms": 8.2,
            "viento_10m_dir_deg": 220,
            "rafaga_10m_ms": 12.0,
            "pm2_5": 12.0,
            "pm10": 25.0,
            "so2": 1.0,
            "no2": 3.0,
            "icap": 24,
            "nivel_icap": "Bueno",
        },
        "nieve": {
            "snowfall_mm_acum_horizonte": 1.2,
            "acumulacion_proxy_cm": 1.2,
            "acumulacion_24h_cm": 0.8,
            "nota": "proxy",
        },
        "operaciones": {
            "nivel_global": "verde",
            "actividades": {
                "izaje": {"nivel": "verde", "razones": []},
                "caminos": {"nivel": "verde", "razones": []},
                "botaderos": {"nivel": "verde", "razones": []},
            },
        },
        "flags": {
            "nivel_global": "verde",
            "flag_nieve_activa": False,
            "flag_izaje_restringido": False,
            "flag_caminos_restringido": False,
            "flag_botaderos_restringido": False,
        },
        "serie_nival": [],
        "serie_meteo": [],
        "serie_aire": [],
    }

    c = create_app().test_client()
    with patch(
        "api_rest.paquete_ambiental_service.construir_paquete_ambiental",
        return_value=fake,
    ):
        r = c.get("/api/public/operaciones/faena/escondida/paquete-ambiental")
        assert r.status_code == 200
        body = r.get_json()
        assert body["faena_id"] == "escondida"
        assert "actual" in body

        rh = c.get("/api/public/operaciones/faena/escondida/informe?formato=html")
        assert rh.status_code == 200
        assert "text/html" in rh.content_type
        assert b"Escondida" in rh.data or b"informe" in rh.data.lower()

    rl = c.get("/api/public/operaciones/faenas")
    assert rl.status_code == 200
    assert any(f["id"] == "escondida" for f in rl.get_json()["faenas"])

    r404 = c.get("/api/public/operaciones/faena/no_existe/paquete-ambiental")
    assert r404.status_code == 404

    ru = c.get("/api/public/operaciones/umbrales-operativos")
    assert ru.status_code == 200
    assert "izaje" in ru.get_json()["umbrales"]
def test_informe_csv_y_formatos():
    _setup_api()
    from unittest.mock import patch

    from api_rest.app import create_app
    from api_rest.informe_faena_service import construir_informe_csv, construir_mvo_csv

    fake_pkg = {
        "faena_id": "escondida",
        "nombre": "Escondida",
        "lat": -24.27,
        "lon": -69.07,
        "altitud_m": 3075,
        "generado_en": "2026-07-28T12:00:00-04:00",
        "horizonte_horas": 72,
        "fuente": {"tipo_dato": "modelo"},
        "actual": {"temperatura_c": 5.0, "pm2_5": 12.0, "pm10": 25.0},
        "nieve": {"acumulacion_24h_cm": 0.5},
        "flags": {"nivel_global": "verde", "flag_nieve_activa": False},
        "operaciones": {"actividades": {"izaje": {"nivel": "verde", "razones": []}}},
        "estaciones_area": [
            {"id": "escondida_rajo", "rol": "rajo", "lat": -24.27, "lon": -69.07, "fuente": "modelo"}
        ],
        "serie_meteo": [
            {
                "fecha_hora": "2026-07-28T00:00",
                "temperature_2m": 5.0,
                "snowfall": 0.1,
                "wind_speed_10m": 8.0,
                "wind_gusts_10m": 12.0,
                "wind_direction_10m": 200,
                "visibility": 10000,
                "relative_humidity_2m": 40,
                "precipitation": 0,
            }
        ],
        "serie_aire": [{"fecha_hora": "2026-07-28T00:00", "pm2_5": 12, "pm10": 25}],
        "serie_nival": [
            {
                "fecha_hora": "2026-07-28T00:00",
                "snowfall_mm": 0.1,
                "snowfall_cm": 0.1,
                "acum_rolling_24h_cm": 0.1,
            }
        ],
    }
    fake_mvo = {
        "faena_id": "escondida",
        "nombre": "Escondida",
        "estacion_id": "escondida_rajo",
        "estado": "sin_observado",
        "dias": 14,
        "aire": {"pares": [], "n_pares": 0},
        "meteo": {"pares": []},
        "iot": {"n_lecturas": 0},
    }
    with patch(
        "api_rest.paquete_ambiental_service.construir_paquete_ambiental",
        return_value=fake_pkg,
    ), patch(
        "api_rest.modelo_vs_observado_service.reporte_modelo_vs_observado",
        return_value=fake_mvo,
    ):
        csv_doc = construir_informe_csv("escondida")
        assert csv_doc is not None
        assert "fecha_hora" in csv_doc
        assert "tipo_dato" in csv_doc
        assert construir_mvo_csv("escondida", dias=7) is not None

    c = create_app().test_client()
    with patch(
        "api_rest.paquete_ambiental_service.construir_paquete_ambiental",
        return_value=fake_pkg,
    ), patch(
        "api_rest.modelo_vs_observado_service.reporte_modelo_vs_observado",
        return_value=fake_mvo,
    ):
        rcsv = c.get("/api/public/operaciones/faena/escondida/informe?formato=csv")
        assert rcsv.status_code == 200
        assert "text/csv" in rcsv.content_type
        assert b"fecha_hora" in rcsv.data
        assert c.get("/api/public/operaciones/faena/escondida/informe?formato=xlsx").status_code == 400
        rmvo = c.get("/api/public/operaciones/faena/escondida/modelo-vs-observado?formato=csv")
        assert rmvo.status_code == 200
        assert "text/csv" in rmvo.content_type


def test_m7_demo_observado_y_status():
    _setup_api()
    from unittest.mock import patch

    from api_rest.app import create_app
    from api_rest import m7_observado_service

    with patch("api_rest.integracion.aire_store.guardar_aire", return_value=7), patch(
        "api_rest.iot_services.registrar_lectura", return_value={"ok": True}
    ):
        out = m7_observado_service.activar_demo_observado("paipote", dias=5)
        assert out["ok"] is True
        assert out["total_observado"] >= 7
        assert "paipote" in out["faenas"]

    with patch(
        "api_rest.modelo_vs_observado_service.reporte_modelo_vs_observado",
        return_value={
            "faena_id": "paipote",
            "estado": "ok",
            "aire": {"n_pares": 5, "n_modelo": 5, "n_observado": 5, "pm10": {"sesgo_medio": 8.0}},
            "iot": {"n_lecturas": 6, "estado": "ok"},
            "guia": {},
        },
    ):
        st = m7_observado_service.estado_observado_faena("paipote")
        assert st["listo_produccion"] is True
        assert st["documentos"]["csv"].endswith("formato=csv")

    c = create_app().test_client()
    with patch("api_rest.integracion.aire_store.guardar_aire", return_value=3), patch(
        "api_rest.iot_services.registrar_lectura", return_value={}
    ):
        r = c.post("/api/cron/faena/demo-observado?faena=paipote&dias=3")
        assert r.status_code == 200
        assert r.get_json()["ok"] is True

    rs = c.get("/api/public/operaciones/faena/paipote/observado-status")
    assert rs.status_code == 200
    assert "estado_mvo" in rs.get_json()
