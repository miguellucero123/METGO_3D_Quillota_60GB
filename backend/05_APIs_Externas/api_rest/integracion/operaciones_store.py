#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Persistencia de ventanas operacionales (E8 — Mantos Blancos).

Tabla public.operaciones_ventanas: una fila por hora y punto de faena, con el
semáforo por actividad (tronadura/transporte/izaje) y el nivel global.
"""

from __future__ import annotations

from typing import Any

_ACTIVIDADES = ("tronadura", "transporte", "izaje", "exposicion_uv")


def _client():
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        return get_supabase_client() or None
    except Exception as exc:  # pragma: no cover
        print(f"operaciones_store: Supabase no disponible: {exc}")
        return None


def _fila_a_registro(estacion_id: str, fila: dict[str, Any]) -> dict[str, Any] | None:
    fecha_hora = fila.get("fecha_hora")
    if not fecha_hora:
        return None
    act = fila.get("actividades") or {}
    return {
        "estacion_id": estacion_id,
        "fecha_hora": fecha_hora,
        "viento_sostenido": fila.get("viento_sostenido"),
        "viento_racha": fila.get("viento_racha"),
        "viento_direccion": fila.get("viento_direccion"),
        "visibilidad": fila.get("visibilidad"),
        "precipitacion": fila.get("precipitacion"),
        "uv_index": fila.get("uv_index"),
        "nivel_tronadura": (act.get("tronadura") or {}).get("nivel"),
        "nivel_transporte": (act.get("transporte") or {}).get("nivel"),
        "nivel_izaje": (act.get("izaje") or {}).get("nivel"),
        "nivel_exposicion_uv": (act.get("exposicion_uv") or {}).get("nivel"),
        "nivel_global": fila.get("nivel_global"),
        "uv_index": fila.get("uv_index"),
        "so2": fila.get("so2"),
    }


def guardar_ventanas(estacion_id: str, serie: list[dict[str, Any]], fuente: str = "openmeteo_forecast") -> int:
    client = _client()
    if not client or not serie:
        return 0
    registros = [r for r in (_fila_a_registro(estacion_id, f) for f in serie) if r]
    if not registros:
        return 0
    for r in registros:
        r["fuente"] = fuente
    try:
        client.table("operaciones_ventanas").upsert(
            registros, on_conflict="estacion_id,fecha_hora,fuente"
        ).execute()
        return len(registros)
    except Exception as exc:
        print(f"operaciones_store.guardar_ventanas {estacion_id}: {exc}")
        return 0


def _registro_a_fila(row: dict[str, Any]) -> dict[str, Any]:
    """Reconstruye el formato anidado que devuelve operaciones_service."""
    return {
        "fecha_hora": row.get("fecha_hora"),
        "viento_sostenido": row.get("viento_sostenido"),
        "viento_racha": row.get("viento_racha"),
        "viento_direccion": row.get("viento_direccion"),
        "visibilidad": row.get("visibilidad"),
        "precipitacion": row.get("precipitacion"),
        "uv_index": row.get("uv_index"),
        "nivel_global": row.get("nivel_global"),
        "uv_index": row.get("uv_index"),
        "so2": row.get("so2"),
        "actividades": {
            act: {"nivel": row.get(f"nivel_{act}"), "factores": []} for act in _ACTIVIDADES
        },
        "fuente": row.get("fuente"),
        "degradado": True,
    }


def leer_ventanas(estacion_id: str, limite: int = 48) -> list[dict[str, Any]]:
    client = _client()
    if not client:
        return []
    try:
        res = (
            client.table("operaciones_ventanas")
            .select("*")
            .eq("estacion_id", estacion_id)
            .order("fecha_hora", desc=False)
            .limit(max(1, limite))
            .execute()
        )
        return [_registro_a_fila(r) for r in (res.data or [])]
    except Exception as exc:
        print(f"operaciones_store.leer_ventanas {estacion_id}: {exc}")
        return []
