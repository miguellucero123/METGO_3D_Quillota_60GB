#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catálogo de planes y precios escalonados por sitio/faena.

Fuente: docs/roadmap/PRECIOS_VALOR_VS_LISTA.md
Moneda de lista: **USD**/mes (sin IVA).
Lista = ~15–25 % del valor techo del stack completo (no cobramos el 100 %).
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

# Referencia CLP solo informativa (facturación Chile / cotización)
_CLP_PER_USD = 950

# Lista USD/mes por sitio (entrada / medio / enterprise-desde). Trial siempre 0.
# Ver PRECIOS_VALOR_VS_LISTA.md — techo vs lista.
_SITE_LIST_USD: dict[str, dict[str, int]] = {
    "spati": {"starter": 299, "pro": 499, "enterprise": 1_199},
    "mantos_blancos": {"starter": 249, "pro": 449, "enterprise": 999},
    "copiapo": {"starter": 199, "pro": 399, "enterprise": 799},
    "quillota": {"starter": 99, "pro": 179, "enterprise": 399},
    "paine": {"starter": 49, "pro": 99, "enterprise": 249},
}

# Valor techo interno (referencia; no se usa para cobro)
_SITE_VALUE_CEILING_USD: dict[str, tuple[int, int]] = {
    "spati": (1_800, 3_000),
    "mantos_blancos": (1_200, 2_200),
    "copiapo": (900, 1_800),
    "quillota": (400, 800),
    "paine": (200, 500),
}

# Precio base = SPATI (fallback si sitio desconocido)
_BASE_PLANS: dict[str, dict[str, Any]] = {
    "trial": {
        "plan_code": "trial",
        "nombre": "Piloto 15 días",
        "nombre_corto": "Piloto",
        "precio_mensual_usd": 0,
        "seats": 2,
        "faenas_max": 1,
        "gruas_max": 1,
        "features": ["panel", "ambiente", "ahora"],
        "trial_days": 15,
        "canales_alerta": ["email"],
        "descripcion": "Acceso completo al sitio por 15 días, sin tarjeta.",
        "entregables": ["panel_web", "pdf_operacion"],
    },
    "starter": {
        "plan_code": "starter",
        "nombre": "Básico",
        "nombre_corto": "Básico",
        "precio_mensual_usd": 299,
        "seats": 3,
        "faenas_max": 1,
        "gruas_max": 2,
        "features": ["panel", "ambiente", "ahora", "alertas"],
        "canales_alerta": ["email"],
        "descripcion": (
            "1 sitio/faena. Panel + pronóstico, alertas por correo e informe PDF."
        ),
        "entregables": ["panel_web", "pdf_operacion", "datasheet"],
        "publico_objetivo": "Operación que necesita decidir con datos en el punto.",
    },
    "pro": {
        "plan_code": "pro",
        "nombre": "Pro",
        "nombre_corto": "Pro",
        "precio_mensual_usd": 499,
        "seats": 10,
        "faenas_max": 3,
        "gruas_max": 5,
        "features": [
            "panel",
            "ambiente",
            "ahora",
            "dron",
            "umbrales",
            "alertas",
            "reporte_mensual",
        ],
        "canales_alerta": ["email", "whatsapp"],
        "recomendado": True,
        "descripcion": (
            "Hasta 3 faenas/zonas. WhatsApp, umbrales editables, módulos avanzados "
            "y reporte mensual."
        ),
        "entregables": [
            "panel_web",
            "pdf_operacion",
            "reporte_mensual",
            "datasheet",
            "propuesta_comercial",
        ],
        "publico_objetivo": "Jefes de operaciones con flota o varias zonas activas.",
    },
    "enterprise": {
        "plan_code": "enterprise",
        "nombre": "Enterprise",
        "nombre_corto": "Enterprise",
        "precio_mensual_usd": 1_199,
        "precio_etiqueta": "desde",
        "seats": None,
        "faenas_max": None,
        "gruas_max": None,
        "features": [
            "panel",
            "ambiente",
            "ahora",
            "dron",
            "umbrales",
            "alertas",
            "reporte_mensual",
            "multi_faena",
            "api",
            "sla",
            "ops_board",
            "account_manager",
            "white_label",
            "erp_integration",
        ],
        "canales_alerta": ["email", "whatsapp", "sms"],
        "contacto": True,
        "sla_uptime": 0.995,
        "descripcion": (
            "Multi-sitio, API + webhooks, SLA 99.5%, soporte 24/7, account manager "
            "e integración ERP / white-label."
        ),
        "entregables": [
            "panel_web",
            "pdf_operacion_certificado",
            "reporte_mensual_ejecutivo",
            "datasheet_sla",
            "propuesta_comercial",
            "kit_alianza",
            "api_sandbox",
            "runbook_ops",
        ],
        "publico_objetivo": (
            "Mandantes, EPC y empresas con varias faenas o redes de estaciones."
        ),
        "incluye": [
            "Board ops multi-faena (/ops)",
            "API REST + webhooks + sandbox",
            "Hasta 5 días-hombre de integración ERP/SAP o conector BI",
            "SLA 99.5% contractual con créditos de servicio",
            "Account manager + canal 24/7",
            "Reporte mensual ejecutivo personalizado",
            "PDF con firma digital y pack legal",
            "Umbrales y destinos por faena/zona",
            "Revisión trimestral de exactitud del modelo",
        ],
        "add_ons": [
            {"codigo": "integracion_extra", "nombre": "Días-hombre integración extra"},
            {"codigo": "white_label_dominio", "nombre": "White-label dominio propio"},
            {"codigo": "iot_anemometro", "nombre": "Sensor / IoT anemómetro"},
            {"codigo": "capacitacion", "nombre": "Capacitación in-company"},
            {"codigo": "informe_pericial", "nombre": "Informe pericial / caso legal"},
        ],
    },
    "preview": {
        "plan_code": "preview",
        "nombre": "Vista previa 1 h",
        "nombre_corto": "Preview",
        "precio_mensual_usd": 0,
        "seats": 1,
        "faenas_max": 1,
        "gruas_max": 1,
        "features": ["panel", "ahora"],
        "trial_days": 0,
        "hidden": True,
        "ttl_hours": 1,
        "canales_alerta": [],
        "descripcion": "Solo Ahora + Panel técnico. Expira en 1 hora y se elimina.",
        "entregables": ["panel_web"],
    },
}

