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
    assert {
        "copiapo_centro",
        "paipote",
        "tierra_amarilla",
    } <= set(slugs_de_sitio("copiapo"))


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


def test_aire_store_mapeo_registro():
    _setup_api()
    from api_rest.integracion import aire_store

    fila = {
        "actualizado": "2026-07-23T15:00",
        "pm2_5": 80.0,
        "pm10": 120.0,
        "icap": 200.0,
        "nivel": "alerta",
    }
    reg = aire_store._fila_a_registro("copiapo_centro", fila, "openmeteo_cams", "modelo")
    assert reg is not None
    assert reg["estacion_id"] == "copiapo_centro"
    assert reg["fecha_hora"] == "2026-07-23T15:00"
    assert reg["pm25"] == 80.0
    assert reg["so2"] is None
    assert reg["categoria"] == "alerta"
    assert reg["tipo_dato"] == "modelo"

    # Fila diaria (sin hora) → mediodía local
    diaria = aire_store._fila_a_registro(
        "paipote", {"fecha": "2026-07-20", "pm2_5": 10.0, "pm10": 30.0}, "openmeteo_cams", "observado"
    )
    assert diaria["fecha_hora"] == "2026-07-20T12:00:00"

    # Sin marca temporal → descartada
    assert aire_store._fila_a_registro("paipote", {"pm2_5": 1.0}, "f", "modelo") is None


def test_api_public_aire_alertas():
    _setup_api()
    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/public/aire/alertas?sitio=copiapo")
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        body = r.get_json()
        assert body["sitio"] == "copiapo"
        assert "hay_alerta" in body
        assert isinstance(body["estaciones"], list)
        assert "umbral" in body


def test_sinca_stub_estado(monkeypatch):
    """E12.1: con ejemplos → listo_csv; sin ejemplos ni env → pendiente_fuente."""
    _setup_api()
    from api_rest import sinca_service
    from api_rest.app import create_app

    monkeypatch.delenv("METGO_SINCA_CSV_DIR", raising=False)
    monkeypatch.setenv("METGO_SINCA_USE_EJEMPLOS", "1")
    est = sinca_service.estado_sinca()
    assert est["fuente"] == "sinca_mma"
    assert est["estado"] == "listo_csv"
    assert est["csv_dir_origen"] == "ejemplos"
    assert est["estaciones_con_codigo"] == 0

    r = create_app().test_client().get("/api/public/aire/sinca/estado")
    assert r.status_code == 200
    assert r.get_json()["estado"] == "listo_csv"

    monkeypatch.setenv("METGO_SINCA_USE_EJEMPLOS", "0")
    est2 = sinca_service.estado_sinca()
    assert est2["estado"] == "pendiente_fuente"
    sync = sinca_service.sincronizar_sinca()
    assert sync.get("omitido") is True


def test_sinca_calcular_sesgo():
    _setup_api()
    from api_rest.sinca_service import calcular_sesgo

    metricas = calcular_sesgo(
        [
            {"fecha": "2026-07-20", "cams_pm10": 40.0, "sinca_pm10": 30.0, "cams_pm25": 12.0, "sinca_pm25": 10.0},
            {"fecha": "2026-07-21", "cams_pm10": 50.0, "sinca_pm10": 40.0, "cams_pm25": 14.0, "sinca_pm25": 10.0},
        ]
    )
    assert metricas["n_pares"] == 2
    assert metricas["pm10"]["sesgo_medio"] == 10.0
    assert metricas["pm25"]["mae"] == 3.0


def test_api_public_sinca_sesgo_y_fuentes_y_ml_dominios():
    _setup_api()
    from api_rest.app import create_app

    c = create_app().test_client()
    rs = c.get("/api/public/aire/sinca/sesgo?estacion_id=copiapo_centro")
    assert rs.status_code == 200
    body = rs.get_json()
    assert body["estacion_id"] == "copiapo_centro"
    assert "n_pares" in body

    rf = c.get("/api/public/datos/fuentes?sitio=copiapo")
    assert rf.status_code == 200
    fuentes = rf.get_json()
    assert fuentes["total"] >= 1
    assert any(f.get("proveedor") == "sinca_mma" for f in fuentes["fuentes"])

    rm = c.get("/api/public/ml/dominios?sitio=copiapo")
    assert rm.status_code == 200
    ml = rm.get_json()
    assert ml["total"] >= 1
    assert ml["servibles"] >= 1
    assert any(m["id"] == "pm10_episodio_copiapo" and m.get("servible") for m in ml["modelos"])


def test_sinca_csv_ingest(tmp_path, monkeypatch):
    _setup_api()
    from pathlib import Path
    import shutil
    from api_rest import sinca_service

    fixture = Path(__file__).resolve().parent / "fixtures" / "sinca"
    dest = tmp_path / "sinca"
    dest.mkdir()
    shutil.copy(fixture / "copiapo_centro.csv", dest / "copiapo_centro.csv")
    monkeypatch.setenv("METGO_SINCA_CSV_DIR", str(dest))
    monkeypatch.setenv("METGO_SINCA_IDS", '{"copiapo_centro":"DEMO"}')

    # Sin Supabase: guardar_aire → 0, pero sync no debe omitir por sin_csv
    sync = sinca_service.sincronizar_sinca(["copiapo_centro"])
    assert sync.get("motivo") in (None, "csv_sin_filas")
    assert "copiapo_centro" in sync.get("sinca_sync", {})
    assert sinca_service.estado_sinca()["estaciones_con_codigo"] >= 1


