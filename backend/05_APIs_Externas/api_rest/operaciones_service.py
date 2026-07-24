#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ventanas operacionales de faena (E8 — Mantos Blancos).

Semáforo (verde/amarillo/rojo) por actividad crítica según meteorología:
  - **Tronadura**: viento alto descontrola la nube de polvo; viento muy bajo la
    estanca; baja visibilidad impide el disparo seguro.
  - **Transporte** (rutas): visibilidad (niebla/polvo), precipitación (barro) y
    ráfagas que levantan polvo.
  - **Izaje** (grúas): ráfagas y viento sostenido (límites de carta de grúa).
  - **Exposición UV**: índice UV para turnos a cielo abierto (HSE).
  - **SO₂**: concentración (CAMS) como factor de riesgo sanitario en faena.

Umbrales: defaults conservadores, sobrescribibles por sitio y por
`METGO_OP_UMBRALES_JSON` (JSON en env de Render).

Alertas por turno (día 07:00–19:00 / noche 19:00–07:00).
Fuente: Open-Meteo Forecast (+ Air Quality para SO₂).
"""

from __future__ import annotations

import copy
import json
import os
from datetime import datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from api_rest.dispersion_service import FORECAST_API_BASE, _get_json
from api_rest.estaciones_catalogo import COORDS, ESTACIONES_POR_SITIO, SLUG_A_NOMBRE

TZ_CHILE = ZoneInfo("America/Santiago")
AIR_API_BASE = "https://air-quality-api.open-meteo.com/v1/air-quality"

_NIVEL_ORDEN = {"verde": 0, "amarillo": 1, "rojo": 2}
_ACTIVIDADES = ("tronadura", "transporte", "izaje", "exposicion_uv")

# Defaults (amarillo, rojo). Cliente puede ajustar vía env o endpoint de consulta.
UMBRALES_DEFAULT: dict[str, dict[str, Any]] = {
    "izaje": {
        "racha": (11.0, 17.0),
        "viento_sostenido": (10.0, 14.0),
    },
    "tronadura": {
        "viento_sostenido": (10.0, 14.0),
        "racha": (12.0, 16.0),
        "visibilidad": (5.0, 2.0),
        "viento_min_dispersion": 1.5,
    },
    "transporte": {
        "visibilidad": (5.0, 1.0),
        "precipitacion": (2.0, 8.0),
        "racha": (16.0, 22.0),
    },
    "exposicion_uv": {
        "uv_index": (6.0, 10.0),  # OMS: alto / extremo
    },
    "so2": {
        "so2": (50.0, 125.0),  # µg/m³ — precaución / crítico (orden de norma)
    },
}

# Overrides opcionales por sitio (vacío = usa DEFAULT; útil para otras faenas).
UMBRALES_POR_SITIO: dict[str, dict[str, Any]] = {
    "mantos_blancos": {},
}

# Compat tests / imports antiguos
UMBRALES = UMBRALES_DEFAULT

_HOURLY = [
    "wind_speed_10m",
    "wind_gusts_10m",
    "wind_direction_10m",
    "visibility",
    "precipitation",
    "uv_index",
    "temperature_2m",
]


def _merge_umbrales(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(base)
    for act, params in (override or {}).items():
        if not isinstance(params, dict):
            continue
        slot = out.setdefault(act, {})
        for k, v in params.items():
            if isinstance(v, (list, tuple)) and len(v) == 2:
                slot[k] = (float(v[0]), float(v[1]))
            else:
                slot[k] = v
    return out


def obtener_umbrales(sitio: str = "mantos_blancos") -> dict[str, Any]:
    """Umbrales efectivos: default → sitio → METGO_OP_UMBRALES_JSON."""
    sitio = (sitio or "mantos_blancos").strip().lower()
    umb = _merge_umbrales(UMBRALES_DEFAULT, UMBRALES_POR_SITIO.get(sitio) or {})
    raw = (os.getenv("METGO_OP_UMBRALES_JSON") or "").strip()
    if raw:
        try:
            umb = _merge_umbrales(umb, json.loads(raw))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            print(f"operaciones: METGO_OP_UMBRALES_JSON inválido: {exc}")
    return umb


def umbrales_publicos(sitio: str = "mantos_blancos") -> dict[str, Any]:
    """Payload documentado para SPA / HSE (tuplas → listas)."""
    umb = obtener_umbrales(sitio)

    def _ser(v: Any) -> Any:
        if isinstance(v, tuple):
            return list(v)
        if isinstance(v, dict):
            return {k: _ser(x) for k, x in v.items()}
        return v

    return {
        "sitio": sitio,
        "fuente": "default+sitio+env",
        "actividades": _ACTIVIDADES,
        "umbrales": _ser(umb),
        "unidades": {
            "racha": "m/s",
            "viento_sostenido": "m/s",
            "visibilidad": "km",
            "precipitacion": "mm/h",
            "uv_index": "índice UV",
            "so2": "µg/m³",
            "viento_min_dispersion": "m/s",
        },
        "nota": (
            "Pares (amarillo, rojo). Visibilidad es umbral inverso (menor = peor). "
            "Override: variable de entorno METGO_OP_UMBRALES_JSON."
        ),
    }


# ------------------------------------------------------------------ semáforo


def _nivel_directo(valor: float | None, amarillo: float, rojo: float) -> str:
    if valor is None:
        return "verde"
    if valor >= rojo:
        return "rojo"
    if valor >= amarillo:
        return "amarillo"
    return "verde"


def _nivel_inverso(valor: float | None, amarillo: float, rojo: float) -> str:
    """Menor valor = peor (p. ej. visibilidad)."""
    if valor is None:
        return "verde"
    if valor <= rojo:
        return "rojo"
    if valor <= amarillo:
        return "amarillo"
    return "verde"


def _peor(*niveles: str) -> str:
    return max(niveles, key=lambda n: _NIVEL_ORDEN.get(n, 0)) if niveles else "verde"


def _par(u: dict[str, Any], clave: str, default: tuple[float, float]) -> tuple[float, float]:
    v = u.get(clave, default)
    if isinstance(v, (list, tuple)) and len(v) >= 2:
        return float(v[0]), float(v[1])
    return default


def _evaluar_izaje(reg: dict[str, Any], umb: dict[str, Any] | None = None) -> dict[str, Any]:
    u = (umb or UMBRALES_DEFAULT)["izaje"]
    factores = []
    n_racha = _nivel_directo(reg.get("viento_racha"), *_par(u, "racha", (11.0, 17.0)))
    n_vel = _nivel_directo(reg.get("viento_sostenido"), *_par(u, "viento_sostenido", (10.0, 14.0)))
    if n_racha != "verde":
        factores.append(f"ráfaga {reg.get('viento_racha')} m/s")
    if n_vel != "verde":
        factores.append(f"viento {reg.get('viento_sostenido')} m/s")
    return {"nivel": _peor(n_racha, n_vel), "factores": factores}


def _evaluar_tronadura(reg: dict[str, Any], umb: dict[str, Any] | None = None) -> dict[str, Any]:
    u = (umb or UMBRALES_DEFAULT)["tronadura"]
    factores = []
    n_vel = _nivel_directo(reg.get("viento_sostenido"), *_par(u, "viento_sostenido", (10.0, 14.0)))
    n_racha = _nivel_directo(reg.get("viento_racha"), *_par(u, "racha", (12.0, 16.0)))
    n_vis = _nivel_inverso(reg.get("visibilidad"), *_par(u, "visibilidad", (5.0, 2.0)))
    niveles = [n_vel, n_racha, n_vis]
    vel = reg.get("viento_sostenido")
    vmin = float(u.get("viento_min_dispersion", 1.5))
    if vel is not None and vel < vmin:
        niveles.append("amarillo")
        factores.append("viento insuficiente para dispersar polvo")
    if n_vel != "verde":
        factores.append(f"viento {vel} m/s")
    if n_racha != "verde":
        factores.append(f"ráfaga {reg.get('viento_racha')} m/s")
    if n_vis != "verde":
        factores.append(f"visibilidad {reg.get('visibilidad')} km")
    return {"nivel": _peor(*niveles), "factores": factores}


def _evaluar_transporte(reg: dict[str, Any], umb: dict[str, Any] | None = None) -> dict[str, Any]:
    u = (umb or UMBRALES_DEFAULT)["transporte"]
    factores = []
    n_vis = _nivel_inverso(reg.get("visibilidad"), *_par(u, "visibilidad", (5.0, 1.0)))
    n_pp = _nivel_directo(reg.get("precipitacion"), *_par(u, "precipitacion", (2.0, 8.0)))
    n_racha = _nivel_directo(reg.get("viento_racha"), *_par(u, "racha", (16.0, 22.0)))
    if n_vis != "verde":
        factores.append(f"visibilidad {reg.get('visibilidad')} km")
    if n_pp != "verde":
        factores.append(f"precipitación {reg.get('precipitacion')} mm/h")
    if n_racha != "verde":
        factores.append(f"ráfaga {reg.get('viento_racha')} m/s")
    # SO₂ (si viene en el registro) como factor de transporte / HSE en ruta
    so2_u = (umb or UMBRALES_DEFAULT).get("so2") or {}
    n_so2 = _nivel_directo(reg.get("so2"), *_par(so2_u, "so2", (50.0, 125.0)))
    if n_so2 != "verde":
        factores.append(f"SO₂ {reg.get('so2')} µg/m³")
    return {"nivel": _peor(n_vis, n_pp, n_racha, n_so2), "factores": factores}


def _evaluar_exposicion_uv(reg: dict[str, Any], umb: dict[str, Any] | None = None) -> dict[str, Any]:
    u = (umb or UMBRALES_DEFAULT).get("exposicion_uv") or {}
    factores = []
    n_uv = _nivel_directo(reg.get("uv_index"), *_par(u, "uv_index", (6.0, 10.0)))
    if n_uv != "verde":
        factores.append(f"UV {reg.get('uv_index')}")
    return {"nivel": n_uv, "factores": factores}


_EVALUADORES = {
    "tronadura": _evaluar_tronadura,
    "transporte": _evaluar_transporte,
    "izaje": _evaluar_izaje,
    "exposicion_uv": _evaluar_exposicion_uv,
}


def evaluar_hora(reg: dict[str, Any], umb: dict[str, Any] | None = None) -> dict[str, Any]:
    """Evalúa el semáforo de cada actividad para un registro horario."""
    umbrales = umb or UMBRALES_DEFAULT
    actividades = {act: _EVALUADORES[act](reg, umbrales) for act in _ACTIVIDADES}
    nivel_global = _peor(*(a["nivel"] for a in actividades.values()))
    return {**reg, "actividades": actividades, "nivel_global": nivel_global}


# --------------------------------------------------------------------- fetch


def _coords(estacion_id: str) -> dict[str, float] | None:
    key = estacion_id.lower().replace("-", "_")
    if key not in SLUG_A_NOMBRE:
        return None
    return COORDS.get(key)


def _fetch(lat: float, lon: float, forecast_days: int) -> dict[str, Any] | None:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(_HOURLY),
        "wind_speed_unit": "ms",
        "timezone": "America/Santiago",
        "forecast_days": max(1, min(forecast_days, 16)),
    }
    return _get_json(FORECAST_API_BASE, params)


def _fetch_so2_actual(lat: float, lon: float) -> float | None:
    """SO₂ actual (µg/m³) desde Open-Meteo Air Quality (CAMS)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "sulphur_dioxide",
        "timezone": "America/Santiago",
    }
    data = _get_json(AIR_API_BASE, params)
    if not data:
        return None
    val = (data.get("current") or {}).get("sulphur_dioxide")
    try:
        return round(float(val), 1) if val is not None else None
    except (TypeError, ValueError):
        return None