_FAENA_MULTIPLIER: dict[str, float] = {
    "escondida": 1.25,
    "los_bronces": 1.15,
    "collahuasi": 1.2,
    "andina": 1.1,
    "el_teniente": 1.15,
}

_PLAN_RANK = {"preview": 0, "trial": 0, "starter": 1, "pro": 2, "enterprise": 3}

TAB_FEATURE = {
    "panel": "panel",
    "ahora": "ahora",
    "dron": "dron",
    "umbrales": "umbrales",
    "ambiente": "ambiente",
}

TAB_SISTEMA = {
    "panel": "izaje",
    "ahora": "izaje",
    "dron": "dron",
    "umbrales": "ops",
    "ambiente": "ambiente",
}


def plan_rank(code: str | None) -> int:
    return _PLAN_RANK.get((code or "trial").lower(), 0)


def _lista_usd_sitio(sitio: str) -> dict[str, int]:
    key = (sitio or "spati").strip().lower()
    return dict(_SITE_LIST_USD.get(key) or _SITE_LIST_USD["spati"])


def listar_planes(sitio: str, faena: str | None = None) -> dict[str, Any]:
    sitio_l = (sitio or "spati").strip().lower()
    lista = _lista_usd_sitio(sitio_l)
    mult = _FAENA_MULTIPLIER.get((faena or "").lower(), 1.0) if sitio_l == "spati" else 1.0
    ceiling = _SITE_VALUE_CEILING_USD.get(sitio_l) or _SITE_VALUE_CEILING_USD["spati"]
    planes = []
    for code, p in _BASE_PLANS.items():
        if p.get("hidden"):
            continue
        item = deepcopy(p)
        if code == "trial":
            usd = 0
        elif code in lista:
            usd = int(round(lista[code] * mult))
        else:
            base_usd = p.get("precio_mensual_usd") or 0
            usd = int(round(base_usd * mult))
        item["precio_mensual_usd"] = usd
        item["precio_mensual_clp"] = int(round(usd * _CLP_PER_USD))
        item["precio_display"] = f"USD {usd:,}".replace(",", ".")
        item["multiplicador_faena"] = mult
        item["moneda"] = "USD"
        item["iva"] = "no_incluido"
        planes.append(item)
    return {
        "sitio": sitio_l,
        "faena": faena,
        "moneda": "USD",
        "iva": "no_incluido",
        "valor_techo_usd": {"min": ceiling[0], "max": ceiling[1]},
        "nota": (
            "Precios de lista en USD (sin IVA), ~15–25 % del valor del stack completo. "
            "Enterprise: cotización a medida. Chile puede liquidar en CLP al tipo del día. "
            "Detalle: docs/roadmap/PRECIOS_VALOR_VS_LISTA.md"
        ),
        "planes": planes,
    }


def features_for_plan(plan_code: str) -> set[str]:
    p = _BASE_PLANS.get((plan_code or "trial").lower()) or _BASE_PLANS["trial"]
    return set(p.get("features") or [])


def trial_days() -> int:
    try:
        return max(1, int((_BASE_PLANS.get("trial") or {}).get("trial_days") or 15))
    except (TypeError, ValueError):
        return 15
