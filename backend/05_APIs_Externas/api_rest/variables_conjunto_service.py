#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Variables en conjunto (catálogo extensible) — estilo Quillota ComboMeteo ampliado.

Permite activar series por clave sin rediseñar el panel. Nuevas capas =
registrar en CATALOGO + rellenar en armar_conjunto().
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from api_rest import dispersion_service
from api_rest.estaciones_catalogo import COORDS, SLUG_A_NOMBRE
from api_rest.ventilacion_service import codigo_desde_indice

TZ_CHILE = ZoneInfo("America/Santiago")

# Catálogo versionado: el front descubre slots disponibles.
CATALOGO: list[dict[str, Any]] = [
    {
        "id": "temp_2m",
        "nombre": "Temperatura 2 m",
        "unidad": "°C",
        "eje": "temp",
        "tipo": "line",
        "color": "#16a34a",
        "default": True,
    },
    {
        "id": "viento",
        "nombre": "Viento 10 m",
        "unidad": "m/s",
        "eje": "viento",
        "tipo": "line",
        "color": "#2563eb",
        "default": True,
    },
    {
        "id": "nubosidad_baja",
        "nombre": "Nubosidad baja",
        "unidad": "%",
        "eje": "nubes",
        "tipo": "bar",
        "color": "#94a3b8",
        "default": True,
    },
    {
        "id": "indice_dispersion",
        "nombre": "Índice dispersión",
        "unidad": "0-100",
        "eje": "idx",
        "tipo": "line",
        "color": "#f59e0b",
        "default": True,
    },
    {
        "id": "ventilacion_code",
        "nombre": "Ventilación (N=2 R=1 M=0)",
        "unidad": "código",
        "eje": "vent",
        "tipo": "step",
        "color": "#dc2626",
        "default": False,
    },
    {
        "id": "humedad_relativa",
        "nombre": "Humedad relativa",
        "unidad": "%",
        "eje": "hr",
        "tipo": "line",
        "color": "#06b6d4",
        "default": False,
    },
    {
        "id": "altura_capa_limite",
        "nombre": "Capa límite",
        "unidad": "m",
        "eje": "pbl",
        "tipo": "line",
        "color": "#8b5cf6",
        "default": False,
    },
    {
        "id": "pm25",
        "nombre": "PM2.5",
        "unidad": "µg/m³",
        "eje": "pm",
        "tipo": "line",
        "color": "#ea580c",
        "default": False,
    },
]

_VENT_NUM = {"N": 2, "R": 1, "M": 0}


def catalogo_publico() -> dict[str, Any]:
    return {
        "version": 1,
        "sitio_tipico": "copiapo",
        "slots": CATALOGO,
        "nota": "Activar series por id en GET .../conjunto?series=temp_2m,viento,...",
    }


def armar_conjunto(
    estacion_id: str = "paipote",
    horas: int = 72,
    series: list[str] | None = None,
) -> dict[str, Any] | None:
    slug = (estacion_id or "paipote").strip().lower().replace("-", "_")
    if slug not in SLUG_A_NOMBRE or COORDS.get(slug) is None:
        return None

    horas = max(6, min(int(horas), 168))
    ids_default = [s["id"] for s in CATALOGO if s.get("default")]
    pedidas = series or ids_default
    pedidas = [p for p in pedidas if any(c["id"] == p for c in CATALOGO)]
    if not pedidas:
        pedidas = ids_default

    filas = dispersion_service.dispersion_horaria(slug, horas=horas) or []
    labels = [f.get("fecha_hora") for f in filas]

    series_out: dict[str, list[Any]] = {}
    for sid in pedidas:
        if sid == "temp_2m":
            series_out[sid] = [f.get("temp_2m") for f in filas]
        elif sid == "viento":
            series_out[sid] = [f.get("viento_velocidad") for f in filas]
        elif sid == "nubosidad_baja":
            series_out[sid] = [f.get("nubosidad_baja") for f in filas]
        elif sid == "indice_dispersion":
            series_out[sid] = [f.get("indice_dispersion") for f in filas]
        elif sid == "ventilacion_code":
            series_out[sid] = [
                _VENT_NUM.get(codigo_desde_indice(f.get("indice_dispersion")), 1) for f in filas
            ]
        elif sid == "humedad_relativa":
            series_out[sid] = [f.get("humedad_relativa") for f in filas]
        elif sid == "altura_capa_limite":
            series_out[sid] = [f.get("altura_capa_limite") for f in filas]
        elif sid == "pm25":
            series_out[sid] = _serie_pm25(slug, labels)
        else:
            series_out[sid] = [None] * len(filas)

    meta_slots = [dict(c) for c in CATALOGO if c["id"] in pedidas]

    return {
        "estacion_id": slug,
        "estacion_nombre": SLUG_A_NOMBRE.get(slug, slug),
        "horas": horas,
        "labels": labels,
        "series": series_out,
        "slots_activos": meta_slots,
        "catalogo_version": 1,
        "generado": datetime.now(TZ_CHILE).isoformat(timespec="seconds"),
    }


def _serie_pm25(slug: str, labels: list) -> list[Any]:
    """PM2.5: un valor actual repetido (histórico CAMS horario no siempre en store)."""
    try:
        from api_rest import aire_service

        actual = aire_service.aire_actual(slug) or {}
        pm = actual.get("pm2_5") or actual.get("pm25")
        if pm is None:
            return [None] * len(labels)
        return [pm] * len(labels)
    except Exception:
        return [None] * len(labels)
