#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Riego, cultivos y análisis económico (módulo 02) vía API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CULTIVOS_QUILLOTA = [
    {"id": "palto", "nombre": "Palto", "riego_mm_dia_base": 8},
    {"id": "vid", "nombre": "Vid", "riego_mm_dia_base": 5},
    {"id": "citricos", "nombre": "Cítricos", "riego_mm_dia_base": 7},
    {"id": "tomate", "nombre": "Tomate", "riego_mm_dia_base": 10},
    {"id": "lechuga", "nombre": "Lechuga", "riego_mm_dia_base": 6},
    {"id": "hortalizas", "nombre": "Hortalizas", "riego_mm_dia_base": 5},
    {"id": "cereales", "nombre": "Cereales", "riego_mm_dia_base": 4},
]


def listar_cultivos() -> list[dict[str, Any]]:
    return CULTIVOS_QUILLOTA


def recomendacion_riego(
    resumen_meteo: dict[str, Any],
    cultivo_id: str = "palto",
    estacion_id: str | None = None,
) -> dict[str, Any]:
    cultivo = next((c for c in CULTIVOS_QUILLOTA if c["id"] == cultivo_id), CULTIVOS_QUILLOTA[0])
    hum = float(resumen_meteo.get("humedad") or 50)
    precip = float(resumen_meteo.get("precipitacion") or 0)
    temp = float(resumen_meteo.get("temperatura") or resumen_meteo.get("temperatura_max") or 20)
    t_min = float(resumen_meteo.get("temperatura_min") or 10)
    deficit = max(0, 70 - hum)
    mm = cultivo["riego_mm_dia_base"] * (1 + deficit / 100)
    cronograma = None
    if estacion_id:
        try:
            from api_rest import services

            cronograma = services.cronograma_riego_inteligente(estacion_id, cultivo_id)
        except Exception:
            cronograma = None
    if cronograma and cronograma.get("accion") == "posponer_riego":
        return {
            "cultivo": cultivo,
            "mm_sugeridos_hoy": 0,
            "accion": "posponer_riego",
            "dias_posponer": cronograma.get("dias_posponer", 2),
            "motivo": cronograma.get("motivo", "Lluvia esperada"),
            "precipitacion_48h_mm": cronograma.get("precipitacion_48h_mm"),
            "modulo": "02_riego_inteligente",
            "integrado": True,
            "fuente_pronostico": "calibrado",
        }
    if cronograma and cronograma.get("accion") == "suspender_riego_helada":
        return {
            "cultivo": cultivo,
            "mm_sugeridos_hoy": 0,
            "accion": "suspender_riego_helada",
            "motivo": cronograma.get("motivo"),
            "modulo": "02_riego_inteligente",
            "integrado": True,
        }
    if precip > 2:
        mm *= 0.3
    if temp > 32:
        mm *= 1.15
    if t_min <= 4:
        mm = 0
    accion = "riego_recomendado" if mm >= 4 else "suspender_riego"
    motivo = f"Humedad {hum:.0f}%, precipitación {precip:.1f} mm, T {temp:.1f}°C"
    if cronograma:
        motivo = f"{motivo}; pronóstico 48h: {cronograma.get('precipitacion_48h_mm', 0)} mm"
    return {
        "cultivo": cultivo,
        "mm_sugeridos_hoy": round(mm, 1),
        "accion": accion,
        "motivo": motivo,
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
