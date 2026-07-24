#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SINCA (MMA Chile) — stub E7/E12 para validar CAMS con observación oficial.

SINCA no publica API REST estable; el acceso habitual es CSV/HTML del portal
https://sinca.mma.gob.cl. Este módulo deja:

- Catálogo de estaciones del airshed Copiapó (códigos a completar con IDs reales).
- Interfaz `sincronizar_sinca()` lista para enchufar un scraper/CSV diario.
- Mientras tanto, marca el estado como `pendiente_fuente` sin fallar el cron.

Cuando exista un feed (CSV diario o scraping autorizado), implementar
`_fetch_estacion()` y persistir vía `aire_store.guardar_aire(..., fuente='sinca',
tipo_dato='observado')`.
"""

from __future__ import annotations

from typing import Any

# Códigos SINCA a confirmar en el portal MMA (placeholders documentados).
ESTACIONES_SINCA_COPIAPO: dict[str, dict[str, Any]] = {
    "copiapo_centro": {
        "sinca_id": None,  # completar con código oficial SINCA
        "nombre_sinca": "Copiapó",
        "contaminantes": ["PM25", "PM10", "SO2", "NO2", "O3"],
    },
    "paipote": {
        "sinca_id": None,
        "nombre_sinca": "Paipote",
        "contaminantes": ["PM10", "SO2"],
    },
    "tierra_amarilla": {
        "sinca_id": None,
        "nombre_sinca": "Tierra Amarilla",
        "contaminantes": ["PM10"],
    },
}


def estado_sinca() -> dict[str, Any]:
    """Estado de la integración SINCA (para /api/datos/etl/status y docs)."""
    configuradas = sum(1 for e in ESTACIONES_SINCA_COPIAPO.values() if e.get("sinca_id"))
    return {
        "fuente": "sinca_mma",
        "portal": "https://sinca.mma.gob.cl",
        "estado": "pendiente_fuente" if configuradas == 0 else "parcial",
        "estaciones_catalogo": len(ESTACIONES_SINCA_COPIAPO),
        "estaciones_con_codigo": configuradas,
        "nota": (
            "SINCA sin API oficial. Completar sinca_id en ESTACIONES_SINCA_COPIAPO "
            "y conectar scraper/CSV diario (E12)."
        ),
    }


def sincronizar_sinca(estaciones: list[str] | None = None) -> dict[str, Any]:
    """ETL SINCA → aire_registros (observado). Stub: no escribe hasta tener códigos."""
    estado = estado_sinca()
    if estado["estaciones_con_codigo"] == 0:
        return {
            "sinca_sync": {},
            "omitido": True,
            "motivo": "sin_codigos_sinca",
            "estado": estado,
        }
    # Futuro: fetch + aire_store.guardar_aire(slug, filas, fuente='sinca', tipo_dato='observado')
    return {
        "sinca_sync": {},
        "omitido": True,
        "motivo": "fetch_no_implementado",
        "estado": estado,
    }
