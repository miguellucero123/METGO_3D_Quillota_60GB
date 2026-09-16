#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests: cálculo real de resonancia pendular (T=2π√(L/g)) en izaje portuario."""

from __future__ import annotations

import math
import os

import pytest

os.environ.setdefault("METGO_JWT_SECRET", "test-secret-resonancia-min-32-bytes!!")

from api_rest.spati.physics_engine import (
    GRAVEDAD_MS2,
    evaluar_resonancia_pendular,
    periodo_pendulo_simple,
)


def test_periodo_pendulo_formula_fisica():
    # T = 2*pi*sqrt(L/g); para L=9.81 -> T = 2*pi segundos (caso trivial)
    t = periodo_pendulo_simple(GRAVEDAD_MS2)
    assert t == pytest.approx(2 * math.pi)


def test_periodo_pendulo_longitud_invalida():
    with pytest.raises(ValueError):
        periodo_pendulo_simple(0)
    with pytest.raises(ValueError):
        periodo_pendulo_simple(-5)


def test_evaluar_resonancia_detecta_coincidencia():
    # L=25m -> T_pendulo ~10.03s; oleaje Tp=10.1s -> deberian estar en resonancia
    out = evaluar_resonancia_pendular(25.0, 10.1, banda_alerta_s=1.5)
    assert out["en_resonancia"] is True
    assert out["periodo_pendulo_s"] == pytest.approx(10.03, abs=0.05)
    assert out["delta_s"] < 1.5


def test_evaluar_resonancia_sin_coincidencia():
    # L=5m -> T_pendulo ~4.49s; oleaje Tp=14s -> muy separados, sin resonancia
    out = evaluar_resonancia_pendular(5.0, 14.0, banda_alerta_s=1.5)
    assert out["en_resonancia"] is False
    assert out["delta_s"] > 1.5


def test_resonancia_depende_de_longitud_real_no_umbral_fijo():
    """Dos longitudes de cable distintas ante el mismo oleaje deben dar
    resultados distintos -- confirma que no es un umbral fijo desconectado
    de la operacion real (el bug que se corrige)."""
    tp = 12.0
    corto = evaluar_resonancia_pendular(10.0, tp)
    largo = evaluar_resonancia_pendular(50.0, tp)
    assert corto["periodo_pendulo_s"] != largo["periodo_pendulo_s"]
    assert corto["en_resonancia"] != largo["en_resonancia"] or corto["delta_s"] != largo["delta_s"]
