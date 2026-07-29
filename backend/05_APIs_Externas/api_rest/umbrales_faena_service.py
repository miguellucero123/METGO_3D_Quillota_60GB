#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Umbrales operativos multi-faena (M3) — izaje, caminos, botaderos.

Niveles: verde | amarillo | rojo.
Nieve: proxy mm agua Open-Meteo → cm (factor por temperatura).
"""

from __future__ import annotations

import copy
import os
from typing import Any

# Conservadores para faena minera alta montaña (m/s, mm, cm, m).
UMBRALES_DEFAULT: dict[str, dict[str, float]] = {
    "izaje": {
        "rafaga_amarillo_ms": 7.2,  # ~26 km/h
        "rafaga_rojo_ms": 10.0,  # ~36 km/h
        "snowfall_hora_amarillo_mm": 0.5,
        "snowfall_hora_rojo_mm": 1.5,
        "acum_24h_amarillo_cm": 5.0,
        "acum_24h_rojo_cm": 15.0,
        "visibilidad_amarillo_m": 2000.0,
        "visibilidad_rojo_m": 500.0,
    },
    "caminos": {
        "rafaga_amarillo_ms": 12.0,
        "rafaga_rojo_ms": 18.0,
        "snowfall_hora_amarillo_mm": 0.8,
        "snowfall_hora_rojo_mm": 2.0,
        "acum_24h_amarillo_cm": 3.0,
        "acum_24h_rojo_cm": 10.0,
        "visibilidad_amarillo_m": 1000.0,
        "visibilidad_rojo_m": 200.0,
    },
    "botaderos": {
        "rafaga_amarillo_ms": 10.0,
        "rafaga_rojo_ms": 15.0,
        "snowfall_hora_amarillo_mm": 0.6,
        "snowfall_hora_rojo_mm": 1.8,
        "acum_24h_amarillo_cm": 5.0,
        "acum_24h_rojo_cm": 12.0,
        "visibilidad_amarillo_m": 1500.0,
        "visibilidad_rojo_m": 400.0,
    },
}

_NIVEL_RANK = {"verde": 0, "amarillo": 1, "rojo": 2}


def umbrales_efectivos() -> dict[str, dict[str, float]]:
    """Copia defaults; override opcional vía env JSON no requerido en M3."""
    out = copy.deepcopy(UMBRALES_DEFAULT)
    # Escalado global opcional (ej. METGO_NIEVE_FACTOR=1.2 endurece acum)
    try:
        factor = float(os.getenv("METGO_NIEVE_UMBRAL_FACTOR", "1") or "1")
    except ValueError:
        factor = 1.0
    if factor != 1.0 and factor > 0:
        for act in out.values():
            for k in ("acum_24h_amarillo_cm", "acum_24h_rojo_cm"):
                if k in act:
                    act[k] = round(act[k] / factor, 2)
    return out


def mm_agua_a_cm_nieve(mm: float | None, temp_c: float | None = None) -> float:
    """Proxy profundidad nieve fresca desde mm agua equivalente (SWE)."""
    if mm is None or mm <= 0:
        return 0.0
    factor = 1.0
    if temp_c is not None:
        if temp_c > 0:
            factor = 0.7  # más densa / húmeda
        elif temp_c < -10:
            factor = 1.2  # polvo
    return round(float(mm) * factor, 2)


def _peor(a: str, b: str) -> str:
    return a if _NIVEL_RANK.get(a, 0) >= _NIVEL_RANK.get(b, 0) else b


def _nivel_directo(valor: float | None, amarillo: float, rojo: float) -> str:
    """Mayor valor = peor (viento, snowfall, acumulación)."""
    if valor is None:
        return "verde"
    if valor >= rojo:
        return "rojo"
    if valor >= amarillo:
        return "amarillo"
    return "verde"


def _nivel_inverso(valor: float | None, amarillo: float, rojo: float) -> str:
    """Menor valor = peor (visibilidad)."""
    if valor is None:
        return "verde"
    if valor <= rojo:
        return "rojo"
    if valor <= amarillo:
        return "amarillo"
    return "verde"


def evaluar_actividad(
    actividad: str,
    *,
    rafaga_ms: float | None,
    snowfall_hora_mm: float | None,
    acum_24h_cm: float | None,
    visibilidad_m: float | None,
    umbrales: dict[str, dict[str, float]] | None = None,
) -> dict[str, Any]:
    u = (umbrales or umbrales_efectivos()).get(actividad) or UMBRALES_DEFAULT["izaje"]
    n_raf = _nivel_directo(rafaga_ms, u["rafaga_amarillo_ms"], u["rafaga_rojo_ms"])
    n_snow = _nivel_directo(
        snowfall_hora_mm, u["snowfall_hora_amarillo_mm"], u["snowfall_hora_rojo_mm"]
    )
    n_acum = _nivel_directo(acum_24h_cm, u["acum_24h_amarillo_cm"], u["acum_24h_rojo_cm"])
    n_vis = _nivel_inverso(
        visibilidad_m, u["visibilidad_amarillo_m"], u["visibilidad_rojo_m"]
    )
    nivel = "verde"
    for n in (n_raf, n_snow, n_acum, n_vis):
        nivel = _peor(nivel, n)
    razones: list[str] = []
    if n_raf != "verde":
        razones.append(f"ráfaga→{n_raf}")
    if n_snow != "verde":
        razones.append(f"snowfall_hora→{n_snow}")
    if n_acum != "verde":
        razones.append(f"acum_24h→{n_acum}")
    if n_vis != "verde":
        razones.append(f"visibilidad→{n_vis}")
    return {
        "actividad": actividad,
        "nivel": nivel,
        "componentes": {
            "rafaga": n_raf,
            "snowfall_hora": n_snow,
            "acum_24h": n_acum,
            "visibilidad": n_vis,
        },
        "razones": razones,
        "umbrales": u,
    }


def evaluar_operaciones(
    *,
    rafaga_ms: float | None,
    snowfall_hora_mm: float | None,
    acum_24h_cm: float | None,
    visibilidad_m: float | None,
    umbrales: dict[str, dict[str, float]] | None = None,
) -> dict[str, Any]:
    umb = umbrales or umbrales_efectivos()
    acts = {
        act: evaluar_actividad(
            act,
            rafaga_ms=rafaga_ms,
            snowfall_hora_mm=snowfall_hora_mm,
            acum_24h_cm=acum_24h_cm,
            visibilidad_m=visibilidad_m,
            umbrales=umb,
        )
        for act in ("izaje", "caminos", "botaderos")
    }
    global_nivel = "verde"
    for a in acts.values():
        global_nivel = _peor(global_nivel, a["nivel"])
    return {
        "nivel_global": global_nivel,
        "actividades": acts,
        "umbrales": umb,
        "inputs": {
            "rafaga_ms": rafaga_ms,
            "snowfall_hora_mm": snowfall_hora_mm,
            "acum_24h_cm": acum_24h_cm,
            "visibilidad_m": visibilidad_m,
        },
    }


def construir_serie_nival(serie_meteo: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Serie horaria con acumulación desde inicio y rolling 24 h (proxy cm)."""
    out: list[dict[str, Any]] = []
    acum = 0.0
    ventana: list[float] = []
    for f in serie_meteo:
        mm = f.get("snowfall")
        try:
            mm_f = float(mm) if mm is not None else 0.0
        except (TypeError, ValueError):
            mm_f = 0.0
        temp = f.get("temperature_2m")
        try:
            temp_f = float(temp) if temp is not None else None
        except (TypeError, ValueError):
            temp_f = None
        cm = mm_agua_a_cm_nieve(mm_f, temp_f)
        acum = round(acum + cm, 2)
        ventana.append(cm)
        if len(ventana) > 24:
            ventana.pop(0)
        roll = round(sum(ventana), 2)
        out.append(
            {
                "fecha_hora": f.get("fecha_hora"),
                "snowfall_mm": round(mm_f, 2),
                "snowfall_cm": cm,
                "temperatura_c": temp_f,
                "acum_desde_inicio_cm": acum,
                "acum_rolling_24h_cm": roll,
                "flag_nieve": mm_f > 0.05 or cm > 0.05,
            }
        )
    return out


