#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mapas meteorológicos regionales y globales (datos determinísticos / OpenMeteo)."""

from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from typing import Any

from flask import jsonify, request

from api_rest.auth_routes import auth_required
from api_rest.meteo_avanzado_core import COORDS_ESTACIONES, validar_estacion
from api_rest.meteo_modelos_core import comparacion_gfs_ecmwf
from api_rest.services import ESTACIONES_PRINCIPALES, pronostico_meteo, resumen_meteo

logger = logging.getLogger(__name__)

VARIABLES_MAPA = [
    "temperatura",
    "humedad",
    "presion",
    "precipitacion",
    "radiacion",
    "nubosidad",
    "viento_velocidad",
]

UNIDADES = {
    "temperatura": "°C",
    "humedad": "%",
    "presion": "hPa",
    "precipitacion": "mm",
    "radiacion": "W/m²",
    "nubosidad": "%",
    "viento_velocidad": "m/s",
}


def _valor_desde_fila(variable: str, row: dict[str, Any]) -> float:
    temp = row.get("temperatura")
    if temp is None:
        tmax, tmin = row.get("temperatura_max"), row.get("temperatura_min")
        if tmax is not None and tmin is not None:
            temp = (float(tmax) + float(tmin)) / 2
        else:
            temp = tmax
    rad = row.get("radiacion_solar")
    if rad is None and row.get("radiacion_solar_sum") is not None:
        mj = float(row["radiacion_solar_sum"])
        rad = (mj * 1e6) / (12 * 3600)
    if rad is None:
        rad = max(120.0, 650.0 - abs(-32.9) * 8)
    m = {
        "temperatura": temp,
        "humedad": row.get("humedad"),
        "presion": row.get("presion"),
        "precipitacion": row.get("precipitacion"),
        "radiacion": rad,
        "nubosidad": row.get("cobertura_nubosa"),
        "viento_velocidad": row.get("viento"),
    }
    return float(m.get(variable) or 0)


def _valor_estacion(variable: str, resumen: dict[str, Any]) -> float:
    m = {
        "temperatura": resumen.get("temperatura_max"),
        "humedad": resumen.get("humedad"),
        "presion": resumen.get("presion"),
        "precipitacion": resumen.get("precipitacion"),
        "radiacion": resumen.get("radiacion_solar") or 500,
        "nubosidad": resumen.get("cobertura_nubosa") or 50,
        "viento_velocidad": resumen.get("viento"),
    }
    return float(m.get(variable) or 0)


def _idw(
    lat: float,
    lon: float,
    puntos: list[tuple[float, float, float]],
    potencia: float = 2.0,
) -> float:
    if not puntos:
        return 0.0
    num, den = 0.0, 0.0
    for plat, plon, val in puntos:
        d = math.hypot(lat - plat, lon - plon)
        if d < 1e-6:
            return val
        w = 1.0 / (d**potencia)
        num += w * val
        den += w
    return num / den if den else puntos[0][2]


def _puntos_estaciones_mapa(
    variable: str, dia_idx: int = 0
) -> tuple[list[dict[str, Any]], str | None]:
    puntos: list[dict[str, Any]] = []
    fecha_frame: str | None = None
    for slug in ESTACIONES_PRINCIPALES:
        pron = pronostico_meteo(slug, 7) or []
        if len(pron) <= dia_idx:
            continue
        row = pron[dia_idx]
        val = _valor_desde_fila(variable, row)
        if fecha_frame is None:
            fecha_frame = row.get("fecha")
        c = COORDS_ESTACIONES[slug]
        puntos.append(
            {
                "estacion_id": slug,
                "nombre": slug.replace("_", " ").title(),
                "lat": c["lat"],
                "lon": c["lon"],
                "valor": round(val, 2),
            }
        )
    return puntos, fecha_frame


