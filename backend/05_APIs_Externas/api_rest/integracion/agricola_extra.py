#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Riego, cultivos y análisis económico (módulo 02) vía API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CULTIVOS_QUILLOTA = [
    {"id": "palto", "nombre": "Palto", "riego_mm_dia_base": 8},
    {"id": "uva", "nombre": "Uva de mesa", "riego_mm_dia_base": 6},
    {"id": "citricos", "nombre": "Cítricos", "riego_mm_dia_base": 7},
    {"id": "hortalizas", "nombre": "Hortalizas", "riego_mm_dia_base": 5},
    {"id": "cereales", "nombre": "Cereales", "riego_mm_dia_base": 4},
]


def listar_cultivos() -> list[dict[str, Any]]:
    return CULTIVOS_QUILLOTA


def recomendacion_riego(resumen_meteo: dict[str, Any], cultivo_id: str = "palto") -> dict[str, Any]:
    cultivo = next((c for c in CULTIVOS_QUILLOTA if c["id"] == cultivo_id), CULTIVOS_QUILLOTA[0])
    hum = float(resumen_meteo.get("humedad") or 50)
    precip = float(resumen_meteo.get("precipitacion") or 0)
    temp = float(resumen_meteo.get("temperatura") or resumen_meteo.get("temperatura_max") or 20)
    deficit = max(0, 70 - hum)
    mm = cultivo["riego_mm_dia_base"] * (1 + deficit / 100)
    if precip > 2:
        mm *= 0.3
    if temp > 32:
        mm *= 1.15
    accion = "riego_recomendado" if mm >= 4 else "suspender_riego"
    return {
        "cultivo": cultivo,
        "mm_sugeridos_hoy": round(mm, 1),
        "accion": accion,
        "motivo": f"Humedad {hum:.0f}%, precipitación {precip:.1f} mm, T {temp:.1f}°C",
        "modulo": "02_riego_inteligente",
        "integrado": True,
    }


def analisis_economico(estacion_id: str) -> dict[str, Any]:
    for p in Path(__file__).resolve().parents:
        reportes = p / "backend" / "07_Sistema_Monitoreo" / "reportes" / "reportes"
        if reportes.is_dir():
            for f in sorted(reportes.glob("expansion_regional*.json"), reverse=True):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    return {
                        "estacion_id": estacion_id,
                        "fuente": f.name,
                        "regiones": len(data.get("regiones", data.get("estaciones", []))),
                        "resumen": data.get("resumen", data.get("titulo", "Expansión regional METGO")),
                        "integrado": True,
                    }
                except (json.JSONDecodeError, OSError):
                    continue
    return {
        "estacion_id": estacion_id,
        "integrado": True,
        "nota": "Proyección demo: ahorro riego 12%, reducción heladas 8%",
        "ahorro_estimado_clp_mes": 450000,
    }
