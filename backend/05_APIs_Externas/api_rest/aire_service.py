#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calidad del aire (E7 — Copiapó): Open-Meteo Air Quality (CAMS) + ICAP chileno.

ICAP (Índice de Calidad del Aire por Partículas, MMA Chile):
interpolación lineal por tramos sobre concentraciones 24 h.
Categorías: Bueno <100 · Regular 100–199 · Alerta 200–299 ·
Preemergencia 300–499 · Emergencia >=500.
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests

from api_rest.estaciones_catalogo import COORDS, ESTACIONES_POR_SITIO, SLUG_A_NOMBRE

TZ_CHILE = ZoneInfo("America/Santiago")

AIR_API_BASE = "https://air-quality-api.open-meteo.com/v1/air-quality"

HOURLY_VARS = [
    "pm2_5",
    "pm10",
    "sulphur_dioxide",
    "nitrogen_dioxide",
    "ozone",
    "carbon_monoxide",
    "dust",
]

# Breakpoints (ICAP, concentración µg/m³ promedio 24 h) — DS 59 / DS 12 MMA
_BP_PM10 = [(0, 0.0), (100, 150.0), (200, 195.0), (300, 240.0), (500, 330.0)]
_BP_PM25 = [(0, 0.0), (100, 50.0), (200, 80.0), (300, 110.0), (500, 170.0)]

CATEGORIAS = (
    (100, "bueno", "Bueno"),
    (200, "regular", "Regular"),
    (300, "alerta", "Alerta"),
    (500, "preemergencia", "Preemergencia"),
    (float("inf"), "emergencia", "Emergencia"),
)

RECOMENDACIONES_SALUD: dict[str, list[str]] = {
    "bueno": [
        "Condiciones normales: actividades al aire libre sin restricción.",
    ],
    "regular": [
        "Grupos sensibles (asmáticos, adultos mayores, niños): reducir ejercicio intenso prolongado al aire libre.",
    ],
    "alerta": [
        "Evitar actividad física intensa al aire libre.",
        "Grupos sensibles: permanecer en interiores con ventanas cerradas.",
    ],
    "preemergencia": [
        "Suspender actividades deportivas al aire libre.",
        "Usar mascarilla certificada si debe permanecer en exteriores.",
        "Ventilar la vivienda solo en horas de menor concentración.",
    ],
    "emergencia": [
        "Permanecer en interiores; salir solo si es imprescindible.",
        "Grupos sensibles: consultar red de salud ante síntomas respiratorios.",
        "Seguir instrucciones de la autoridad sanitaria (episodio crítico).",
    ],
}


def _interp(bp: list[tuple[float, float]], conc: float) -> float:
    """ICAP por interpolación lineal (índice, concentración)."""
    if conc <= 0:
        return 0.0
    for (i0, c0), (i1, c1) in zip(bp, bp[1:]):
        if conc <= c1:
            return i0 + (conc - c0) * (i1 - i0) / (c1 - c0)
    # Extrapola sobre el último tramo (Emergencia)
    (i0, c0), (i1, c1) = bp[-2], bp[-1]
    return i1 + (conc - c1) * (i1 - i0) / (c1 - c0)


def icap_pm25(conc: float | None) -> float | None:
    return None if conc is None else round(_interp(_BP_PM25, float(conc)), 1)


def icap_pm10(conc: float | None) -> float | None:
    return None if conc is None else round(_interp(_BP_PM10, float(conc)), 1)


def categoria_icap(indice: float | None) -> dict[str, Any]:
    if indice is None:
        return {"nivel": None, "etiqueta": "Sin datos", "recomendaciones": []}
    for limite, nivel, etiqueta in CATEGORIAS:
        if indice < limite:
            return {
                "nivel": nivel,
                "etiqueta": etiqueta,
                "recomendaciones": RECOMENDACIONES_SALUD[nivel],
            }
    # inalcanzable
    return {"nivel": "emergencia", "etiqueta": "Emergencia", "recomendaciones": []}


