#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preferencias y favoritos por usuario+sitio (E9)."""

from __future__ import annotations

from typing import Any


def _client():
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        return get_supabase_client() or None
    except Exception as exc:  # pragma: no cover
        print(f"preferencias_store: Supabase no disponible: {exc}")
        return None


def leer(usuario: str, sitio: str) -> dict[str, Any]:
    client = _client()
    empty = {
        "usuario": usuario,
        "sitio": sitio,
        "prefs": {},
        "favorites": [],
        "existe": False,
    }
    if not client or not usuario:
        return empty
    try:
        res = (
            client.table("user_preferencias")
            .select("*")
            .eq("usuario", usuario)
            .eq("sitio", sitio)
            .limit(1)
            .execute()
        )
        if not res.data:
            return empty
        row = res.data[0]
        return {
            "usuario": usuario,
            "sitio": sitio,
            "prefs": row.get("prefs") or {},
            "favorites": row.get("favorites") or [],
            "updated_at": row.get("updated_at"),
            "existe": True,
        }
    except Exception as exc:
        print(f"preferencias_store.leer: {exc}")
        return empty


def guardar(
    usuario: str,
    sitio: str,
    prefs: dict[str, Any] | None = None,
    favorites: list[Any] | None = None,
) -> bool:
    client = _client()
    if not client or not usuario:
        return False
    actual = leer(usuario, sitio)
    data = {
        "usuario": usuario,
        "sitio": sitio,
        "prefs": prefs if prefs is not None else actual.get("prefs") or {},
        "favorites": favorites if favorites is not None else actual.get("favorites") or [],
    }
    try:
        client.table("user_preferencias").upsert(
            data, on_conflict="usuario,sitio"
        ).execute()
        return True
    except Exception as exc:
        print(f"preferencias_store.guardar: {exc}")
        return False