def test_oficiales_dmc_csv(tmp_path, monkeypatch):
    _setup_api()
    from pathlib import Path
    import shutil
    from api_rest import oficiales_service

    fixture = Path(__file__).resolve().parent / "fixtures" / "dmc"
    dest = tmp_path / "dmc"
    dest.mkdir()
    shutil.copy(fixture / "quillota.csv", dest / "quillota.csv")
    monkeypatch.setenv("METGO_DMC_CSV_DIR", str(dest))
    monkeypatch.setenv("METGO_DMC_IDS", '{"quillota":"330007"}')

    filas = oficiales_service.fetch_dmc_historico("quillota", dias=10)
    assert len(filas) == 3
    assert filas[0]["fecha"] == "2026-07-20"
    assert filas[0]["temperatura_max"] == 18.5

    est = oficiales_service.estado_fuentes()
    assert est["dmc"]["disponible"] is True
    assert est["dmc"]["estaciones"]["quillota"]["codigo"] == "330007"

    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/public/datos/oficiales/estado")
    assert r.status_code == 200
    assert "agromet" in r.get_json()


def test_ml_pm10_episodio_baseline():
    _setup_api()
    from api_rest import ml_domain_service

    assert ml_domain_service._prob_desde_icap(100) < 0.5
    assert ml_domain_service._prob_desde_icap(200) >= 0.55
    assert ml_domain_service._prob_desde_icap(400) > 0.7

    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get(
        "/api/public/ml/dominios/pm10_episodio_copiapo/prediccion?estacion_id=copiapo_centro"
    )
    assert r.status_code == 200
    body = r.get_json()
    assert body["servible"] is True
    assert body["modo"] in ("sklearn_regresor", "baseline_regla")
    assert "prediccion" in body
    if body["modo"] == "sklearn_regresor" and body.get("prediccion"):
        assert "icap_predicho" in body["prediccion"]


def test_ml_viento_extremo_baseline():
    _setup_api()
    from api_rest import ml_domain_service

    out = ml_domain_service.prediccion_dominio(
        "viento_extremo_mantos", viento_ms=15.0
    )
    assert out["servible"] is True
    assert out["prediccion"]["extremo"] is True

    out2 = ml_domain_service.prediccion_dominio(
        "viento_extremo_paine", viento_ms=5.0
    )
    assert out2["prediccion"]["extremo"] is False


def test_ml_helada_baseline():
    _setup_api()
    from api_rest import ml_domain_service

    # Con o sin artefacto joblib: debe ser servible (baseline o sklearn).
    out = ml_domain_service.prediccion_helada_quillota("quillota", cultivo="palto")
    assert out["servible"] is True
    assert out["modo"] in ("sklearn_clasificador", "baseline_regla")
    if out["modo"] == "sklearn_clasificador" and out.get("prediccion"):
        assert "probabilidad" in out["prediccion"]
        assert "riesgo_helada" in out["prediccion"]

    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get(
        "/api/public/ml/dominios/helada_quillota/prediccion?estacion_id=quillota&cultivo=palto"
    )
    assert r.status_code == 200
    body = r.get_json()
    assert body["servible"] is True
    assert body["modo"] in ("sklearn_clasificador", "baseline_regla")


def test_etl_retry_queue(tmp_path, monkeypatch):
    _setup_api()
    from api_rest.integracion import etl_retry_queue

    qpath = tmp_path / "etl_retry_queue.jsonl"
    monkeypatch.setattr(etl_retry_queue, "_queue_path", lambda: qpath)
    monkeypatch.setattr(etl_retry_queue, "_drain_limit", lambda: 5)
    monkeypatch.setattr(etl_retry_queue, "_max_attempts", lambda: 3)

    etl_retry_queue.enqueue("sinca", "boom")
    assert etl_retry_queue.estado_cola()["pendientes"] == 1

    # Job omitido por sin_csv no debe quedar en cola
    monkeypatch.setattr(
        etl_retry_queue,
        "_resolver_job",
        lambda name: (lambda: {"omitido": True, "motivo": "sin_csv_dir"}),
    )
    out = etl_retry_queue.drain()
    assert out["ok"] >= 1
    assert etl_retry_queue.estado_cola()["pendientes"] == 0

    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/public/datos/etl/retry-queue")
    assert r.status_code == 200
    assert "pendientes" in r.get_json()


def test_sinca_circuit_breaker(monkeypatch):
    _setup_api()
    from api_rest import sinca_service

    monkeypatch.setattr(sinca_service, "_CB_FALLA", 0)
    monkeypatch.setattr(sinca_service, "_CB_HASTA", 0.0)
    monkeypatch.setattr(sinca_service, "_CB_UMBRAL", 2)
    monkeypatch.setattr(sinca_service, "_CB_COOLDOWN_S", 60)

    import api_rest.sinca_service as mod

    for _ in range(2):
        mod._cb_registrar_fallo()
    assert mod._cb_abierto() is True
    assert mod._fetch_csv_url("http://invalid/{slug}.csv", "copiapo_centro", None) == []


