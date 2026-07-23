#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datos agrícolas reales vía API METGO para dashboards Streamlit (8503, 8508)."""

from __future__ import annotations

from typing import Any

from meteo_dashboard_utils import filtrar_historico_hasta_hoy, hoy_chile

ESTACIONES_VALLE = [
    "Quillota",
    "Los Nogales",
    "Hijuelas",
    "Limache",
    "Olmue",
]

CULTIVO_A_SLUG = {
    "Palta": "palto",
    "Cítricos": "citricos",
    "Vid": "vid",
    "Tomate": "tomate",
    "Lechuga": "lechuga",
}


def _fila_por_fecha(hist: list[dict], fecha: str) -> dict | None:
    for r in reversed(hist):
        if str(r.get("fecha", ""))[:10] == fecha:
            return r
    return None


def _delta_vs_ayer(hoy: dict, ayer: dict | None, campo: str) -> float | None:
    if not ayer:
        return None
    try:
        return round(float(hoy.get(campo) or 0) - float(ayer.get(campo) or 0), 1)
    except (TypeError, ValueError):
        return None


def cargar_contexto_agricola(estacion_nombre: str, cultivo_label: str) -> dict[str, Any]:
    """Resumen meteo observado + recomendaciones + riego desde API (módulo 02)."""
    from api_rest.services import historico_meteo, nombre_a_slug, resumen_meteo, recomendaciones_agricolas

    slug = nombre_a_slug(estacion_nombre)
    hist = filtrar_historico_hasta_hoy(historico_meteo(slug, 30) or [])
    ref = hoy_chile()
    hoy_row = _fila_por_fecha(hist, ref) if hist else None

    resumen = resumen_meteo(slug) or {}
    if hoy_row:
        resumen = {**resumen, **hoy_row, "fecha": ref, "tipo_dato": "observado"}
    elif resumen:
        resumen = {**resumen, "tipo_dato": resumen.get("tipo_dato", "pronostico")}

    ayer_row = None
    if hist and hoy_row:
        idx = next(
            (i for i, r in enumerate(hist) if str(r.get("fecha", ""))[:10] == ref),
            len(hist) - 1,
        )
        if idx > 0:
            ayer_row = hist[idx - 1]

    cultivo_id = CULTIVO_A_SLUG.get(cultivo_label, "palto")

    riego: dict[str, Any] = {}
    try:
        from api_rest.integracion import agricola_extra

        if resumen:
            riego = agricola_extra.recomendacion_riego(resumen, cultivo_id)
    except Exception:
        pass

    recs = recomendaciones_agricolas(slug, avanzado=True)

    economico: dict[str, Any] = {}
    try:
        from api_rest.integracion import agricola_extra

        economico = agricola_extra.analisis_economico(slug)
    except Exception:
        pass

    temp = float(resumen.get("temperatura") or 0)
    return {
        "estacion_id": slug,
        "estacion": estacion_nombre,
        "fecha_referencia": ref,
        "resumen": resumen,
        "historico": hist,
        "temperatura": temp,
        "temperatura_min": float(resumen.get("temperatura_min") or temp),
        "temperatura_max": float(resumen.get("temperatura_max") or temp),
        "humedad": float(resumen.get("humedad") or 0),
        "precipitacion": float(resumen.get("precipitacion") or 0),
        "viento": float(resumen.get("viento") or 0),
        "fuente": resumen.get("fuente", "OpenMeteo"),
        "tipo_dato": resumen.get("tipo_dato", "observado"),
        "delta_temp": _delta_vs_ayer(resumen, ayer_row, "temperatura"),
        "delta_humedad": _delta_vs_ayer(resumen, ayer_row, "humedad"),
        "delta_precip": _delta_vs_ayer(resumen, ayer_row, "precipitacion"),
        "recomendaciones_api": recs,
        "riego": riego,
        "cultivo_id": cultivo_id,
        "economico": economico,
    }