def _grilla_valle_determinista(
    variable: str, resolucion: float, dia_idx: int = 0
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[tuple[float, ...], ...], float, float, str | None, list[dict[str, Any]]]:
    """Grilla regional Valle de Aconcagua interpolada desde estaciones METGO."""
    puntos_meta, fecha_frame = _puntos_estaciones_mapa(variable, dia_idx)
    puntos_valor = [(p["lat"], p["lon"], p["valor"]) for p in puntos_meta]

    lat_min, lat_max = -33.15, -32.75
    lon_min, lon_max = -71.35, -71.05
    lats = tuple(
        round(lat_min + i * resolucion, 4)
        for i in range(int((lat_max - lat_min) / resolucion) + 1)
    )
    lons = tuple(
        round(lon_min + j * resolucion, 4)
        for j in range(int((lon_max - lon_min) / resolucion) + 1)
    )
    valores: list[list[float]] = []
    for la in lats:
        fila: list[float] = []
        for lo in lons:
            fila.append(round(_idw(la, lo, puntos_valor), 2))
        valores.append(fila)

    flat = [v for fila in valores for v in fila]
    return lats, lons, tuple(tuple(f) for f in valores), min(flat), max(flat), fecha_frame, puntos_meta


def _grilla_global_fisica(
    variable: str, resolucion: float
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[tuple[float, ...], ...], float, float]:
    """Grilla global simplificada (fórmulas físicas determinísticas, sin ruido aleatorio)."""
    lat_min, lat_max = -60.0, 60.0
    lon_min, lon_max = -180.0, 180.0
    lats = tuple(
        round(lat_min + i * resolucion, 2)
        for i in range(int((lat_max - lat_min) / resolucion) + 1)
    )
    lons = tuple(
        round(lon_min + j * resolucion, 2)
        for j in range(int((lon_max - lon_min) / resolucion) + 1)
    )
    valores: list[list[float]] = []
    for la in lats:
        fila: list[float] = []
        abs_lat = abs(la)
        for lo in lons:
            if variable == "temperatura":
                v = 25 - abs_lat * 0.5
            elif variable == "humedad":
                v = min(100, max(0, 60 + (1 - abs_lat / 90) * 30))
            elif variable == "presion":
                v = 1013 - (1 - abs_lat / 90) * 20
            elif variable == "precipitacion":
                v = max(0, abs(math.sin(math.radians(la * 2))) * 50)
            elif variable == "radiacion":
                v = max(0, 500 * (1 - abs_lat / 90))
            elif variable == "nubosidad":
                v = min(100, max(0, 50 + math.sin(math.radians(lo)) * 30))
            elif variable == "viento_velocidad":
                v = min(30, abs_lat / 30 * 15)
            else:
                v = 0.0
            fila.append(round(v, 2))
        valores.append(fila)
    flat = [v for fila in valores for v in fila]
    return lats, lons, tuple(tuple(f) for f in valores), min(flat), max(flat)


def obtener_datos_mapa(
    variable: str,
    resolucion: str,
    ambito: str = "global",
    dia_idx: int = 0,
) -> dict[str, Any]:
    res = float(resolucion)
    fecha_frame = None
    puntos_estacion: list[dict[str, Any]] = []
    if ambito == "regional":
        lats, lons, valores, vmin, vmax, fecha_frame, puntos_estacion = _grilla_valle_determinista(
            variable, res, dia_idx
        )
        modelo = "METGO-IDW"
    else:
        res = max(0.5, res)
        lats, lons, valores, vmin, vmax = _grilla_global_fisica(variable, res)
        modelo = "fisica-deterministica"

    out = {
        "variable": variable,
        "modelo": modelo,
        "resolucion": str(resolucion),
        "fecha_datos": datetime.now(timezone.utc).isoformat(),
        "lats": list(lats),
        "lons": list(lons),
        "valores": [list(f) for f in valores],
        "minVal": float(vmin),
        "maxVal": float(vmax),
        "unidad": UNIDADES.get(variable, ""),
        "dia_idx": dia_idx,
    }
    if fecha_frame:
        out["fecha_frame"] = fecha_frame
    if puntos_estacion:
        out["puntos_estacion"] = puntos_estacion
        out["bounds"] = {
            "lat_min": -33.15,
            "lat_max": -32.75,
            "lon_min": -71.35,
            "lon_max": -71.05,
        }
    return out


