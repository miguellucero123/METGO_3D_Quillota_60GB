#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Multi-tenant por producto/sitio (E9).

Complementa el mapa geográfico legacy (`tenants.py`: quillota|costa|rm) con el
catálogo de productos METGO (`estaciones_catalogo.SITIOS`):
quillota | paine | copiapo | mantos_blancos | demo.

- `sitio=None` (solo admin global): acceso a todos los sitios.
- Resto de usuarios: un sitio fijo (membresía).
"""

from __future__ import annotations

import json
import os
from typing import Any

from api_rest.estaciones_catalogo import ESTACIONES_POR_SITIO, SITIOS, SITIOS_META, normalizar_sitio

# Membresía por defecto (demo). Override: METGO_USER_SITIO_JSON='{"metgo":"quillota"}'
USER_SITIO: dict[str, str | None] = {
    "admin": None,  # admin global
    "metgo": "quillota",
    "agronomo": "quillota",
    "operador": "quillota",
    "user": "quillota",
    "lector": "quillota",
    "copiapo": "copiapo",
    "mantos": "mantos_blancos",
    "paine": "paine",
}


def _overrides() -> dict[str, str | None]:
    raw = (os.getenv("METGO_USER_SITIO_JSON") or "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            return {}
        out: dict[str, str | None] = {}
        for k, v in data.items():
            key = str(k).lower().strip()
            if v is None or str(v).strip() in ("", "*", "all", "none"):
                out[key] = None
            else:
                out[key] = normalizar_sitio(str(v))
        return out
    except (json.JSONDecodeError, TypeError, ValueError):
        return {}


def sitios_validos() -> tuple[str, ...]:
    return tuple(SITIOS)


def sitio_conocido(sitio: str | None) -> bool:
    if sitio is None:
        return True
    return sitio in ESTACIONES_POR_SITIO


def sitio_de_usuario(usuario: str) -> str | None:
    """None = acceso a todos los sitios (admin global)."""
    u = (usuario or "").lower().strip()
    overrides = _overrides()
    if u in overrides:
        return overrides[u]
    if u in USER_SITIO:
        return USER_SITIO[u]
    # Registrados / desconocidos: default de producto
    return normalizar_sitio(os.getenv("METGO_SITIO_DEFAULT", "quillota"))


def resolver_sitio_login(usuario: str, solicitado: str | None) -> tuple[str | None, str | None]:
    """Devuelve (sitio_efectivo, error).

    - Admin global (membresía None): puede pedir cualquier sitio o None (todos).
    - Usuario de sitio: solo su sitio (si pide otro → error).
    """
    membresia = sitio_de_usuario(usuario)
    sol = (solicitado or "").strip().lower() or None
    if sol in ("*", "all", "todos"):
        sol = None

    if sol is not None and sol not in ESTACIONES_POR_SITIO:
        return None, f"Sitio desconocido: {sol}"

    if membresia is None:
        # Admin global: token puede quedar scoped al sitio pedido
        return sol, None

    if sol is None:
        return membresia, None
    if sol != membresia:
        return None, f"Sin acceso al sitio '{sol}' (membresía: {membresia})"
    return membresia, None


def sitio_permitido(user_sitio: str | None, recurso_sitio: str) -> bool:
    """¿Puede el usuario acceder a un recurso de `recurso_sitio`?"""
    if user_sitio is None:
        return True
    return user_sitio == normalizar_sitio(recurso_sitio)


def estacion_permitida(user_sitio: str | None, estacion_id: str) -> bool:
    """¿Puede el JWT acceder a datos de esta estación?"""
    if user_sitio is None:
        return True
    from api_rest.estaciones_catalogo import sitio_de_estacion

    dueño = sitio_de_estacion(estacion_id)
    if dueño is None:
        # Estaciones fuera del catálogo multi-sitio: solo admin global
        return False
    return sitio_permitido(user_sitio, dueño)


def estaciones_de_sitio(sitio: str | None) -> list[str]:
    if sitio is None:
        # Unión de todos los sitios activos (sin plantilla demo si se desea filtrar)
        out: list[str] = []
        for slug, ests in ESTACIONES_POR_SITIO.items():
            if slug == "demo":
                continue
            out.extend(ests)
        return out
    return list(ESTACIONES_POR_SITIO.get(normalizar_sitio(sitio), []))


def listar_sitios_auth(incluir_plantilla: bool = False) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for slug in SITIOS:
        meta = dict(SITIOS_META.get(slug, {"slug": slug, "nombre": slug}))
        if not incluir_plantilla and meta.get("estado") == "plantilla":
            continue
        meta["estaciones"] = list(ESTACIONES_POR_SITIO.get(slug, []))
        meta["num_estaciones"] = len(meta["estaciones"])
        out.append(meta)
    return out