def _fila(hourly: dict[str, Any], i: int, so2: float | None = None) -> dict[str, Any]:
    def val(clave):
        serie = hourly.get(clave) or []
        v = serie[i] if i < len(serie) else None
        return round(float(v), 2) if isinstance(v, (int, float)) else None

    vis = val("visibility")
    return {
        "fecha_hora": (hourly.get("time") or [None] * (i + 1))[i],
        "viento_sostenido": val("wind_speed_10m"),
        "viento_racha": val("wind_gusts_10m"),
        "viento_direccion": val("wind_direction_10m"),
        "visibilidad": round(vis / 1000.0, 2) if vis is not None else None,
        "precipitacion": val("precipitation"),
        "uv_index": val("uv_index"),
        "temperatura": val("temperature_2m"),
        "so2": so2,
    }


# ------------------------------------------------------------------ servicios


def _sitio_de_estacion(estacion_id: str) -> str:
    key = estacion_id.lower().replace("-", "_")
    for sitio, slugs in ESTACIONES_POR_SITIO.items():
        if key in slugs:
            return sitio
    return "mantos_blancos"


def ventanas_operacionales(
    estacion_id: str,
    horas: int = 48,
    sitio: str | None = None,
) -> list[dict[str, Any]] | None:
    """Serie horaria con semáforo por actividad (24/48/72 h)."""
    coords = _coords(estacion_id)
    if coords is None:
        return None
    horas = max(1, min(horas, 168))
    dias = (horas + 23) // 24 + 1
    umb = obtener_umbrales(sitio or _sitio_de_estacion(estacion_id))
    payload = _fetch(coords["lat"], coords["lon"], forecast_days=dias)
    if not payload:
        return _leer_store(estacion_id, horas) or None
    so2 = _fetch_so2_actual(coords["lat"], coords["lon"])
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
        filas.append(evaluar_hora(_fila(hourly, i, so2=so2), umb))
        if len(filas) >= horas:
            break
    return filas


