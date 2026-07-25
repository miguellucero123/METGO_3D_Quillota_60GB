#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Olas de calor estacionales (otoño / invierno) — faena Paipote / airshed.

Definición operativa METGO (hemisferio sur):
  - Umbral diario: percentil 90 de Tmáx histórica (±15 días) sobre Archive ~7 años.
  - Ola: ≥3 días consecutivos con Tmáx ≥ P90 y anomalía media ≥ +3 °C.
  - Intensidad: leve | moderada | fuerte (duración + °C·día acumulados).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from api_rest.estaciones_catalogo import COORDS, SLUG_A_NOMBRE
from api_rest.ventilacion_service import historico_diario

TZ_CHILE = ZoneInfo("America/Santiago")

# Meses hemisferio sur
_ESTACIONES = {
    "otono": {3, 4, 5},
    "invierno": {6, 7, 8},
    "primavera": {9, 10, 11},
    "verano": {12, 1, 2},
}


def _parse_fecha(s: str) -> date | None:
    try:
        return date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


def _doy_ventana(d: date, radio: int = 15) -> list[int]:
    """Días del año vecinos (±radio), con wrap 1–366."""
    base = d.replace(year=2000)  # año bisiesto-friendly
    out = []
    for off in range(-radio, radio + 1):
        x = base + timedelta(days=off)
        out.append(x.timetuple().tm_yday)
    return out


def _p90(vals: list[float]) -> float | None:
    if len(vals) < 5:
        return None
    s = sorted(vals)
    idx = int(round(0.9 * (len(s) - 1)))
    return s[idx]


def _media(vals: list[float]) -> float | None:
    if not vals:
        return None
    return sum(vals) / len(vals)


def _intensidad(duracion: int, acum_anom: float) -> str:
    if duracion >= 6 or acum_anom >= 25:
        return "fuerte"
    if duracion >= 4 or acum_anom >= 12:
        return "moderada"
    return "leve"


def _filtrar_estacion(filas: list[dict], estacion_ano: str) -> list[dict]:
    if estacion_ano in ("todas", "actual", "anual"):
        return filas
    meses = _ESTACIONES.get(estacion_ano)
    if not meses:
        return filas
    out = []
    for f in filas:
        d = _parse_fecha(f.get("fecha") or "")
        if d and d.month in meses:
            out.append(f)
    return out


def _climatologia_p90(filas: list[dict]) -> dict[int, dict[str, float]]:
    """doy -> {p90_tmax, media_tmax, p90_tmin}."""
    por_doy: dict[int, list[float]] = {}
    por_doy_tmin: dict[int, list[float]] = {}
    por_doy_med: dict[int, list[float]] = {}
    for f in filas:
        d = _parse_fecha(f.get("fecha") or "")
        tmax = f.get("tmax")
        if d is None or tmax is None:
            continue
        doy = d.timetuple().tm_yday
        for nd in _doy_ventana(d, 15):
            por_doy.setdefault(nd, []).append(float(tmax))
            por_doy_med.setdefault(nd, []).append(float(tmax))
            if f.get("tmin") is not None:
                por_doy_tmin.setdefault(nd, []).append(float(f["tmin"]))
    out: dict[int, dict[str, float]] = {}
    for doy, vals in por_doy.items():
        p = _p90(vals)
        m = _media(por_doy_med.get(doy) or vals)
        pt = _p90(por_doy_tmin.get(doy) or [])
        if p is not None and m is not None:
            slot: dict[str, float] = {"p90_tmax": round(p, 2), "media_tmax": round(m, 2)}
            if pt is not None:
                slot["p90_tmin"] = round(pt, 2)
            out[doy] = slot
    return out


def _detectar_eventos(
    filas: list[dict],
    clima: dict[int, dict[str, float]],
    min_dias: int = 3,
    anom_min: float = 3.0,
) -> list[dict[str, Any]]:
    marcados: list[tuple[date, float, float, float]] = []  # fecha, tmax, p90, anom
    for f in filas:
        d = _parse_fecha(f.get("fecha") or "")
        tmax = f.get("tmax")
        if d is None or tmax is None:
            continue
        c = clima.get(d.timetuple().tm_yday)
        if not c:
            continue
        p90 = c["p90_tmax"]
        media = c["media_tmax"]
        anom = float(tmax) - media
        if float(tmax) >= p90 and anom >= anom_min:
            marcados.append((d, float(tmax), p90, anom))

    eventos: list[dict[str, Any]] = []
    if not marcados:
        return eventos

    bloque = [marcados[0]]
    for item in marcados[1:]:
        if item[0] == bloque[-1][0] + timedelta(days=1):
            bloque.append(item)
        else:
            if len(bloque) >= min_dias:
                eventos.append(_evento_desde_bloque(bloque))
            bloque = [item]
    if len(bloque) >= min_dias:
        eventos.append(_evento_desde_bloque(bloque))
    return eventos


