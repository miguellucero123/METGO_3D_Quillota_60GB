#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests: índice MJO real (ROMI) — parseo, fase, ajuste de precipitación."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("METGO_JWT_SECRET", "test-secret-mjo-index-min-32-bytes!!!!")

from api_rest.spati import mjo_index_service as mjo


def test_parsear_ultima_linea_valida():
    texto = "2026 9 10 0 -0.32573 0.27723 0.42774\n2026 9 11 0 -0.34214 0.37268 0.50591\n"
    reg = mjo._parsear_ultima_linea_valida(texto)
    assert reg["fecha"] == "2026-09-11"
    assert reg["pc1"] == -0.34214
    assert reg["amplitud"] == 0.5059


def test_parsear_lineas_invalidas_devuelve_none():
    assert mjo._parsear_ultima_linea_valida("basura\nmas basura") is None


def test_fase_desde_pc_ocho_sectores():
    # angulo 0 grados (pc1>0, pc2=0) -> sector 1 (0-45)
    assert mjo._fase_desde_pc(1.0, 0.0) == 1
    # angulo ~90 grados -> sector 3 (90-135)
    assert mjo._fase_desde_pc(0.0, 1.0) == 3
    # angulo ~270 grados -> sector 7 (270-315)
    assert mjo._fase_desde_pc(0.0, -1.0) == 7


def test_factor_ajuste_precipitacion_inactivo():
    out = mjo.factor_ajuste_precipitacion(fase=3, amplitud=0.5)
    assert out["activo"] is False
    assert out["factor"] == 1.0


def test_factor_ajuste_precipitacion_activo_acotado():
    for fase in range(1, 9):
        out = mjo.factor_ajuste_precipitacion(fase=fase, amplitud=1.5)
        assert out["activo"] is True
        assert 0.85 <= out["factor"] <= 1.15


def test_ajustar_precipitacion_mjo_expone_base_y_ajustada():
    out = mjo.ajustar_precipitacion_mjo(10.0, fase=2, amplitud=1.5)
    assert out["precipitacion_base_mm"] == 10.0
    assert out["precipitacion_ajustada_mjo_mm"] == pytest.approx(11.0)


def test_obtener_indice_mjo_real_fallback_sin_red(monkeypatch, tmp_path):
    def boom(*a, **k):
        raise RuntimeError("sin red")

    monkeypatch.setattr(mjo.requests, "get", boom)
    monkeypatch.setattr(mjo, "_runtime_cache_path", lambda: tmp_path / "no_existe.txt")
    mjo._MEM_CACHE["registro"] = None
    mjo._MEM_CACHE["ts"] = 0.0

    out = mjo.obtener_indice_mjo_real(forzar_refresh=True)
    assert out["disponible"] is False
    assert "motivo" in out


def test_obtener_indice_mjo_real_usa_cache_memoria(monkeypatch, tmp_path):
    llamadas = {"n": 0}

    def fake_get(url, timeout=None):
        llamadas["n"] += 1

        class R:
            text = "2026 9 11 0 -0.34214 0.37268 0.50591\n"

            def raise_for_status(self):
                return None

        return R()

    monkeypatch.setattr(mjo.requests, "get", fake_get)
    monkeypatch.setattr(mjo, "_runtime_cache_path", lambda: tmp_path / "romi_lastgood.txt")
    mjo._MEM_CACHE["registro"] = None
    mjo._MEM_CACHE["ts"] = 0.0

    out1 = mjo.obtener_indice_mjo_real()
    out2 = mjo.obtener_indice_mjo_real()
    assert out1["disponible"] is True
    assert out2["desde_cache"] is True
    assert llamadas["n"] == 1
