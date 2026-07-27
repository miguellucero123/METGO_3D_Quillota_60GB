#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Potencial de dispersión de contaminantes (E7 — Copiapó).

Meteorología que gobierna la dispersión en el airshed de Copiapó:
  - Inversión térmica (gradiente 2 m ↔ 925 hPa; capa límite).
  - Intensidad y dirección del viento (ventilación horizontal).
  - Altura de la capa límite (mezcla vertical).
  - Nubosidad baja / niebla / neblina costera (camanchaca) y su efecto de
    atrapamiento bajo la inversión.

Salidas:
  - Horaria: 24 / 48 / 72 h (detalle para episodios).
  - Diaria: 7 días (agregado representativo por día).
  - Proyección: 16-30 días por climatología del archivo (baja confianza).

Fuente: Open-Meteo Forecast API (modelo, niveles de presión + capa límite).
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import requests

from api_rest.estaciones_catalogo import COORDS, ESTACIONES_POR_SITIO, SLUG_A_NOMBRE

TZ_CHILE = ZoneInfo("America/Santiago")

FORECAST_API_BASE = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_API_BASE = "https://archive-api.open-meteo.com/v1/archive"

_TIMEOUT = int(os.getenv("METGO_OPENMETEO_TIMEOUT", "25"))
_RETRIES = int(os.getenv("METGO_OPENMETEO_RETRIES", "3"))

# Variables horarias relevantes para dispersión.
_HOURLY_BASE = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "visibility",
    "cloud_cover_low",
    "cloud_cover",
    "wind_speed_10m",
    "wind_gusts_10m",
    "wind_direction_10m",
    "temperature_925hPa",
    "temperature_850hPa",
    "surface_pressure",
]
# La capa límite no está en todos los modelos; se pide aparte y con fallback.
_HOURLY_PBL = "boundary_layer_height"

# Umbral de índice de dispersión (0-100) bajo el cual se emite alerta.
UMBRAL_ALERTA_DISPERSION = int(os.getenv("METGO_DISPERSION_UMBRAL_ALERTA", "40"))


# ------------------------------------------------------------------ cooldown OM


def _cooldown_helpers():
    """Reusa el circuit breaker de datos_reales_openmeteo si está disponible."""
    try:
        import importlib

        mod = importlib.import_module("datos_reales_openmeteo")
        return mod.openmeteo_en_cooldown, mod.marcar_openmeteo_cooldown
    except Exception:
        return (lambda: False), (lambda *_a, **_k: None)


# --------------------------------------------------------------------- fetch HTTP


def _get_json(base: str, params: dict[str, Any], *, ignore_cooldown: bool = False) -> dict[str, Any] | None:
    """HTTP JSON a Open-Meteo.

    ignore_cooldown=True: usado por endpoints on-demand (sounding, archive olas).
    No bloquea por circuit breaker global y ante 429 espera breve sin alargar el cooldown.
    """
    en_cooldown, marcar = _cooldown_helpers()
    if not ignore_cooldown and en_cooldown():
        return None
    for intento in range(1, _RETRIES + 1):
        try:
            r = requests.get(base, params=params, timeout=_TIMEOUT)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                if ignore_cooldown:
                    # Backoff local corto; no reinicia el breaker global (evita bucle 2 min).
                    if intento < _RETRIES:
                        time.sleep(min(3 * intento, 10))
                        continue
                    return None
                marcar()
                return None
            if r.status_code in (500, 502, 503, 504) and intento < _RETRIES:
                time.sleep(min(2**intento, 8))
                continue
            return None
        except Exception:
            if intento < _RETRIES:
                time.sleep(min(2**intento, 8))
    return None


def _fetch_forecast(lat: float, lon: float, forecast_days: int) -> dict[str, Any] | None:
    """Forecast horario; incluye capa límite y reintenta sin ella si el modelo no la ofrece."""
    hourly = _HOURLY_BASE + [_HOURLY_PBL]
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(hourly),
        "wind_speed_unit": "ms",
        "timezone": "America/Santiago",
        "forecast_days": max(1, min(forecast_days, 16)),
    }
    data = _get_json(FORECAST_API_BASE, params)
    if data is None:
        # Reintento sin boundary_layer_height (modelo puede no soportarla).
        params["hourly"] = ",".join(_HOURLY_BASE)
        data = _get_json(FORECAST_API_BASE, params)
    return data