def obtener_animacion_regional(
    estacion_id: str, variable: str, resolucion: str = "0.1", dias: int = 7
) -> dict[str, Any]:
    frames = []
    for dia in range(min(dias, 7)):
        frame = obtener_datos_mapa(variable, resolucion, "regional", dia)
        frame["frame"] = dia
        frames.append(frame)
    meta = COORDS_ESTACIONES.get(estacion_id.lower(), COORDS_ESTACIONES["quillota"])
    return {
        "estacion_id": estacion_id,
        "variable": variable,
        "frames": frames,
        "total_frames": len(frames),
        "centro": {"lat": meta["lat"], "lon": meta["lon"]},
        "velocidad_recomendada_ms": 500,
    }


def register_mapas_routes(app) -> None:
    @app.get("/api/mapas/global/<variable>")
    @auth_required
    def mapa_global(variable: str):
        if variable not in VARIABLES_MAPA:
            return jsonify({"error": f"Variable {variable} no válida"}), 400
        resolucion = request.args.get("resolucion", "1.0")
        try:
            return jsonify(obtener_datos_mapa(variable, resolucion, "global"))
        except Exception as e:
            logger.exception("mapa global: %s", e)
            return jsonify({"error": "Error interno"}), 500

    @app.get("/api/mapas/regional/<estacion_id>/<variable>")
    @auth_required
    def mapa_regional(estacion_id: str, variable: str):
        try:
            validar_estacion(estacion_id)
            if variable not in VARIABLES_MAPA:
                return jsonify({"error": f"Variable {variable} no válida"}), 400
            resolucion = request.args.get("resolucion", "0.02")
            datos = obtener_datos_mapa(variable, resolucion, "regional")
            meta = COORDS_ESTACIONES[estacion_id.lower()]
            datos["estacion_id"] = estacion_id
            datos["centro"] = {"lat": meta["lat"], "lon": meta["lon"]}
            return jsonify(datos)
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logger.exception("mapa regional: %s", e)
            return jsonify({"error": "Error interno"}), 500

    @app.get("/api/mapas/global/comparativa-variables")
    @auth_required
    def mapa_comparativa():
        resolucion = request.args.get("resolucion", "1.0")
        vars_req = ["temperatura", "humedad", "precipitacion", "nubosidad", "radiacion"]
        return jsonify(
            {
                "variables": {
                    v: obtener_datos_mapa(v, resolucion, "global") for v in vars_req
                },
                "fecha_datos": datetime.now(timezone.utc).isoformat(),
            }
        )

    @app.get("/api/mapas/comparacion-modelos/<estacion_id>/<variable>")
    @auth_required
    def comparacion_modelos(estacion_id: str, variable: str):
        try:
            dias = request.args.get("dias", 7, type=int)
            return jsonify(comparacion_gfs_ecmwf(estacion_id, variable, dias))
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logger.exception("comparacion modelos: %s", e)
            return jsonify({"error": "Error interno"}), 500

    @app.get("/api/mapas/regional/<estacion_id>/<variable>/animacion")
    @auth_required
    def mapa_regional_animacion(estacion_id: str, variable: str):
        try:
            validar_estacion(estacion_id)
            if variable not in VARIABLES_MAPA:
                return jsonify({"error": f"Variable {variable} no válida"}), 400
            resolucion = request.args.get("resolucion", "0.02")
            dias = request.args.get("dias", 7, type=int)
            return jsonify(
                obtener_animacion_regional(estacion_id, variable, resolucion, dias)
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logger.exception("mapa animacion: %s", e)
            return jsonify({"error": "Error interno"}), 500
