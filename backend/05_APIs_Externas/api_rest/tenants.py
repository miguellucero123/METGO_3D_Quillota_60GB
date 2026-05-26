#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Multi-tenant regional (Fase 3.3)."""

from __future__ import annotations

import os
from typing import Any

# Organizaciones / comunas agrupadas
TENANTS: dict[str, dict[str, Any]] = {
    "quillota": {
        "id": "quillota",
        "nombre": "Valle de Aconcagua · Quillota",
        "estaciones": ["quillota", "los_nogales", "hijuelas", "limache", "olmue"],
    },
    "costa": {
        "id": "costa",
        "nombre": "Costa · Valparaíso y Viña",
        "estaciones": ["valparaiso", "vina_del_mar", "casablanca"],
    },
    "rm": {
        "id": "rm",
        "nombre": "Región Metropolitana",
        "estaciones": ["santiago"],
    },
}

USER_TENANT: dict[str, str | None] = {
    "admin": None,
    "metgo": "quillota",
    "agronomo": "quillota",
    "operador": "quillota",
    "user": "quillota",
    "lector": "quillota",
}


def tenant_de_usuario(usuario: str) -> str | None:
    """None = acceso a todos los tenants (admin)."""
    if usuario in USER_TENANT:
        return USER_TENANT[usuario]
    return os.getenv("METGO_TENANT_DEFAULT", "quillota") or "quillota"


def listar_tenants() -> list[dict[str, Any]]:
    return [
        {
            "id": t["id"],
            "nombre": t["nombre"],
            "estaciones": t["estaciones"],
            "num_estaciones": len(t["estaciones"]),
        }
        for t in TENANTS.values()
    ]


def estaciones_de_tenant(tenant_id: str | None) -> list[str]:
    if not tenant_id:
        from api_rest.services import ESTACIONES_PRINCIPALES

        return list(ESTACIONES_PRINCIPALES)
    cfg = TENANTS.get(tenant_id)
    if not cfg:
        return []
    return list(cfg["estaciones"])


def tenant_permitido(user_tenant: str | None, tenant_id: str) -> bool:
    if user_tenant is None:
        return True
    return user_tenant == tenant_id
