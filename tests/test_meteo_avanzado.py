#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests modelos y core de meteorología avanzada."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths

metgo_paths.setup_paths("01_meteo", "05_api_rest")
_apis = metgo_paths.MODULE_PATHS["05_api_rest"]
if str(_apis) not in sys.path:
    sys.path.insert(0, str(_apis))

from api_rest.meteo_avanzado import (
    AnalizadorNubosidad,
    ModeloHeladaRadiativa,
    PredictorNiebla,
    calcular_bulbo_humedo,
    calcular_punto_rocio,
    evaluar_criterio_psicrometro,
)
from api_rest.meteo_avanzado_core import (
    _riesgo_helada_simple,
    _riesgo_niebla_simple,
    estimar_visibilidad_km,
    validar_estacion,
)


def test_calcular_punto_rocio_saturacion():
    pr = calcular_punto_rocio(20.0, 100.0)
    assert pr == pytest.approx(20.0, abs=1.0)


def test_calcular_bulbo_humedo_entre_td_y_t():
    t, hr = 10.0, 70.0
    td = calcular_punto_rocio(t, hr)
    th = calcular_bulbo_humedo(t, hr)
    assert td <= th <= t


def test_criterio_psicrometro_riesgo_inminente():
    crit = evaluar_criterio_psicrometro(
        punto_rocio=-1.0,
        bulbo_humedo=1.5,
        cobertura_nubosa=5,
        velocidad_viento=0.5,
    )
    assert crit["riesgo_inminente"] is True
    assert crit["nivel"] == "inminente"


def test_modelo_helada_alto_riesgo_cielo_despejado():
    modelo = ModeloHeladaRadiativa("quillota")
    res = modelo.calcular_riesgo_helada(
        temperatura_pronosticada=18,
        temperatura_minima_pronosticada=-3,
        cobertura_nubosa=5,
        velocidad_viento=0.8,
        humedad_relativa=88,
        punto_rocio=-4,
        fecha=datetime.now(ZoneInfo("America/Santiago")),
        temperatura_atardecer=6.0,
        bulbo_humedo=1.5,
    )
    assert res["probabilidad_helada"] > 50
    assert res["riesgo_severo"] or res["riesgo_moderado"]
    assert res["riesgo_inminente"] is True
    assert len(res["factores_contribuyentes"]) >= 2
    assert "criterio_psicrometro" in res


def test_modelo_helada_bajo_riesgo():
    modelo = ModeloHeladaRadiativa("quillota")
    res = modelo.calcular_riesgo_helada(
        temperatura_pronosticada=25,
        temperatura_minima_pronosticada=12,
        cobertura_nubosa=90,
        velocidad_viento=12,
        humedad_relativa=40,
        punto_rocio=5,
        fecha=datetime.now(ZoneInfo("America/Santiago")),
        temperatura_atardecer=20.0,
        bulbo_humedo=12.0,
    )
    assert res["probabilidad_helada"] < 30
    assert res["riesgo_inminente"] is False


def test_analizador_nubosidad_clasificacion():
    assert AnalizadorNubosidad.clasificar_cobertura(5).value == "despejado"
    assert AnalizadorNubosidad.clasificar_cobertura(85).value == "muy_nublado"


def test_analizador_radiacion_menor_con_nubes():
    despejado = AnalizadorNubosidad.estimar_radiacion_solar(800, 5)
    nublado = AnalizadorNubosidad.estimar_radiacion_solar(800, 90)
    assert despejado["radiacion_global_superficie"] > nublado["radiacion_global_superficie"]


def test_predictor_niebla_alta_probabilidad():
    pred = PredictorNiebla("quillota")
    res = pred.predecir_niebla(
        temperatura=4,
        humedad_relativa=96,
        visibilidad_pronosticada=0.4,
        velocidad_viento=0.3,
        punto_rocio=3.8,
        hora_del_dia=5,
        cobertura_nubosa=85,
        fecha_iso="2026-06-03",
    )
    assert res["probabilidad_niebla"] > 40
    assert res["severidad"] in ("densa", "muy_densa", "moderada")


def test_validar_estacion_invalida():
    with pytest.raises(ValueError):
        validar_estacion("estacion_inexistente")


def test_riesgos_simples():
    assert _riesgo_helada_simple(-6) == "CRÍTICO"
    assert _riesgo_niebla_simple(90, 3.5, 3.8) == "ALTO"


def test_estimar_visibilidad_baja():
    vis = estimar_visibilidad_km(3, 95, 2.8)
    assert vis < 1.0


def test_visibilidad_hourly_openmeteo():
    from datos_reales_openmeteo import OpenMeteoData

    om = OpenMeteoData()
    data = {
        "hourly": {
            "time": [
                "2026-06-03T03:00",
                "2026-06-03T05:00",
                "2026-06-03T12:00",
                "2026-06-04T04:00",
            ],
            "visibility": [800, 500, 10000, 1200],
        }
    }
    stats = om._visibilidad_diaria_desde_hourly(data)
    assert len(stats) == 2
    first = list(stats.values())[0]
    assert first["min"] == pytest.approx(0.5, abs=0.01)
    assert first["madrugada"] == pytest.approx(0.5, abs=0.01)


def test_helada_desde_fila_deriva_tmin():
    import importlib

    repo = importlib.import_module("backend.08_Gestion_Datos.supabase_db.meteo_repository")
    assert repo._helada_desde_fila({"temperatura_min": -1.2}) is True
    assert repo._helada_desde_fila({"temperatura_min": 3.0}) is False
    assert repo._helada_desde_fila({"helada": True, "temperatura_min": 5}) is True


def test_resumen_heladas_cuenta_riesgo():
    from api_rest.meteo_avanzado_core import _resumen_heladas

    resumen = _resumen_heladas(
        [
            {"probabilidad_helada": 55, "riesgo_severo": False, "riesgo_moderado": True, "temperatura_minima_esperada": -1},
            {"probabilidad_helada": 10, "riesgo_severo": False, "riesgo_moderado": False, "temperatura_minima_esperada": 4},
        ]
    )
    assert resumen["dias_con_riesgo"] == 1
    assert resumen["dias_riesgo_moderado"] == 1
    assert resumen["temperatura_minima_7d"] == -1
