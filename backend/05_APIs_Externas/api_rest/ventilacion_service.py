#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ventilación operativa faena Paipote (Observatorio Atmosférico).

Códigos por hora de proyección:
  N = Normal · R = Regular · M = Mala

Horizontes:
  - Horaria: 72 h (código N/R/M cada hora)
  - Diaria: 14 d (código representativo = peor del día)
  - Proyección: 30–90 d (climatología / tendencia)

Corridas oficiales del producto: **06 UTC** y **18 UTC**.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from api_rest import dispersion_service
from api_rest.estaciones_catalogo import COORDS, SLUG_A_NOMBRE

TZ_CHILE = ZoneInfo("America/Santiago")
TZ_UTC = timezone.utc

ESTACION_ANCLA = "paipote"
CORRIDAS_UTC = (6, 18)

_CACHE_DIR = Path(__file__).resolve().parents[3] / "metgo" / "cache" / "ventilacion_paipote"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Índice de dispersión → código operativo
# N: ventilación favorable (≥55) · R: intermedia · M: deficiente (<35)
def codigo_desde_indice(indice: float | None) -> str:
    if indice is None:
        return "R"
    if indice >= 55:
        return "N"
    if indice >= 35:
        return "R"
    return "M"


def label_codigo(codigo: str) -> str:
    return {"N": "normal", "R": "regular", "M": "mala"}.get(codigo, "regular")


def peor_codigo(codigos: list[str]) -> str:
    orden = {"M": 0, "R": 1, "N": 2}
    if not codigos:
        return "R"
    return min(codigos, key=lambda c: orden.get(c, 1))


def _ahora_utc() -> datetime:
    return datetime.now(TZ_UTC)


def corrida_vigente(ahora: datetime | None = None) -> dict[str, Any]:
    """Última corrida 06/18 UTC ya transcurrida y próxima."""
    now = ahora or _ahora_utc()
    if now.tzinfo is None:
        now = now.replace(tzinfo=TZ_UTC)
    else:
        now = now.astimezone(TZ_UTC)

    hoy = now.date()
    candidatos: list[datetime] = []
    for d_off in range(0, 3):
        dia = hoy - timedelta(days=d_off)
        for h in CORRIDAS_UTC:
            candidatos.append(datetime(dia.year, dia.month, dia.day, h, 0, 0, tzinfo=TZ_UTC))
    pasadas = [c for c in candidatos if c <= now]
    vigente = max(pasadas) if pasadas else candidatos[-1]

    futuras = []
    for d_off in range(0, 3):
        dia = hoy + timedelta(days=d_off)
        for h in CORRIDAS_UTC:
            t = datetime(dia.year, dia.month, dia.day, h, 0, 0, tzinfo=TZ_UTC)
            if t > now:
                futuras.append(t)
    proxima = min(futuras) if futuras else vigente + timedelta(hours=12)

    return {
        "corrida_utc": f"{vigente.hour:02d}",
        "corrida_en": vigente.isoformat(timespec="seconds"),
        "proxima_corrida_utc": f"{proxima.hour:02d}",
        "proxima_corrida_en": proxima.isoformat(timespec="seconds"),
        "generado_referencia_utc": now.isoformat(timespec="seconds"),
    }


def _cache_path(corrida_en: str) -> Path:
    safe = corrida_en.replace(":", "").replace("+", "_")
    return _CACHE_DIR / f"corrida_{safe}.json"


