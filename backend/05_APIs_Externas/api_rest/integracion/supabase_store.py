#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cliente Supabase compartido (API REST)."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

_supabase_client = None
_supabase_init_error: str | None = None


def _resolve_supabase_creds() -> tuple[str | None, str | None]:
    url = (
        os.getenv("SUPABASE_URL")
        or os.getenv("METGO_SUPABASE_URL")
        or os.getenv("VITE_SUPABASE_URL")
        or ""
    ).strip().strip('"').strip("'") or None
    key = (
        os.getenv("SUPABASE_KEY")
        or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("METGO_SUPABASE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or ""
    ).strip().strip('"').strip("'") or None
    return url, key


def supabase_configurado() -> bool:
    url, key = _resolve_supabase_creds()
    return bool(url and key)


def supabase_status() -> dict[str, Any]:
    """Diagnóstico seguro (sin secretos) para /api/health."""
    url, key = _resolve_supabase_creds()
    host = ""
    if url:
        try:
            host = urlparse(url).netloc
        except Exception:
            host = "invalid_url"
    client = get_supabase_client()
    return {
        "configurado": bool(url and key),
        "client_ok": client is not None,
        "url_host": host,
        "key_len": len(key) if key else 0,
        "error": _supabase_init_error,
    }


def get_supabase_client():
    """Singleton. None si no hay credenciales o falló el init (ver supabase_status)."""
    global _supabase_client, _supabase_init_error
    if _supabase_client is not None:
        return _supabase_client

    url, key = _resolve_supabase_creds()
    if not url or not key:
        _supabase_init_error = "Faltan SUPABASE_URL y/o SUPABASE_KEY (o SERVICE_ROLE/ANON)"
        return None

    try:
        from supabase import create_client

        _supabase_client = create_client(url, key)
        _supabase_init_error = None
        return _supabase_client
    except ImportError as exc:
        _supabase_init_error = f"ImportError supabase: {exc}"
        return None
    except Exception as exc:
        _supabase_init_error = f"{type(exc).__name__}: {exc}"
        return None


# Compat: módulos antiguos leen estas globals
SUPABASE_URL, SUPABASE_KEY = _resolve_supabase_creds()


def guardar_registros(estacion_id: str, filas: list[dict[str, Any]], fuente: str = "openmeteo") -> int:
    client = get_supabase_client()
    if not client:
        return 0
    if not filas:
        return 0

    n = 0
    for row in filas:
        fecha = str(row.get("fecha") or row.get("actualizado") or "")[:10]
        if not fecha:
            continue
        try:
            data = {
                "estacion_id": estacion_id,
                "fecha": fecha,
                "temperatura_max": row.get("temperatura_max"),
                "temperatura_min": row.get("temperatura_min"),
                "humedad": row.get("humedad"),
                "precipitacion": row.get("precipitacion"),
                "viento": row.get("viento"),
                "presion": row.get("presion"),
                "fuente": fuente,
            }
            client.table("meteo_registros").upsert(data, on_conflict="estacion_id,fecha").execute()
            n += 1
        except Exception as e:
            print(f"Error al guardar registro en Supabase: {e}")
            continue
    return n


def leer_registros(estacion_id: str, dias: int = 30) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if not client:
        return []

    try:
        res = (
            client.table("meteo_registros")
            .select("*")
            .eq("estacion_id", estacion_id)
            .order("fecha", desc=True)
            .limit(dias)
            .execute()
        )

        out = []
        for row in res.data:
            out.append(
                {
                    "estacion_id": estacion_id,
                    "fecha": row.get("fecha"),
                    "temperatura_max": row.get("temperatura_max"),
                    "temperatura_min": row.get("temperatura_min"),
                    "humedad": row.get("humedad"),
                    "precipitacion": row.get("precipitacion"),
                    "viento": row.get("viento"),
                    "presion": row.get("presion"),
                    "fuente": row.get("fuente") or "supabase_db",
                }
            )
        return list(reversed(out))
    except Exception as e:
        print(f"Error al leer registros en Supabase: {e}")
        return []


def estadisticas_store() -> dict[str, Any]:
    client = get_supabase_client()
    url, _ = _resolve_supabase_creds()
    if not client:
        return {
            "registros": 0,
            "estaciones": 0,
            "db": "supabase (inactivo)",
            "error": _supabase_init_error,
        }
    try:
        res = client.table("meteo_registros").select("estacion_id", count="exact").limit(1).execute()
        total = res.count if res.count is not None else 0
        return {"registros": total, "estaciones": 0, "db": url}
    except Exception as e:
        return {"registros": 0, "estaciones": 0, "db": url, "error": str(e)}
