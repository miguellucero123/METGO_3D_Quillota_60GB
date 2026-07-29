#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catálogo de planes y precios escalonados por sitio/faena."""

from __future__ import annotations

from typing import Any

# Precio base CLP/mes por plan (referencia MVP; Stripe Price IDs vía env en S2)
_BASE_PLANS: dict[str, dict[str, Any]] = {
    "trial": {
        "plan_code": "trial",
        "nombre": "Prueba 14 días",
        "precio_mensual_clp": 0,
        "seats": 1,
        "features": ["panel", "ambiente"],
        "trial_days": 14,
    },
    "starter": {
        "plan_code": "starter",
        "nombre": "Starter",
        "precio_mensual_clp": 149_000,
        "seats": 3,
        "features": ["panel", "ambiente", "dron"],
    },
    "pro": {
        "plan_code": "pro",
        "nombre": "Pro",
        "precio_mensual_clp": 399_000,
        "seats": 10,
        "features": ["panel", "ambiente", "dron", "umbrales", "alertas"],
    },
    "enterprise": {
        "plan_code": "enterprise",
        "nombre": "Enterprise",
        "precio_mensual_clp": None,
        "seats": None,
        "features": ["panel", "ambiente", "dron", "umbrales", "alertas", "multi_faena", "sla"],
        "contacto": True,
    },
}

# Multiplicador comercial por faena (escalado; 1.0 = base)
_FAENA_MULTIPLIER: dict[str, float] = {
    "escondida": 1.25,
    "los_bronces": 1.15,
    "collahuasi": 1.2,
    "andina": 1.1,
    "el_teniente": 1.15,
}

_PLAN_RANK = {"trial": 0, "starter": 1, "pro": 2, "enterprise": 3}

# Mapeo tab SPA → feature / sistema
TAB_FEATURE = {
    "panel": "panel",
    "dron": "dron",
    "umbrales": "umbrales",
    "ambiente": "ambiente",
}

TAB_SISTEMA = {
    "panel": "izaje",
    "dron": "dron",
    "umbrales": "ops",
    "ambiente": "ambiente",
}


def plan_rank(code: str | None) -> int:
    return _PLAN_RANK.get((code or "trial").lower(), 0)


def listar_planes(sitio: str, faena: str | None = None) -> dict[str, Any]:
    mult = _FAENA_MULTIPLIER.get((faena or "").lower(), 1.0) if sitio == "spati" else 1.0
    planes = []
    for code, p in _BASE_PLANS.items():
        item = dict(p)
        base = p.get("precio_mensual_clp")
        if base is not None:
            item["precio_mensual_clp"] = int(round(base * mult))
        item["multiplicador_faena"] = mult
        planes.append(item)
    return {
        "sitio": sitio,
        "faena": faena,
        "moneda": "CLP",
        "planes": planes,
    }


def features_for_plan(plan_code: str) -> set[str]:
    p = _BASE_PLANS.get((plan_code or "trial").lower()) or _BASE_PLANS["trial"]
    return set(p.get("features") or [])
