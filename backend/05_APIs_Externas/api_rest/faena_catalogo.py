#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catálogo de faenas atmosféricas (E7 Paipote · E8 Mantos Blancos).

Permite reutilizar ventilación N/R/M, satélite, olas de calor e histórico
sin hardcodear `paipote` en las rutas públicas.
"""

from __future__ import annotations

from typing import Any

# id faena → metadatos operativos
FAENAS: dict[str, dict[str, Any]] = {
    "paipote": {
        "id": "paipote",
        "sitio": "copiapo",
        "nombre": "Paipote",
        "estacion_ancla": "paipote",
        "region": "Atacama · valle Copiapó",
        "modelo_ventilacion": "METGO-Ventilacion-Paipote-v1",
        "satelite_sector": "ssa",
        "bbox": {"west": -70.45, "south": -27.6, "east": -70.2, "north": -27.25},
    },
    "mantos_blancos": {
        "id": "mantos_blancos",
        "sitio": "mantos_blancos",
        "nombre": "Mantos Blancos",
        "estacion_ancla": "mb_rajo",
        "region": "Antofagasta · faena minera",
        "modelo_ventilacion": "METGO-Ventilacion-Mantos-v1",
        "satelite_sector": "ssa",
        "bbox": {"west": -70.35, "south": -23.55, "east": -69.95, "north": -23.30},
    },
}

# Alias cortos / legacy
_ALIASES = {
    "paipote": "paipote",
    "copiapo": "paipote",
    "mantos": "mantos_blancos",
    "mantos_blancos": "mantos_blancos",
    "mb": "mantos_blancos",
}


def normalizar_faena_id(raw: str | None) -> str | None:
    key = (raw or "").strip().lower().replace("-", "_")
    if not key:
        return None
    return _ALIASES.get(key) or (key if key in FAENAS else None)


def get_faena(faena_id: str | None) -> dict[str, Any] | None:
    nid = normalizar_faena_id(faena_id)
    if not nid:
        return None
    return dict(FAENAS[nid])


def estacion_ancla(faena_id: str | None) -> str | None:
    f = get_faena(faena_id)
    return f["estacion_ancla"] if f else None


def listar_faenas() -> list[dict[str, Any]]:
    return [dict(v) for v in FAENAS.values()]