def evaluar_icap(pm25: float | None, pm10: float | None) -> dict[str, Any]:
    """ICAP combinado: el peor de PM2.5 y PM10 manda (contaminante rector)."""
    i25 = icap_pm25(pm25)
    i10 = icap_pm10(pm10)
    candidatos = [(v, k) for v, k in ((i25, "pm2_5"), (i10, "pm10")) if v is not None]
    if not candidatos:
        return {"icap": None, "contaminante_rector": None, **categoria_icap(None)}
    indice, rector = max(candidatos)
    return {"icap": indice, "contaminante_rector": rector, **categoria_icap(indice)}


# ---------------------------------------------------------------- HTTP + caché

_TIMEOUT = int(os.getenv("METGO_OPENMETEO_TIMEOUT", "25"))
_RETRIES = int(os.getenv("METGO_OPENMETEO_RETRIES", "3"))


def _get_json(params: dict[str, Any]) -> dict[str, Any] | None:
    for intento in range(1, _RETRIES + 1):
        try:
            r = requests.get(AIR_API_BASE, params=params, timeout=_TIMEOUT)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503, 504) and intento < _RETRIES:
                time.sleep(min(2**intento, 8))
                continue
            return None
        except Exception:
            if intento < _RETRIES:
                time.sleep(min(2**intento, 8))
    return None


def _json_cached(clave: str, fetcher):
    """Usa el caché TTL de cache_openmeteo si está disponible (mismo patrón meteo)."""
    try:
        from api_rest import services

        cache = getattr(services, "_CACHE_JSON", None)
    except ImportError:
        cache = None
    if cache is not None:
        return cache(clave, fetcher)
    return fetcher()


def _coords_de(estacion_id: str) -> dict[str, float] | None:
    key = estacion_id.lower().replace("-", "_")
    if key not in SLUG_A_NOMBRE:
        return None
    return COORDS.get(key)


def _fetch_aire(lat: float, lon: float, forecast_days: int, past_days: int) -> dict | None:
    params: dict[str, Any] = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(HOURLY_VARS),
        "current": ",".join(HOURLY_VARS),
        "timezone": "America/Santiago",
        "forecast_days": max(1, min(forecast_days, 7)),
    }
    if past_days:
        params["past_days"] = min(past_days, 92)
    return _get_json(params)