def _leer_store(estacion_id: str, horas: int) -> list[dict[str, Any]]:
    try:
        from api_rest.integracion import operaciones_store

        return operaciones_store.leer_ventanas(
            estacion_id.lower().replace("-", "_"), limite=horas
        )
    except Exception:
        return []


def proxima_ventana(serie: list[dict[str, Any]], actividad: str) -> dict[str, Any] | None:
    """Primera hora con semáforo verde para una actividad."""
    for f in serie:
        act = (f.get("actividades") or {}).get(actividad)
        if act and act.get("nivel") == "verde":
            return {"fecha_hora": f.get("fecha_hora"), "nivel": "verde"}
    return None


def _rango_turno(turno: str, ahora: datetime) -> tuple[datetime, datetime]:
    """Ventana del próximo turno (día 07-19 / noche 19-07)."""
    hoy = ahora.date()
    if turno == "noche":
        ini = datetime.combine(hoy, time(19, 0), tzinfo=TZ_CHILE)
        if ahora >= datetime.combine(hoy, time(7, 0), tzinfo=TZ_CHILE) and ahora < ini:
            fin = ini + timedelta(hours=12)
        else:
            if ahora < ini:
                ini = ini - timedelta(days=1)
            fin = ini + timedelta(hours=12)
    else:  # día
        ini = datetime.combine(hoy, time(7, 0), tzinfo=TZ_CHILE)
        if ahora >= datetime.combine(hoy, time(19, 0), tzinfo=TZ_CHILE):
            ini = ini + timedelta(days=1)
        fin = ini + timedelta(hours=12)
    return ini, fin