# ------------------------------------------------------------------ física disp.

_VIENTO_CATS = (
    (0.5, "calma"),
    (1.5, "flojo"),
    (3.0, "leve"),
    (5.5, "moderado"),
    (8.0, "favorable"),
    (float("inf"), "fuerte"),
)


def categoria_viento(vel_ms: float | None) -> str | None:
    if vel_ms is None:
        return None
    for limite, nombre in _VIENTO_CATS:
        if vel_ms < limite:
            return nombre
    return "fuerte"


def clasificar_inversion(temp_2m: float | None, temp_925: float | None, temp_850: float | None) -> dict[str, Any]:
    """Inversión térmica desde el gradiente 2 m ↔ 925 hPa (~760 m)."""
    if temp_2m is None or temp_925 is None:
        return {"gradiente_termico": None, "inversion": None, "inversion_intensidad": None}
    grad = round(temp_925 - temp_2m, 2)  # >0 → T sube con la altura = inversión
    # Refuerzo con el tramo 925↔850 hPa si está disponible.
    if temp_850 is not None and (temp_850 - temp_925) > grad:
        grad = round(temp_850 - temp_925, 2)
    intensidad = max(0.0, grad)
    return {
        "gradiente_termico": grad,
        "inversion": grad > 0.5,
        "inversion_intensidad": round(intensidad, 2),
    }


def clasificar_nubosidad(
    nubosidad_baja: float | None, visibilidad_km: float | None, humedad: float | None
) -> dict[str, Any]:
    """Niebla / neblina / estratos (baja costera) para atrapamiento de contaminantes."""
    niebla = visibilidad_km is not None and visibilidad_km < 1.0
    if niebla:
        tipo = "niebla"
    elif visibilidad_km is not None and visibilidad_km < 5.0 and (humedad or 0) >= 85:
        tipo = "neblina"
    elif (nubosidad_baja or 0) >= 60:
        tipo = "estratos"
    else:
        tipo = "despejado"
    return {"niebla": bool(niebla), "tipo_nubosidad": tipo}


def indice_dispersion(
    viento_ms: float | None,
    inversion_intensidad: float | None,
    tipo_nubosidad: str | None,
    capa_limite: float | None,
) -> dict[str, Any]:
    """Índice 0-100 (mayor = mejor dispersión) y categoría cualitativa.

    Combina ventilación horizontal (viento), estabilidad (inversión), mezcla
    vertical (capa límite) y atrapamiento por nubosidad baja / niebla.
    """
    if viento_ms is None:
        return {"indice_dispersion": None, "potencial_dispersion": None, "alerta_dispersion": None}

    # Ventilación horizontal: satura hacia 8 m/s.
    base = min(viento_ms / 8.0, 1.0) * 100.0

    # Penalización por inversión (estabilidad estática).
    inv = inversion_intensidad or 0.0
    if inv >= 4:
        f_estab = 0.25
    elif inv >= 2:
        f_estab = 0.5
    elif inv > 0.5:
        f_estab = 0.75
    else:
        f_estab = 1.0

    # Penalización por nubosidad baja / niebla (atrapamiento).
    f_nub = {"niebla": 0.4, "neblina": 0.6, "estratos": 0.8}.get(tipo_nubosidad or "despejado", 1.0)

    # Bono/penalización por altura de capa límite (mezcla vertical).
    if capa_limite is not None:
        if capa_limite < 200:
            f_pbl = 0.5
        elif capa_limite < 500:
            f_pbl = 0.8
        elif capa_limite > 1200:
            f_pbl = 1.1
        else:
            f_pbl = 1.0
    else:
        f_pbl = 1.0

    indice = max(0.0, min(100.0, base * f_estab * f_nub * f_pbl))

    if indice < 20:
        cat = "muy_baja"
    elif indice < 40:
        cat = "baja"
    elif indice < 60:
        cat = "moderada"
    elif indice < 80:
        cat = "buena"
    else:
        cat = "muy_buena"

    return {
        "indice_dispersion": round(indice, 1),
        "potencial_dispersion": cat,
        "alerta_dispersion": indice < UMBRAL_ALERTA_DISPERSION,
    }