def _promedios_diarios(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Agrega horario → diario (promedio 24 h, base de la norma chilena)."""
    hourly = payload.get("hourly") or {}
    tiempos = hourly.get("time") or []
    por_dia: dict[str, dict[str, list[float]]] = {}
    for idx, ts in enumerate(tiempos):
        dia = str(ts)[:10]
        acc = por_dia.setdefault(dia, {v: [] for v in HOURLY_VARS})
        for var in HOURLY_VARS:
            serie = hourly.get(var) or []
            val = serie[idx] if idx < len(serie) else None
            if val is not None:
                acc[var].append(float(val))
    filas = []
    for dia in sorted(por_dia):
        acc = por_dia[dia]
        fila: dict[str, Any] = {"fecha": dia}
        for var in HOURLY_VARS:
            vals = acc[var]
            fila[var] = round(sum(vals) / len(vals), 1) if vals else None
        fila.update(evaluar_icap(fila.get("pm2_5"), fila.get("pm10")))
        fila["fuente"] = "openmeteo_cams"
        filas.append(fila)
    return filas


# ------------------------------------------------------------------- servicios


def _serie_24h_desde_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Últimas ≤24 h de PM/ICAP a partir del bloque hourly CAMS."""
    hourly = payload.get("hourly") or {}
    tiempos = hourly.get("time") or []
    if not tiempos:
        return []
    n = len(tiempos)
    start = max(0, n - 24)
    out: list[dict[str, Any]] = []
    pm25_s = hourly.get("pm2_5") or []
    pm10_s = hourly.get("pm10") or []
    for idx in range(start, n):
        pm25 = pm25_s[idx] if idx < len(pm25_s) else None
        pm10 = pm10_s[idx] if idx < len(pm10_s) else None
        try:
            pm25_f = float(pm25) if pm25 is not None else None
        except (TypeError, ValueError):
            pm25_f = None
        try:
            pm10_f = float(pm10) if pm10 is not None else None
        except (TypeError, ValueError):
            pm10_f = None
        eval_ = evaluar_icap(pm25_f, pm10_f)
        out.append(
            {
                "fecha_hora": tiempos[idx],
                "pm2_5": round(pm25_f, 1) if pm25_f is not None else None,
                "pm10": round(pm10_f, 1) if pm10_f is not None else None,
                "icap": eval_.get("icap"),
                "nivel": eval_.get("nivel"),
            }
        )
    return out


def _enrich_viento(data: dict[str, Any], lat: float, lon: float) -> dict[str, Any]:
    """Añade viento 10 m desde Forecast API (CAMS AQ no trae viento)."""
    # TODO: viento — unificar con serie horaria de dispersion_service cuando haya caché compartida.
    data.setdefault("viento_velocidad", None)
    data.setdefault("viento_direccion", None)
    data.setdefault("viento_unidad", "m/s")
    try:
        from api_rest.dispersion_service import FORECAST_API_BASE, _get_json

        payload = _get_json(
            FORECAST_API_BASE,
            {
                "latitude": lat,
                "longitude": lon,
                "current": "wind_speed_10m,wind_direction_10m",
                "wind_speed_unit": "ms",
                "timezone": "America/Santiago",
            },
        )
        cur = (payload or {}).get("current") or {}
        if cur.get("wind_speed_10m") is not None:
            data["viento_velocidad"] = round(float(cur["wind_speed_10m"]), 2)
        if cur.get("wind_direction_10m") is not None:
            data["viento_direccion"] = round(float(cur["wind_direction_10m"]), 1)
    except Exception:
        pass
    return data


def aire_actual(estacion_id: str) -> dict[str, Any] | None:
    """Condición actual de calidad del aire + ICAP + recomendaciones."""
    coords = _coords_de(estacion_id)
    if coords is None:
        return None

    def fetch():
        payload = _fetch_aire(coords["lat"], coords["lon"], forecast_days=1, past_days=0)
        if not payload:
            return None
        current = payload.get("current") or {}
        data: dict[str, Any] = {
            "estacion_id": estacion_id.lower().replace("-", "_"),
            "fuente": "openmeteo_cams",
            "tipo_dato": "modelo",
            "actualizado": current.get("time")
            or datetime.now(TZ_CHILE).isoformat(timespec="minutes"),
        }
        for var in HOURLY_VARS:
            val = current.get(var)
            data[var] = round(float(val), 1) if val is not None else None
        data.update(evaluar_icap(data.get("pm2_5"), data.get("pm10")))
        data["serie_24h"] = _serie_24h_desde_payload(payload)
        _enrich_viento(data, coords["lat"], coords["lon"])
        return data

    data = _json_cached(f"aire_actual_v2|{estacion_id}", fetch)
    if data is None:
        # Fallback: último registro persistido (CAMS caído o en cooldown).
        respaldo = _ultimo_aire_store(estacion_id.lower().replace("-", "_"))
        if respaldo is not None:
            respaldo["degradado"] = True
            respaldo.setdefault("viento_velocidad", None)
            respaldo.setdefault("viento_direccion", None)
            respaldo.setdefault("serie_24h", [])
            return respaldo
    return data


def _etiquetar_tipo(filas: list[dict[str, Any]], tipo_dato: str) -> list[dict[str, Any]]:
    for f in filas:
        f["tipo_dato"] = tipo_dato
        f.setdefault("fuente", "openmeteo_cams")
    return filas


def aire_pronostico(estacion_id: str, dias: int = 5) -> list[dict[str, Any]] | None:
    """Pronóstico diario (promedios 24 h) con ICAP por día."""
    coords = _coords_de(estacion_id)
    if coords is None:
        return None

    def fetch():
        payload = _fetch_aire(coords["lat"], coords["lon"], forecast_days=dias, past_days=0)
        if not payload:
            return None
        hoy = datetime.now(TZ_CHILE).date().isoformat()
        filas = [f for f in _promedios_diarios(payload) if f["fecha"] >= hoy][:dias]
        return _etiquetar_tipo(filas, "pronostico")

    return _json_cached(f"aire_pronostico|{estacion_id}|{dias}", fetch)


def aire_historico(estacion_id: str, dias: int = 7) -> list[dict[str, Any]] | None:
    """Histórico diario reciente (past_days CAMS, máx 92)."""
    coords = _coords_de(estacion_id)
    if coords is None:
        return None

    def fetch():
        payload = _fetch_aire(coords["lat"], coords["lon"], forecast_days=1, past_days=dias)
        if not payload:
            return None
        hoy = datetime.now(TZ_CHILE).date().isoformat()
        # CAMS past_days es modelo/reanálisis, no observación in situ (SINCA = observado).
        filas = [f for f in _promedios_diarios(payload) if f["fecha"] < hoy][-dias:]
        return _etiquetar_tipo(filas, "modelo")

    data = _json_cached(f"aire_historico|{estacion_id}|{dias}", fetch)
    if not data:
        respaldo = _leer_aire_store(estacion_id.lower().replace("-", "_"), dias)
        if respaldo:
            return respaldo
    return data


# ------------------------------------------------------- persistencia / alertas


def _ultimo_aire_store(estacion_id: str) -> dict[str, Any] | None:
    try:
        from api_rest.integracion import aire_store

        return aire_store.ultimo_aire(estacion_id)
    except Exception:
        return None


def _leer_aire_store(estacion_id: str, dias: int) -> list[dict[str, Any]]:
    try:
        from api_rest.integracion import aire_store

        return aire_store.leer_aire(estacion_id, dias=dias)
    except Exception:
        return []


# Umbral ICAP a partir del cual se emite alerta de salud (nivel "alerta").
ICAP_UMBRAL_ALERTA = int(os.getenv("METGO_ICAP_UMBRAL_ALERTA", "200"))


def sincronizar_aire(estaciones: list[str] | None = None) -> dict[str, Any]:
    """ETL aire: CAMS (actual + pronóstico + histórico) → aire_registros.

    Pensado para el cron: idempotente y tolerante a fallos por estación.
    """
    try:
        from api_rest.integracion import aire_store
    except Exception as exc:  # pragma: no cover
        return {"aire_sync": {}, "error": f"aire_store no disponible: {exc}"}

    slugs = estaciones or ESTACIONES_POR_SITIO.get("copiapo", [])
    detalle: dict[str, int] = {}
    errores: list[str] = []
    for slug in slugs:
        escritos = 0
        try:
            actual = aire_actual(slug)
            if actual and actual.get("fuente") == "openmeteo_cams":
                escritos += aire_store.guardar_aire(slug, [actual], tipo_dato="modelo")
        except Exception as exc:
            errores.append(f"{slug} (actual): {exc}")
        try:
            hist = aire_historico(slug, dias=7) or []
            escritos += aire_store.guardar_aire(slug, hist, tipo_dato="modelo")
        except Exception as exc:
            errores.append(f"{slug} (historico): {exc}")
        try:
            pron = aire_pronostico(slug, dias=5) or []
            escritos += aire_store.guardar_aire(slug, pron, tipo_dato="pronostico")
        except Exception as exc:
            errores.append(f"{slug} (pronostico): {exc}")
        detalle[slug] = escritos
    return {"aire_sync": detalle, "errores": errores, "umbral_alerta": ICAP_UMBRAL_ALERTA}


def alertas_aire(sitio: str = "copiapo") -> dict[str, Any]:
    """Estaciones del sitio con ICAP >= umbral (banner de alerta de salud)."""
    slugs = ESTACIONES_POR_SITIO.get(sitio, [])
    activas: list[dict[str, Any]] = []
    for slug in slugs:
        try:
            actual = aire_actual(slug)
        except Exception:
            actual = None
        if not actual:
            continue
        icap = actual.get("icap")
        if icap is not None and icap >= ICAP_UMBRAL_ALERTA:
            activas.append(
                {
                    "estacion_id": slug,
                    "nombre": SLUG_A_NOMBRE.get(slug, slug),
                    "icap": icap,
                    "nivel": actual.get("nivel"),
                    "etiqueta": actual.get("etiqueta"),
                    "contaminante_rector": actual.get("contaminante_rector"),
                    "recomendaciones": actual.get("recomendaciones", []),
                    "actualizado": actual.get("actualizado"),
                    "degradado": bool(actual.get("degradado")),
                }
            )
    nivel_max = None
    if activas:
        peor = max(activas, key=lambda a: a["icap"])
        nivel_max = peor.get("nivel")
    return {
        "sitio": sitio,
        "umbral": ICAP_UMBRAL_ALERTA,
        "hay_alerta": bool(activas),
        "nivel_max": nivel_max,
        "estaciones": activas,
    }
