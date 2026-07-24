#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Persistencia calidad del aire (E7 — Copiapó): tabla public.aire_registros.

Mismo patrón que meteo_store: upsert idempotente en Supabase, degradación
silenciosa a 0/[] si Supabase no está configurado. Fuente CAMS (Open-Meteo)
hoy; SINCA observado a futuro comparte la misma tabla vía `fuente`.
"""

from __future__ import annotations

from typing import Any

# Mapa campo API aire_service -> columna aire_registros
_MAPA_VARS: dict[str, str] = {
    "pm2_5": "pm25",
    "pm10": "pm10",
    "sulphur_dioxide": "so2",
    "nitrogen_dioxide": "no2",
    "ozone": "o3",
    "carbon_monoxide": "co",
    "dust": "dust",
}


def _client():
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        return get_supabase_client() or None
    except Exception as exc:  # pragma: no cover - import defensivo
        print(f"aire_store: Supabase no disponible: {exc}")
        return None


def _fila_a_registro(estacion_id: str, fila: dict[str, Any], fuente: str, tipo_dato: str) -> dict[str, Any] | None:
    """Normaliza una fila (actual/diaria) al esquema aire_registros."""
    fecha_hora = fila.get("fecha_hora") or fila.get("actualizado")
    if not fecha_hora and fila.get("fecha"):
        # Fila diaria (promedio 24 h): representa el día a mediodía local.
        fecha_hora = f"{str(fila['fecha'])[:10]}T12:00:00"
    if not fecha_hora:
        return None
    data: dict[str, Any] = {
        "estacion_id": estacion_id,
        "fecha_hora": fecha_hora,
        "icap": fila.get("icap"),
        "categoria": fila.get("nivel") or fila.get("categoria"),
        "fuente": fuente,
        "tipo_dato": fila.get("tipo_dato") or tipo_dato,
    }
    for api_var, col in _MAPA_VARS.items():
        data[col] = fila.get(api_var)
    return data


def guardar_aire(
    estacion_id: str,
    filas: list[dict[str, Any]],
    fuente: str = "openmeteo_cams",
    tipo_dato: str = "modelo",
) -> int:
    """Upsert idempotente de registros de aire. Devuelve nº de filas escritas."""
    client = _client()
    if not client or not filas:
        return 0
    registros = [
        r for r in (_fila_a_registro(estacion_id, f, fuente, tipo_dato) for f in filas) if r
    ]
    if not registros:
        return 0
    try:
        client.table("aire_registros").upsert(
            registros, on_conflict="estacion_id,fecha_hora,fuente"
        ).execute()
        return len(registros)
    except Exception as exc:
        print(f"aire_store.guardar_aire {estacion_id}: {exc}")
        return 0


def _registro_a_fila(row: dict[str, Any]) -> dict[str, Any]:
    """Convierte una fila de BD al formato que consume el frontend (pm2_5, etc.)."""
    fila: dict[str, Any] = {
        "fecha_hora": row.get("fecha_hora"),
        "fecha": str(row.get("fecha_hora") or "")[:10],
        "icap": row.get("icap"),
        "nivel": row.get("categoria"),
        "fuente": row.get("fuente"),
        "tipo_dato": row.get("tipo_dato"),
    }
    for api_var, col in _MAPA_VARS.items():
        fila[api_var] = row.get(col)
    return fila


def leer_aire(
    estacion_id: str,
    dias: int = 7,
    tipo_dato: str | None = None,
    fuente: str | None = None,
) -> list[dict[str, Any]]:
    """Lee registros recientes desde aire_registros (fallback ante CAMS caído)."""
    client = _client()
    if not client:
        return []
    try:
        q = (
            client.table("aire_registros")
            .select("*")
            .eq("estacion_id", estacion_id)
        )
        if tipo_dato:
            q = q.eq("tipo_dato", tipo_dato)
        if fuente:
            q = q.eq("fuente", fuente)
        res = q.order("fecha_hora", desc=True).limit(max(1, dias) * 24).execute()
        filas = [_registro_a_fila(r) for r in (res.data or [])]
        return list(reversed(filas))
    except Exception as exc:
        print(f"aire_store.leer_aire {estacion_id}: {exc}")
        return []


def leer_aire_por_fuente(
    estacion_id: str,
    fuente: str,
    dias: int = 14,
) -> list[dict[str, Any]]:
    """Lee serie de una fuente concreta (p. ej. CAMS vs SINCA para sesgo E12)."""
    return leer_aire(estacion_id, dias=dias, fuente=fuente)


# ------------------------------------------------------------- aire_dispersion

# Columnas de public.aire_dispersion que aceptamos en upsert.
_COLS_DISPERSION = (
    "temp_2m",
    "temp_925hpa",
    "temp_850hpa",
    "gradiente_termico",
    "inversion",
    "inversion_intensidad",
    "altura_capa_limite",
    "viento_velocidad",
    "viento_direccion",
    "viento_racha",
    "viento_categoria",
    "nubosidad_baja",
    "visibilidad",
    "niebla",
    "tipo_nubosidad",
    "humedad_relativa",
    "indice_dispersion",
    "potencial_dispersion",
    "alerta_dispersion",
)


def guardar_dispersion(
    estacion_id: str,
    filas: list[dict[str, Any]],
    horizonte: str = "horaria",
    fuente: str = "openmeteo_forecast",
    confianza: str = "alta",
) -> int:
    """Upsert idempotente de meteorología de dispersión (tabla aire_dispersion)."""
    client = _client()
    if not client or not filas:
        return 0
    registros: list[dict[str, Any]] = []
    for f in filas:
        fecha_hora = f.get("fecha_hora")
        if not fecha_hora and f.get("fecha"):
            fecha_hora = f"{str(f['fecha'])[:10]}T12:00:00"
        if not fecha_hora:
            continue
        reg: dict[str, Any] = {
            "estacion_id": estacion_id,
            "fecha_hora": fecha_hora,
            "horizonte": horizonte,
            "fuente": fuente,
            "confianza": f.get("confianza") or confianza,
            "tipo_dato": f.get("tipo_dato") or ("proyeccion" if horizonte == "proyeccion" else "pronostico"),
        }
        for col in _COLS_DISPERSION:
            if col in f:
                reg[col] = f.get(col)
        registros.append(reg)
    if not registros:
        return 0
    try:
        client.table("aire_dispersion").upsert(
            registros, on_conflict="estacion_id,fecha_hora,horizonte,fuente"
        ).execute()
        return len(registros)
    except Exception as exc:
        print(f"aire_store.guardar_dispersion {estacion_id}: {exc}")
        return 0


def leer_dispersion(estacion_id: str, horizonte: str = "horaria", limite: int = 72) -> list[dict[str, Any]]:
    """Lee la serie de dispersión persistida (fallback ante forecast caído)."""
    client = _client()
    if not client:
        return []
    try:
        res = (
            client.table("aire_dispersion")
            .select("*")
            .eq("estacion_id", estacion_id)
            .eq("horizonte", horizonte)
            .order("fecha_hora", desc=False)
            .limit(max(1, limite))
            .execute()
        )
        return list(res.data or [])
    except Exception as exc:
        print(f"aire_store.leer_dispersion {estacion_id}: {exc}")
        return []


def ultimo_aire(estacion_id: str) -> dict[str, Any] | None:
    """Último registro conocido de una estación (para fallback de aire_actual)."""
    client = _client()
    if not client:
        return None
    try:
        res = (
            client.table("aire_registros")
            .select("*")
            .eq("estacion_id", estacion_id)
            .order("fecha_hora", desc=True)
            .limit(1)
            .execute()
        )
        if res.data:
            return _registro_a_fila(res.data[0])
    except Exception as exc:
        print(f"aire_store.ultimo_aire {estacion_id}: {exc}")
    return None
