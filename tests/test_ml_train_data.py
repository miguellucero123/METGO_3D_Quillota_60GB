#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Entrenamiento ML: datos reales por defecto, sintético opt-in."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths

metgo_paths.setup_paths("05_api_rest")
_apis = metgo_paths.MODULE_PATHS["05_api_rest"]
if str(_apis) not in sys.path:
    sys.path.insert(0, str(_apis))


def test_allow_synthetic_off_by_default(monkeypatch):
    monkeypatch.delenv("METGO_ML_ALLOW_SYNTHETIC", raising=False)
    from api_rest.integracion import ml_train_runner as tr

    assert tr._allow_synthetic() is False


def test_obtener_filas_sin_sintetico_si_no_hay_reales(monkeypatch):
    monkeypatch.delenv("METGO_ML_ALLOW_SYNTHETIC", raising=False)
    from api_rest.integracion import ml_train_runner as tr

    monkeypatch.setattr(tr, "_filas_desde_meteo", lambda *a, **k: [])
    monkeypatch.setattr(
        tr,
        "_sincronizar_datos_reales",
        lambda *a, **k: {"csv": {"importados": 0}, "openmeteo_filas": 0},
    )
    filas, origen, _ = tr._obtener_filas_entrenamiento("quillota", 30)
    assert filas == []
    assert origen == "sin_datos_reales"


def test_manifest_incluye_provenance(monkeypatch, tmp_path):
    monkeypatch.setenv("METGO_ML_ALLOW_SYNTHETIC", "1")
    from api_rest.integracion import ml_train_runner as tr

    monkeypatch.setattr(tr, "_manifest_path", lambda: tmp_path / "model_manifest.json")
    filas_fake = [
        {
            "fecha": "2024-01-01",
            "temperatura_max": 20,
            "temperatura_min": 8,
            "humedad": 60,
            "precipitacion": 0,
            "viento": 5,
            "presion": 1013,
        }
        for _ in range(40)
    ]
    monkeypatch.setattr(
        tr,
        "_obtener_filas_entrenamiento",
        lambda *a, **k: (filas_fake, "sintetico_ci", None),
    )
    monkeypatch.setattr(tr, "catalogo_completo", lambda: [])
    out = tr.entrenar_todos("quillota", 30)
    assert out["filas"] == 40
    manifest = (tmp_path / "model_manifest.json").read_text(encoding="utf-8")
    assert "provenance" in manifest
    assert "origen_datos" in manifest
