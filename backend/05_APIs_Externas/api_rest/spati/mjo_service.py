#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pronóstico subestacional MJO_Chile — fase/amplitud reales (NOAA/PSL ROMI).

Reemplaza la simulación anterior (fase por día del mes + amplitud aleatoria).
La clasificación de impacto por fase es la misma heurística ya documentada
por el equipo, pero ahora se aplica sobre datos reales; ver
``mjo_index_service.py`` para el detalle de fuente y limitaciones.
"""

from __future__ import annotations

from api_rest.spati.mjo_index_service import obtener_indice_mjo_real


def _clasificar_impacto(fase: int) -> dict[str, object]:
    if fase in (6, 7, 8):
        return {
            "impacto_viento": "Anomalía positiva (Vientos fuertes)",
            "impacto_oleaje": "Alta probabilidad de marejadas intensas",
            "probabilidad_bloqueo_anticiclonico": 0.75,
            "recomendacion_estrategica": "Planificar campañas críticas antes de la semana 3.",
        }
    if fase in (1, 2):
        return {
            "impacto_viento": "Anomalía negativa (Vientos calmos)",
            "impacto_oleaje": "Oleaje por debajo del promedio",
            "probabilidad_bloqueo_anticiclonico": 0.15,
            "recomendacion_estrategica": "Ventanas operacionales extendidas favorables.",
        }
    return {
        "impacto_viento": "Normal",
        "impacto_oleaje": "Normal",
        "probabilidad_bloqueo_anticiclonico": 0.4,
        "recomendacion_estrategica": "Condiciones típicas de la temporada.",
    }


def obtener_pronostico_extendido_mjo(sitio_id: str) -> dict:
    """Pronóstico subestacional MJO_Chile para un sitio. Datos reales; si la
    fuente no está disponible, retorna ``disponible: False`` explícito en vez
    de inventar una fase/amplitud."""
    indice = obtener_indice_mjo_real()
    if not indice.get("disponible"):
        return {
            "sitio_id": sitio_id,
            "disponible": False,
            "fuente": indice.get("fuente", "no_disponible"),
            "motivo": indice.get("motivo"),
            "mensaje": "Índice MJO real no disponible en este momento; no se muestra un valor simulado.",
        }

    fase = int(indice["fase"])
    amplitud = float(indice["amplitud"])
    impacto = _clasificar_impacto(fase)

    return {
        "sitio_id": sitio_id,
        "disponible": True,
        "fase_mjo": fase,
        "amplitud_mjo": round(amplitud, 2),
        "fecha_indice": indice.get("fecha"),
        "fuente": indice.get("fuente"),
        "fuente_url": indice.get("fuente_url"),
        "desde_cache": indice.get("desde_cache", False),
        "degradado": indice.get("degradado", False),
        **impacto,
        "nota_metodologica": (
            "Fase/amplitud reales (índice ROMI, NOAA/PSL). La clasificación de "
            "impacto es una heurística por fase, no un modelo dinámico validado."
        ),
    }
