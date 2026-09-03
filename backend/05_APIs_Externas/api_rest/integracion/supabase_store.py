#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cliente Supabase compartido (API REST).

Preferencia:
1. SDK ``supabase.create_client`` si está instalado
2. Fallback HTTP PostgREST con ``requests`` (Render a veces rompe el SDK)
"""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()

_supabase_client = None
_supabase_init_error: str | None = None
_rest_ok: bool | None = None


def _env_is_production() -> bool:
    env = (os.getenv("METGO_ENV") or "").strip().lower()
    if env in ("production", "prod"):
        return True
    return (os.getenv("RENDER") or "").strip().lower() in ("true", "1", "yes")


def _looks_like_anon_key(key: str) -> bool:
    k = (key or "").strip()
    if not k:
        return False
    low = k.lower()
    if low.startswith("sb_publishable_"):
        return True
    if k.startswith("eyJ"):
        try:
            import base64
            import json

            parts = k.split(".")
            if len(parts) < 2:
                return False
            pad = "=" * (-len(parts[1]) % 4)
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + pad))
            return str(payload.get("role") or "").lower() == "anon"
        except Exception:
            return False
    return False


def _resolve_supabase_creds() -> tuple[str | None, str | None]:
    url = (
        os.getenv("SUPABASE_URL")
        or os.getenv("METGO_SUPABASE_URL")
        or os.getenv("VITE_SUPABASE_URL")
        or ""
    ).strip().strip('"').strip("'") or None
    if _env_is_production():
        key = (
            os.getenv("SUPABASE_KEY")
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("METGO_SUPABASE_KEY")
            or ""
        ).strip().strip('"').strip("'") or None
    else:
        key = (
            os.getenv("SUPABASE_KEY")
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("METGO_SUPABASE_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
            or ""
        ).strip().strip('"').strip("'") or None
    if key and _env_is_production() and _looks_like_anon_key(key):
        raise RuntimeError(
            "METGO: SUPABASE_KEY parece anon/publishable en production. "
            "Use service_role / sb_secret_ (nunca anon en Render)."
        )
    return url, key


def _creds_or_none() -> tuple[str | None, str | None]:
    global _supabase_init_error
    try:
        return _resolve_supabase_creds()
    except RuntimeError as exc:
        _supabase_init_error = str(exc)
        return None, None


def supabase_configurado() -> bool:
    url, key = _creds_or_none()
    return bool(url and key)


def _rest_headers(key: str) -> dict[str, str]:
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def rest_select(
    table: str,
    *,
    params: dict[str, str] | None = None,
    limit: int = 100,
    timeout: int = 20,
) -> list[dict[str, Any]]:
    """GET /rest/v1/{table} sin SDK."""
    global _rest_ok, _supabase_init_error
    url, key = _creds_or_none()
    if not url or not key:
        return []
    endpoint = f"{url.rstrip('/')}/rest/v1/{table}"
    q = dict(params or {})
    q.setdefault("limit", str(limit))
    try:
        res = requests.get(endpoint, headers=_rest_headers(key), params=q, timeout=timeout)
        if res.status_code >= 400:
            _rest_ok = False
            _supabase_init_error = f"PostgREST {res.status_code}: {res.text[:180]}"
            return []
        _rest_ok = True
        data = res.json()
        return data if isinstance(data, list) else []
    except Exception as exc:
        _rest_ok = False
        _supabase_init_error = f"REST {type(exc).__name__}: {exc}"
        return []


def rest_insert(table: str, row: dict[str, Any]) -> list[dict[str, Any]]:
    """POST /rest/v1/{table} con Prefer return=representation."""
    url, key = _creds_or_none()
    if not url or not key or not row:
        return []
    endpoint = f"{url.rstrip('/')}/rest/v1/{table}"
    try:
        res = requests.post(
            endpoint,
            headers=_rest_headers(key),
            json=row,
            timeout=30,
        )
        if res.status_code >= 400:
            print(f"rest_insert {table}: {res.status_code} {res.text[:200]}")
            return []
        data = res.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []
    except Exception as exc:
        print(f"rest_insert {table}: {exc}")
        return []


def rest_patch(table: str, match: dict[str, str], patch: dict[str, Any]) -> list[dict[str, Any]]:
    """PATCH /rest/v1/{table}?col=eq.val"""
    url, key = _creds_or_none()
    if not url or not key or not patch:
        return []
    endpoint = f"{url.rstrip('/')}/rest/v1/{table}"
    params = dict(match or {})
    try:
        res = requests.patch(
            endpoint,
            headers=_rest_headers(key),
            params=params,
            json=patch,
            timeout=30,
        )
        if res.status_code >= 400:
            print(f"rest_patch {table}: {res.status_code} {res.text[:200]}")
            return []
        data = res.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []
    except Exception as exc:
        print(f"rest_patch {table}: {exc}")
        return []


def rest_delete(table: str, match: dict[str, str]) -> int:
    """DELETE /rest/v1/{table}?col=eq.val — retorna filas afectadas (si Prefer return=representation)."""
    url, key = _creds_or_none()
    if not url or not key or not match:
        return 0
    endpoint = f"{url.rstrip('/')}/rest/v1/{table}"
    headers = _rest_headers(key)
    headers["Prefer"] = "return=representation"
    try:
        res = requests.delete(
            endpoint,
            headers=headers,
            params=dict(match),
            timeout=30,
        )
        if res.status_code >= 400:
            print(f"rest_delete {table}: {res.status_code} {res.text[:200]}")
            return 0
        if not res.content:
            return 1
        data = res.json()
        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict):
            return 1
        return 1
    except Exception as exc:
        print(f"rest_delete {table}: {exc}")
        return 0


def rest_upsert(table: str, rows: list[dict[str, Any]], on_conflict: str) -> int:
    url, key = _creds_or_none()
    if not url or not key or not rows:
        return 0
    endpoint = f"{url.rstrip('/')}/rest/v1/{table}"
    headers = _rest_headers(key)
    headers["Prefer"] = f"resolution=merge-duplicates,return=minimal"
    params = {"on_conflict": on_conflict}
    try:
        res = requests.post(endpoint, headers=headers, params=params, json=rows, timeout=30)
        if res.status_code >= 400:
            print(f"rest_upsert {table}: {res.status_code} {res.text[:200]}")
            return 0
        return len(rows)
    except Exception as exc:
        print(f"rest_upsert {table}: {exc}")
        return 0


def supabase_status() -> dict[str, Any]:
    url, key = _creds_or_none()
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
        "rest_ok": _rest_ok,
        "url_host": host,
        "key_len": len(key) if key else 0,
        "error": _supabase_init_error,
        "mode": "sdk" if client is not None else ("rest" if _rest_ok else "none"),
    }


def get_supabase_client():
    """Singleton SDK. None si el paquete falla (usar rest_select)."""
    global _supabase_client, _supabase_init_error
    if _supabase_client is not None:
        return _supabase_client

    url, key = _creds_or_none()
    if not url or not key:
        _supabase_init_error = _supabase_init_error or "Faltan SUPABASE_URL y/o SUPABASE_KEY"
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


try:
    SUPABASE_URL, SUPABASE_KEY = _resolve_supabase_creds()
except RuntimeError:
    SUPABASE_URL, SUPABASE_KEY = None, None
    _supabase_init_error = (
        "METGO: SUPABASE_KEY parece anon/publishable en production. "
        "Use service_role / sb_secret_."
    )


def guardar_registros(estacion_id: str, filas: list[dict[str, Any]], fuente: str = "openmeteo") -> int:
    client = get_supabase_client()
    rows = []
    for row in filas or []:
        fecha = str(row.get("fecha") or row.get("actualizado") or "")[:10]
        if not fecha:
            continue
        rows.append(
            {
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
        )
    if not rows:
        return 0
    if client:
        n = 0
        for data in rows:
            try:
                client.table("meteo_registros").upsert(data, on_conflict="estacion_id,fecha").execute()
                n += 1
            except Exception as e:
                print(f"Error al guardar registro en Supabase: {e}")
        return n
    return rest_upsert("meteo_registros", rows, "estacion_id,fecha")


def leer_registros(estacion_id: str, dias: int = 30) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if client:
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
            for row in res.data or []:
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
            print(f"Error al leer registros en Supabase SDK: {e}")

    raw = rest_select(
        "meteo_registros",
        params={
            "estacion_id": f"eq.{estacion_id}",
            "order": "fecha.desc",
            "select": "*",
        },
        limit=max(1, int(dias)),
    )
    out = []
    for row in raw:
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


def estadisticas_store() -> dict[str, Any]:
    url, _ = _creds_or_none()
    # Usar rest_select con timeout muy corto (3s) para evitar bloquear el /health
    # si el proyecto Supabase está pausado.
    sample = rest_select(
        "meteo_registros",
        params={"select": "estacion_id", "limit": "1"},
        limit=1,
        timeout=3,
    )
    if _rest_ok:
        return {
            "registros": 1 if sample else 0,
            "estaciones": 0,
            "db": url,
            "mode": "rest_fast",
        }
    return {
        "registros": 0,
        "estaciones": 0,
        "db": url or "supabase (inactivo)",
        "error": _supabase_init_error,
    }
    if _rest_ok:
        return {
            "registros": len(sample),
            "estaciones": 0,
            "db": url,
            "mode": "rest",
        }
    return {
        "registros": 0,
        "estaciones": 0,
        "db": "supabase (inactivo)",
        "error": _supabase_init_error,
    }
