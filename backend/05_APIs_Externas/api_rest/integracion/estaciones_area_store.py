#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Persistencia estaciones por área de faena (M4 → faena_estaciones_area)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _client():
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        return get_supabase_client() or None
    except Exception as exc:  # pragma: no cover
        print(f"estaciones_area_store: Supabase no disponible: {exc}")
        return None


def _row_to_dict(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "faena_id": row.get("faena_id"),
        "nombre": row.get("nombre"),
        "rol": row.get("rol"),
        "lat": row.get("lat"),
        "lon": row.get("lon"),
        "altitud_m": row.get("altitud_m"),
        "fuente": row.get("fuente") or "modelo",
        "activa": row.get("activa", True),
        "synced_at": row.get("synced_at"),
    }


def leer_estaciones_area(faena_id: str | None = None) -> list[dict[str, Any]]:
    client = _client()
    if not client:
        return []
    try:
        q = client.table("faena_estaciones_area").select("*").eq("activa", True)
        if faena_id:
            q = q.eq("faena_id", faena_id)
        res = q.order("faena_id").order("rol").execute()
        return [_row_to_dict(r) for r in (res.data or [])]
    except Exception as exc:
        print(f"estaciones_area_store.leer: {exc}")
        return []


def upsert_estaciones_area(filas: list[dict[str, Any]]) -> int:
    client = _client()
    if not client or not filas:
        return 0
    now = datetime.now(timezone.utc).isoformat()
    registros = []
    for f in filas:
        eid = f.get("id")
        fid = f.get("faena_id")
        if not eid or not fid:
            continue
        registros.append(
            {
                "id": eid,
                "faena_id": fid,
                "nombre": f.get("nombre") or eid,
                "rol": f.get("rol") or "otro",
                "lat": float(f["lat"]),
                "lon": float(f["lon"]),
                "altitud_m": f.get("altitud_m"),
                "fuente": f.get("fuente") or "modelo",
                "activa": bool(f.get("activa", True)),
                "synced_at": now,
            }
        )
    if not registros:
        return 0
    try:
        client.table("faena_estaciones_area").upsert(
            registros, on_conflict="id"
        ).execute()
        return len(registros)
    except Exception as exc:
        print(f"estaciones_area_store.upsert: {exc}")
        return 0


def sincronizar_desde_catalogo(*, solo_faena: str | None = None) -> dict[str, Any]:
    """Upsert puntos del catálogo código → Supabase."""
    from api_rest.faena_catalogo import get_faena, listar_faenas

    faenas = listar_faenas(incluir_izaje=True)
    if solo_faena:
        f = get_faena(solo_faena)
        faenas = [f] if f else []

    filas: list[dict[str, Any]] = []
    for faena in faenas:
        if not faena:
            continue
        fid = faena["id"]
        for e in faena.get("estaciones_area") or []:
            filas.append(
                {
                    "id": e["id"],
                    "faena_id": fid,
                    "nombre": e.get("nombre"),
                    "rol": e.get("rol") or "otro",
                    "lat": e.get("lat"),
                    "lon": e.get("lon"),
                    "altitud_m": faena.get("altitud_m"),
                    "fuente": e.get("fuente") or "modelo",
                    "activa": True,
                }
            )

    n = upsert_estaciones_area(filas)
    return {
        "faenas": len(faenas),
        "puntos": n,
        "supabase": bool(_client()),
        "solo_faena": solo_faena,
    }
