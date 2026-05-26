#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Puente integración → ml_registry_core (módulo 06)."""

from __future__ import annotations

from typing import Any

from api_rest import ml_registry_core as core


def _registry_path():
    return core._registry_path()


def sincronizar_registro() -> dict[str, Any]:
    return core.sincronizar_registro(forzar=True)


def leer_registro() -> dict[str, Any]:
    return core.leer_registro()


def prediccion_batch(variables: list[str] | None, estacion_id: str = "quillota") -> list[dict[str, Any]]:
    reg = leer_registro()
    servibles = [m for m in reg.get("modelos", []) if m.get("servible")]
    vars_target = variables or [m["variable"] for m in servibles[:8]]
    out = []
    for var in vars_target:
        pred = core.predecir_registrado(var, estacion_id)
        out.append(
            {
                "variable": var,
                "ok": "error" not in pred,
                "prediccion": pred,
            }
        )
    return out
