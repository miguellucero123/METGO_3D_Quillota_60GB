#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests: clasificación de estabilidad atmosférica (Pasquill) y corriente
superficial por viento con profundidad de Ekman real (Thorade)."""

from __future__ import annotations

import math
import os

import pytest

os.environ.setdefault("METGO_JWT_SECRET", "test-secret-estabilidad-min-32-bytes!")

from api_rest.spati.physics_engine import (
    clasificar_estabilidad_pasquill,
    corriente_superficial_por_viento,
    exponente_estabilidad,
    extrapolar_power_law_estabilidad,
    profundidad_ekman_m,
)


def test_dia_viento_debil_cielo_despejado_es_inestable():
    clase = clasificar_estabilidad_pasquill(1.5, 20.0, True)
    assert clase in ("A", "B")


def test_dia_viento_fuerte_es_neutro():
    clase = clasificar_estabilidad_pasquill(6.0, 50.0, True)
    assert clase == "D"


def test_noche_viento_debil_cielo_despejado_es_muy_estable():
    clase = clasificar_estabilidad_pasquill(1.0, 10.0, False)
    assert clase == "F"


def test_noche_cielo_cubierto_tiende_a_neutro():
    clase = clasificar_estabilidad_pasquill(2.5, 80.0, False)
    assert clase == "D"


def test_exponente_estabilidad_ordenado_por_severidad():
    # Estable (F) debe tener mayor cizalle (exponente) que inestable (A)
    assert exponente_estabilidad("F") > exponente_estabilidad("D")
    assert exponente_estabilidad("D") > exponente_estabilidad("A")


def test_extrapolar_power_law_estabilidad_mayor_en_condiciones_estables():
    # Mismo viento base, pero de noche/calma (estable) el exponente es mayor
    # -> a 100m el viento estable debe ser MAYOR que el neutro/inestable
    # relativo a la base (mayor cizalle vertical en capas estables).
    estable = extrapolar_power_law_estabilidad(
        5.0, 100.0, wind_speed_10m_ms=1.0, cloud_cover_pct=10.0, is_day=False
    )
    inestable = extrapolar_power_law_estabilidad(
        5.0, 100.0, wind_speed_10m_ms=1.0, cloud_cover_pct=10.0, is_day=True
    )
    assert estable["clase_estabilidad"] == "F"
    assert inestable["clase_estabilidad"] in ("A", "B")
    assert estable["v_ms"] > inestable["v_ms"]


def test_extrapolar_power_law_altura_invalida():
    with pytest.raises(ValueError):
        extrapolar_power_law_estabilidad(5.0, 0.0)


def test_profundidad_ekman_depende_de_latitud():
    # Mismo viento, mayor latitud -> mayor sin(lat) -> MENOR profundidad Ekman
    d_baja_lat = profundidad_ekman_m(10.0, 20.0)
    d_alta_lat = profundidad_ekman_m(10.0, 33.58)
    assert d_baja_lat > d_alta_lat > 0


def test_profundidad_ekman_formula_thorade():
    # D_E = 7.6*W/sqrt(sin(lat))
    w, lat = 8.0, 30.0
    esperado = 7.6 * w / math.sqrt(math.sin(math.radians(30.0)))
    assert profundidad_ekman_m(w, lat) == pytest.approx(esperado, rel=1e-6)


def test_corriente_superficial_magnitud_2pct_viento():
    out = corriente_superficial_por_viento(10.0, 90.0, -20.0)
    # 2% de 10 m/s = 0.2 m/s = 0.3889 kn
    assert out["speed_surface_kn"] == pytest.approx(0.2 * 1.94384, abs=0.01)
    assert out["profundidad_ekman_m"] > 0
    assert out["fuente"] == "parametrizacion_viento_ekman_thorade"


def test_corriente_desviacion_difiere_por_hemisferio():
    sur = corriente_superficial_por_viento(10.0, 0.0, -20.0)
    norte = corriente_superficial_por_viento(10.0, 0.0, 20.0)
    assert sur["direction_surface_deg"] != norte["direction_surface_deg"]