def alertas_turno(sitio: str = "mantos_blancos", turno: str = "dia") -> dict[str, Any]:
    """Resumen del próximo turno: actividades bloqueadas por punto de faena."""
    turno = turno if turno in ("dia", "noche") else "dia"
    sitio = (sitio or "mantos_blancos").strip().lower()
    slugs = ESTACIONES_POR_SITIO.get(sitio, [])
    ahora = datetime.now(TZ_CHILE)
    ini, fin = _rango_turno(turno, ahora)
    umb = obtener_umbrales(sitio)
    estaciones: list[dict[str, Any]] = []
    for slug in slugs:
        serie = ventanas_operacionales(slug, horas=72, sitio=sitio) or []
        ventana = []
        for f in serie:
            try:
                t = datetime.fromisoformat(str(f.get("fecha_hora"))).replace(tzinfo=TZ_CHILE)
            except (ValueError, TypeError):
                continue
            if ini <= t < fin:
                ventana.append(f)
        if not ventana:
            continue
        resumen_act: dict[str, Any] = {}
        for act in _ACTIVIDADES:
            niveles = [(v.get("actividades") or {}).get(act, {}).get("nivel", "verde") for v in ventana]
            horas_rojo = sum(1 for n in niveles if n == "rojo")
            horas_amarillo = sum(1 for n in niveles if n == "amarillo")
            resumen_act[act] = {
                "nivel_peor": _peor(*niveles) if niveles else "verde",
                "horas_rojo": horas_rojo,
                "horas_amarillo": horas_amarillo,
                "bloqueada": horas_rojo > 0,
            }
        so2_vals = [v.get("so2") for v in ventana if v.get("so2") is not None]
        estaciones.append(
            {
                "estacion_id": slug,
                "nombre": SLUG_A_NOMBRE.get(slug, slug),
                "nivel_global": _peor(*(a["nivel_peor"] for a in resumen_act.values())),
                "actividades": resumen_act,
                "so2": so2_vals[0] if so2_vals else None,
                "proxima_ventana": {
                    act: proxima_ventana(ventana, act) for act in _ACTIVIDADES
                },
            }
        )
    hay_bloqueo = any(
        a["bloqueada"] for e in estaciones for a in e["actividades"].values()
    )
    return {
        "sitio": sitio,
        "turno": turno,
        "desde": ini.isoformat(timespec="minutes"),
        "hasta": fin.isoformat(timespec="minutes"),
        "hay_bloqueo": hay_bloqueo,
        "umbrales_aplicados": umbrales_publicos(sitio)["umbrales"],
        "estaciones": estaciones,
    }


def sincronizar_operaciones(estaciones: list[str] | None = None) -> dict[str, Any]:
    """ETL ventanas operacionales → operaciones_ventanas (48 h) para la faena."""
    try:
        from api_rest.integracion import operaciones_store
    except Exception as exc:  # pragma: no cover
        return {"operaciones_sync": {}, "error": f"operaciones_store no disponible: {exc}"}

    slugs = estaciones or ESTACIONES_POR_SITIO.get("mantos_blancos", [])
    detalle: dict[str, int] = {}
    errores: list[str] = []
    for slug in slugs:
        try:
            serie = ventanas_operacionales(slug, horas=48) or []
            detalle[slug] = operaciones_store.guardar_ventanas(slug, serie)
        except Exception as exc:
            errores.append(f"{slug}: {exc}")
            detalle[slug] = 0
    return {"operaciones_sync": detalle, "errores": errores}