def _guardar_snapshot(payload: dict[str, Any]) -> None:
    try:
        path = _cache_path(payload.get("corrida_en") or "na")
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        # Mantener solo últimas 6 corridas
        archivos = sorted(_CACHE_DIR.glob("corrida_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for viejo in archivos[6:]:
            try:
                viejo.unlink()
            except OSError:
                pass
    except Exception:
        pass


def _cargar_ultimo_snapshot() -> dict[str, Any] | None:
    try:
        archivos = sorted(_CACHE_DIR.glob("corrida_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not archivos:
            return None
        return json.loads(archivos[0].read_text(encoding="utf-8"))
    except Exception:
        return None


def _enriquecer_hora(fila: dict[str, Any]) -> dict[str, Any]:
    codigo = codigo_desde_indice(fila.get("indice_dispersion"))
    out = dict(fila)
    out["ventilacion"] = codigo
    out["ventilacion_label"] = label_codigo(codigo)
    return out


def _icono_meteo(fila: dict[str, Any]) -> str:
    if fila.get("niebla") or fila.get("tipo_nubosidad") == "niebla":
        return "niebla"
    if fila.get("tipo_nubosidad") == "neblina":
        return "neblina"
    precip = fila.get("precipitacion")
    if precip is not None and precip > 0.2:
        return "lluvia"
    nub = fila.get("nubosidad_baja")
    if nub is None:
        nub = 0
    if nub >= 80:
        return "cubierto"
    if nub >= 40:
        return "parcialmente_nublado"
    return "despejado"


def _sinoptica_heuristica(filas: list[dict[str, Any]]) -> list[str]:
    """Etiquetas sinópticas tipificadas Atacama / valle Copiapó."""
    if not filas:
        return ["sin_dato"]
    dirs = [f.get("viento_direccion") for f in filas[:24] if f.get("viento_direccion") is not None]
    invs = sum(1 for f in filas[:24] if f.get("inversion"))
    vels = [f.get("viento_velocidad") or 0 for f in filas[:24]]
    vel_med = sum(vels) / len(vels) if vels else 0
    tags: list[str] = []
    if invs >= 8 and vel_med < 2.5:
        tags.append("inversion_radiativa_valle")
    if dirs:
        # Meteorológico FROM: S/SW = anticiclón SE Pacífico típico
        s_sw = sum(1 for d in dirs if 160 <= d <= 250)
        n = sum(1 for d in dirs if d < 40 or d > 320)
        if s_sw >= len(dirs) * 0.4:
            tags.append("anticiclon_se_pacifico")
        if n >= len(dirs) * 0.35:
            tags.append("flujo_norte_valle")
    if vel_med >= 5:
        tags.append("ventilacion_sinoptica_activa")
    elif vel_med < 1.5:
        tags.append("calma_atrapamiento")
    if not tags:
        tags.append("regimen_local_valle")
    return tags


def construir_paquete(
    estacion_id: str = ESTACION_ANCLA,
    forzar_recalculo: bool = False,
) -> dict[str, Any] | None:
    """Construye (o reusa snapshot) el paquete de ventilación de la corrida vigente."""
    meta = corrida_vigente()
    if not forzar_recalculo:
        snap = _cargar_ultimo_snapshot()
        if snap and snap.get("corrida_en") == meta["corrida_en"]:
            snap["meta_consulta"] = meta
            return snap

    slug = (estacion_id or ESTACION_ANCLA).strip().lower().replace("-", "_")
    if slug not in SLUG_A_NOMBRE or COORDS.get(slug) is None:
        return None

    horaria_raw = dispersion_service.dispersion_horaria(slug, horas=72) or []
    horaria = [_enriquecer_hora(f) for f in horaria_raw]

    # Diaria 14 d: forecast hasta 16 d
    diaria_raw = dispersion_service.dispersion_diaria(slug, dias=14) or []
    diaria: list[dict[str, Any]] = []
    # Agrupar horas por día para icono + peor código
    por_dia: dict[str, list[dict[str, Any]]] = {}
    for f in horaria:
        dia = str(f.get("fecha_hora") or "")[:10]
        if dia:
            por_dia.setdefault(dia, []).append(f)
    for d in diaria_raw:
        fecha = d.get("fecha") or str(d.get("fecha_hora") or "")[:10]
        grupo = por_dia.get(fecha) or []
        codigos = [g["ventilacion"] for g in grupo] if grupo else [
            codigo_desde_indice(d.get("indice_dispersion"))
        ]
        codigo = peor_codigo(codigos)
        icono = _icono_meteo(grupo[0] if grupo else d)
        if grupo:
            # Icono del peor escenario nuboso del día
            prioridad = ["lluvia", "niebla", "neblina", "cubierto", "parcialmente_nublado", "despejado"]
            icons = [_icono_meteo(g) for g in grupo]
            for p in prioridad:
                if p in icons:
                    icono = p
                    break
        diaria.append(
            {
                **d,
                "fecha": fecha,
                "ventilacion": codigo,
                "ventilacion_label": label_codigo(codigo),
                "icono": icono,
                "caracteristica": _texto_dia(codigo, icono, d),
            }
        )

    proy_30_60 = dispersion_service.dispersion_proyeccion(slug, dia_ini=30, dia_fin=60)
    proy_60_90 = dispersion_service.dispersion_proyeccion(slug, dia_ini=60, dia_fin=90)
    proyeccion = _armar_proyeccion(slug, proy_30_60, proy_60_90)

    tramos_3h = _tramos_3h(horaria[:24])
    sinoptica = _sinoptica_heuristica(horaria)

    payload = {
        "faena": "paipote",
        "estacion_id": slug,
        "estacion_nombre": SLUG_A_NOMBRE.get(slug, slug),
        "modelo": "METGO-Ventilacion-Paipote-v1",
        "codigos": {"N": "normal", "R": "regular", "M": "mala"},
        "corrida_utc": meta["corrida_utc"],
        "corrida_en": meta["corrida_en"],
        "proxima_corrida_utc": meta["proxima_corrida_utc"],
        "proxima_corrida_en": meta["proxima_corrida_en"],
        "generado_en": datetime.now(TZ_CHILE).isoformat(timespec="seconds"),
        "horaria": horaria,
        "diaria": diaria[:14],
        "proyeccion": proyeccion,
        "tramos_3h_24h": tramos_3h,
        "sinoptica_predominante": sinoptica,
        "resumen_72h": {
            "n": sum(1 for f in horaria if f.get("ventilacion") == "N"),
            "r": sum(1 for f in horaria if f.get("ventilacion") == "R"),
            "m": sum(1 for f in horaria if f.get("ventilacion") == "M"),
            "horas": len(horaria),
        },
    }
    _guardar_snapshot(payload)
    return payload


def _texto_dia(codigo: str, icono: str, d: dict[str, Any]) -> str:
    vent = label_codigo(codigo)
    icono_txt = icono.replace("_", " ")
    v = d.get("viento_velocidad")
    vtxt = f"{v} m/s" if v is not None else "viento n/d"
    return f"Cielo {icono_txt}; ventilación {vent}; {vtxt}."


def _tramos_3h(horaria_24: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tramos: list[dict[str, Any]] = []
    for i in range(0, min(24, len(horaria_24)), 3):
        bloque = horaria_24[i : i + 3]
        if not bloque:
            break
        codigos = [b["ventilacion"] for b in bloque]
        vels = [b.get("viento_velocidad") for b in bloque if b.get("viento_velocidad") is not None]
        dirs = [b.get("viento_direccion") for b in bloque if b.get("viento_direccion") is not None]
        nubs = [b.get("nubosidad_baja") for b in bloque if b.get("nubosidad_baja") is not None]
        codigo = peor_codigo(codigos)
        tramos.append(
            {
                "inicio": bloque[0].get("fecha_hora"),
                "fin": bloque[-1].get("fecha_hora"),
                "ventilacion": codigo,
                "ventilacion_label": label_codigo(codigo),
                "viento_velocidad": round(sum(vels) / len(vels), 2) if vels else None,
                "viento_direccion": round(sum(dirs) / len(dirs), 1) if dirs else None,
                "viento_categoria": bloque[0].get("viento_categoria"),
                "nubosidad_baja": round(sum(nubs) / len(nubs), 1) if nubs else None,
                "icono": _icono_meteo(bloque[0]),
                "inversion": any(b.get("inversion") for b in bloque),
            }
        )
    return tramos


def _armar_proyeccion(
    slug: str,
    p1: dict[str, Any] | None,
    p2: dict[str, Any] | None,
) -> dict[str, Any]:
    bloques = []
    for p, label in ((p1, "30-60"), (p2, "60-90")):
        if not p:
            continue
        codigo = codigo_desde_indice(p.get("indice_dispersion"))
        bloques.append(
            {
                "periodo": label,
                "dia_desde": p.get("dia_desde"),
                "dia_hasta": p.get("dia_hasta"),
                "ventilacion": codigo,
                "ventilacion_label": label_codigo(codigo),
                "confianza": p.get("confianza", "baja"),
                "viento_superficie_ms": p.get("viento_velocidad"),
                "nubosidad_media": p.get("nubosidad_media"),
                "inversion_probable": p.get("inversion_probable"),
                "indice_dispersion": p.get("indice_dispersion"),
            }
        )
    # Predominancia vientos (proxy climatológico)
    coords = COORDS.get(slug) or {}
    vientos_niveles = _vientos_niveles_climatologia(coords.get("lat"), coords.get("lon"))
    return {
        "horizonte": "30-90",
        "confianza": "baja",
        "metodo": "climatologia_archivo_stm_proxy",
        "stm_nota": (
            "Proyección subestacional-estacional proxy (climatología Open-Meteo Archive); "
            "no sustituye outlook oficial DMC/ENSO."
        ),
        "bloques": bloques,
        "vientos_predominantes": vientos_niveles,
    }


def _vientos_niveles_climatologia(lat: float | None, lon: float | None) -> dict[str, Any]:
    """Rosa simplificada superficie; media/altos desde forecast actual 850/500 si hay."""
    if lat is None or lon is None:
        return {}
    # Superficie: última proyección diaria viento
    out: dict[str, Any] = {
        "superficie_10m": {"fuente": "climatologia_proyeccion", "nota": "ver bloques.viento_superficie_ms"},
        "atmosfera_media": {"nivel_hpa": 700, "nota": "proxy desde forecast corto si disponible"},
        "niveles_altos": {"nivel_hpa": 500, "nota": "proxy geopotencial/viento modelo"},
    }
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "wind_speed_850hPa,wind_direction_850hPa,wind_speed_500hPa,wind_direction_500hPa",
            "wind_speed_unit": "ms",
            "timezone": "America/Santiago",
            "forecast_days": 3,
        }
        data = dispersion_service._get_json(dispersion_service.FORECAST_API_BASE, params)
        hourly = (data or {}).get("hourly") or {}
        if hourly.get("wind_direction_850hPa"):
            dirs = [d for d in hourly["wind_direction_850hPa"][:48] if d is not None]
            spds = [s for s in (hourly.get("wind_speed_850hPa") or [])[:48] if s is not None]
            if dirs:
                out["atmosfera_media"] = {
                    "nivel_hpa": 850,
                    "dir_predominante_deg": round(_dir_circular_media(dirs), 1),
                    "velocidad_media_ms": round(sum(spds) / len(spds), 2) if spds else None,
                }
        if hourly.get("wind_direction_500hPa"):
            dirs = [d for d in hourly["wind_direction_500hPa"][:48] if d is not None]
            spds = [s for s in (hourly.get("wind_speed_500hPa") or [])[:48] if s is not None]
            if dirs:
                out["niveles_altos"] = {
                    "nivel_hpa": 500,
                    "dir_predominante_deg": round(_dir_circular_media(dirs), 1),
                    "velocidad_media_ms": round(sum(spds) / len(spds), 2) if spds else None,
                }
    except Exception:
        pass
    return out


def _dir_circular_media(dirs_deg: list[float]) -> float:
    xs = sum(math.cos(math.radians(d)) for d in dirs_deg)
    ys = sum(math.sin(math.radians(d)) for d in dirs_deg)
    ang = math.degrees(math.atan2(ys, xs)) % 360.0
    return ang


def ventilacion_horizonte(
    horizonte: str = "horaria",
    estacion_id: str = ESTACION_ANCLA,
    forzar: bool = False,
) -> dict[str, Any] | None:
    pkg = construir_paquete(estacion_id, forzar_recalculo=forzar)
    if pkg is None:
        return None
    h = (horizonte or "horaria").strip().lower()
    base = {
        "faena": pkg["faena"],
        "estacion_id": pkg["estacion_id"],
        "corrida_utc": pkg["corrida_utc"],
        "corrida_en": pkg["corrida_en"],
        "proxima_corrida_utc": pkg["proxima_corrida_utc"],
        "proxima_corrida_en": pkg["proxima_corrida_en"],
        "generado_en": pkg["generado_en"],
        "codigos": pkg["codigos"],
        "horizonte": h,
    }
    if h == "diaria":
        return {**base, "filas": pkg["diaria"]}
    if h in ("proyeccion", "estacional", "30-90"):
        return {**base, "proyeccion": pkg["proyeccion"]}
    return {**base, "filas": pkg["horaria"], "resumen_72h": pkg["resumen_72h"]}


def sincronizar_corrida(estacion_id: str = ESTACION_ANCLA) -> dict[str, Any]:
    """Forzar recálculo (llamar desde cron 06/18 UTC)."""
    pkg = construir_paquete(estacion_id, forzar_recalculo=True)
    if not pkg:
        return {"ok": False, "error": "sin_datos"}
    return {
        "ok": True,
        "corrida_utc": pkg["corrida_utc"],
        "corrida_en": pkg["corrida_en"],
        "horas": len(pkg.get("horaria") or []),
        "dias": len(pkg.get("diaria") or []),
    }


# ------------------------------------------------------------------ histórico 7 años


def historico_diario(
    estacion_id: str = ESTACION_ANCLA,
    anios: int = 7,
) -> dict[str, Any] | None:
    """Serie diaria Archive Open-Meteo (~7 años) para estudios / olas de calor."""
    slug = (estacion_id or ESTACION_ANCLA).strip().lower().replace("-", "_")
    coords = COORDS.get(slug)
    if not coords:
        return None
    anios = max(1, min(int(anios), 10))
    hoy = datetime.now(TZ_CHILE).date()
    ini = hoy.replace(year=hoy.year - anios)
    # Archive limita rangos largos: trocear por año
    filas: list[dict[str, Any]] = []
    for y in range(ini.year, hoy.year + 1):
        start = max(ini, datetime(y, 1, 1).date())
        end = min(hoy, datetime(y, 12, 31).date())
        if start > end:
            continue
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": (
                "temperature_2m_max,temperature_2m_min,precipitation_sum,"
                "wind_speed_10m_max,wind_direction_10m_dominant,cloud_cover_mean"
            ),
            "wind_speed_unit": "ms",
            "timezone": "America/Santiago",
        }
        data = dispersion_service._get_json(dispersion_service.ARCHIVE_API_BASE, params)
        daily = (data or {}).get("daily") or {}
        times = daily.get("time") or []
        for i, t in enumerate(times):
            def _v(key):
                serie = daily.get(key) or []
                v = serie[i] if i < len(serie) else None
                return round(float(v), 2) if isinstance(v, (int, float)) else None

            filas.append(
                {
                    "fecha": t,
                    "tmax": _v("temperature_2m_max"),
                    "tmin": _v("temperature_2m_min"),
                    "precip": _v("precipitation_sum"),
                    "viento_max": _v("wind_speed_10m_max"),
                    "viento_dir": _v("wind_direction_10m_dominant"),
                    "nubosidad": _v("cloud_cover_mean"),
                }
            )
    return {
        "estacion_id": slug,
        "anios": anios,
        "desde": filas[0]["fecha"] if filas else None,
        "hasta": filas[-1]["fecha"] if filas else None,
        "n": len(filas),
        "filas": filas,
        "fuente": "openmeteo_archive",
    }