def flags_desde_serie_y_actual(
    serie_nival: list[dict[str, Any]],
    actual: dict[str, Any],
    ops: dict[str, Any],
) -> dict[str, Any]:
    """Flags resumen M3 para UI / informe."""
    nieve_activa = bool(actual.get("snowfall_mm") and float(actual["snowfall_mm"]) > 0.05)
    if not nieve_activa and serie_nival:
        nieve_activa = any(r.get("flag_nieve") for r in serie_nival[:6])
    acum_24 = None
    if serie_nival:
        acum_24 = serie_nival[min(23, len(serie_nival) - 1)].get("acum_rolling_24h_cm")
        # Mejor: último punto de la serie
        acum_24 = serie_nival[-1].get("acum_rolling_24h_cm")
    acts = ops.get("actividades") or {}
    return {
        "flag_nieve_activa": nieve_activa,
        "flag_acum_relevante": bool(acum_24 is not None and float(acum_24) >= 3.0),
        "flag_izaje_restringido": (acts.get("izaje") or {}).get("nivel") in ("amarillo", "rojo"),
        "flag_caminos_restringido": (acts.get("caminos") or {}).get("nivel")
        in ("amarillo", "rojo"),
        "flag_botaderos_restringido": (acts.get("botaderos") or {}).get("nivel")
        in ("amarillo", "rojo"),
        "nivel_global": ops.get("nivel_global"),
    }
