#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Puente al motor agrícola del módulo 02."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd


def _setup_agricola() -> None:
    for p in Path(__file__).resolve().parents:
        scripts = p / "backend" / "02_Sistema_Agricola" / "scripts"
        if scripts.is_dir() and str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
            return


def meteo_a_dataframe(filas: list[dict[str, Any]]) -> pd.DataFrame:
    if not filas:
        return pd.DataFrame()
    rows = []
    for r in filas:
        tmax = float(r.get("temperatura_max") or 0)
        tmin = float(r.get("temperatura_min") or 0)
        fecha = r.get("fecha") or r.get("actualizado") or datetime_now_iso()[:10]
        rows.append(
            {
                "fecha": pd.to_datetime(fecha),
                "temperatura": (tmax + tmin) / 2,
                "temperatura_min": tmin,
                "temperatura_max": tmax,
                "humedad_relativa": float(r.get("humedad") or 0),
                "precipitacion": float(r.get("precipitacion") or 0),
                "velocidad_viento": float(r.get("viento") or 0),
            }
        )
    return pd.DataFrame(rows)


def datetime_now_iso() -> str:
    from datetime import datetime

    return datetime.now().isoformat()


def reporte_integral(filas_meteo: list[dict[str, Any]]) -> dict[str, Any]:
    _setup_agricola()
    try:
        from sistema_recomendaciones_agricolas_avanzado import SistemaRecomendacionesAvanzado
    except ImportError as e:
        return {"error": f"Modulo 02 no disponible: {e}"}

    df = meteo_a_dataframe(filas_meteo)
    if df.empty:
        return {"error": "Sin datos meteorológicos para análisis agrícola"}

    sistema = SistemaRecomendacionesAvanzado()
    reporte = sistema.generar_reporte_integral(df)
    return _json_safe(reporte)


def recomendaciones_lista(filas_meteo: list[dict[str, Any]], estacion_slug: str) -> list[dict[str, Any]]:
    """Convierte reporte integral a lista tipo API legacy."""
    rep = reporte_integral(filas_meteo)
    if rep.get("error"):
        return [{"cultivo": "General", "accion": "Sin análisis", "motivo": rep["error"]}]

    out: list[dict[str, Any]] = []
    resumen = rep.get("resumen_ejecutivo") or {}
    for msg in resumen.get("recomendaciones_principales") or []:
        out.append({"cultivo": "Integral", "accion": msg, "motivo": "Resumen ejecutivo módulo 02"})

    heladas = rep.get("analisis_heladas") or {}
    for eid, data in heladas.items():
        if eid.replace("_", "") not in estacion_slug.replace("_", "") and estacion_slug not in eid:
            continue
        riesgo = data.get("riesgo") or {}
        if riesgo.get("nivel") in ("alto", "medio"):
            out.append(
                {
                    "cultivo": "Heladas",
                    "accion": "Protección antihielo",
                    "motivo": f"Riesgo {riesgo.get('nivel')} ({riesgo.get('probabilidad', 0):.0f}%)",
                }
            )
        for rec in (data.get("recomendaciones") or [])[:2]:
            out.append(
                {
                    "cultivo": "Heladas",
                    "accion": rec.get("accion", "Revisar"),
                    "motivo": rec.get("descripcion", ""),
                }
            )

    if not out:
        out.append(
            {
                "cultivo": "General",
                "accion": "Monitoreo rutinario",
                "motivo": "Sin alertas críticas en motor avanzado 02",
            }
        )
    return out[:12]


def _json_safe(obj: Any) -> Any:
    import numpy as np

    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(x) for x in obj]
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return obj
