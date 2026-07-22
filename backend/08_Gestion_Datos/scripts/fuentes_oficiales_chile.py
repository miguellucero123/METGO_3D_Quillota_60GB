"""Conectores oficiales Chile — Agromet (INIA) y DMC.

Etapa E del plan de calidad: OpenMeteo Archive es la fuente inmediata.
Este módulo define el contrato y stubs para estaciones físicas del valle.
No inventa series: sin API key / estación registrada → datos vacíos.
"""

from __future__ import annotations

from typing import Any

# Códigos tentativos — completar tras registro oficial (ver estaciones_oficiales_mapeo.md)
AGROMET_ESTACIONES: dict[str, dict[str, Any]] = {
    "quillota": {"codigo": None, "nombre": "Quillota", "estado": "pendiente_registro"},
    "los_nogales": {"codigo": None, "nombre": "Los Nogales", "estado": "pendiente_registro"},
    "hijuelas": {"codigo": None, "nombre": "Hijuelas", "estado": "pendiente_registro"},
    "limache": {"codigo": None, "nombre": "Limache", "estado": "pendiente_registro"},
    "olmue": {"codigo": None, "nombre": "Olmue", "estado": "pendiente_registro"},
}

DMC_ESTACIONES: dict[str, dict[str, Any]] = {
    "quillota": {"codigo": None, "nombre": "Quillota", "estado": "pendiente_registro"},
    "limache": {"codigo": None, "nombre": "Limache", "estado": "pendiente_registro"},
}


def estado_fuentes() -> dict[str, Any]:
    return {
        "agromet": {
            "disponible": False,
            "motivo": "Sin códigos de estación ni credenciales AGROMET_* configurados",
            "estaciones": AGROMET_ESTACIONES,
        },
        "dmc": {
            "disponible": False,
            "motivo": "Sin integración DMC activa; usar OpenMeteo Archive entre tanto",
            "estaciones": DMC_ESTACIONES,
        },
        "fuente_activa": "openmeteo_archive",
    }


def fetch_agromet_historico(estacion_id: str, dias: int = 30) -> list[dict[str, Any]]:
    """Stub: devolver [] hasta registrar estación y API key."""
    meta = AGROMET_ESTACIONES.get(estacion_id)
    if not meta or not meta.get("codigo"):
        return []
    # Futuro: GET API Agromet → normalizar a filas meteo_registros
    return []


def fetch_dmc_historico(estacion_id: str, dias: int = 30) -> list[dict[str, Any]]:
    """Stub: devolver [] hasta conectar DMC."""
    meta = DMC_ESTACIONES.get(estacion_id)
    if not meta or not meta.get("codigo"):
        return []
    return []
