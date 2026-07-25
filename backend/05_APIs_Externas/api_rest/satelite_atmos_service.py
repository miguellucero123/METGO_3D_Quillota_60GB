#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Satélite atmosférico VIS / IR / WV (GOES sector Sudamérica) + diagnóstico valle.

Fuente: NOAA STAR CDN (GOES-East sector `samer`). No es producto DMC oficial.
Diagnóstico de incursión nubosa / niebla fusiona frames disponibles + meteo Open-Meteo.
"""

from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests

from api_rest.dispersion_service import clasificar_nubosidad, dispersion_horaria
from api_rest.estaciones_catalogo import COORDS, SLUG_A_NOMBRE

TZ_CHILE = ZoneInfo("America/Santiago")

# GOES-19 (East) — sector South America
_CDN = "https://cdn.star.nesdis.noaa.gov/GOES19/ABI/SECTOR/samer"
_BANDAS = {
    "vis": {
        "code": "02",
        "nombre": "Visible",
        "descripcion": "Reflectancia diurna — nubosidad baja/media",
    },
    "ir": {
        "code": "13",
        "nombre": "Infrarrojo",
        "descripcion": "Temperatura de topes nubosos (24 h)",
    },
    "wv": {
        "code": "09",
        "nombre": "Vapor de agua",
        "descripcion": "Humedad troposfera media",
    },
}

_TIMEOUT = 20
_CACHE: dict[str, tuple[float, Any]] = {}
_CACHE_TTL = 900.0  # 15 min


def _listar_frames(banda_code: str, limite: int = 12) -> list[dict[str, Any]]:
    """Parsea el índice HTML del CDN NOAA y devuelve URLs de imágenes recientes."""
    cache_key = f"list|{banda_code}|{limite}"
    now = time.time()
    if cache_key in _CACHE and now - _CACHE[cache_key][0] < _CACHE_TTL:
        return _CACHE[cache_key][1]

    url = f"{_CDN}/{banda_code}/"
    try:
        r = requests.get(url, timeout=_TIMEOUT)
        if r.status_code != 200:
            return []
        # Archivos tipo 2026206120019_GOES19-ABI-samer-13-1000x1000.jpg
        names = sorted(set(re.findall(r'href="(\d{13}_GOES19[^"]+\.jpg)"', r.text)))
        # Preferir 1000x1000
        pref = [n for n in names if "1000x1000" in n] or names
        pref = pref[-limite:]
        frames = []
        for name in pref:
            # timestamp YYYY DDD HH MM SS (doy)
            ts = name.split("_", 1)[0]
            frames.append(
                {
                    "id": ts,
                    "url": f"{url}{name}",
                    "thumb_url": f"{url}{name}",
                }
            )
        _CACHE[cache_key] = (now, frames)
        return frames
    except Exception:
        return []


def _diagnostico_valle(estacion_id: str = "paipote") -> dict[str, Any]:
    serie = dispersion_horaria(estacion_id, horas=6) or []
    if not serie:
        return {
            "etiqueta": "sin_dato",
            "detalle": "Sin meteo horaria para fusionar con satélite",
        }
    f0 = serie[0]
    nub = clasificar_nubosidad(
        f0.get("nubosidad_baja"), f0.get("visibilidad"), f0.get("humedad_relativa")
    )
    precip = f0.get("precipitacion")
    tipo = nub.get("tipo_nubosidad") or "despejado"
    if precip is not None and precip > 0.5:
        etiqueta = "lluvia_debil"
    elif precip is not None and precip > 0.1:
        etiqueta = "llovizna"
    elif tipo == "niebla":
        etiqueta = "niebla"
    elif tipo == "neblina":
        etiqueta = "neblina"
    elif (f0.get("nubosidad_baja") or 0) >= 70:
        etiqueta = "nubes_bajas_valle"
    elif (f0.get("nubosidad_baja") or 0) >= 40:
        etiqueta = "incursion_parcial"
    else:
        etiqueta = "despejado"
    return {
        "etiqueta": etiqueta,
        "tipo_nubosidad": tipo,
        "niebla": nub.get("niebla"),
        "nubosidad_baja": f0.get("nubosidad_baja"),
        "visibilidad_km": f0.get("visibilidad"),
        "humedad_relativa": f0.get("humedad_relativa"),
        "inversion": f0.get("inversion"),
        "fecha_hora": f0.get("fecha_hora"),
        "detalle": (
            f"Fusión satélite+modelo: {etiqueta.replace('_', ' ')}. "
            "Validar visualmente bandas VIS (día) / IR / WV."
        ),
    }


def satelite_atmos(
    estacion_id: str = "paipote",
    bandas: list[str] | None = None,
    horas_frames: int = 12,
) -> dict[str, Any] | None:
    slug = (estacion_id or "paipote").strip().lower().replace("-", "_")
    if slug not in SLUG_A_NOMBRE:
        return None
    coords = COORDS.get(slug) or {}
    wanted = bandas or ["vis", "ir", "wv"]
    out_bandas = []
    for b in wanted:
        meta = _BANDAS.get(b)
        if not meta:
            continue
        frames = _listar_frames(meta["code"], limite=max(4, min(horas_frames, 24)))
        out_bandas.append(
            {
                "id": b,
                "nombre": meta["nombre"],
                "descripcion": meta["descripcion"],
                "goes_band": meta["code"],
                "frames": frames,
                "frame_activo": frames[-1] if frames else None,
                "disponible": bool(frames),
            }
        )

    return {
        "estacion_id": slug,
        "estacion_nombre": SLUG_A_NOMBRE.get(slug, slug),
        "lat": coords.get("lat"),
        "lon": coords.get("lon"),
        "sector": "samer",
        "satelite": "GOES-19",
        "fuente": "NOAA STAR CDN",
        "nota": (
            "Imágenes geostacionarias públicas (sector Sudamérica). "
            "Uso operativo METGO; no sustituye producto DMC."
        ),
        "bandas": out_bandas,
        "diagnostico": _diagnostico_valle(slug),
        "generado": datetime.now(TZ_CHILE).isoformat(timespec="seconds"),
    }
