#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resumen drones y satelital (módulo 03)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _drones_dir() -> Path | None:
    for p in Path(__file__).resolve().parents:
        d = p / "backend" / "03_Sistema_IoT_Drones" / "datos" / "datos_drones_optimizado" / "reportes"
        if d.is_dir():
            return d
    return None


def resumen_drones() -> dict[str, Any]:
    d = _drones_dir()
    if not d:
        return {"integrado": False, "vuelos": 0, "drones": []}
    ultimo = None
    for f in sorted(d.glob("reporte_drones_*.json"), reverse=True):
        try:
            ultimo = json.loads(f.read_text(encoding="utf-8"))
            break
        except (json.JSONDecodeError, OSError):
            continue
    if not ultimo:
        return {"integrado": True, "vuelos": 0, "drones": [], "reportes_html": len(list(d.glob("*.html")))}
    archivos = sorted(d.glob("reporte_drones_*.json"), reverse=True)
    return {
        "integrado": True,
        "archivo": archivos[0].name if archivos else None,
        "resumen": ultimo.get("resumen", ultimo.get("titulo", "Operaciones drones")),
        "vuelos": len(ultimo.get("vuelos", ultimo.get("operaciones", []))),
        "drones": ultimo.get("drones", []),
    }


def info_satelital() -> dict[str, Any]:
    for p in Path(__file__).resolve().parents:
        script = p / "backend" / "03_Sistema_IoT_Drones" / "scripts" / "datos_satelitales_metgo.py"
        if script.is_file():
            return {
                "integrado": True,
                "script": str(script.relative_to(p)),
                "capas": ["NDVI", "humedad_suelo", "temperatura_superficie"],
                "proveedor": "simulado_mvp",
            }
    return {"integrado": False}