def _evento_desde_bloque(bloque: list[tuple[date, float, float, float]]) -> dict[str, Any]:
    anomias = [b[3] for b in bloque]
    acum = sum(anomias)
    dur = len(bloque)
    return {
        "inicio": bloque[0][0].isoformat(),
        "fin": bloque[-1][0].isoformat(),
        "duracion_dias": dur,
        "tmax_max": round(max(b[1] for b in bloque), 2),
        "anomalia_media": round(sum(anomias) / dur, 2),
        "anomalia_acumulada": round(acum, 2),
        "intensidad": _intensidad(dur, acum),
        "noche_calida": False,  # se completa abajo si hay tmin
    }


def analizar_olas_calor(
    estacion_id: str = "paipote",
    estacion_ano: str = "otono",
    anios: int = 7,
    filas_hist: list[dict] | None = None,
) -> dict[str, Any] | None:
    slug = (estacion_id or "paipote").strip().lower().replace("-", "_")
    if slug not in SLUG_A_NOMBRE or COORDS.get(slug) is None:
        return None

    if filas_hist is None:
        hist = historico_diario(slug, anios=anios)
        if not hist or not hist.get("filas"):
            return {
                "estacion_id": slug,
                "error": "sin_historico",
                "estacion_ano": estacion_ano,
                "eventos": [],
            }
        filas = hist["filas"]
        meta_hist = {"desde": hist.get("desde"), "hasta": hist.get("hasta"), "n": hist.get("n")}
    else:
        filas = filas_hist
        meta_hist = {"n": len(filas)}

    clima = _climatologia_p90(filas)
    subset = _filtrar_estacion(filas, estacion_ano)
    eventos = _detectar_eventos(subset, clima)

    # Marcar noches cálidas (Tmín ≥ P90 Tmín)
    for ev in eventos:
        noches = 0
        d0 = date.fromisoformat(ev["inicio"])
        d1 = date.fromisoformat(ev["fin"])
        d = d0
        while d <= d1:
            fila = next((f for f in filas if f.get("fecha") == d.isoformat()), None)
            c = clima.get(d.timetuple().tm_yday) or {}
            if fila and fila.get("tmin") is not None and c.get("p90_tmin") is not None:
                if float(fila["tmin"]) >= float(c["p90_tmin"]):
                    noches += 1
            d += timedelta(days=1)
        ev["noche_calida"] = noches >= max(1, ev["duracion_dias"] // 2)
        ev["noches_calidas"] = noches

    # Estado reciente (últimos 14 días del histórico)
    hoy = datetime.now(TZ_CHILE).date()
    recientes = [
        f
        for f in filas
        if (d := _parse_fecha(f.get("fecha") or "")) and d >= hoy - timedelta(days=14)
    ]
    alerta_actual = False
    dias_sobre_p90 = 0
    for f in recientes:
        d = _parse_fecha(f["fecha"])
        if not d or f.get("tmax") is None:
            continue
        c = clima.get(d.timetuple().tm_yday)
        if not c:
            continue
        if float(f["tmax"]) >= c["p90_tmax"] and (float(f["tmax"]) - c["media_tmax"]) >= 3:
            dias_sobre_p90 += 1
    if dias_sobre_p90 >= 2:
        alerta_actual = True

    return {
        "estacion_id": slug,
        "estacion_nombre": SLUG_A_NOMBRE.get(slug, slug),
        "estacion_ano": estacion_ano,
        "definicion": {
            "percentil": 90,
            "ventana_doy_dias": 15,
            "min_dias_consecutivos": 3,
            "anomalia_min_c": 3.0,
            "hemisferio": "sur",
            "meses": sorted(_ESTACIONES.get(estacion_ano, set())) or "todas",
        },
        "historico": meta_hist,
        "n_eventos": len(eventos),
        "eventos": sorted(eventos, key=lambda e: e["inicio"], reverse=True),
        "alerta_reciente": alerta_actual,
        "dias_sobre_umbral_14d": dias_sobre_p90,
        "generado": datetime.now(TZ_CHILE).isoformat(timespec="seconds"),
    }


# API de prueba con series sintéticas (sin red)
def _eventos_desde_serie_sintetica(
    fechas_tmax: list[tuple[str, float]],
    p90: float = 20.0,
    media: float = 17.0,
) -> list[dict[str, Any]]:
    filas = [{"fecha": f, "tmax": t, "tmin": t - 8} for f, t in fechas_tmax]
    clima = {}
    for f, _t in fechas_tmax:
        d = date.fromisoformat(f)
        clima[d.timetuple().tm_yday] = {"p90_tmax": p90, "media_tmax": media, "p90_tmin": p90 - 8}
    return _detectar_eventos(filas, clima)
