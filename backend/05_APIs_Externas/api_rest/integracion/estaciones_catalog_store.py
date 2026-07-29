#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M8 — sync catálogo faena → public.estaciones (FK aire_registros)."""

from __future__ import annotations

from typing import Any


def _client():
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        return get_supabase_client() or None
    except Exception as exc:  # pragma: no cover
        print(f"estaciones_catalog_store: Supabase no disponible: {exc}")
        return None


def filas_desde_catalogo(*, solo_faena: str | None = None) -> list[dict[str, Any]]:
    """IDs únicos de estaciones_area (+ anclas con coords) para public.estaciones."""
    from api_rest.faena_catalogo import get_faena, listar_faenas

    faenas = listar_faenas(incluir_izaje=True)
    if solo_faena:
        f = get_faena(solo_faena)
        faenas = [f] if f else []

    seen: dict[str, dict[str, Any]] = {}
    for faena in faenas:
        if not faena:
            continue
        sitio = str(faena.get("sitio") or faena["id"])
        for e in faena.get("estaciones_area") or []:
            eid = str(e.get("id") or "").strip()
            if not eid or eid in seen:
                continue
            lat, lon = e.get("lat"), e.get("lon")
            if lat is None or lon is None:
                continue
            seen[eid] = {
                "id": eid,
                "nombre": e.get("nombre") or eid,
                "sitio": sitio,
                "lat": float(lat),
                "lon": float(lon),
                "activa": True,
            }
        ancla = faena.get("estacion_ancla")
        if (
            ancla
            and str(ancla) not in seen
            and faena.get("lat") is not None
            and faena.get("lon") is not None
        ):
            seen[str(ancla)] = {
                "id": str(ancla),
                "nombre": faena.get("nombre") or ancla,
                "sitio": sitio,
                "lat": float(faena["lat"]),
                "lon": float(faena["lon"]),
                "activa": True,
            }
    return list(seen.values())


def upsert_estaciones(filas: list[dict[str, Any]]) -> int:
    client = _client()
    if not client or not filas:
        return 0
    try:
        client.table("estaciones").upsert(filas, on_conflict="id").execute()
        return len(filas)
    except Exception as exc:
        print(f"estaciones_catalog_store.upsert: {exc}")
        return 0


def sincronizar_estaciones_publicas(*, solo_faena: str | None = None) -> dict[str, Any]:
    """Upsert public.estaciones desde catálogo multi-faena (M8)."""
    filas = filas_desde_catalogo(solo_faena=solo_faena)
    n = upsert_estaciones(filas)
    return {
        "fase": "M8",
        "puntos": n,
        "catalogo": len(filas),
        "supabase": bool(_client()),
        "solo_faena": solo_faena,
    }


def marcar_fuente_observado(estacion_ids: list[str]) -> int:
    """Marca faena_estaciones_area.fuente='observado' para IDs con SINCA/CSV."""
    client = _client()
    ids = [str(i).strip() for i in estacion_ids if i]
    if not client or not ids:
        return 0
    try:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).isoformat()
        n = 0
        for eid in ids:
            client.table("faena_estaciones_area").update(
                {"fuente": "observado", "synced_at": now}
            ).eq("id", eid).execute()
            n += 1
        return n
    except Exception as exc:
        print(f"estaciones_catalog_store.marcar_observado: {exc}")
        return 0