def _evaluar_hora(reg: dict[str, Any]) -> dict[str, Any]:
    """Enriquece un registro horario con inversión, nubosidad e índice."""
    inv = clasificar_inversion(
        reg.get("temp_2m"), reg.get("temp_925hpa"), reg.get("temp_850hpa")
    )
    nub = clasificar_nubosidad(
        reg.get("nubosidad_baja"), reg.get("visibilidad"), reg.get("humedad_relativa")
    )
    idx = indice_dispersion(
        reg.get("viento_velocidad"),
        inv.get("inversion_intensidad"),
        nub.get("tipo_nubosidad"),
        reg.get("altura_capa_limite"),
    )
    reg.update(inv)
    reg.update(nub)
    reg.update(idx)
    reg["viento_categoria"] = categoria_viento(reg.get("viento_velocidad"))
    return reg


def _fila_horaria(hourly: dict[str, Any], i: int) -> dict[str, Any]:
    def val(clave):
        serie = hourly.get(clave) or []
        v = serie[i] if i < len(serie) else None
        return round(float(v), 2) if isinstance(v, (int, float)) else None

    vis = val("visibility")
    reg = {
        "fecha_hora": (hourly.get("time") or [None] * (i + 1))[i],
        "temp_2m": val("temperature_2m"),
        "temp_925hpa": val("temperature_925hPa"),
        "temp_850hpa": val("temperature_850hPa"),
        "humedad_relativa": val("relative_humidity_2m"),
        "nubosidad_baja": val("cloud_cover_low"),
        "visibilidad": round(vis / 1000.0, 2) if vis is not None else None,  # m → km
        "viento_velocidad": val("wind_speed_10m"),
        "viento_racha": val("wind_gusts_10m"),
        "viento_direccion": val("wind_direction_10m"),
        "altura_capa_limite": val(_HOURLY_PBL),
    }
    return _evaluar_hora(reg)


# ------------------------------------------------------------------ servicios


def _coords(estacion_id: str) -> dict[str, float] | None:
    key = estacion_id.lower().replace("-", "_")
    if key not in SLUG_A_NOMBRE:
        return None
    return COORDS.get(key)


def dispersion_horaria(estacion_id: str, horas: int = 72) -> list[dict[str, Any]] | None:
    """Serie horaria de dispersión (24/48/72 h)."""
    coords = _coords(estacion_id)
    if coords is None:
        return None
    horas = max(1, min(horas, 168))
    dias = (horas + 23) // 24 + 1
    payload = _fetch_forecast(coords["lat"], coords["lon"], forecast_days=dias)
    if not payload:
        return _leer_dispersion_store(estacion_id, "horaria", horas) or None
    hourly = payload.get("hourly") or {}
    tiempos = hourly.get("time") or []
    ahora = datetime.now(TZ_CHILE)
    filas: list[dict[str, Any]] = []
    for i, ts in enumerate(tiempos):
        try:
            t = datetime.fromisoformat(str(ts)).replace(tzinfo=TZ_CHILE)
        except ValueError:
            continue
        if t < ahora - timedelta(hours=1):
            continue
        filas.append(_fila_horaria(hourly, i))
        if len(filas) >= horas:
            break
    return filas