def test_artefacto_pm10_existe():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    joblib = (
        root
        / "backend"
        / "06_Modelos_ML_IA"
        / "modelos"
        / "modelos_dominio_copiapo"
        / "pm10_episodio.joblib"
    )
    meta = joblib.with_name("meta.json")
    assert joblib.is_file()
    assert meta.is_file()


# --------------------------------------------------- dispersión de contaminantes


def test_airshed_copiapo_siete_puntos():
    _setup_api()
    from api_rest.estaciones_catalogo import slugs_de_sitio

    slugs = set(slugs_de_sitio("copiapo"))
    assert len(slugs) >= 7
    assert {"copiapo_centro", "paipote", "tierra_amarilla", "chamonate",
            "la_chimba", "punta_del_cobre", "nantoco"} <= slugs


def test_categoria_viento():
    _setup_api()
    from api_rest.dispersion_service import categoria_viento

    assert categoria_viento(0.2) == "calma"
    assert categoria_viento(1.0) == "flojo"
    assert categoria_viento(2.0) == "leve"
    assert categoria_viento(4.0) == "moderado"
    assert categoria_viento(7.0) == "favorable"
    assert categoria_viento(12.0) == "fuerte"
    assert categoria_viento(None) is None


def test_clasificar_inversion():
    _setup_api()
    from api_rest.dispersion_service import clasificar_inversion

    # T sube con la altura (925 hPa más cálido que 2 m) → inversión
    inv = clasificar_inversion(temp_2m=8.0, temp_925=12.0, temp_850=10.0)
    assert inv["inversion"] is True
    assert inv["inversion_intensidad"] == 4.0

    # Perfil normal (T baja con altura) → sin inversión
    normal = clasificar_inversion(temp_2m=20.0, temp_925=14.0, temp_850=9.0)
    assert normal["inversion"] is False
    assert normal["inversion_intensidad"] == 0.0


def test_clasificar_nubosidad_niebla():
    _setup_api()
    from api_rest.dispersion_service import clasificar_nubosidad

    assert clasificar_nubosidad(90, 0.4, 98)["tipo_nubosidad"] == "niebla"
    assert clasificar_nubosidad(90, 0.4, 98)["niebla"] is True
    assert clasificar_nubosidad(20, 3.0, 90)["tipo_nubosidad"] == "neblina"
    assert clasificar_nubosidad(80, 8.0, 60)["tipo_nubosidad"] == "estratos"
    assert clasificar_nubosidad(10, 10.0, 40)["tipo_nubosidad"] == "despejado"


def test_indice_dispersion_extremos():
    _setup_api()
    from api_rest.dispersion_service import indice_dispersion

    # Calma + inversión fuerte + niebla → muy baja dispersión y alerta
    malo = indice_dispersion(0.3, 5.0, "niebla", 150)
    assert malo["potencial_dispersion"] in ("muy_baja", "baja")
    assert malo["alerta_dispersion"] is True

    # Viento fuerte, sin inversión, despejado, capa alta → buena/muy buena
    bueno = indice_dispersion(9.0, 0.0, "despejado", 1500)
    assert bueno["potencial_dispersion"] in ("buena", "muy_buena")
    assert bueno["alerta_dispersion"] is False


def test_api_dispersion_endpoints():
    _setup_api()
    from api_rest.app import create_app

    c = create_app().test_client()

    r404 = c.get("/api/public/aire/no_existe/dispersion")
    assert r404.status_code == 404

    r = c.get("/api/public/aire/copiapo_centro/dispersion?horas=24")
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        filas = r.get_json()
        assert isinstance(filas, list)
        if filas:
            assert "indice_dispersion" in filas[0]
            assert "potencial_dispersion" in filas[0]

    ra = c.get("/api/public/aire/dispersion/alertas?sitio=copiapo&horizonte=horaria")
    assert ra.status_code in (200, 503)
    if ra.status_code == 200:
        body = ra.get_json()
        assert body["horizonte"] == "horaria"
        assert "hay_alerta" in body


def test_api_airshed_modeler():
    """METGO Airshed Modeler (proxy AERMOD) — smoke endpoint."""
    _setup_api()
    from api_rest.app import create_app

    c = create_app().test_client()

    r404 = c.get("/api/public/aire/modelo/airshed?sitio=no_existe")
    assert r404.status_code == 404

    r = c.get("/api/public/aire/modelo/airshed?sitio=copiapo&nx=16&ny=16&frames=2")
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        body = r.get_json()
        assert body["modelo"] == "METGO-Airshed-v1"
        assert len(body["pipeline"]) == 5
        assert isinstance(body["frames"], list)
        assert len(body["frames"]) >= 1
        g0 = body["frames"][0]["grid"]
        assert "values" in g0
        assert "heat_geojson" in g0
        assert "wind_vectors" in g0
        assert g0["max"]["value"] >= 0
