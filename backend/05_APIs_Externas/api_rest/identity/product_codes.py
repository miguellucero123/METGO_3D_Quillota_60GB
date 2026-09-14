#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Códigos de producto SPA (no confundir marcas).

- ``ventora`` / ``ventora_alta`` → VENTORA alta montaña (frontend/spati → metgo-spati)
- ``ventora_mar`` / ``izaje-mar`` / ``ventora-izaje-mar`` → Izaje Mar (ventora-izaje-mar)
"""

from __future__ import annotations

# SPA portuario
PRODUCTOS_IZAJE_MAR = frozenset(
    {
        "ventora_mar",
        "izaje-mar",
        "ventora-izaje-mar",
    }
)

# SPA minera (marca comercial VENTORA)
PRODUCTOS_VENTORA_ALTA = frozenset(
    {
        "ventora",
        "ventora_alta",
        "spati_izaje",
    }
)


def normalizar_producto(raw: str | None) -> str:
    return str(raw or "").strip().lower()


def es_izaje_mar(producto: str | None = None, sitio: str | None = None) -> bool:
    p = normalizar_producto(producto)
    s = normalizar_producto(sitio)
    if p in PRODUCTOS_IZAJE_MAR:
        return True
    if s in ("ventora_mar", "izaje-mar"):
        return True
    return False


def es_ventora_alta(producto: str | None = None, sitio: str | None = None) -> bool:
    p = normalizar_producto(producto)
    s = normalizar_producto(sitio)
    if p in PRODUCTOS_VENTORA_ALTA:
        return True
    # sitio=ventora histórico mal usado; si no es mar explícito, tratar como alta
    if s == "ventora" and p not in PRODUCTOS_IZAJE_MAR:
        return True
    return False


def es_familia_ventora(producto: str | None = None, sitio: str | None = None) -> bool:
    """Registro simplificado (piloto) para cualquiera de las dos líneas VENTORA."""
    return es_izaje_mar(producto, sitio) or es_ventora_alta(producto, sitio)
