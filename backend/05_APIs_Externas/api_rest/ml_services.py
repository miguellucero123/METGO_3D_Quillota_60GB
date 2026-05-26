#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MLOps: catálogo y predicción vía ml_registry (módulo 06)."""

from __future__ import annotations

from typing import Any

from api_rest import ml_registry_core as registry


def listar_modelos() -> list[dict[str, Any]]:
    """Lista modelos desde registro (servible / no servible)."""
    try:
        return registry.listar_desde_registro()
    except Exception:
        return registry.sincronizar_registro().get("modelos", [])


def predecir(variable: str, estacion_id: str = "quillota") -> dict[str, Any]:
    """Predice solo si el modelo pasó sanity-check (servible)."""
    return registry.predecir_registrado(variable, estacion_id)


def resumen_mlops() -> dict[str, Any]:
    base = registry.resumen_registro()
    modelos = listar_modelos()
    base["variables"] = [m["variable"] for m in modelos if m.get("servible")]
    base["disponibles"] = base.get("servibles", 0)
    return base


def sincronizar_registro() -> dict[str, Any]:
    return registry.sincronizar_registro(forzar=True)


def leer_registro() -> dict[str, Any]:
    return registry.leer_registro()