def _agregar_diario(filas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Resumen diario: caso más desfavorable (peor índice) + promedios."""
    por_dia: dict[str, list[dict[str, Any]]] = {}
    for f in filas:
        dia = str(f.get("fecha_hora") or "")[:10]
        if dia:
            por_dia.setdefault(dia, []).append(f)
    salida: list[dict[str, Any]] = []
    for dia in sorted(por_dia):
        grupo = por_dia[dia]
        idxs = [g["indice_dispersion"] for g in grupo if g.get("indice_dispersion") is not None]
        vientos = [g["viento_velocidad"] for g in grupo if g.get("viento_velocidad") is not None]
        inversiones = [g for g in grupo if g.get("inversion")]
        peor = min(grupo, key=lambda g: g.get("indice_dispersion", 999)) if grupo else {}
        salida.append(
            {
                "fecha_hora": f"{dia}T12:00:00",
                "fecha": dia,
                "indice_dispersion": round(min(idxs), 1) if idxs else None,
                "indice_dispersion_promedio": round(sum(idxs) / len(idxs), 1) if idxs else None,
                "potencial_dispersion": peor.get("potencial_dispersion"),
                "alerta_dispersion": bool(peor.get("alerta_dispersion")),
                "viento_velocidad": round(sum(vientos) / len(vientos), 2) if vientos else None,
                "viento_categoria": peor.get("viento_categoria"),
                "inversion": len(inversiones) > 0,
                "horas_inversion": len(inversiones),
                "tipo_nubosidad": peor.get("tipo_nubosidad"),
                "niebla": any(g.get("niebla") for g in grupo),
            }
        )
    return salida


def dispersion_diaria(estacion_id: str, dias: int = 7) -> list[dict[str, Any]] | None:
    """Resumen diario de dispersión hasta 7 días (peor caso del día)."""
    coords = _coords(estacion_id)
    if coords is None:
        return None
    dias = max(1, min(dias, 16))
    payload = _fetch_forecast(coords["lat"], coords["lon"], forecast_days=dias)
    if not payload:
        return _leer_dispersion_store(estacion_id, "diaria", dias) or None
    hourly = payload.get("hourly") or {}
    tiempos = hourly.get("time") or []
    filas = [_fila_horaria(hourly, i) for i in range(len(tiempos))]
    return _agregar_diario(filas)[:dias]


def _leer_dispersion_store(estacion_id: str, horizonte: str, limite: int) -> list[dict[str, Any]]:
    try:
        from api_rest.integracion import aire_store

        return aire_store.leer_dispersion(
            estacion_id.lower().replace("-", "_"), horizonte=horizonte, limite=limite
        )
    except Exception:
        return []


# ---------------------------------------------- proyección climatológica 16-30 d


def _fetch_climatologia(lat: float, lon: float, dia_ini: int, dia_fin: int, anios: int = 3) -> dict[str, list[float]]:
    """Trae del archivo la ventana [hoy+dia_ini, hoy+dia_fin] en los últimos `anios`."""
    hoy = datetime.now(TZ_CHILE).date()
    acumulado: dict[str, list[float]] = {"viento": [], "rango_termico": [], "nubosidad": []}
    for k in range(1, anios + 1):
        ini = hoy.replace(year=hoy.year - k) + timedelta(days=dia_ini)
        fin = hoy.replace(year=hoy.year - k) + timedelta(days=dia_fin)
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": ini.isoformat(),
            "end_date": fin.isoformat(),
            "daily": "temperature_2m_max,temperature_2m_min,wind_speed_10m_max,cloud_cover_mean",
            "wind_speed_unit": "ms",
            "timezone": "America/Santiago",
        }
        data = _get_json(ARCHIVE_API_BASE, params)
        daily = (data or {}).get("daily") or {}
        vmax = daily.get("wind_speed_10m_max") or []
        tmax = daily.get("temperature_2m_max") or []
        tmin = daily.get("temperature_2m_min") or []
        nub = daily.get("cloud_cover_mean") or []
        for i in range(len(vmax)):
            if vmax[i] is not None:
                acumulado["viento"].append(float(vmax[i]))
            if i < len(tmax) and i < len(tmin) and tmax[i] is not None and tmin[i] is not None:
                acumulado["rango_termico"].append(float(tmax[i]) - float(tmin[i]))
            if i < len(nub) and nub[i] is not None:
                acumulado["nubosidad"].append(float(nub[i]))
    return acumulado


def dispersion_proyeccion(estacion_id: str, dia_ini: int = 16, dia_fin: int = 30) -> dict[str, Any] | None:
    """Proyección estadística (climatología) para 16-30 días. Baja confianza."""
    coords = _coords(estacion_id)
    if coords is None:
        return None
    clima = _fetch_climatologia(coords["lat"], coords["lon"], dia_ini, dia_fin)
    vientos = clima.get("viento") or []
    rangos = clima.get("rango_termico") or []
    nubes = clima.get("nubosidad") or []
    if not vientos:
        return None
    viento_medio = sum(vientos) / len(vientos)
    rango_medio = sum(rangos) / len(rangos) if rangos else None
    nub_media = sum(nubes) / len(nubes) if nubes else None
    # Heurística: gran amplitud térmica nocturna ⇒ inversión radiativa probable.
    inv_intensidad = 2.0 if (rango_medio or 0) > 14 else (1.0 if (rango_medio or 0) > 10 else 0.0)
    tipo_nub = "estratos" if (nub_media or 0) > 60 else "despejado"
    idx = indice_dispersion(viento_medio, inv_intensidad, tipo_nub, None)
    return {
        "estacion_id": estacion_id.lower().replace("-", "_"),
        "horizonte": "proyeccion",
        "dia_desde": dia_ini,
        "dia_hasta": dia_fin,
        "confianza": "baja",
        "metodo": "climatologia_archivo",
        "viento_velocidad": round(viento_medio, 2),
        "rango_termico_medio": round(rango_medio, 1) if rango_medio is not None else None,
        "nubosidad_media": round(nub_media, 1) if nub_media is not None else None,
        "inversion_probable": inv_intensidad > 0,
        **idx,
    }


# ------------------------------------------------------------------ ETL + alertas


def sincronizar_dispersion(estaciones: list[str] | None = None) -> dict[str, Any]:
    """ETL dispersión → aire_dispersion (horaria 72 h + diaria 7 d) para el airshed."""
    try:
        from api_rest.integracion import aire_store
    except Exception as exc:  # pragma: no cover
        return {"dispersion_sync": {}, "error": f"aire_store no disponible: {exc}"}

    slugs = estaciones or ESTACIONES_POR_SITIO.get("copiapo", [])
    detalle: dict[str, int] = {}
    errores: list[str] = []
    for slug in slugs:
        escritos = 0
        try:
            horaria = dispersion_horaria(slug, horas=72) or []
            escritos += aire_store.guardar_dispersion(slug, horaria, horizonte="horaria")
        except Exception as exc:
            errores.append(f"{slug} (horaria): {exc}")
        try:
            diaria = dispersion_diaria(slug, dias=7) or []
            escritos += aire_store.guardar_dispersion(slug, diaria, horizonte="diaria")
        except Exception as exc:
            errores.append(f"{slug} (diaria): {exc}")
        detalle[slug] = escritos
    return {"dispersion_sync": detalle, "errores": errores}


def alertas_dispersion(sitio: str = "copiapo", horizonte: str = "horaria") -> dict[str, Any]:
    """Alertas de mala dispersión (acumulación de contaminantes) por horizonte."""
    slugs = ESTACIONES_POR_SITIO.get(sitio, [])
    activas: list[dict[str, Any]] = []
    for slug in slugs:
        try:
            if horizonte == "diaria":
                serie = dispersion_diaria(slug, dias=7) or []
            elif horizonte == "proyeccion":
                proy = dispersion_proyeccion(slug)
                serie = [proy] if proy else []
            else:
                serie = dispersion_horaria(slug, horas=72) or []
        except Exception:
            serie = []
        ventanas = [
            {
                "estacion_id": slug,
                "nombre": SLUG_A_NOMBRE.get(slug, slug),
                "fecha_hora": f.get("fecha_hora"),
                "indice_dispersion": f.get("indice_dispersion"),
                "potencial_dispersion": f.get("potencial_dispersion"),
                "inversion": f.get("inversion") or f.get("inversion_probable"),
                "tipo_nubosidad": f.get("tipo_nubosidad"),
                "viento_categoria": f.get("viento_categoria"),
            }
            for f in serie
            if f.get("alerta_dispersion")
        ]
        if ventanas:
            activas.append(
                {
                    "estacion_id": slug,
                    "nombre": SLUG_A_NOMBRE.get(slug, slug),
                    "ventanas_alerta": len(ventanas),
                    "primera": ventanas[0],
                }
            )
    return {
        "sitio": sitio,
        "horizonte": horizonte,
        "umbral_indice": UMBRAL_ALERTA_DISPERSION,
        "hay_alerta": bool(activas),
        "estaciones": activas,
    }
