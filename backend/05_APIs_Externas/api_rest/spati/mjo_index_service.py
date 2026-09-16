#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Índice MJO real (NOAA/PSL ROMI) y ajuste heurístico de precipitación.

Fuente: NOAA Physical Sciences Laboratory, índice ROMI (Real-time OLR-based
MJO Index, Kiladis et al. 2014), texto público sin autenticación:
https://psl.noaa.gov/mjo/mjoindex/romi.cpcolr.1x.txt

Verificado en vivo el 2026-09-15: archivo accesible sin bloqueo, con datos
hasta ~3-4 días antes de la fecha de consulta (near-real-time). La fuente
alternativa BOM (bom.gov.au) bloquea peticiones no interactivas (HTTP 403)
y por eso no se usa como primaria.

Formato de cada línea: ``YYYY MM DD <flag> PC1 PC2 AMPLITUD``.

IMPORTANTE — honestidad científica: el "ajuste de precipitación" que expone
este módulo es una **heurística documentada y acotada**, no un modelo
dinámico validado. Se basa en la convención estándar de 8 fases MJO
(amplitud/fase vía PC1/PC2) y en la tendencia general, descrita en literatura
de teleconexiones MJO-Sudamérica, de mayor/menor actividad frontal sobre
Chile central según la fase activa. No reemplaza el pronóstico base: siempre
se expone también el valor sin ajustar.
"""

from __future__ import annotations

import logging
import math
import os
import time
from datetime import date
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

ROMI_URL = (
    os.getenv("METGO_MJO_ROMI_URL") or "https://psl.noaa.gov/mjo/mjoindex/romi.cpcolr.1x.txt"
).strip()
_TIMEOUT = int(os.getenv("METGO_MJO_TIMEOUT", "15"))
_CACHE_TTL_S = int(os.getenv("METGO_MJO_CACHE_TTL", str(6 * 3600)))  # 6 h: el índice se actualiza a diario

_MEM_CACHE: dict[str, Any] = {"ts": 0.0, "registro": None}


class MjoIndiceNoDisponibleError(RuntimeError):
    pass


def _runtime_cache_path() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            d = p / "backend" / "08_Gestion_Datos" / "datos_runtime" / "mjo"
            d.mkdir(parents=True, exist_ok=True)
            return d / "romi_lastgood.txt"
    d = Path("mjo_cache")
    d.mkdir(parents=True, exist_ok=True)
    return d / "romi_lastgood.txt"


def _parsear_ultima_linea_valida(texto: str) -> dict[str, Any] | None:
    for linea in reversed(texto.strip().splitlines()):
        partes = linea.split()
        if len(partes) < 6:
            continue
        try:
            anio, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
            pc1, pc2, amplitud = float(partes[-3]), float(partes[-2]), float(partes[-1])
        except (ValueError, IndexError):
            continue
        return {
            "fecha": date(anio, mes, dia).isoformat(),
            "pc1": pc1,
            "pc2": pc2,
            "amplitud": round(amplitud, 4),
        }
    return None


def _fase_desde_pc(pc1: float, pc2: float) -> int:
    """Fase 1-8 sobre el círculo PC1/PC2 (convención estándar de 8 sectores de 45°)."""
    angulo = math.degrees(math.atan2(pc2, pc1))
    if angulo < 0:
        angulo += 360.0
    return int(angulo // 45.0) + 1


def _fetch_romi_real() -> dict[str, Any]:
    r = requests.get(ROMI_URL, timeout=_TIMEOUT)
    r.raise_for_status()
    registro = _parsear_ultima_linea_valida(r.text)
    if not registro:
        raise MjoIndiceNoDisponibleError("ROMI: no se pudo parsear ninguna línea válida")
    registro["fase"] = _fase_desde_pc(registro["pc1"], registro["pc2"])
    registro["fuente"] = "noaa_psl_romi"
    registro["fuente_url"] = ROMI_URL
    try:
        _runtime_cache_path().write_text(r.text[-4000:], encoding="utf-8")
    except Exception as exc:
        logger.warning("MJO ROMI: no se pudo guardar last-good (%s)", exc)
    return registro


def _fetch_romi_lastgood() -> dict[str, Any] | None:
    path = _runtime_cache_path()
    if not path.exists():
        return None
    try:
        registro = _parsear_ultima_linea_valida(path.read_text(encoding="utf-8"))
        if registro:
            registro["fase"] = _fase_desde_pc(registro["pc1"], registro["pc2"])
            registro["fuente"] = "noaa_psl_romi_lastgood"
            registro["fuente_url"] = ROMI_URL
        return registro
    except Exception as exc:
        logger.warning("MJO ROMI lastgood: %s", exc)
        return None


def obtener_indice_mjo_real(*, forzar_refresh: bool = False) -> dict[str, Any]:
    """Índice MJO real (fase 1-8, amplitud) con caché de 6h y fallback last-good.

    Nunca genera valores aleatorios: si no hay dato real ni caché, retorna
    ``disponible: False`` explícito para que el caller degrade sin fingir.
    """
    now = time.time()
    if not forzar_refresh and _MEM_CACHE["registro"] and now - _MEM_CACHE["ts"] < _CACHE_TTL_S:
        return {**_MEM_CACHE["registro"], "disponible": True, "desde_cache": True}

    try:
        registro = _fetch_romi_real()
        _MEM_CACHE["ts"] = now
        _MEM_CACHE["registro"] = registro
        return {**registro, "disponible": True, "desde_cache": False}
    except Exception as exc:
        logger.warning("MJO ROMI fetch real falló (%s); probando last-good", exc)

    lastgood = _fetch_romi_lastgood()
    if lastgood:
        return {**lastgood, "disponible": True, "desde_cache": True, "degradado": True}

    return {
        "disponible": False,
        "fuente": "no_disponible",
        "motivo": "NOAA/PSL ROMI no accesible y sin caché local previa",
    }


# Ajuste heurístico de precipitación por fase MJO — tendencia general de
# teleconexión MJO -> actividad frontal en Chile central, documentada en
# literatura de subestacional (no un modelo dinámico calibrado). Factor
# acotado a ±15% y solo aplicado si el MJO está "activo" (amplitud >= 1.0,
# umbral convencional en la literatura RMM/OMI/ROMI).
_FACTOR_POR_FASE: dict[int, float] = {
    1: 1.05, 2: 1.10, 3: 1.08, 4: 1.00,
    5: 0.95, 6: 0.90, 7: 0.92, 8: 1.00,
}
_AMPLITUD_ACTIVA_MIN = 1.0


def factor_ajuste_precipitacion(fase: int, amplitud: float) -> dict[str, Any]:
    if amplitud < _AMPLITUD_ACTIVA_MIN:
        return {
            "factor": 1.0,
            "activo": False,
            "nota": f"MJO inactivo (amplitud {amplitud:.2f} < {_AMPLITUD_ACTIVA_MIN}); sin ajuste.",
        }
    factor = _FACTOR_POR_FASE.get(int(fase), 1.0)
    return {
        "factor": factor,
        "activo": True,
        "nota": (
            f"MJO activo, fase {fase} (amplitud {amplitud:.2f}). Ajuste heurístico "
            f"{'+' if factor >= 1 else ''}{round((factor - 1) * 100)}% sobre precipitación "
            "base, según tendencia general de teleconexión MJO-Chile central "
            "(no es un modelo dinámico validado; usar como contexto, no como valor único)."
        ),
    }


def ajustar_precipitacion_mjo(precip_mm: float, fase: int, amplitud: float) -> dict[str, Any]:
    ajuste = factor_ajuste_precipitacion(fase, amplitud)
    return {
        "precipitacion_base_mm": round(precip_mm, 2),
        "precipitacion_ajustada_mjo_mm": round(precip_mm * ajuste["factor"], 2),
        **ajuste,
    }
