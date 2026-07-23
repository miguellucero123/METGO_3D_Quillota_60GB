#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catálogo multi-sitio METGO (Quillota / Paine / futuros).

Fuente de verdad en código; espejo SQL opcional en supabase/migrations.
"""

from __future__ import annotations

from typing import Any

# Sitios conocidos (slug API)
SITIOS = ("quillota", "paine", "copiapo", "demo")

# Metadatos de producto / SPA (tabla sitios en Supabase es espejo)
SITIOS_META: dict[str, dict[str, Any]] = {
    "quillota": {
        "slug": "quillota",
        "nombre": "METGO Quillota",
        "region": "Valle de Aconcagua",
        "dominio": "agro",
        "estado": "activo",
        "primary": "#00ffaa",
        "center": {"lat": -32.8833, "lon": -71.25},
        "modules": ["meteo", "agricola", "iot", "ml"],
    },
    "paine": {
        "slug": "paine",
        "nombre": "METGO Paine",
        "region": "Torres del Paine",
        "dominio": "criosfera",
        "estado": "activo",
        "primary": "#22d3ee",
        "center": {"lat": -50.96, "lon": -73.05},
        "modules": ["meteo", "lugares"],
    },
    "copiapo": {
        "slug": "copiapo",
        "nombre": "METGO Copiapó",
        "region": "Copiapó · Región de Atacama",
        "dominio": "aire",
        "estado": "activo",
        "primary": "#fbbf24",
        "center": {"lat": -27.3668, "lon": -70.3323},
        "modules": ["meteo", "aire", "alertas_salud"],
    },
    "demo": {
        "slug": "demo",
        "nombre": "METGO Demo",
        "region": "Valle Demo (ficticio)",
        "dominio": "template",
        "estado": "plantilla",
        "primary": "#a78bfa",
        "center": {"lat": -33.32, "lon": -71.42},
        "modules": ["meteo", "lugares"],
    },
}

# slug -> nombre OpenMeteo (clave en OpenMeteoData.estaciones)
SLUG_A_NOMBRE: dict[str, str] = {
    # Quillota / Valle de Aconcagua
    "quillota": "Quillota",
    "los_nogales": "Los Nogales",
    "hijuelas": "Hijuelas",
    "limache": "Limache",
    "olmue": "Olmue",
    "santiago": "Santiago",
    "valparaiso": "Valparaiso",
    "vina_del_mar": "Viña del Mar",
    "casablanca": "Casablanca",
    # Torres del Paine (METGO Glaciares)
    "base_torres": "Base Torres",
    "glaciar_grey": "Glaciar Grey",
    "valle_frances": "Valle del Frances",
    "paine_grande": "Paine Grande",
    "campamento_italiano": "Campamento Italiano",
    "los_cuernos": "Los Cuernos",
    # Copiapó (calidad del aire, E7)
    "copiapo_centro": "Copiapo Centro",
    "paipote": "Paipote",
    "tierra_amarilla": "Tierra Amarilla",
    # Sitio plantilla E6 (ficticio; coords cerca Casablanca)
    "demo_norte": "Demo Norte",
    "demo_sur": "Demo Sur",
}

NOMBRE_A_SLUG = {v: k for k, v in SLUG_A_NOMBRE.items()}

# Coordenadas canónicas (también se registran en OpenMeteoData)
COORDS: dict[str, dict[str, float]] = {
    "quillota": {"lat": -32.8833, "lon": -71.25},
    "los_nogales": {"lat": -32.9333, "lon": -71.2167},
    "hijuelas": {"lat": -32.8000, "lon": -71.1333},
    "limache": {"lat": -33.0167, "lon": -71.2667},
    "olmue": {"lat": -33.0000, "lon": -71.2167},
    "santiago": {"lat": -33.4489, "lon": -70.6693},
    "valparaiso": {"lat": -33.0458, "lon": -71.6197},
    "vina_del_mar": {"lat": -33.0153, "lon": -71.5508},
    "casablanca": {"lat": -33.3167, "lon": -71.4167},
    "base_torres": {"lat": -50.9417, "lon": -72.9667},
    "glaciar_grey": {"lat": -51.0, "lon": -73.23},
    "valle_frances": {"lat": -50.9667, "lon": -73.0833},
    "paine_grande": {"lat": -50.9500, "lon": -73.1167},
    "campamento_italiano": {"lat": -50.9583, "lon": -73.0667},
    "los_cuernos": {"lat": -50.9750, "lon": -73.0500},
    "copiapo_centro": {"lat": -27.3668, "lon": -70.3323},
    "paipote": {"lat": -27.4064, "lon": -70.2853},
    "tierra_amarilla": {"lat": -27.4667, "lon": -70.2667},
    "demo_norte": {"lat": -33.30, "lon": -71.40},
    "demo_sur": {"lat": -33.34, "lon": -71.44},
}

# Dashboard Quillota (default) — no incluir Paine en ETL nocturno por defecto
ESTACIONES_PRINCIPALES: list[str] = [
    "quillota",
    "los_nogales",
    "hijuelas",
    "limache",
    "olmue",
]

ESTACIONES_POR_SITIO: dict[str, list[str]] = {
    "quillota": list(ESTACIONES_PRINCIPALES),
    "paine": [
        "base_torres",
        "glaciar_grey",
        "valle_frances",
        "paine_grande",
        "campamento_italiano",
        "los_cuernos",
    ],
    "copiapo": ["copiapo_centro", "paipote", "tierra_amarilla"],
    "demo": ["demo_norte", "demo_sur"],
}

# Metadatos opcionales (UI Paine)
META_EXTRA: dict[str, dict[str, Any]] = {
    "base_torres": {"circuito": "W", "altitud": 900},
    "glaciar_grey": {"circuito": "W", "altitud": 50},
    "valle_frances": {"circuito": "W", "altitud": 300},
    "paine_grande": {"circuito": "O", "altitud": 50},
    "campamento_italiano": {"circuito": "W", "altitud": 120},
    "los_cuernos": {"circuito": "O", "altitud": 200},
}


def normalizar_sitio(sitio: str | None) -> str:
    s = (sitio or "quillota").strip().lower()
    if s not in ESTACIONES_POR_SITIO:
        return "quillota"
    return s


def slugs_de_sitio(sitio: str | None) -> list[str]:
    return list(ESTACIONES_POR_SITIO[normalizar_sitio(sitio)])


def listar_sitios(incluir_plantilla: bool = True) -> list[dict[str, Any]]:
    """Catálogo de sitios METGO (fuente en código; espejo SQL `sitios`)."""
    out: list[dict[str, Any]] = []
    for slug in SITIOS:
        meta = dict(SITIOS_META.get(slug, {"slug": slug, "nombre": slug.title()}))
        if not incluir_plantilla and meta.get("estado") == "plantilla":
            continue
        meta["estaciones"] = list(ESTACIONES_POR_SITIO.get(slug, []))
        out.append(meta)
    return out
